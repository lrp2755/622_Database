from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database import SessionLocal, engine
from models import Base, Employee, Client, Investment, Company

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

        # --- Check Client ---
        client = db.query(Client).filter(Client.email == email).first()
        if client and check_password_hash(client.password_hash, password):
            session.clear()
            session["user_type"] = "client"
            session["user_id"] = client.client_id
            return redirect(url_for("client_dashboard"))

        # --- Check Employee ---
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
# Manager Dashboard
# ----------------------------
@app.route("/manager_dashboard")
def manager_dashboard():
    if session.get("user_type") != "manager":
        return redirect(url_for("login"))

    db = SessionLocal()
    manager = db.query(Employee).get(session["user_id"])
    if not manager:
        return "Manager not found", 404

    employees = db.query(Employee).filter(Employee.manager_id == manager.employee_id).all()

    verified_client_id = session.get("verified_client_id")

    # Build hierarchy: employee -> clients
    hierarchy = []
    for emp in employees:
        emp_clients = db.query(Client).filter(Client.advisor_id == emp.employee_id).all()
        clients_list = []
        for c in emp_clients:
            # Load investments only if this client is verified
            if verified_client_id == c.client_id:
                investments = db.query(Investment).filter(Investment.client_id == c.client_id).all()
                for inv in investments:
                    inv.company = db.query(Company).get(inv.company_id)
                c_investments = investments
            else:
                c_investments = []  # keep empty if not verified

            clients_list.append({"client": c, "investments": c_investments})
        hierarchy.append({"employee": emp, "clients": clients_list})

    return render_template(
        "manager_dashboard.html",
        manager=manager,
        employees=employees,
        hierarchy=hierarchy
    )

# ----------------------------
# Employee Dashboard
# ----------------------------
@app.route("/employee_dashboard")
def employee_dashboard():
    if session.get("user_type") != "employee":
        return redirect(url_for("login"))

    db = SessionLocal()
    employee = db.query(Employee).get(session["user_id"])
    if not employee:
        return "Employee not found", 404

    # Build clients hierarchy
    verified_client_id = session.get("verified_client_id")
    clients_list = []
    emp_clients = db.query(Client).filter(Client.advisor_id == employee.employee_id).all()
    for c in emp_clients:
        if verified_client_id == c.client_id:
            investments = db.query(Investment).filter(Investment.client_id == c.client_id).all()
            for inv in investments:
                inv.company = db.query(Company).get(inv.company_id)
            c_investments = investments
        else:
            c_investments = []

        clients_list.append({"client": c, "investments": c_investments})

    return render_template(
        "employee_dashboard.html",
        employee=employee,
        clients=clients_list
    )
# ----------------------------
# Client Dashboard
# ----------------------------
@app.route("/client_dashboard")
def client_dashboard():
    if session.get("user_type") != "client":
        return redirect(url_for("login"))

    db = SessionLocal()
    client = db.query(Client).get(session["user_id"])
    if not client:
        return "Client not found", 404

    advisor = db.query(Employee).get(client.advisor_id)

    # Attach companies to each investment
    investments = db.query(Investment).filter(Investment.client_id == client.client_id).all()
    for inv in investments:
        inv.company = db.query(Company).get(inv.company_id)

    return render_template(
        "client_dashboard.html",
        client=client,
        advisor=advisor,
        investments=investments
    )


# ----------------------------
# Request Client Info
# ----------------------------
@app.route("/request_client_info/<int:client_id>", methods=["POST"])
def request_client_info(client_id):
    if session.get("user_type") not in ["manager", "employee"]:
        return redirect(url_for("login"))

    session["requested_client_id"] = client_id
    return redirect(url_for("security_check", client_id=client_id))


# ----------------------------
# Security Check
# ----------------------------
@app.route("/security_check/<int:client_id>", methods=["GET", "POST"])
def security_check(client_id):
    db = SessionLocal()
    user = db.query(Employee).get(session["user_id"])

    if request.method == "POST":
        password = request.form.get("password")
        if check_password_hash(user.password_hash, password):
            session["verified_client_id"] = client_id
            # Redirect back to dashboard depending on user type
            if session["user_type"] == "manager":
                return redirect(url_for("manager_dashboard"))
            else:
                return redirect(url_for("employee_dashboard"))
        else:
            flash("Incorrect password")

    return render_template("security_check.html", client_id=client_id)

# ----------------------------
# Logout
# ----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
