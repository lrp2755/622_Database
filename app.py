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
from models import Base, Employee, Client, Investment, Company

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

    # show to user
    return render_template(
        "employee_dashboard.html",
        employee=employee,
        clients=clients_list
    )

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

    # show to client user
    return render_template(
        "client_dashboard.html",
        client=client,
        advisor=advisor,
        investments=investments
    )


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
