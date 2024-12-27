from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="Environ.env")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///Kumar_Appliances.sqlite3")
db = SQLAlchemy(app)

class Admin(db.Model):
    __tablename__ = 'admin'
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)

class ServiceProfessional(db.Model):
    __tablename__ = 'service_professional'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    date_created = db.Column(db.Date, nullable=False)
    description = db.Column(db.String)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    service_type = db.Column(db.String, nullable=False)
    experience = db.Column(db.String)
    attach_file = db.Column(db.LargeBinary)
    status = db.Column(db.String, nullable=False)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)

class Service(db.Model):
    __tablename__ = 'service'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    service_type = db.Column(db.String, nullable=False, unique=True)
    time_required = db.Column(db.String)
    description = db.Column(db.String)
    location = db.Column(db.String)
    pincode = db.Column(db.Integer)
class ServiceRequest(db.Model):
    __tablename__ = 'service_request'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    service_name = db.Column(db.String, db.ForeignKey('service.name'), nullable=False)
    service_type = db.Column(db.String, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer_name = db.Column(db.String, db.ForeignKey('customer.name'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=True)
    professional_name = db.Column(db.String, db.ForeignKey('service_professional.name'), nullable=True)
    date_of_request = db.Column(db.Date, nullable=False)
    date_of_completion = db.Column(db.Date, nullable=False)
    service_status = db.Column(db.String, nullable=False)
    customer_remarks = db.Column(db.String)
    professional_remarks = db.Column(db.String)

    __table_args__ = (
        CheckConstraint(
            "service_status IN ('requested', 'assigned', 'closed')", 
            name='check_service_status'
        ),
    )
    
def create_tables():
    with app.app_context():
        db.create_all()

        if Admin.query.count() == 0:
            admin1 = Admin(username='Shrikkumar', password='S@3141')
            admin2 = Admin(username='Sakura', password='S@3141')
            db.session.add(admin1)
            db.session.add(admin2)
            db.session.commit()