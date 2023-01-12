from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .models import Ziak

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    ziaci = Ziak.query.all()
    return render_template('home.html', user=current_user, ziaci=ziaci)
