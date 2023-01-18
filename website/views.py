import datetime
import json

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from .models import Ziak, MQTT, Predmet, Attendance
from . import mqtt, db, create_app
from sqlalchemy import desc
import os

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    predmety = Predmet.query.all()

    if request.method == 'POST':
        id = request.form.get('inlineFormCustomSelectPref')
        return redirect(url_for('results', id=id))

    return render_template('home.html', user=current_user, predmety=predmety)


@views.route('/submit', methods=['POST'])
@login_required
def submit():
    if request.method == 'POST':
        id = request.form.get('inlineFormCustomSelectPref')
        return redirect(url_for('views.results', id=id))

    redirect(url_for('views.home'))


@views.route('/search/<id>', methods=['GET'])
@login_required
def results(id):
    prezencky = Attendance.query.filter(Attendance.Hodina_id == id).all()
    ziaci = Ziak.query.all()
    return render_template("results.html", user=current_user, prezencka_ziaci=prezencky, ziaci=ziaci)


@views.route('/mqtt-send', methods=['GET', 'POST'])
@login_required
def mqtt_actions():
    messages = MQTT.query.order_by(desc(MQTT.date)).limit(10).all()

    if request.method == 'POST':
        isic_number = request.form.get('send-isic')
        send_week = request.form.get('send-time')
        hodina_id = request.form.get('send-id')
        topic = request.form.get('send-topic')

        if len(isic_number) > 20:
            flash('ISIC nesmie byt vacsi ako 20 znakov!', category='error')
            return render_template('mqtt_actions.html', user=current_user, spravy=messages)
        elif len(send_week) > 13 or len(send_week) < 1:
            flash('Tyzden musi byt 1-13!', category='error')
            return render_template('mqtt_actions.html', user=current_user, spravy=messages)
        elif not send_week.isnumeric():
            flash('Tyzden musi byt cislo!', category='error')
            return render_template('mqtt_actions.html', user=current_user, spravy=messages)
        elif topic != 'home/prezencka' and topic != 'home/ospravedlnenie':
            flash(f'Not subscribed to topic {topic}', category='error')
            return render_template('mqtt_actions.html', user=current_user, spravy=messages)

        send_msg = {
            'isic': isic_number,
            'week': send_week,
            'hodina_id': hodina_id
        }

        mqtt.publish(f'{topic}', f'{json.dumps(send_msg)}')

        flash('Published!', category='success')

        return redirect(url_for('views.mqtt_actions'))

    return render_template('mqtt_actions.html', user=current_user, spravy=messages, date=datetime.datetime.now())


@views.route('/admin-create-user', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if request.method == 'POST':
        first_name = request.form.get('ziak-firstname')
        last_name = request.form.get('ziak-lastname')
        isic_number = request.form.get('ziak-isic')

        if len(first_name) > 150:
            flash('Meno nesmie byt vacsie ako 150 znakov!', category='error')
            return render_template('admin_create_user.html', user=current_user)
        elif len(last_name) > 150:
            flash('Priezvisko nesmie byt vacsie ako 150 znakov!', category='error')
            return render_template('admin_create_user.html', user=current_user)
        elif len(isic_number) > 20:
            flash('ISIC nesmie byt vacsi ako 20 znakov!', category='error')
            return render_template('admin_create_user.html', user=current_user)

        new_ziak = Ziak(first_name=first_name, last_name=last_name,isic_number=isic_number)
        db.session.merge(new_ziak)
        db.session.commit()
        flash('Ziak vytvoreny!', category='success')

    return render_template('admin_create_user.html', user=current_user)
