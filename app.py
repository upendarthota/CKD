import os
from flask import Flask, render_template, request, session, redirect, url_for , make_response
import pickle
import numpy as np
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
# from werkzeug.security import generate_password_hash, check_password_hash


os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.password}')"

with app.app_context():
    db.create_all()

def predict(values, dic):
    try:
        if len(values) == 24:
            model = pickle.load(open('models/kidney.pkl','rb'))
            values = np.asarray(values)
            return model.predict(values.reshape(1, -1))[0]
    except Exception as e:
        return f"Error in prediction: {e}"


# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
         
#         user = User.query.filter_by(email=email).first()
#         if user:
#             if user.password == password:
#                 session ['email'] = email
#                 return render_template('home.html')
#             else:
#                 return render_template('login.html',error="Invalid Password")
#         else:
#             return render_template('login.html')
    
#     return render_template('login.html')

# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         password = request.form['password']

#         hashed_password = generate_password_hash(password)
#         user = User(name=name, email=email, password=hashed_password)
#         db.session.add(user)
#         db.session.commit()
#         return redirect(url_for('login'))
#     return render_template('register.html')
# ###############################################

############## admin code    ###############################
@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        email = request.form['adminemail']
        password = request.form['adminpassword']
        
        # Static credentials
        admin_email = "admin@gmail.com"
        admin_password = "admin"  # Use a secure password in a real application
        
        if email == admin_email and password == admin_password:
            users = User.query.all() 
            return render_template('admin_dashboard.html' , users=users)  # Redirect to the admin dashboard
        else:
            return render_template('admin_login.html', error="User not found")
    
    return render_template('admin_login.html')


@app.route("/logout", endpoint='admin_logout')
def logout():
    # session.clear()
    # return redirect(url_for('index'))  # Redirect to the admin login page
    
    
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('logged_in', '', expires=0)  # Clear the cookie
    return resp

############################################################
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                session['email'] = email
                return render_template('home.html')
            else:
                return render_template('login.html', error="Invalid Password")
        else:
            return render_template('login.html', error="User not found")
    
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')


##############################################################

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route("/")
def index():
    return render_template('inde.html')

@app.route("/home")
def home():
    if session.get('email'):
        user = User.query.filter_by(email=session['email']).first()
        return render_template('home.html', user=user)
    return redirect(url_for('login'))

@app.route("/kidney", methods=['GET', 'POST'])
def kidneyPage():
    if session.get('email'):
        user = User.query.filter_by(email=session['email']).first()
        return render_template('kidney.html', user=user)
    return redirect(url_for('login'))

@app.route("/predict", methods=['POST', 'GET'])
def predictPage():
    try:
        if request.method == 'POST':
            to_predict_dict = request.form.to_dict()

            for key, value in to_predict_dict.items():
                try:
                    to_predict_dict[key] = int(value)
                except ValueError:
                    to_predict_dict[key] = float(value)

            to_predict_list = list(map(float, list(to_predict_dict.values())))
            pred = predict(to_predict_list, to_predict_dict)
    except:
        message = "Please enter valid data"
        return render_template("home.html", message=message)

    return render_template('predict.html', pred=pred)




if __name__ == '__main__':
    app.run(debug=True)
