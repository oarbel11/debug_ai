import duckdb
import os

# Define path: The database resides in the current directory (companies_data)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "corporate.duckdb")


def create_raw_layer():
    # Delete old database if exists (to start fresh)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    print(f"🏗️ Creating RAW layer in: {DB_PATH}")

    # 1. Companies Table
    con.execute("""
    CREATE OR REPLACE TABLE raw.companies AS SELECT * FROM (VALUES
        (1, 'TechGlobal', 'New York', 'Software'),
        (2, 'MoneyCorp', 'London', 'Finance'),
        (3, 'HealthPlus', 'Tel Aviv', 'Healthcare'),
        (4, 'CyberShield', 'Tel Aviv', 'Cyber')
    ) AS t(company_id, name, location, industry);
    """)

    # 2. Employees Table
    con.execute("""
    CREATE OR REPLACE TABLE raw.employees AS SELECT * FROM (VALUES
        (101, 'Alice Jones', '1990-05-12', 'F'),
        (102, 'Bob Smith', '1985-11-20', 'M'),
        (103, 'Charlie Brown', '1992-03-15', 'M'),
        (104, 'Dana White', '1988-07-30', 'F'),
        (105, 'Eve Black', '1995-01-10', 'F')
    ) AS t(emp_id, full_name, birth_date, gender);
    """)

    # 3. Job History Table
    con.execute("""
    CREATE OR REPLACE TABLE raw.job_history AS SELECT * FROM (VALUES
        (1, 101, 2, 'Analyst', 60000, '2015-01-01', '2018-01-01', 0),
        (2, 101, 1, 'Senior Analyst', 85000, '2018-02-01', NULL, 1),
        (3, 102, 1, 'Developer', 70000, '2010-06-01', '2015-06-01', 0),
        (4, 102, 1, 'Team Lead', 110000, '2015-06-02', NULL, 1),
        (5, 103, 3, 'Nurse', 40000, '2014-01-01', '2015-01-01', 0),
        (6, 103, 2, 'Consultant', 55000, '2015-02-01', '2016-02-01', 0),
        (7, 103, 4, 'Sales', 60000, '2016-03-01', NULL, 1),
        (8, 104, 2, 'VP Finance', 150000, '2012-01-01', NULL, 1)
    ) AS t(job_id, emp_id, company_id, role, salary, start_date, end_date, is_current);
    """)

    print("✅ Database created successfully.")
    con.close()


if __name__ == "__main__":
    create_raw_layer()