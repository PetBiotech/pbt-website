import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import column
import re
import json
import razorpay
from razorpay.resources import payment
import secret
import simplejson as json
import json


import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



from flask import Flask,request,render_template,redirect,url_for
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy


# Emails
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

# Define to/from
sender = 'admin1@petbiotech.net'
sender_title = "PBT Admin"
recipient = 'petbiotech1@gmail.com'


###### for try
from flask import flash, session
######


app = Flask(__name__)

app.config['SECRET_KEY']= 'anandandkaustubh'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://pbt:utpal%40101@localhost/websiteDB'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:Petbiotech12@pbt-portal.czufb7vlwyub.ap-south-1.rds.amazonaws.com/ebdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()
login_manager = LoginManager(app)
admin = Admin(app, template_mode='bootstrap4')




# table creation
########## GLOBAL VARIABLE ################
admin_auth = False
###########################################

class testDb (db.Model):
    test_id = db.Column(db.String(10), unique=True,
                        nullable=False, primary_key=True)
    category = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    requirements = db.Column(db.String(500), nullable=False)
    cost = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return '<test %r>' % self.test_id


class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)

class Username(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))

db.create_all()

def check_user_exists(username1, password1):
    user = Username.query.filter_by(username=username1, password=password1).first()
    return True if user else False

username1 = "admin"
password1 = "admin123"

if check_user_exists(username1, password1):
    pass
else:
    tr=Username(username="admin",password="admin123")
    db.session.add(tr)
    db.session.commit()


if db.session.query(testDb).count() == 0:
    # Open your CSV file
    with open('testdb.csv', 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            test = testDb(
                test_id=row[0],
                category=row[1],
                name=row[2],
                requirements=row[3],
                cost=int(row[4])
            )
            db.session.add(test)

    # Commit the changes
    db.session.commit()
else:
    print("The table is not empty.")






showCart = 0
arr = ""
datas = []
itemCodes = ""



@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path,'static'),'favicon.png',mimetype='image/favicon.png')


@app.route("/")
def home():
    global arr, showCart
    xyz = -1
    return render_template('index.html', cartArray=arr, showCart=xyz)

@app.route("/privacyPolicy")
def privacyPolicy():
    global arr, showCart
    xyz = -1
    return render_template('privacyPolicy.html', cartArray=arr, showCart=xyz)


@app.route("/tnc")
def TnC():
    global arr, showCart
    xyz = -1
    return render_template('termsAndCondition.html', cartArray=arr, showCart=xyz)


@app.route("/refundPolicy")
def refundPolicy():
    global arr, showCart
    xyz = -1
    return render_template('refundPolicy.html', cartArray=arr, showCart=xyz)


@app.route('/showCart/<int:n>/<items>', methods=['GET', 'POST'])
def showCartMenu(n, items):
    global arr, showCart, datas, itemCodes
    showCart = 0
    itemCodes=""
    
    items = json.loads(items)
    for item1 in items:
        itemCodes += item1+"***"
    i = 0
    arr = ""
    datas.clear()
    for item in items:
        try:
            if (len(item) > 1):
                itemData = testDb.query.filter_by(test_id=item).first()
                id = str(itemData.test_id)
                category = str(itemData.category)
                name = str(itemData.name)
                requirements = str(itemData.requirements)
                cost = str(itemData.cost)
                datas.append(id+"***"+category+"***"+name+"***" +
                             requirements+"***"+cost+"|||***")
                i = i+1
        except:
            return render_template('index.html', cartArray=arr, showCart=showCart)
    if (len(datas) > 0):
        showCart = 1
        for i in range(0, n):
            arr += datas[i]
    return redirect("/showCartOpen")


@app.route('/showCartOpen')
def showCartOpen():
    global showCart,arr
    return render_template('index.html', cartArray=arr, showCart=showCart)


@app.route("/add")
def add():
    return render_template('add.html', message="Welcome")



@app.route('/hello', methods=['GET', 'POST'])
def hello():

    email = request.form.get('email')
    name = request.form.get('name')
    phno = request.form.get('phno')
    ad1 = request.form.get('ad1')
    ad2 = request.form.get('ad2')
    ad3 = request.form.get('ad3')
    ad4 = request.form.get('ad4')
    ad5 = request.form.get('ad5')
    address = ad1+" "+ad2+" "+ad3+" "+ad4+" "+ad5

    user = users(email=email, name=name, phone=phno, address=address)
    db.session.add(user)
    db.session.commit()
    msg_text = f"Name:{name}\nPhone Number:{phno}\nEmail:{email}\nAddress:{address}\n\n"
    msg = MIMEText(msg_text, 'plain', 'utf-8')
    msg['Subject'] =  Header("Customer Contact Alert", 'utf-8')
    msg['From'] = formataddr((str(Header(sender_title, 'utf-8')), sender))
    msg['To'] = recipient
    server = smtplib.SMTP_SSL('smtp.zoho.in', 465)
    server.login('admin1@petbiotech.net', 'Admin1@pbt1')
    server.sendmail(sender, [recipient], msg.as_string())
    server.quit()
    flash('Form was submitted successfully')


    return redirect(url_for('home'))



@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    return render_template('index.html', cartArray=arr, showCart=showCart)


@app.errorhandler(404)
def pagenotfound(e):
    return render_template("error404.html")
# payment coding ends here


#####################################################
#Admin Login
#####################################################

@login_manager.user_loader
def load_user(user_id):
    return Username.query.get(int(user_id))

class UserAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    column_display_pk=True
    page_size=30

admin.add_view(UserAdminView(Username, db.session,name="Users"))
admin.add_view(UserAdminView(testDb, db.session,name="Tests"))
admin.add_view(UserAdminView(users, db.session,name="Orders"))

admin.add_link(MenuLink(name='Logout', category='', url="/logout"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Username.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user,remember=False)
            print(current_user.is_authenticated)
            logged_in=current_user.is_authenticated
            return redirect('/admin')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')



#####################################################
#Site map
#####################################################
@app.route('/sitemap.xml')
def sitemap():
    sitemap_xml=render_template(url_for('sitemap'))
    response=make_response(sitemap_xml)
    response.headers['Content-Type']="application/xml"

    return response
###################################################################


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="localhost",port=8000,debug=False)
    
    
