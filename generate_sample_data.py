"""
Generates fictional sample source files so the demo can run end-to-end
without any real client data. Re-run any time to get a fresh dummy dataset.
"""
import random
from datetime import date, timedelta
import pandas as pd

random.seed(42)

FIRST = ["Ava", "Noah", "Mia", "Leo", "Zoe", "Ivan", "Priya", "Omar", "Yuki", "Sofia",
         "Liam", "Elena", "Kai", "Nina", "Diego", "Amara", "Felix", "Rosa", "Theo", "Lena"]
LAST = ["Mercer", "Lindqvist", "Okafor", "Tanaka", "Novak", "Alvarez", "Byrne", "Kowalski",
        "Singh", "Costa", "Fischer", "Duarte", "Haddad", "Petrov", "Reyes"]

COUNTRIES = [
    ("Germany", "EMEA", "A. Kowalski"),
    ("Netherlands", "EMEA", "T. Byrne"),
    ("France", "EMEA", "M. Costa"),
    ("Spain", "EMEA", "M. Costa"),
    ("United States", "NAMER", "J. Alvarez"),
    ("Canada", "NAMER", "R. Singh"),
    ("Mexico", "NAMER", "R. Singh"),
    ("India", "APAC", "R. Singh"),
    ("Japan", "APAC", "R. Singh"),
    ("Australia", "APAC", "R. Singh"),
]

DEPTS = ["sales of mumbai", "engineering platform", "finance shared services",
         "customer support emea", "marketing digital", "operations logistics",
         "human resources", "it infrastructure"]

JOB_NAMES = ["Analyst", "Senior Analyst", "Associate Manager", "Manager", "Specialist", "Coordinator"]
INCENTIVE_PROGS = ["SALES", "STI", "COMMISSION"]
CURRENCY_BY_COUNTRY = {"Germany": "EUR", "Netherlands": "EUR", "France": "EUR", "Spain": "EUR",
                        "United States": "USD", "Canada": "CAD", "Mexico": "MXN",
                        "India": "INR", "Japan": "JPY", "Australia": "AUD"}


def rand_date(start_year=2018, end_year=2025):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))


def gen_people(n):
    people = []
    for i in range(1, n + 1):
        first, last = random.choice(FIRST), random.choice(LAST)
        country, region, distributee = random.choice(COUNTRIES)
        dept_id = str(random.randint(100, 199))
        dept_name = random.choice(DEPTS)
        people.append({
            "person_number": f"P{10000+i}",
            "first_name": first,
            "last_name": last,
            "display_name": f"{first} {last}",
            "country": country,
            "region": region,
            "distributee": distributee,
            "dept_full": f"{dept_id} {dept_name}",
            "job_name": random.choice(JOB_NAMES),
            "incentive_prog": random.choice(INCENTIVE_PROGS),
            "salary": random.randint(45000, 140000),
            "currency": CURRENCY_BY_COUNTRY[country],
            "dob": rand_date(1970, 2000),
            "hire_date": rand_date(2015, 2025),
            "seniority_date": rand_date(2015, 2025),
            "gender": random.choice(["M", "F"]),
            "grade": random.choice(["G5", "G6", "G7", "G8"]),
        })
    return people


PEOPLE = gen_people(90)


def build_comp_roster():
    rows = []
    for p in PEOPLE:
        rows.append({
            "Person Number": p["person_number"],
            "Display Name": p["display_name"],
            "Grade Code": p["grade"],
            "Incentive Prog": p["incentive_prog"],
            "Incentive Target %": random.choice([0.1, 0.15, 0.2, 0.25]),
            "Legislation": p["country"],
            "Level 01 Organization Name": "Global Operations",
            "Location Name": p["country"],
            "Department Name": p["dept_full"],
            "Department Set Name": "Standard",
            "Annualized Salary": p["salary"],
            "Salary Currency": p["currency"],
            "Regular/Temporary": "Regular",
            "Seniority Date": p["seniority_date"],
        })
    return pd.DataFrame(rows)


def build_distribution_list():
    seen = {}
    for c, r, d in COUNTRIES:
        seen[c] = (r, d)
    rows = [{"Legislation": c, "Region": r, "Distributee": d} for c, (r, d) in seen.items()]
    return pd.DataFrame(rows)


def build_functional_info(subset):
    rows = []
    for p in subset:
        rows.append({
            "Person Number": p["person_number"],
            "First Name": p["first_name"],
            "Last Name": p["last_name"],
            "Job Name": p["job_name"],
            "Cost Center ID": f"CC-{random.randint(1000,1999)}",
            "Annualized Salary": p["salary"],
            "Location Name": p["country"],
            "Person Gender": p["gender"],
            "Hire Date": p["hire_date"],
            "Work Email": f"{p['first_name'].lower()}.{p['last_name'].lower()}@example-corp.com",
            "Business Unit Name": "Example Corp " + p["region"],
            "Legal Employer Name": "Example Corp " + p["region"],
        })
    return pd.DataFrame(rows)


def build_personal_info(subset):
    rows = [{"Person Number": p["person_number"], "Person Date of Birth": p["dob"]} for p in subset]
    return pd.DataFrame(rows)


def build_terminations(subset):
    rows = []
    for p in subset:
        rows.append({
            "Person Number": p["person_number"],
            "Person Name": p["display_name"],
            "Last day in service": rand_date(2025, 2026),
            "Job Name": p["job_name"],
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "sample_data")
    os.makedirs(out, exist_ok=True)

    build_comp_roster().to_excel(f"{out}/comp_roster.xlsx", index=False)
    build_distribution_list().to_excel(f"{out}/distribution_list.xlsx", index=False)

    new_hires = PEOPLE[:12]
    leavers = PEOPLE[12:20]
    prior_month_people = PEOPLE[20:]

    build_functional_info(new_hires).to_excel(f"{out}/functional_info.xlsx", index=False)
    build_personal_info(new_hires).to_excel(f"{out}/personal_info.xlsx", index=False)
    build_terminations(leavers).to_excel(f"{out}/terminations.xlsx", index=False)
    build_functional_info(prior_month_people + leavers).to_excel(f"{out}/prior_month_functional_info.xlsx", index=False)

    print("Sample data generated in", out)
