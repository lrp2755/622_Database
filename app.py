from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database import SessionLocal, engine
from models import Base, Employee, Client, Investment, Company

app = Flask(__name__)
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
@app.route("/manager_dashboard")
def manager_dashboard():
    if session.get("user_type") != "manager":
        return redirect(url_for("login"))

    db = SessionLocal()
    manager = db.query(Employee).get(session["user_id"])

    # Employees under this manager
    employees = db.query(Employee).filter(Employee.manager_id == manager.employee_id).all()

    # Map employee -> clients and investments
    employee_data = []
    for emp in employees:
        clients = db.query(Client).filter(Client.advisor_id == emp.employee_id).all()
        investments = db.query(Investment).filter(Investment.advisor_id == emp.employee_id).all()
        for inv in investments:
            inv.company = db.query(Company).get(inv.company_id)
        employee_data.append({
            "employee": emp,
            "clients": clients,
            "investments": investments
        })

    return render_template("manager_dashboard.html",
                           manager=manager,
                           employee_data=employee_data)

# ----------------------------
# Logout
# ----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
