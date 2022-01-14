from flask import Blueprint, render_template, request, flash
from flask_login import login_user, login_required, logout_user, current_user, login_manager
from .models import role_required

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    flash('Вы успешно вошли!' + str(current_user), category='success')
    return render_template("home.html")

@views.route('/Admin/')
@role_required('Admin')
def admin():
    return render_template("admin.html")
