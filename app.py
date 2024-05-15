import os
from peewee import *
from flask import Flask, render_template, request, redirect, url_for
from datetime import date
from datetime import datetime
app = Flask(__name__)
db = SqliteDatabase('bad_docs.db')
        
class Doctor(Model):
    id = IntegerField(unique=True)
    clean_name = CharField()
    doctor_type = CharField()
    license_num = CharField()
    
    class Meta:
        database = db
        table_name = 'doctor_info'

class Text(Model):
    id = IntegerField(unique=True)
    filename = CharField()
    text = CharField()

    class Meta:
        database = db
        table_name = 'text'

class Alert(Model):
    id = CharField(unique=True)
    file_id = CharField(unique=True)
    text_id = ForeignKeyField(Text)
    url = CharField(unique=True)
    doctor_info_id = ForeignKeyField(Doctor)
    first_name = CharField()
    middle_name = CharField()
    last_name = CharField()
    suffix = CharField()
    type = CharField()
    year = IntegerField()
    date = DateField()
    date_str = CharField()
    
    class Meta:
        database = db
        table_name = 'clean_alerts'

class Cases(Model):
    id  = IntegerField(unique=True)
    case_num = CharField()
    file_id = CharField()
    alert_id = ForeignKeyField(Alert)

    class Meta:
        database = db
        table_name = 'all_cases'




@app.route("/")
def index():
    notice_count = Doctor.select().count()
    all_docs = Doctor.select()
    template = 'index.html'
    top_five = Alert.select().order_by(Alert.date.desc()).limit(5)
    type_table = Doctor.select(Doctor.doctor_type, fn.COUNT(Doctor.doctor_type).alias('count')).group_by(Doctor.doctor_type)
    return render_template(template, top_five = top_five, type_table = type_table)

@app.route("/searchdocs", methods=['POST'])
def searchdocs():
    # Get search term from form
    top_five = Alert.select().order_by(Alert.date.desc()).limit(5)
    type_table = Doctor.select(Doctor.doctor_type, fn.COUNT(Doctor.doctor_type).alias('count')).group_by(Doctor.doctor_type)
    search_term = request.form.get('search_term')
    if search_term == "":
        results = "No doctor results found"
    else:
        results = Doctor.select().where(Doctor.clean_name.contains(search_term) | Doctor.license_num.contains(search_term))
    return render_template('index.html', resultsd=results, search_term=search_term, top_five = top_five, type_table=type_table)

@app.route("/searchtext", methods=['POST'])
def searchtext():
    # Get search term from form
    top_five = Alert.select().order_by(Alert.date.desc()).limit(5)
    type_table = Doctor.select(Doctor.doctor_type, fn.COUNT(Doctor.doctor_type).alias('count')).group_by(Doctor.doctor_type)
    search_term = request.form.get('search_term')
    if search_term == "":
        results = "No text results found"
    else:
        textresults = Text.select().where(Text.text.contains(search_term))
        alerts = Alert.select().where(Alert.text_id.in_(textresults))
    return render_template('index.html', resultst=alerts, search_term=search_term, top_five = top_five, type_table = type_table)

@app.route('/doctor/<slug>')
def detail(slug):
    doctor = Doctor.get(Doctor.clean_name==slug)
    doctor_id = doctor.id
    alerts = Alert.select().where(Alert.doctor_info_id==doctor_id)
    cases = Cases.select(Cases.case_num).where(Cases.alert_id.in_(alerts)).distinct()
    top_record = alerts[0]
    return render_template("doctor.html", doctor = doctor, cases = cases, top_record = top_record, alerts = alerts)

@app.route('/type/<slug>')
def type(slug):
    doctors = Doctor.select().where(Doctor.doctor_type==slug)
    count_doc = doctors.count()
    alerts = Alert.select().where(Alert.doctor_info_id.in_(doctors))
    count_alerts = alerts.count()
    cases = Cases.select().where(Cases.alert_id.in_(alerts))
    count_cases = cases.count()
    c1 = cases[0]
    return render_template("type.html", doctors = doctors, alerts = alerts, cases = cases, 
                           countd = count_doc, counta = count_alerts, countc = count_cases, c1 = c1)

# Route for search form submission
@app.route("/dataset")
def dataset():
    cases = Cases.select()
    return render_template("dataset.html", cases = cases)

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)