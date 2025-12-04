'''
    CSCI - 622 - Data Security & Privacy
    Project Phase 4 - create_data.py
    Authors: Samuel Roberts (svr9047) & Lianna Pottgen (lrp2755)

    This create_data.py file will create the randomized data and will create
    the database for the entire system. This utilizes faker to create randomly
    generated data for all of the users. Our team attempted to create these manually
    randomly, but there became a lot more overlap and this library seemed to solve that
    issue!
'''
import random
from faker import Faker
from werkzeug.security import generate_password_hash
from database import SessionLocal, engine
from models import Base, Employee, Client, Investment, Company
from snn_key import encrypt_ssn, ssn_hash
import secrets
import string

fake = Faker()


# -- generate passwords --
def generate_given_passwords():
    characters = string.ascii_letters + string.digits + string.punctuation

    # Select random characters for all passwords
    fixed_manager_pwd = ''.join(secrets.choice(characters) for i in range(15))
    fixed_advisor_pwd = ''.join(secrets.choice(characters) for i in range(15))
    fixed_client_pwd = ''.join(secrets.choice(characters) for i in range(15))

    return [fixed_manager_pwd, fixed_advisor_pwd, fixed_client_pwd]


pwd_array = generate_given_passwords()
fixed_manager_pwd = pwd_array[0]
fixed_advisor_pwd = pwd_array[1]
fixed_client_pwd = pwd_array[2]

# -- create companies --
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


# -- create employees & managers --
def create_employees():
    employees = []

    # get random data for the personal side
    for i in range(10):
        gender = random.choice(["Male", "Female"])
        first_name = fake.first_name_male() if gender == "Male" else fake.first_name_female()
        last_name = fake.last_name()
        job_title = "Manager" if i < 2 else random.choice(["Financial Advisor", "Analyst"])
        work_email = f"{first_name.lower()}.{last_name.lower()}@fakeinvest.com"
        password_hash = generate_password_hash("password")

        # create the employee data
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
            license_expiry_date=fake.date_between(start_date='+1y', end_date='+5y'),
        )
        # add this to the employees list
        employees.append(emp)

    # assign managers for those that aren't mangers
    managers = []
    for employee in employees:
        if employee.job_title == "Manager":
            managers.append(employee)

    for employee in employees:
        if employee.job_title != "Manager":
            employee.manager_id = random.choice(managers).employee_id

    # add a fixed manager and employee(advisor) for consistent login
    fixed_manager = Employee(
        employee_id=9991,
        first_name="Manager",
        last_name="One",
        date_of_birth=fake.date_of_birth(minimum_age=35, maximum_age=60),
        gender="Male",
        work_email="manager@example.com",
        password_hash= fixed_manager_pwd,
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
        password_hash= fixed_advisor_pwd,
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

    # add these 2 extra users
    employees.extend([fixed_manager, fixed_advisor])

    return employees, managers + [fixed_manager]


# -- create clients --
def create_clients(employees, companies):
    # initiate clients
    clients = []
    advisors = []
    for employee in employees:
        if employee.job_title != "Manager":
            advisors.append(employee)

    # prep for user investments
    used_investment_ids = set()

    # generate 20 random clients!
    for i in range(20):
        gender = random.choice(["Male", "Female"])
        first_name = fake.first_name_male() if gender == "Male" else fake.first_name_female()
        last_name = fake.last_name()
        email = fake.email()
        password_hash = generate_password_hash("password")
        advisor = random.choice(advisors)
        plain_ssn = fake.ssn()

        client = Client(
            client_id=2000 + i,
            first_name=first_name,  # use generated
            last_name=last_name,  # use generated
            encrypted_ssn=encrypt_ssn(plain_ssn),  # required (NOT NULL)
            ssn_hash=ssn_hash(plain_ssn),  # required (UNIQUE)
            date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=80),
            gender=gender,  # use generated
            marital_status=random.choice(["Single", "Married", "Divorced", "Widowed"]),
            email=email,  # use generated (unique)
            password_hash=password_hash,
            phone_number=fake.phone_number(),
            address=fake.address(),
            employment_status=random.choice(["Employed", "Self-employed", "Retired"]),
            annual_income=random.randint(40000, 250000),
            risk_tolerance=random.choice(["Conservative", "Moderate", "Aggressive"]),
            advisor_id=advisor.employee_id,  # use the chosen advisor
        )

        # generate random investments for client
        client.investments = []
        random_number_of_investments = (random.randint(1, 5))
        for i in range(0, random_number_of_investments):
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
            # calculate market value and gain/loss simply
            inv.market_value = round(inv.shares_purchased * inv.current_price, 2)
            inv.gain_loss_percent = round((inv.current_price - inv.purchase_price_per_share) / inv.purchase_price_per_share * 100, 2)
            client.investments.append(inv)

        # assign the client to advisor's list
        advisor.clients.append(client)
        clients.append(client)

    # adding a fixed client for login for the client
    fixed_plain_ssn = "666-11-1111"
    fixed_client = Client(
        client_id=9999,
        first_name="Client",
        last_name="One",
        encrypted_ssn=encrypt_ssn(fixed_plain_ssn),  
        ssn_hash=ssn_hash(fixed_plain_ssn),
        date_of_birth=fake.date_of_birth(minimum_age=30, maximum_age=65),
        gender="Female",
        marital_status="Single",
        email="client@example.com",
        password_hash= fixed_client_pwd,
        phone_number=fake.phone_number(),
        address=fake.address(),
        employment_status="Employed",
        annual_income=75000,
        risk_tolerance="Moderate",
        advisor_id= 9992
    )

    # generate investment for fixed client
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


# -- create full database --
def main():
    # create databse
    db = SessionLocal()

    # create new tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # create companies
    companies = create_companies()
    for company in companies:
        db.add(company)

    # create employees and managers
    employees, managers = create_employees()
    for employee in employees:
        db.add(employee)

    # create clients and their investments
    clients = create_clients(employees, companies)
    for client in clients:
        db.add(client)
        for investment in getattr(client, "investments", []):
            db.add(investment)
    
    # add all to the db!
    db.commit()

    # printing for double check on success
    print("Database created successfully!")
    print("\nSample Login Credentials:")
    print("Manager login: manager@example.com, Password: "+str(fixed_manager_pwd))
    print("Advisor login: advisor@example.com, Password: "+str(fixed_advisor_pwd))
    print("Client login: client@example.com, Password: "+str(fixed_client_pwd))

if __name__ == "__main__":
    main()
