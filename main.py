from authy.api import AuthyApiClient
from flask import (Flask, Response, request, redirect,
    render_template, session, url_for, flash)
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt

app = Flask(__name__)

# Authy API configuration
app.config['AUTHY_API_KEY'] = '7oEm6tW1sBme8ZmZdXjRrm2ZLphlNjI9'

# Secret key for session management
app.secret_key = 'dummy'
app.config['SECRET_KEY'] = 'dummy'

# MySQL database configuration
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'nimish755435'
app.config['MYSQL_DB'] = 'loginsystem'
mysql = MySQL(app)

# Hashed password and dummy email for login functionality
dummy_password = 'password123'
hashed_dummy_password = sha256_crypt.encrypt(dummy_password)
dummy_email = 'example@example.com'

# Initialize Authy API client
api = AuthyApiClient(app.config['AUTHY_API_KEY'])

@app.route("/")
def home():
    return redirect(url_for("phone_login"))

@app.route("/phone_login", methods=["GET", "POST"])
def phone_login():
    if request.method == "POST":
        country_code = request.form.get("country_code")
        phone_number = request.form.get("phone_number")
        method = request.form.get("method")

        # Store country code and phone number in session
        session['country_code'] = country_code
        session['phone_number'] = phone_number

        # Start phone verification using Authy API
        api.phones.verification_start(phone_number, country_code, via=method)

        return redirect(url_for("verify"))

    return render_template("phone_login.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        token = request.form.get("token")
        phone_number = session.get("phone_number")
        country_code = session.get("country_code")

        # Verify the entered token using Authy API
        verification = api.phones.verification_check(phone_number, country_code, token)

        if verification.ok():
            cursor = mysql.connection.cursor()
            query = "SELECT id FROM users WHERE phone_number = %s"
            cursor.execute(query, (phone_number,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]
            else:
                # Insert the new user into the database
                insert_query = "INSERT INTO users (phone_number) VALUES (%s)"
                cursor.execute(insert_query, (phone_number,))
                mysql.connection.commit()
                session['userid'] = cursor.lastrowid
            
            # Return success message with user ID
            return Response("<h1>Success! Welcome - User Id = {}</h1>".format(session['userid']))
        else:
            flash('Incorrect OTP', 'danger')
            return render_template('verify.html')
    
    return render_template("verify.html") 


@app.route('/email_login',methods=['GET','POST'])
def login():
    cur = mysql.connection.cursor()
    x=cur.execute("SELECT * FROM users WHERE email=%s",(dummy_email,))
    if(x==0):
        # Insert the dummy email and password into the database
        cur.execute("INSERT INTO users(email,password) VALUES(%s,%s)",(dummy_email,hashed_dummy_password))
        mysql.connection.commit()
    cur.close()
    if(request.method=='POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        session['email']=email
        cur1 = mysql.connection.cursor()
        x=cur1.execute("SELECT * FROM users WHERE email=%s",(email,))
        if (x!=0):
            data=cur1.fetchone()
            # User exists in the database, verify the password
            if(sha256_crypt.verify(password,data[3])):
                session['userid'] = data[0]
                session['email']=data[2]
                return Response("<h1>Success! Welcome - User Id = {}</h1>".format(session['userid']))
            else:
                flash('wrong password','danger')
                return render_template('email_login.html')
        else:
            # User is not registered, display error message
            flash('user not registered')
            return render_template('email_login.html')
    return render_template('email_login.html')

if __name__ == '__main__':
    app.run(debug=False)


