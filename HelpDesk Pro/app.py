from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Arjun@1226",
    database="employee_management"
)

@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    cursor = db.cursor()
    cursor.execute("INSERT INTO employees (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    db.commit()
    cursor.close()

    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    email = request.form['email']
    password = request.form['password']

    cursor = db.cursor()
    cursor.execute("SELECT * FROM employees WHERE email = %s AND password = %s", (email, password))
    employee = cursor.fetchone()
    cursor.close()

    if employee:
        session['employee_id'] = employee[0]
        return redirect(url_for('dashboard'))
    else:
        return "Invalid credentials"

@app.route('/dashboard')
def dashboard():
    if 'employee_id' not in session:
        return redirect(url_for('login'))

    employee_id = session['employee_id']
    cursor = db.cursor()
    cursor.execute("SELECT * FROM problems WHERE employee_id = %s", (employee_id,))
    problems = cursor.fetchall()
    cursor.close()

    return render_template('dashboard.html', problems=problems)

@app.route('/raise_problem', methods=['POST'])
def raise_problem():
    if 'employee_id' not in session:
        return redirect(url_for('login'))

    employee_id = session['employee_id']
    title = request.form['title']
    description = request.form['description']

    cursor = db.cursor()
    cursor.execute("INSERT INTO problems (employee_id, title, description) VALUES (%s, %s, %s)", (employee_id, title, description))
    db.commit()
    cursor.close()

    return redirect(url_for('dashboard'))

@app.route('/admin')
def admin():
    cursor = db.cursor()
    cursor.execute("SELECT problems.id, employees.name, problems.title, problems.description, problems.created_at, tracking.status FROM problems JOIN employees ON problems.employee_id = employees.id LEFT JOIN tracking ON problems.id = tracking.problem_id")
    problems = cursor.fetchall()
    cursor.close()

    return render_template('admin.html', problems=problems)

@app.route('/update_status/<int:problem_id>', methods=['POST'])
def update_status(problem_id):
    status = request.form['status']
    comment = request.form['comment']

    cursor = db.cursor()
    cursor.execute("INSERT INTO tracking (problem_id, status, admin_comment) VALUES (%s, %s, %s)", (problem_id, status, comment))
    db.commit()
    cursor.close()

    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)