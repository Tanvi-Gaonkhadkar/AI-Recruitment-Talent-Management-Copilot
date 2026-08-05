"""
scope_guard.py
Layered scope-detection for the AI Recruitment Assistant.

Adapted to this project's actual interfaces:
- ask_llama(prompt: str) -> str            (single prompt string, no kwargs)
- chat_history: list[tuple[str, str]]      (role, message) pairs

Pipeline (each layer only runs if the previous one didn't decide):
  1. ALLOW keywords     -> fast, high-recall recruitment vocabulary
  2. Continuity check   -> "rewrite this", "make it shorter", etc. inherit
                            scope from the previous turn
  3. BLOCK keywords      -> catches obvious off-topic asks
  4. LLM tie-breaker     -> only for what's left. Few-shot, JSON-only output,
                            fails OPEN (defaults to allow) on any error --
                            because by this layer, off-topic is unlikely,
                            and wrongly blocking a real recruiter question
                            is the worse failure mode.
"""

import re
import json

from backend.ollama_client import ask_llama

OUT_OF_SCOPE_MESSAGE = """
❌ Out of Scope

I am an AI Recruitment & Talent Acquisition Assistant.

Please ask a recruitment-related question.
"""


# ---------------------------------------------------------------------------
# Layer 1: ALLOW keywords
# ---------------------------------------------------------------------------
ALLOW_PATTERNS = [
    r"\bresume(s)?\b", r"\bcv\b", r"\bcandidate(s)?\b", r"\bapplicant(s)?\b",
    r"\bscreen(ing)?\b", r"\bshortlist(ed|ing)?\b", r"\brank(ed|ing)?\b",
    r"\bcompare\b", r"\bcomparison\b", r"\bats\b", r"\bmatch(ing)?\s*score\b",
    r"\bskill(s)?\s*gap\b", r"\bhiring\b", r"\bhire(d)?\b", r"\brecruit(er|ment|ing)?\b",
    r"\bjob\s*description\b", r"\bjd\b", r"\binterview(s|ing|er)?\b",
    r"\boffer\s*letter\b", r"\brejection\s*(email|letter)?\b", r"\bonboard(ing)?\b",
    r"\btalent\b", r"\bhr\b", r"\bhuman\s*resources\b", r"\bexperience\s*level\b",
    r"\bqualif(y|ied|ication)\b", r"\beducation\s*background\b", r"\bwork\s*history\b",
    r"\btechnical\s*round\b", r"\bhiring\s*manager\b", r"\bfeedback\s*on\s*candidate\b",
    r"\bsalary\s*negotiat\w*\b", r"\bpipeline\b", r"\bheadcount\b",
    r"\bdiversity\s*hiring\b", r"\bemployee\s*referral\b", r"\bnotice\s*period\b",
    r"\bwork\s*experience\b", r"\bpanel\s*interview\b", r"\bstrengths?\s*and\s*weaknesses\b",
    r"\bemail\b", r"\bfollow[\s-]up\b", r"\bcompensation\b", r"\bjob\s*fit\b",
    r"\bbest\s*practices\b", r"\banalytics\b", r"\bdashboard\b", r"\brejection\b", r"\boffer\b"
]
ALLOW_REGEX = re.compile("|".join(ALLOW_PATTERNS), re.IGNORECASE)


# ---------------------------------------------------------------------------
# Layer 2: Conversation continuity
# ---------------------------------------------------------------------------
FOLLOWUP_PATTERNS = [
    r"^rewrite\b", r"^edit\b", r"^shorten\b", r"^make\s+it\b", r"^improve\s+(it|this)\b",
    r"^fix\s+(it|this)\b", r"^change\s+the\s+tone\b", r"^formal(ize)?\s+it\b",
    r"^summari[sz]e\s+(it|this)\b", r"^expand\s+(it|this|on)\b", r"^tone\s+it\b",
    r"\bthis\s+email\b", r"\bthat\s+email\b", r"\babove\s+response\b",
    r"^regenerate\b", r"^redo\b", r"^polish\b", r"^professional(ize)?\s+it\b",
]
FOLLOWUP_REGEX = re.compile("|".join(FOLLOWUP_PATTERNS), re.IGNORECASE)


def _last_turn_was_in_scope(chat_history):
    """chat_history is a list of (role, msg) tuples. Walk backwards to find
    the last assistant turn and check whether it was the Out-of-Scope reply."""
    if not chat_history:
        return False
    for role, msg in reversed(chat_history):
        if role.lower() == "assistant":
            return "Out of Scope" not in msg
    return False


def _is_followup(question, chat_history):
    if not FOLLOWUP_REGEX.search(question.strip()):
        return False
    return _last_turn_was_in_scope(chat_history)


# ---------------------------------------------------------------------------
# Layer 3: BLOCK keywords
# ---------------------------------------------------------------------------
BLOCK_PATTERNS = [
    r"\bjoke\b", r"\bweather\b", r"\bcapital\s+of\b", r"\bcricket\b", r"\bfootball\b",
    r"\bmovie\b", r"\brecipe\b", r"\bpoem\s+about\b", r"\btranslate\b",
    r"\bpython\s+function\b", r"\bwrite\s+(a\s+)?code\b", r"\bdebug\s+my\b",
    r"\bsolve\s+(this\s+)?equation\b", r"\bnews\s+today\b", r"\bstock\s+price\b",
    r"\bwho\s+won\b", r"\bcelebrity\b", r"\bhoroscope\b",r"\bscript\b",
]
BLOCK_REGEX = re.compile("|".join(BLOCK_PATTERNS), re.IGNORECASE)


# ---------------------------------------------------------------------------
# Layer 4: LLM tie-breaker (only reached for genuinely ambiguous queries)
# ---------------------------------------------------------------------------
CLASSIFIER_PROMPT_TEMPLATE = """You are a strict binary classifier for a Recruitment & Talent Acquisition Assistant.
Decide if the USER QUESTION belongs to the recruitment/HR/hiring domain.

IN-SCOPE includes: resumes, candidates, screening, ATS, shortlisting, ranking,
comparing candidates, skill-gap analysis, hiring recommendations, recruitment
analytics, job descriptions, interview planning/questions, HR emails (offer,
rejection, onboarding), general hiring/recruitment process advice.

OUT-OF-SCOPE includes: sports, jokes, general coding help, geography, movies,
weather, general trivia, or anything unrelated to hiring/recruitment.

Respond with ONLY compact JSON, nothing else:
{{"in_scope": true}} or {{"in_scope": false}}

Examples:
Q: Who is the least skilled candidate?
{{"in_scope": true}}

Q: Generate a rejection email for a candidate.
{{"in_scope": true}}

Q: How can I improve our hiring process?
{{"in_scope": true}}

Q: What's the capital of France?
{{"in_scope": false}}

Q: Tell me a joke.
{{"in_scope": false}}

Q: Write a Python function to sort a list.
{{"in_scope": false}}

Q: {question}
"""


def _classify_with_llm(question):
    try:
        raw = ask_llama(CLASSIFIER_PROMPT_TEMPLATE.format(question=question))
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return True  # fail-open
        data = json.loads(match.group(0))
        return bool(data.get("in_scope", True))
    except Exception:
        return True  # fail-open: never let a classifier bug block a real user


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def is_in_scope(question, chat_history=None, document_context=""):
    chat_history = chat_history or []

    if ALLOW_REGEX.search(question):
        return True

    if _is_followup(question, chat_history):
        return True

    if document_context and document_context.strip() and FOLLOWUP_REGEX.search(question):
        return True

    if BLOCK_REGEX.search(question) and not ALLOW_REGEX.search(question):
        return False

    return _classify_with_llm(question)