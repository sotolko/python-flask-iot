from . import db
from flask_login import UserMixin

predmety_ziakov = db.Table('predmety_ziakov',
                           db.Column('ziak_id', db.Integer, db.ForeignKey('ziak.id')),
                           db.Column('predmet_id', db.Integer, db.ForeignKey('predmet.id'))
                           )

predmety_ucitelov = db.Table('predmety_ucitelov',
                             db.Column('ucitel_id', db.Integer, db.ForeignKey('user.id')),
                             db.Column('predmet_id', db.Integer, db.ForeignKey('predmet.id'))
                             )

prezencka = db.Table('prezencka',
                     db.Column('ziak_id', db.Integer, db.ForeignKey('ziak.id')),
                     db.Column('predmet_id', db.Integer, db.ForeignKey('predmet.id')),
                     db.Column('dni', db.Integer, default=0)
                     )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    hodiny = db.relationship('Predmet', secondary=predmety_ucitelov, backref='ucitelia')


class Ziak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isic_number = db.Column(db.Integer)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    pritomnost = db.Column(db.Boolean, default=False)
    hodiny = db.relationship('Predmet', secondary=predmety_ziakov, backref='ziaci')


class Miestnost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(50))
    predmety = db.relationship('Predmet')


class Predmet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazov = db.Column(db.String(150))
    miestnost_id = db.Column(db.Integer, db.ForeignKey('miestnost.id'))
    skupina = db.Column(db.Integer)
    prezencky = db.relationship('Ziak', secondary=prezencka)
