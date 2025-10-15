import random
from faker import Faker
from werkzeug.security import generate_password_hash
from database import SessionLocal, engine
from models import Base, Employee, Client, Investment, Company

fake = Faker()

# ----------------------------
# Seed Companies
# ----------------------------
def create_companies():
    company_names = ["TechCorp", "FinBank", "HealthInc", "GreenEnergy", "EduSoft"]
    companies = []
    for i, name in enumerate(company_names):
        comp = Company(
            company_id=100 + i,
            company_name=name
        )
        companies.append(comp)
    return companies

# ----------------------------
# Seed Employees & Managers
# ----------------------------
def create_employees():
    employees = []
    for i in range(10):
        gender = random.choice(["Male", "Female"])
        first_name = fake.first_name_male() if gender == "Male" else fake.first_name_female()
        last_name = fake.last_name()
        job_title = "Manager" if i < 2 else random.choice(["Financial Advisor", "Analyst"])
        work_email = f"{first_name.lower()}.{last_name.lower()}@fakeinvest.com"
        password_hash = generate_password_hash("password")

        emp = Employee(
            employee_id=1000 + i,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=65),
            gender=gender,
            work_email=work_email,
            password_hash=password_hash,
            phone_number=fake.phone_number(),
            address=fake.address(),
            start_date=fake.date_between(start_date='-10y', end_date='-1y'),
            job_title=job_title,
            base_salary=random.randint(60000, 150000),
            commission_rate=round(random.uniform(0.01, 0.05), 2),
            license_number=''.join(random.choices('0123456789', k=6)),
            license_expiry_date=fake.date_between(start_date='+1y', end_date='+5y')
        )
        employees.append(emp)

    # Assign manager_id to non-managers
    managers = [e for e in employees if e.job_title == "Manager"]
    for emp in employees:
        if emp.job_title != "Manager":
            emp.manager_id = random.choice(managers).employee_id

    # Add a fixed manager and advisor for login
    fixed_manager = Employee(
        employee_id=9991,
        first_name="Manager",
        last_name="One",
        date_of_birth=fake.date_of_birth(minimum_age=35, maximum_age=60),
        gender="Male",
        work_email="manager@example.com",
        password_hash=generate_password_hash("password"),
        phone_number=fake.phone_number(),
        address=fake.address(),
        start_date=fake.date_between(start_date='-10y', end_date='-1y'),
        job_title="Manager",
        base_salary=120000,
        commission_rate=0.03,
        license_number='123456',
        license_expiry_date=fake.date_between(start_date='+1y', end_date='+5y')
    )
    fixed_advisor = Employee(
        employee_id=9992,
        first_name="Advisor",
        last_name="One",
        date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=50),
        gender="Female",
        work_email="advisor@example.com",
        password_hash=generate_password_hash("password"),
        phone_number=fake.phone_number(),
        address=fake.address(),
        start_date=fake.date_between(start_date='-10y', end_date='-1y'),
        job_title="Financial Advisor",
        base_salary=90000,
        commission_rate=0.04,
        license_number='654321',
        license_expiry_date=fake.date_between(start_date='+1y', end_date='+5y'),
        manager_id=fixed_manager.employee_id
    )

    employees.extend([fixed_manager, fixed_advisor])

    return employees, managers + [fixed_manager]

# ----------------------------
# Seed Clients
# ----------------------------
def create_clients(employees, companies):
    clients = []
    advisors = [e for e in employees if e.job_title != "Manager"]
    used_investment_ids = set()  # Track used investment IDs

    for i in range(20):
        gender = random.choice(["Male", "Female"])
        first_name = fake.first_name_male() if gender == "Male" else fake.first_name_female()
        last_name = fake.last_name()
        email = fake.email()
        password_hash = generate_password_hash("password")
        advisor = random.choice(advisors)

        client = Client(
            client_id=2000 + i,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=80),
            gender=gender,
            marital_status=random.choice(["Single", "Married", "Divorced", "Widowed"]),
            email=email,
            password_hash=password_hash,
            phone_number=fake.phone_number(),
            address=fake.address(),
            employment_status=random.choice(["Employed", "Self-employed", "Retired"]),
            annual_income=random.randint(40000, 250000),
            risk_tolerance=random.choice(["Conservative", "Moderate", "Aggressive"]),
            advisor_id=advisor.employee_id,
        )

        # Generate investments for client
        client.investments = []
        for _ in range(random.randint(1, 5)):
            # Ensure unique investment_id
            while True:
                inv_id = random.randint(1000, 9999)
                if inv_id not in used_investment_ids:
                    used_investment_ids.add(inv_id)
                    break

            inv = Investment(
                investment_id=inv_id,
                client_id=client.client_id,
                advisor_id=advisor.employee_id,
                company_id=random.choice(companies).company_id,
                date=fake.date_between(start_date='-2y', end_date='today'),
                shares_purchased=random.randint(10, 500),
                purchase_price_per_share=round(random.uniform(10, 500), 2),
                broker_fees=round(random.uniform(5, 50), 2),
                current_price=round(random.uniform(10, 600), 2),
                market_value=0,
                gain_loss_percent=0,
                exit_date=None
            )
            # Calculate market value and gain/loss
            inv.market_value = round(inv.shares_purchased * inv.current_price, 2)
            inv.gain_loss_percent = round((inv.current_price - inv.purchase_price_per_share) / inv.purchase_price_per_share * 100, 2)
            client.investments.append(inv)

        # Assign client to advisor's list
        advisor.clients.append(client)
        clients.append(client)

    # Add a fixed client for login
    fixed_client = Client(
        client_id=9999,
        first_name="Client",
        last_name="One",
        date_of_birth=fake.date_of_birth(minimum_age=30, maximum_age=65),
        gender="Female",
        marital_status="Single",
        email="client@example.com",
        password_hash=generate_password_hash("password"),
        phone_number=fake.phone_number(),
        address=fake.address(),
        employment_status="Employed",
        annual_income=75000,
        risk_tolerance="Moderate",
        advisor_id=advisors[0].employee_id
    )

    # Generate one investment for fixed client
    while True:
        inv_id = random.randint(1000, 9999)
        if inv_id not in used_investment_ids:
            used_investment_ids.add(inv_id)
            break

    inv = Investment(
        investment_id=inv_id,
        client_id=fixed_client.client_id,
        advisor_id=fixed_client.advisor_id,
        company_id=random.choice(companies).company_id,
        date=fake.date_between(start_date='-1y', end_date='today'),
        shares_purchased=random.randint(10, 500),
        purchase_price_per_share=round(random.uniform(10, 500), 2),
        broker_fees=round(random.uniform(5, 50), 2),
        current_price=round(random.uniform(10, 600), 2),
        market_value=0,
        gain_loss_percent=0,
        exit_date=None
    )
    inv.market_value = round(inv.shares_purchased * inv.current_price, 2)
    inv.gain_loss_percent = round((inv.current_price - inv.purchase_price_per_share) / inv.purchase_price_per_share * 100, 2)
    fixed_client.investments = [inv]

    clients.append(fixed_client)

    return clients

# ----------------------------
# Seed Database
# ----------------------------
def main():
    db = SessionLocal()

    # Drop old tables and create new
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed companies
    companies = create_companies()
    for comp in companies:
        db.add(comp)

    # Seed employees/managers
    employees, managers = create_employees()
    for emp in employees:
        db.add(emp)

    # Seed clients and investments
    clients = create_clients(employees, companies)
    for client in clients:
        db.add(client)
        for inv in getattr(client, "investments", []):
            db.add(inv)

    db.commit()

    print("Database seeded successfully!")
    print("\nSample Login Credentials (password for all users: 'password'):")
    print("Manager login: manager@example.com")
    print("Advisor login: advisor@example.com")
    print("Client login: client@example.com")

if __name__ == "__main__":
    main()
