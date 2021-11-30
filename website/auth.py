from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask import session as usr
#from .models import Admin, Agent, Clients, engine
from werkzeug.security import generate_password_hash, check_password_hash
#from . import db
from flask_login import login_user, login_required, logout_user, current_user, login_manager
from sqlalchemy.orm import Query, Session
from datetime import datetime, timedelta
from functools import wraps

auth = Blueprint('auth', __name__)
#session = Session(engine)
years = timedelta(days=365)
role = ''

def role_required(role_name):
    def decorator(func):
        @wraps(func)
        def authorize(*args, **kwargs):
            if not usr['current_user'] == role:
                abort(401) # not authorized
            return func(*args, **kwargs)
        return authorize
    return decorator


@auth.route('/login', methods=['GET', 'POST'])
def login():
    from .models import Admin, Agent, Clients, engine
    session = Session(engine)
    if request.method == 'POST':
        Email = request.form.get('email')
        Password = request.form.get('password')
        role = request.form.get('role')
        role_class = eval(role)
        print('done')
        user = session.query(role_class).filter_by(Email=Email).first()
        if user:
            if check_password_hash(user.Password, Password):

                login_user(user, remember=True)
                usr['current_user'] = role
                flash('Вы успешно вошли!' + str(current_user.ClientID), category='success')
                return redirect(url_for('views.home'))
            else:
                flash("Неверный пароль!", category='error')
        else:
            flash("Неверный email!", category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    from .models import Admin, Agent, Clients, engine
    session = Session(engine)
    if request.method == 'POST':
        Email = request.form.get('email')
        FirstName = request.form.get('firstName')
        MiddleName = request.form.get('middleName')
        LastName = request.form.get('lastName')
        DOB = request.form.get('dateOfBirth')
        PhoneNo = request.form.get('phoneNo')
        PostalAddress = request.form.get('address')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        exists = session.query(Clients.Email).filter_by(Email=Email).first()
        date = datetime.strptime(DOB, '%Y-%m-%d')

        if len(Email) < 5:
            flash('Проверьте правильность написания email.', category='error')
        elif exists:
            flash('Пользователь с таким email уже существует.', category='error')
        elif len(FirstName) < 3:
            flash('Имя должно быть длиннее 2 символов.', category='error')
        elif len(LastName) < 3:
            flash('Фамилия должна быть длиннее 2 символов.', category='error')
        elif date < (datetime.now() - years * 110) or date > (datetime.now() - years * 18):
            flash('Вам должно быть больше 18 и меньше 110 лет.', category='error')
        elif len(PhoneNo) < 8:
            flash('Номер телефона должен быть длиннее 7 символов.', category='error')
        elif password1 != password2:
            flash('Пароли не совпадают.', category='error')
        elif len(password1) < 5:
            flash('Пароль должен быть длиннее 4 символов.', category='error')
        else:
            new_client = Clients(Email=Email, FirstName=FirstName, MiddleName=MiddleName,
            LastName=LastName, DOB=DOB, PhoneNo=PhoneNo, PostalAddress=PostalAddress,
            Password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_client)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Учётная запись создана!', category='success')
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", user=current_user)
