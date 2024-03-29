from . import db
from flask_login import UserMixin
import datetime

predmety_ucitelov = db.Table('predmety_ucitelov',
                             db.Column('ucitel_id', db.Integer, db.ForeignKey('user.id')),
                             db.Column('hodina_id', db.Integer, db.ForeignKey('hodina.id'))
                             )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    hodiny = db.relationship('Hodina', secondary=predmety_ucitelov, backref='ucitel')


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Week_1 = db.Column(db.String(1), default='N')
    Week_2 = db.Column(db.String(1), default='N')
    Week_3 = db.Column(db.String(1), default='N')
    Week_4 = db.Column(db.String(1), default='N')
    Week_5 = db.Column(db.String(1), default='N')
    Week_6 = db.Column(db.String(1), default='N')
    Week_7 = db.Column(db.String(1), default='N')
    Week_8 = db.Column(db.String(1), default='N')
    Week_9 = db.Column(db.String(1), default='N')
    Week_10 = db.Column(db.String(1), default='N')
    Week_11 = db.Column(db.String(1), default='N')
    Week_12 = db.Column(db.String(1), default='N')
    Week_13 = db.Column(db.String(1), default='N')
    Hodina_id = db.Column(db.Integer, db.ForeignKey('hodina.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('ziak.id'))
    # ziaci = db.relationship('Ziak', backref='ziaci')
    # prezencka_ziaka = db.relationship('Ziak', secondary=prezencka, backref='prezencka_ziaka')


class Ziak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isic_number = db.Column(db.Integer, unique=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(30))
    attendance = db.relationship('Attendance', backref='ziak')
    # ziakova_prezencka = db.relationship('Attendance', secondary=prezencka, backref='prezencka_ziaka')


class Hodina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Time = db.Column(db.DateTime)
    Class = db.Column(db.String(10))
    Subject_id = db.Column(db.Integer, db.ForeignKey('predmet.id'))
    # Attendances = db.relationship('prezencka', backref='prezencka')
    # ucitelia = db.relationship('User', secondary=predmety_ucitelov, backref='ucitelia')


class Predmet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Nazov = db.Column(db.String(150))
    Hodina = db.relationship('Hodina', backref='Hodina')


class MQTT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100))
    message = db.Column(db.String(20))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
