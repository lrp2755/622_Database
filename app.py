from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database import SessionLocal, engine
from models import Base, Employee, Client, Investment, Company
from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "fake_investing_secret"

# Create tables
Base.metadata.create_all(bind=engine)

# ----------------------------
# Login Route
# ----------------------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    db = SessionLocal()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Please enter both email and password")
            return render_template("login.html")

        # Check client
        client = db.query(Client).filter(Client.email == email).first()
        if client and check_password_hash(client.password_hash, password):
            session.clear()
            session["user_type"] = "client"
            session["user_id"] = client.client_id
            return redirect(url_for("client_dashboard"))

        # Check employee
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

        flash("Invalid credentials")
    return render_template("login.html")

# ----------------------------
# Client Dashboard
# ----------------------------
@app.route("/client_dashboard")
def client_dashboard():
    if session.get("user_type") != "client":
        return redirect(url_for("/login"))

    db = SessionLocal()
    client = db.query(Client).get(session["user_id"])
    advisor = db.query(Employee).get(client.advisor_id)

    # Attach company to each investment
    investments = db.query(Investment).filter(Investment.client_id == client.client_id).all()
    for inv in investments:
        inv.company = db.query(Company).get(inv.company_id)

    return render_template("client_dashboard.html",
                           client=client,
                           advisor=advisor,
                           investments=investments)

# ----------------------------
# Employee Dashboard
# ----------------------------
@app.route("/employee_dashboard")
def employee_dashboard():
    if session.get("user_type") != "employee":
        return redirect(url_for("login"))
    # <-- Security check added here
    if not session.get("verified"):
        return redirect(url_for("security_check"))

    db = SessionLocal()
    employee = db.query(Employee).get(session["user_id"])
    clients = db.query(Client).filter(Client.advisor_id == employee.employee_id).all()

    # Attach company to investments
    investments = db.query(Investment).filter(Investment.advisor_id == employee.employee_id).all()
    for inv in investments:
        inv.company = db.query(Company).get(inv.company_id)

    return render_template("employee_dashboard.html",
                           employee=employee,
                           clients=clients,
                           investments=investments)

# ----------------------------
# Manager Dashboard
# ----------------------------
'''@app.route("/manager_dashboard", methods=["GET", "POST"])
def manager_dashboard():
    if session.get("user_type") != "manager":
        return redirect(url_for("login"))

    db = SessionLocal()
    manager = db.query(Employee).get(session["user_id"])
    employees = db.query(Employee).filter(Employee.manager_id == manager.employee_id).all()

    # Determine if a client has been requested to see investment info
    requested_client_id = session.get("requested_client_id")
    verified = session.get("verified", False)

    data = []  # List of (employee, client, investments)
    for emp in employees:
        for client in emp.clients:
            # By default, no investments visible
            investments = []
            if verified and requested_client_id == client.client_id:
                # Load investments and attach companies
                investments = db.query(Investment).filter(Investment.client_id == client.client_id).all()
                for inv in investments:
                    inv.company = db.query(Company).get(inv.company_id)
            data.append((emp, client, investments))

    return render_template(
        "manager_dashboard.html",
        manager=manager,
        employees=employees,
        data=data,
        verified=verified
    )
'''
@app.route("/manager_dashboard", methods=["GET", "POST"])
def manager_dashboard():
    if session.get("user_type") != "manager":
        return redirect(url_for("login"))

    db = SessionLocal()
    manager = db.query(Employee).get(session["user_id"])
    if not manager:
        return "Manager not found", 404

    employees = db.query(Employee).filter(Employee.manager_id == manager.employee_id).all()

    hierarchy = []
    for emp in employees:
        emp_clients = db.query(Client).filter(Client.advisor_id == emp.employee_id).all()
        clients_list = []
        for c in emp_clients:
            # Initialize empty investments; only show when verified
            c.investments = []
            clients_list.append({"client": c, "investments": c.investments})
        hierarchy.append({"employee": emp, "clients": clients_list})

    return render_template(
        "manager_dashboard.html",
        manager=manager,
        employees=employees,
        hierarchy=hierarchy
    )
# ----------------------------
# Security Check Route
# ----------------------------
@app.route("/security_check/<int:client_id>", methods=["GET", "POST"])
def security_check(client_id):
    db = SessionLocal()

    if request.method == "POST":
        password = request.form.get("password")
        manager = db.query(Employee).get(session["user_id"])
        if check_password_hash(manager.password_hash, password):
            session["verified_client_id"] = client_id
            return redirect(url_for("manager_dashboard"))
        else:
            flash("Incorrect password")

    # Only pass client_id to the template
    return render_template("security_check.html", client_id=client_id)


@app.route("/request_client_info/<int:client_id>", methods=["POST"])
def request_client_info(client_id):
    if session.get("user_type") != "manager":
        return redirect(url_for("login"))

    # Redirect to security check with client_id
    return redirect(url_for("security_check", client_id=client_id))



@app.route("/view_client_investments")
def view_client_investments():
    if not session.get("verified") or "requested_client_id" not in session:
        return redirect(url_for("manager_dashboard"))

    db = SessionLocal()
    client_id = session["requested_client_id"]
    client = db.query(Client).get(client_id)

    # Make sure the manager can only view their own clients
    manager = db.query(Employee).get(session["user_id"])
    if client.advisor.manager_id != manager.employee_id:
        flash("You cannot view this client's data.")
        return redirect(url_for("manager_dashboard"))

    investments = db.query(Investment).filter(Investment.client_id == client.client_id).all()
    for inv in investments:
        inv.company = db.query(Company).get(inv.company_id)

    # Clear the verification/session after viewing
    session.pop("verified", None)
    session.pop("requested_client_id", None)

    return render_template("client_investments.html", client=client, investments=investments)

# ----------------------------
# Logout
# ----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
