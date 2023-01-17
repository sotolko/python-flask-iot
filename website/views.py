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
        if topic != 'home/test':
            flash(f'Not subscribed to topic {topic}', category='error')
            return render_template('mqtt_actions.html', user=current_user, spravy=messages)

        mqtt.publish(f'{topic}', f'{message}')

        new_message = MQTT(topic=str(topic), message=str(message))
        db.session.add(new_message)
        db.session.commit()
        flash('Published!', category='success')
        return redirect(url_for('views.mqtt_actions'))

    return render_template('mqtt_actions.html', user=current_user, spravy=messages)
