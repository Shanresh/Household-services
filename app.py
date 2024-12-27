from flask import render_template, request, redirect, url_for, session, send_file, flash
from db_setup import app, create_tables, ServiceProfessional, Customer, Admin, db, Service,ServiceRequest
from datetime import date,timedelta,datetime
from dotenv import load_dotenv
import io,os

load_dotenv(dotenv_path="Environ.env")

app.secret_key = os.getenv("SECRET_KEY")
create_tables()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user_type = request.form['user_type']
    session['role']=user_type
    if user_type == "admin":
        admin=Admin.query.filter_by(username=username, password=password).first()
        if admin:
            session['name'] = admin.username
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error="Invalid Admin Credentials")
    elif user_type == "service_professional":
        SP=ServiceProfessional.query.filter_by(username=username, password=password).first()
        if SP:
            session['name'] = SP.name
            session['type']="SP"
            session['service_type']=SP.service_type
            return redirect(url_for('service_professional_dashboard'))
        else:
            return render_template('login.html', error="Invalid SP Credentials")
    else:
        Cus=Customer.query.filter_by(username=username, password=password).first()
        if Cus:
            session['name'] = Cus.name
            session['id']=Cus.id
            session['type']="Customer"
            return redirect(url_for('customer_dashboard'))
        else:
            return render_template('login.html', error="Invalid Customer Credentials")

@app.route('/logout')
def logout():
    session.pop('name', None)
    return redirect(url_for('index'))

@app.route('/registerSP', methods=['GET', 'POST'])
def register_sp():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        service_type = request.form['service_type']
        experience=request.form['experience']
        attach_file = request.files['attach_file']
        max_file_size = 2 * 1024 * 1024  # 2 MB
        file_data = None
        if attach_file and attach_file.filename != '':
            if attach_file.content_length > max_file_size:
                return render_template('register_sp.html', error="File size exceeds 2MB")
            else:
                file_data = attach_file.read()
        try:
            new_sp = ServiceProfessional(
                name=name,
                username=username,
                password=password,
                experience=experience,
                service_type=service_type,
                date_created=date.today(),
                status="Admin approval Pending",
                attach_file=file_data
            )
            db.session.add(new_sp)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            return render_template('register_sp.html', error="Registration Failed SP may already be there")

    return render_template('register_sp.html')

@app.route('/download_file/<int:professional_id>')
def download_file(professional_id):
    professional = ServiceProfessional.query.get_or_404(professional_id)
    return send_file(
        io.BytesIO(professional.attach_file),
        as_attachment=True,
        download_name=f"{professional.name}Resume.docx"
    )

@app.route('/registerCustomer', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        try:
            new_customer = Customer(
                name=name,
                username=username,
                password=password,
                status="Active"
            )
            db.session.add(new_customer)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            return render_template('register_customer.html', error="Registration Failed Customer may already be there")

    return render_template('register_customer.html')

@app.route('/toggle_status/<int:id>/<action>/<user_type>', methods=['GET','POST'])
def toggle_status(id, action, user_type):
    
    if action == 'block':
        if user_type == 'customer':
            customer = Customer.query.get(id)
            customer.status = 'blocked'
            db.session.commit()
        else:
            professional = ServiceProfessional.query.get(id)
            professional.status = 'blocked'
            db.session.commit()
    elif action == 'unblock':
        if user_type == 'customer':
            customer = Customer.query.get(id)
            customer.status = 'Active'
            db.session.commit()
        else:
            professional = ServiceProfessional.query.get(id)
            professional.status = 'Active'
            db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/add_service', methods=['POST'])
def add_service():
    if request.method=='POST':
        name=request.form['name']
        servicetype=request.form['service_type']
        price=request.form['price']
        time_required=request.form['time_required']
        description=request.form['description']
        location=request.form['location']
        pincode=request.form['pincode']
        professionals = ServiceProfessional.query.all()
        customers = Customer.query.all()
        services = Service.query.all()
        try:
            new_service= Service(
                name=name,
                service_type=servicetype,
                price=price,
                time_required=time_required,
                description=description,
                location=location,
                pincode=pincode,
            )
            db.session.add(new_service)
            db.session.commit()
            services = Service.query.all()
            return render_template('admin_dashboard.html', Customers=customers, professionals=professionals, services=services)
        except Exception as e:
            db.session.rollback()
            return render_template('admin_dashboard.html', Customers=customers, professionals=professionals, services=services,error="Service not added/already added")

@app.route('/delete_service/<int:id>', methods=['POST'])
def delete_service(id):
    professionals = ServiceProfessional.query.all()
    customers = Customer.query.all()
    try:
        service = Service.query.get(id)
        if service:
            db.session.delete(service)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        return render_template('admin_dashboard.html', Customers=customers,professionals=professionals, services=services,error="service not deleted")
    services = Service.query.all()
    professionals = ServiceProfessional.query.all()
    customers = Customer.query.all()
    return redirect(url_for('admin_dashboard'))

@app.route('/update_service',methods=['POST'])
def update_service():
    professionals = ServiceProfessional.query.all()
    customers = Customer.query.all()
    service = Service.query.get(session['id'])
    try:
        
        service.name=request.form['name']
        service.price=request.form['price']
        service.time_required = request.form['time_required']
        service.description = request.form['description']
        service.location=request.form['location']
        service.pincode=request.form['pincode']
        db.session.commit()
    except:
        db.session.rollback()
        services=Service.query.all()
        return render_template('admin_dashboard.html', Customers=customers,professionals=professionals, services=services,error="service not updated")
    services=Service.query.all()
    return render_template('admin_dashboard.html', Customers=customers,professionals=professionals, services=services)

@app.route('/update_ser/<int:id>',methods=['POST'])
def update_ser(id):
    session['id']=id
    service = Service.query.get(id)
    return render_template('update_service.html',id=id,name=service.name,price=service.price,description=service.description,time_required=service.time_required,location=service.location,pincode=service.pincode)

@app.route('/toggle_request/<int:id>', methods=['GET','POST'])
def toggle_request(id):
    servicerequests=ServiceRequest.query.filter_by(id=id).first()
    servicerequests.service_status='closed'
    db.session.commit()
    if session['type']=="Customer":
        return redirect(url_for('customer_dashboard'))
    return redirect(url_for('service_professional_dashboard'))

@app.route('/reject_request/<int:id>', methods=['GET','POST'])
def reject_request(id):
    servicerequests=ServiceRequest.query.filter_by(id=id).first()
    servicerequests.professional_id = None
    servicerequests.professional_name = None
    servicerequests.service_status = "requested"
    servicerequests.professional_remarks = None
    db.session.commit()
    return redirect(url_for('service_professional_dashboard'))

@app.route('/update_customer_remarks',methods=['POST'])
def update_customer_remarks():
    servicerequests=ServiceRequest.query.filter_by(id=int(request.form['servicereq_id'])).first()
    if servicerequests.customer_remarks:
        servicerequests.customer_remarks = servicerequests.customer_remarks + "\n" + request.form['customer_remarks']
    else:
        servicerequests.customer_remarks = request.form['customer_remarks']
    db.session.commit()
    return redirect(url_for('customer_dashboard'))

@app.route('/update_SP_remarks',methods=['POST'])
def update_SP_remarks():
    servicerequests=ServiceRequest.query.filter_by(id=int(request.form['servicereq_id'])).first()
    if servicerequests.professional_remarks:
        servicerequests.professional_remarks = servicerequests.professional_remarks + "\n" + request.form['professional_remarks']
    else:
        servicerequests.professional_remarks = request.form['professional_remarks']
    db.session.commit()
    return redirect(url_for('service_professional_dashboard'))

@app.route('/request_service',methods=['POST'])
def request_service():
    if request.method=='POST':
        service_id=request.form['service_id']
        services=Service.query.filter_by(id=service_id).first()
        username = session.get('name')
        cus_id=session.get('id')
        try:
            new_request=ServiceRequest(
                service_id=service_id,
                service_name=services.name,
                service_type=services.service_type,
                customer_id=cus_id,
                customer_name=username,
                date_of_request=date.today(),
                date_of_completion=date.today()+timedelta(days=5),
                service_status="requested",
            )
            db.session.add(new_request)
            db.session.commit()
            services=Service.query.all()
            return redirect(url_for('customer_dashboard'))
        except Exception as e:
            db.session.rollback()
            services=Service.query.all()
            servicerequests=ServiceRequest.query.filter_by(customer_id=cus_id).all()
            return render_template('customer_dashboard.html',username=username,services=services, servicerequest=servicerequests,error="Service Not Requested")

@app.route('/service_request_update/<int:id>', methods=['POST'])
def service_request_update(id):
    servicerequests=ServiceRequest.query.filter_by(id=id).first()
    servicerequests.date_of_request = datetime.strptime(request.form['dor'], "%Y-%m-%d").date()
    servicerequests.date_of_completion = datetime.strptime(request.form['doc'], "%Y-%m-%d").date()
    servicerequests.customer_remarks = request.form['remarks']
    db.session.commit()
    return redirect(url_for('customer_dashboard'))

@app.route('/service_req_upd/<int:id>', methods=['GET','POST'])
def service_req_upd(id):
    service=ServiceRequest.query.filter_by(id=id).first()
    return render_template('service_request_update.html',service=service)

@app.route('/update_servicerequest/<int:id>', methods=['POST'])
def update_servicerequest(id):
    sp_id = session['id']
    sp_name = session['name']
    servicerequests=ServiceRequest.query.filter_by(id=id).first()
    servicerequests.professional_id = sp_id
    servicerequests.professional_name = sp_name
    servicerequests.service_status="assigned"
    servicerequests.date_of_completion = servicerequests.date_of_completion + timedelta(days=int(request.form['date_of_completion']))
    db.session.commit()
    return redirect(url_for('service_professional_dashboard'))

@app.route('/delete_sr/<int:id>', methods=['GET','POST'])
def delete_sr(id):
    ServiceRequests=ServiceRequest.query.filter_by(id=id).first()
    db.session.delete(ServiceRequests)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_cus/<int:id>', methods=['GET','POST'])
def delete_cus(id):
    Cust=Customer.query.filter_by(id=id).first()
    sr=ServiceRequest.query.filter_by(customer_id=id).all()
    if sr:
        for s in sr:
            db.session.delete(s)
    db.session.delete(Cust)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_sp/<int:id>', methods=['POST'])
def delete_sp(id):
    Sp=ServiceProfessional.query.filter_by(id=id).first()
    sr=ServiceRequest.query.filter_by(professional_id=id).first()
    if sr:
        sr.professional_id=None
        sr.professional_name=None
        sr.service_status='requested'
        sr.professional_remarks=None
    db.session.delete(Sp)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/update_sr/<int:id>', methods=['GET','POST'])
def update_sr(id):
    servicerequests=ServiceRequest.query.filter_by(id=id).first()
    sname=servicerequests.service_name
    stype=servicerequests.service_type
    dor=servicerequests.date_of_request
    doc=servicerequests.date_of_completion
    return render_template('update_sr.html', sname=sname, stype=stype, dor=dor, doc=doc, id=id)

@app.route('/search_service', methods=['POST'])
def search_service():
    location = request.form.get('location')
    #print(location)
    service_name = request.form.get('service')
    pincode = None
    if request.form.get('pincode'):
        pincode = int(request.form.get('pincode'))
    Available_Services = None

    if location:
        Available_Services = Service.query.filter_by(location=location)
    if service_name:
        Available_Services = Service.query.filter_by(service_type=service_name)
    if pincode:
        Available_Services = Service.query.filter_by(pincode=pincode)
    
    #print(str(Available_Services))
    if Available_Services:
        session['Available'] = [service.id for service in Available_Services]
    return redirect(url_for('customer_dashboard'))
    

@app.route('/admin')
def admin_dashboard():
    if session['role'] == "customer":
        return redirect(url_for('customer_dashboard'))
    elif session['role'] == "service_professional":
        return redirect(url_for('service_professional_dashboard'))
    professionals=ServiceProfessional.query.all()
    customers=Customer.query.all()
    services=Service.query.all()
    servicerequests=ServiceRequest.query.all()
    return render_template('admin_dashboard.html',username=session['name'],servicerequest=servicerequests,Customers=customers, Professionals=professionals, services=services)

@app.route('/service_professional')
def service_professional_dashboard():
    if session['role'] == "admin":
        return redirect(url_for('admin_dashboard'))
    elif session['role'] == "customer":
        return redirect(url_for('customer_dashboard'))
    username = session.get('name')
    service_professional = ServiceProfessional.query.filter_by(name=username).first()
    servicerequestsp=ServiceRequest.query.filter_by(professional_name=username).all()
    servicerequestst=ServiceRequest.query.filter_by(service_type=session['service_type'],professional_name=None).all()
    all_requests = {s.id: s for s in servicerequestsp + servicerequestst}
    servicerequests = list(all_requests.values())
    if service_professional and (service_professional.status == "blocked" or service_professional.status == "Admin approval Pending"):
        return render_template('service_professional_dashboard.html',username=username,error="You have been Blocked or Pending Admin Approval")
    return render_template('service_professional_dashboard.html',username=username, servicerequests=servicerequests)

@app.route('/customer')
def customer_dashboard():
    if session['role'] == "admin":
        return redirect(url_for('admin_dashboard'))
    elif session['role'] == "service_professional":
        return redirect(url_for('service_professional_dashboard'))
    username = session.get('username')
    cus_id=session.get('id')
    cus=Customer.query.filter_by(id=cus_id).first()
    if cus and (cus.status == "blocked"):
        return render_template('customer_dashboard.html',username=cus.name,error="You have been Blocked")
    services=["AC","Fridge","FullHouseClean","Water_RO_Service","Bathroom_Cleaning","Painting"]
    locations=["Chennai","Chengalpattu","Salem","Nagerkoil","Tirunelveli","Tiruppur","Tiruchirappalli","Kanyakumari"]
    Available_Services=[]
    if 'Available' in session and session['Available']:
        Available_Services = Service.query.filter(Service.id.in_(session['Available'])).all()
    servicerequests=ServiceRequest.query.filter_by(customer_id=cus_id).all()
    return render_template('customer_dashboard.html',username=username,services=services, servicerequests=servicerequests,locations=locations, Available_Services=Available_Services)

if __name__ == '__main__':
    app.run(debug = False)