
import streamlit as st
import pandas as pd
import plotly.express as px

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Login.py")
st.set_page_config(page_title="Hiring Analytics", page_icon="📊", layout="wide")

st.title("📊 Hiring Analytics")
st.caption("Business Intelligence dashboard for recruitment performance (Frontend Prototype).")

with st.sidebar:
    st.header("🤖 Analytics AI")
    st.success("Recruitment Analysis AI")
    st.success("Talent Insight AI")
    st.success("Hiring Forecast AI")
    st.success("Executive Summary AI")
    st.info("Dummy AI outputs • No backend")

f1,f2,f3=st.columns(3)
with f1:
    st.selectbox("📅 Time Period",["Last 30 Days","Last 3 Months","Last 6 Months","Last Year"])
with f2:
    st.selectbox("🏢 Department",["All","AI","Backend","Frontend","Data Science","QA"])
with f3:
    st.selectbox("👤 Recruiter",["All Recruiters","Rahul","Sneha","Aditi","Rohan"])

st.divider()

m1,m2,m3,m4=st.columns(4)
m1.metric("Avg. Time to Hire","16 Days","-2 Days")
m2.metric("Offer Acceptance","84%","+3%")
m3.metric("Cost per Hire","₹18,000","-12%")
m4.metric("Recruitment Efficiency","88%","+5%")

dept=pd.DataFrame({
    "Department":["AI","Backend","Frontend","Data Science","QA"],
    "Hires":[28,22,18,15,10]
})
trend=pd.DataFrame({
    "Month":["Jan","Feb","Mar","Apr","May","Jun"],
    "Days":[20,19,18,17,16,16]
})

c1,c2=st.columns(2)
with c1:
    fig=px.bar(dept,x="Department",y="Hires",color="Department",
               title="🏢 Department-wise Hiring")
    st.plotly_chart(fig,width="stretch")
with c2:
    fig=px.line(trend,x="Month",y="Days",markers=True,
                title="📈 Time-to-Hire Trend")
    st.plotly_chart(fig,width="stretch")

pipeline=pd.DataFrame({
    "Stage":["Resume","Screening","Interview","Offer","Joining"],
    "Days":[2,3,8,5,2]
})
offer=pd.DataFrame({
    "Month":["Jan","Feb","Mar","Apr","May","Jun"],
    "Acceptance":[78,80,81,82,84,84]
})

c1,c2=st.columns(2)
with c1:
    fig=px.bar(pipeline,x="Stage",y="Days",color="Stage",
               title="🚦 Pipeline Bottleneck Analysis")
    st.plotly_chart(fig,width="stretch")
with c2:
    fig=px.line(offer,x="Month",y="Acceptance",markers=True,
                title="🎯 Offer Acceptance Trend")
    st.plotly_chart(fig,width="stretch")

st.subheader("🏆 Recruiter Performance")
perf=pd.DataFrame({
    "Recruiter":["Rahul","Sneha","Aditi","Rohan"],
    "Candidates Hired":[18,15,13,11],
    "Avg Time":["16 Days","19 Days","18 Days","22 Days"],
    "Acceptance":["92%","87%","85%","81%"]
})
st.dataframe(perf,hide_index=True,width="stretch")

tabs=st.tabs([
    "🤖 Recruitment Analysis AI",
    "📈 Talent Insight AI",
    "🔮 Hiring Forecast AI",
    "📝 Executive Summary"
])

with tabs[0]:
    st.success("""
### Recruitment Analysis

**Key Findings**
- Interview stage is the biggest hiring bottleneck.
- Backend hiring takes ~25% longer than AI hiring.
- Employee referrals show the highest conversion rate.

**AI Recommendation**
- Increase technical interview slots.
- Expand LinkedIn sourcing for Backend roles.
- Prioritize candidates with Docker & AWS skills.
""")
    st.progress(88,text="Overall Recruitment Health")

with tabs[1]:
    a,b=st.columns(2)
    with a:
        st.subheader("Emerging Skills")
        for s in ["GenAI","FastAPI","Docker","Kubernetes","LangChain","AWS"]:
            st.warning(s)
    with b:
        st.subheader("Talent Insights")
        st.info("""
• Demand for AI Engineers continues to rise.
• Cloud-native skills are becoming mandatory.
• Candidates with CI/CD experience move faster through hiring.
• Data Science hiring remains stable.
""")

with tabs[2]:
    c1,c2,c3=st.columns(3)
    c1.metric("Expected Applications","210")
    c2.metric("Expected Hires","28")
    c3.metric("Forecast Confidence","91%")
    st.info("""
### Next Month Forecast
- High-demand roles: AI Engineer, Backend Developer, Data Scientist
- Expect increased competition for cloud-skilled candidates.
- Referral hiring is projected to improve offer acceptance.
""")

with tabs[3]:
    st.success("""
### AI Executive Summary

Recruitment performance has improved over the past six months.

Business Highlights:
- Average hiring time reduced from 20 to 16 days.
- Offer acceptance stabilized above 84%.
- AI department continues to lead hiring volume.
- Recruiter Rahul recorded the best conversion rate.

Recommended Business Actions:
1. Reduce interview bottlenecks.
2. Increase sourcing for Backend and Cloud roles.
3. Continue investing in employee referrals.
""")

st.download_button(
    "📥 Download Executive Analytics Report",
    data="Dummy Executive Hiring Analytics Report",
    file_name="Hiring_Analytics_Report.txt",
    width="stretch"
)
