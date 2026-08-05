import json


EMPLOYEE_FILE = "data/employees.json"


def load_employees():
    """
    Load all employees from JSON
    """

    with open(EMPLOYEE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_employee(employee_id):
    """
    Return one employee
    """

    employees = load_employees()

    for emp in employees:

        if emp["employee_id"] == employee_id:
            return emp

    return None


def get_departments():
    """
    Return unique departments
    """

    employees = load_employees()

    return sorted(
        list(
            set(emp["department"] for emp in employees)
        )
    )


def search_employee(keyword):
    """
    Search by employee name
    """

    employees = load_employees()

    keyword = keyword.lower()

    return [

        emp

        for emp in employees

        if keyword in emp["name"].lower()

    ]


def filter_department(department):
    """
    Filter employees by department
    """

    employees = load_employees()

    if department == "All":
        return employees

    return [

        emp

        for emp in employees

        if emp["department"] == department

    ]