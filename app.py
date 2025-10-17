'''
    CSCI - 622 - Data Security & Privacy
    Project Phase 2 - app.py
    Authors: Samuel Roberts (svr9047) & Lianna Pottgen (lrp2755)

    This app.py file is our routing file! This will create the flask instance
    and determine how to route the calls to their proper methods and display
    the correct information to the user.
    Since this involves a couple of different sections, the below code is sectioned
    out to make it easier to read through adn determine which call goes to which
    location and why it is set up that way!
'''

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database import SessionLocal, engine
from models import Base, Employee, Client, Investment, Company, InvestmentRequest

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "fake_investing_secret"

# Create tables
Base.metadata.create_all(bind=engine)

# -- login route (starting screen) --
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    db = SessionLocal()
    # send request for post to get email and password
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # create front-end display
        if not email or not password:
            flash("Please enter both email and password")
            return render_template("login.html")

        # getting clients from the database
        client = db.query(Client).filter(Client.email == email).first()
        if client and check_password_hash(client.password_hash, password):
            session.clear()
            session["user_type"] = "client"
            session["user_id"] = client.client_id
            return redirect(url_for("client_dashboard"))

        # getting employees from the database (including managers)
        employee = db.query(Employee).filter(Employee.work_email == email).first()
        if employee and check_password_hash(employee.password_hash, password):
            session.clear()
            if employee.job_title == "Manager":
                session["user_type"] = "manager"
                session["user_id"] = employee.employee_id
                return redirect(url_for("manager_dashboard"))
            else:
                session["user_type"] = "employee"
                session["user_id"] = employee.employee_id
                return redirect(url_for("employee_dashboard"))

        # if we didn't have the right credientials, prompt the user.
        flash("Invalid credentials")

    return render_template("login.html")


# -- manager dashboard --
@app.route("/manager_dashboard")
def manager_dashboard():
    # check we are a manager (not an employee or client)
    if session.get("user_type") != "manager":
        return redirect(url_for("login"))

    # make sure we have this user as a manger
    db = SessionLocal()
    manager = db.query(Employee).get(session["user_id"])
    if not manager:
        return "Manager not found", 404

    # get the employees under this manager
    employees = db.query(Employee).filter(Employee.manager_id == manager.employee_id).all()
    verified_client_id = session.get("verified_client_id")

    # create the table information for the employees and their clients
    hierarchy = []
    for employee in employees:
        # create the filter
        emp_clients = db.query(Client).filter(Client.advisor_id == employee.employee_id).all()
        clients_list = []

        for client in emp_clients:
            # load investments only if this client is verified and we have access
            if verified_client_id == client.client_id:
                investments = db.query(Investment).filter(Investment.client_id == client.client_id).all()

                # get investment company ID too
                for inv in investments:
                    inv.company = db.query(Company).get(inv.company_id)
                c_investments = investments
            else:
                c_investments = []

            clients_list.append({"client": client, "investments": c_investments})
        hierarchy.append({"employee": employee, "clients": clients_list})

    # show to user
    return render_template(
        "manager_dashboard.html",
        manager=manager,
        employees=employees,
        hierarchy=hierarchy
    )

# -- employee dashboard --
@app.route("/employee_dashboard")
def employee_dashboard():
    # check we have an employee
    if session.get("user_type") != "employee":
        return redirect(url_for("login"))

    # make sure we have this user as an employee
    db = SessionLocal()
    employee = db.query(Employee).get(session["user_id"])
    if not employee:
        return "Employee not found", 404

    requests = db.query(InvestmentRequest).filter(
        InvestmentRequest.advisor_id == employee.employee_id
    ).all()

    # build clients for the table for this employee
    verified_client_id = session.get("verified_client_id")
    clients_list = []
    emp_clients = db.query(Client).filter(Client.advisor_id == employee.employee_id).all()

    # for all of the clients this employee has
    for clients in emp_clients:
        if verified_client_id == clients.client_id:
            investments = db.query(Investment).filter(Investment.client_id == clients.client_id).all()
            # get investment info
            for inv in investments:
                inv.company = db.query(Company).get(inv.company_id)
            c_investments = investments
        else:
            c_investments = []

        clients_list.append({"client": clients, "investments": c_investments})

    client_requests = db.query(InvestmentRequest).filter(
        InvestmentRequest.advisor_id == employee.employee_id
    ).order_by(InvestmentRequest.created_at.desc()).all()
    for req in client_requests:
        req.client = db.query(Client).get(req.client_id)
        req.company = db.query(Company).get(req.company_id)

    return render_template(
        "employee_dashboard.html",
        employee=employee,
        clients=clients_list,
        client_requests=client_requests
    )

# -- employee approval --
@app.route("/advisor_create_investment/<int:request_id>", methods=["POST"])
def advisor_create_investment(request_id):
    if session.get("user_type") != "employee":
        return redirect(url_for("login"))

    db = SessionLocal()
    req = db.query(InvestmentRequest).get(request_id)
    req.status = "AdvisorCreated"  # Flag that advisor has prepared investment

    db.commit()
    flash("Investment prepared. Client must approve.")
    return redirect(url_for("employee_dashboard"))

# -- client dashboard --
@app.route("/client_dashboard")
def client_dashboard():
    # check if this is a user
    if session.get("user_type") != "client":
        return redirect(url_for("login"))

    # check if this is a valid user
    db = SessionLocal()
    client = db.query(Client).get(session["user_id"])
    if not client:
        return "Client not found", 404

    # get their financial advisor
    advisor = db.query(Employee).get(client.advisor_id)

    # attach companies to each investment
    investments = db.query(Investment).filter(Investment.client_id == client.client_id).all()
    for inv in investments:
        inv.company = db.query(Company).get(inv.company_id)

    requests = db.query(InvestmentRequest).filter(InvestmentRequest.client_id == client.client_id).all()
    for req in requests:
        req.company = db.query(Company).get(req.company_id)

    # show to client user
    return render_template(
        "client_dashboard.html",
        client=client,
        advisor=advisor,
        investments=investments,
        requests = requests
    )
# -- client request investment -- 
@app.route("/create_investment_request", methods=["POST"])
def create_investment_request():
    if session.get("user_type") != "client":
        return redirect(url_for("login"))

    db = SessionLocal()
    client_id = session["user_id"]
    company_name = request.form.get("company_name")
    shares = int(request.form.get("shares"))

    new_request = InvestmentRequest(
        client_id=client_id,
        company_name=company_name,
        shares=shares,
        status="Pending"
    )
    db.add(new_request)
    db.commit()
    flash("Investment request sent to your advisor.")
    return redirect(url_for("client_dashboard"))

@app.route("/approve_request/<int:request_id>", methods=["POST"])
def approve_request(request_id):
    db = SessionLocal()
    req = db.query(InvestmentRequest).get(request_id)
    if not req:
        flash("Request not found")
        return redirect(url_for("employee_dashboard"))

    req.status = "Approved"
    # Optionally create the investment automatically
    new_investment = Investment(
        client_id=req.client_id,
        advisor_id=req.advisor_id,
        company_id=req.company_id,
        shares_purchased=req.shares,
        purchase_price_per_share=req.purchase_price_per_share,
        current_price=req.purchase_price_per_share
    )
    db.add(new_investment)
    db.commit()
    flash("Investment request approved and investment created")
    return redirect(url_for("employee_dashboard"))

@app.route("/deny_request/<int:request_id>", methods=["POST"])
def deny_request(request_id):
    db = SessionLocal()
    req = db.query(InvestmentRequest).get(request_id)
    if not req:
        flash("Request not found")
        return redirect(url_for("employee_dashboard"))

    req.status = "Rejected"
    db.commit()
    flash("Investment request denied")
    return redirect(url_for("employee_dashboard"))


# -- request route --
'''
@app.route("/request_investment/<int:client_id>", methods=["GET", "POST"])
def request_investment(client_id):
    if session.get("user_type") != "client":
        return redirect(url_for("login"))

    db = SessionLocal()
    client = db.query(Client).get(client_id)
    advisor = db.query(Employee).get(client.advisor_id)
    companies = db.query(Company).all()

    if request.method == "POST":
        company_name = request.form.get("company_name")
        shares = request.form.get("shares")
        purchase_price = request.form.get("purchase_price_per_share")

        # Look up or create company
        company = db.query(Company).filter(Company.company_name == company_name).first()
        if not company:
            company = Company(company_name=company_name)
            db.add(company)
            db.commit()

        # Create InvestmentRequest
        new_request = InvestmentRequest(
            client_id=client.client_id,
            advisor_id=advisor.employee_id,
            company_id=company.company_id,
            shares=int(shares),
            purchase_price_per_share=float(purchase_price),
            status="Pending"
        )
        db.add(new_request)
        db.commit()

        flash("Investment request submitted!")
        return redirect(url_for("client_dashboard"))

    return render_template("request_investment.html", client=client, advisor=advisor, companies = companies)
'''
# -- request investments with no parmas
@app.route("/request_investment", methods=["GET", "POST"])
def request_investment():
    if session.get("user_type") != "client":
        return redirect(url_for("login"))

    db = SessionLocal()
    client = db.query(Client).get(session["user_id"])
    if not client:
        return "Client not found", 404

    advisor = db.query(Employee).get(client.advisor_id)
    if not advisor:
        return "Advisor not found", 404

    # Get all companies for dropdown
    companies = db.query(Company).all()

    if request.method == "POST":
        company_id = request.form.get("company_id")
        shares = request.form.get("shares")
        purchase_price = request.form.get("purchase_price_per_share")

        # Validation
        if not company_id or not shares or not purchase_price:
            flash("All fields are required")
            return redirect(request.url)

        try:
            new_request = InvestmentRequest(
                client_id=client.client_id,
                advisor_id=advisor.employee_id,
                company_id=int(company_id),
                shares=int(shares),
                purchase_price_per_share=float(purchase_price),
                status="Pending"
            )
            db.add(new_request)
            db.commit()
            flash("Investment request submitted successfully!")
            return redirect(url_for("client_dashboard"))
        except Exception as e:
            db.rollback()
            flash(f"Error submitting request: {str(e)}")
            return redirect(request.url)

    return render_template(
        "request_investment.html",
        client=client,
        advisor=advisor,
        companies=companies
    )


# -- client investment approval -- 
@app.route("/approve_investment/<int:request_id>", methods=["POST"])
def approve_investment(request_id):
    if session.get("user_type") != "client":
        return redirect(url_for("login"))

    session["requested_request_id"] = request_id
    return redirect(url_for("security_check_for_investment"))

# -- client investment approval validation -- 
@app.route("/security_check_investment", methods=["GET", "POST"])
def security_check_for_investment():
    db = SessionLocal()
    client = db.query(Client).get(session["user_id"])
    request_id = session.get("requested_request_id")
    req = db.query(InvestmentRequest).get(request_id)

    if request.method == "POST":
        password = request.form.get("password")
        if check_password_hash(client.password_hash, password):
            # Create the actual investment
            investment = Investment(
                client_id=client.client_id,
                company_id=None,  # create company if needed
                shares_purchased=req.shares,
                purchase_price_per_share=0,  # set current price
                current_price=0,
                market_value=0
            )
            db.add(investment)
            req.status = "Approved"
            db.commit()
            session.pop("requested_request_id", None)
            flash("Investment approved and created!")
            return redirect(url_for("client_dashboard"))
        else:
            flash("Incorrect password")

    return render_template("security_check.html", client_id=client.client_id)



# -- requesting to see information --
@app.route("/request_client_info/<int:client_id>", methods=["POST"])
def request_client_info(client_id):

    # check we are a manager / advisor
    if session.get("user_type") not in ["manager", "employee"]:
        return redirect(url_for("login"))

    # get client
    session["requested_client_id"] = client_id
    return redirect(url_for("security_check", client_id=client_id))

# -- security check for seeing investments --
@app.route("/security_check/<int:client_id>", methods=["GET", "POST"])
def security_check(client_id):
    db = SessionLocal()
    # get users
    user = db.query(Employee).get(session["user_id"])

    if request.method == "POST":
        password = request.form.get("password")
        # check if we have the right password
        if check_password_hash(user.password_hash, password):

            # if so, we are verified (yay)
            session["verified_client_id"] = client_id

            if session["user_type"] == "manager":
                return redirect(url_for("manager_dashboard"))
            else:
                return redirect(url_for("employee_dashboard"))
        # else, we are not verified and cannot see the investments
        else:
            flash("Incorrect password")

    # return security check
    return render_template("security_check.html", client_id=client_id)

# -- logout user --
@app.route("/logout")
def logout():
    # logout!
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
