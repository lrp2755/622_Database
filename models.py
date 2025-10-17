'''
    CSCI - 622 - Data Security & Privacy
    Project Phase 2 - models.py
    Authors: Samuel Roberts (svr9047) & Lianna Pottgen (lrp2755)

    This models.py class is the basis for creating all of the different classes
    (aka models or objects :) )for the program! This will create the employee,
    client, company, and investment.
'''
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# -- creating employee --
class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(Date)
    gender = Column(String)
    work_email = Column(String, unique=True)
    password_hash = Column(String)
    phone_number = Column(String)
    address = Column(String)
    start_date = Column(Date)
    job_title = Column(String)
    base_salary = Column(Float)
    commission_rate = Column(Float)
    license_number = Column(String)
    license_expiry_date = Column(Date)
    manager_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=True)  # Managers can be null

    # create relationships
    clients = relationship("Client", back_populates="advisor")
    investments = relationship("Investment", back_populates="advisor")

# -- creating client --
class Client(Base):
    __tablename__ = "clients"

    client_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    ssn = Column(String, unique=True)
    date_of_birth = Column(Date)
    gender = Column(String)
    marital_status = Column(String)
    email = Column(String, unique=True)
    password_hash = Column(String)
    phone_number = Column(String)
    address = Column(String)
    employment_status = Column(String)
    annual_income = Column(Float)
    risk_tolerance = Column(String)
    advisor_id = Column(Integer, ForeignKey("employees.employee_id"))

    # Relationships
    advisor = relationship("Employee", back_populates="clients")
    investments = relationship("Investment", back_populates="client")
    requests = relationship("InvestmentRequest", back_populates="client")

# -- create investment --
class Investment(Base):
    __tablename__ = "investments"

    investment_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"))
    advisor_id = Column(Integer, ForeignKey("employees.employee_id"))
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    date = Column(Date)
    shares_purchased = Column(Float)
    purchase_price_per_share = Column(Float)
    broker_fees = Column(Float)
    current_price = Column(Float)
    market_value = Column(Float)
    gain_loss_percent = Column(Float)
    exit_date = Column(Date, nullable=True)

    client = relationship("Client", back_populates="investments")
    advisor = relationship("Employee", back_populates="investments")
    company = relationship("Company", back_populates="investments")

# -- create investment request
class InvestmentRequest(Base):
    __tablename__ = "investment_requests"
    request_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"))
    advisor_id = Column(Integer, ForeignKey("employees.employee_id"))
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=True)
    shares = Column(Integer)
    purchase_price_per_share = Column(Float, nullable=True)
    status = Column(String, default="Pending")  # Pending, Approved, Rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="requests")
    advisor = relationship("Employee")
    company = relationship("Company")


# -- create company --
class Company(Base):
    __tablename__ = "companies"

    company_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    abbreviation = Column(String)
    isin = Column(String)
    industry = Column(String)
    country = Column(String)
    company_type = Column(String)
    market_cap = Column(Float)
    revenue = Column(Float)
    earnings_per_share = Column(Float)
    target_price = Column(Float)

    # relationship to investments
    investments = relationship("Investment", back_populates="company")