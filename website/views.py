from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Ziak, MQTT
from . import mqtt, db
from sqlalchemy import desc


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    ziaci = Ziak.query.all()
    return render_template('home.html', user=current_user, ziaci=ziaci)


@views.route('/mqtt-send', methods=['GET', 'POST'])
@login_required
def mqtt_actions():
    messages = MQTT.query.order_by(desc(MQTT.date)).limit(10).all()

    if request.method == 'POST':
        message = request.form.get('mqtt-send')
        topic = request.form.get('mqtt-topic')

        if len(message) > 20:
            flash('Sprava nesmie byt vacsia ako 20 znakov!', category='error')
            return render_template('mqtt_actions.html', user=current_user, spravy=messages)
        elif len(topic) > 100:
            flash('Topic nesmie byt vacsi ako 100 znakov!', category='error')
            return render_template('mqtt_actions.html', user=current_user, spravy=messages)
        elif topic != 'home/test':
            flash(f'Not subscribed to topic {topic}', category='error')
            return render_template('mqtt_actions.html', user=current_user, spravy=messages)

        mqtt.publish(f'{topic}', f'{message}')

        new_message = MQTT(topic=str(topic), message=str(message))
        db.session.add(new_message)
        db.session.commit()
        flash('Published!', category='success')
        return redirect(url_for('views.mqtt_actions'))

    return render_template('mqtt_actions.html', user=current_user, spravy=messages)

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
        db.session.add(new_ziak)
        db.session.commit()
        flash('Ziak vytvoreny!', category='success')

    return render_template('admin_create_user.html', user=current_user)
