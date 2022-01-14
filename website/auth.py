from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask import session as usr
#from .models import Admin, Agent, Clients, engine
from werkzeug.security import generate_password_hash, check_password_hash
#from . import db
from flask_login import login_user, logout_user, current_user
from sqlalchemy.orm import Query, Session
from datetime import datetime, timedelta
from functools import wraps
from .models import login_required
from sqlalchemy import desc, null
from . import db
import sys

auth = Blueprint('auth', __name__)
admin = Blueprint('admin', __name__)
agent = Blueprint('agent', __name__)
#session = Session(engine)
years = timedelta(days=365)

from .models import User, Purchase, Policy, Client, Admin, Agent

@auth.route('/', methods=['GET', 'POST'])
@login_required()
def home():
    values = [db.session.query(Agent).count(), db.session.query(Client).count()]
    return render_template("home.html", user=current_user, values=values, route="/")


@admin.route('/', methods=['GET', 'POST'])
@login_required('Admin')
def admin_homepage():
    return render_template("admin.html", user=current_user, route="/Admin")

@agent.route('/', methods=['GET', 'POST'])
@login_required('Agent')
def agent_homepage():
    return render_template("agent.html", user=current_user, route="/Agent")

@auth.route('/my_account', methods=['GET', 'POST'])
@admin.route('/my_account', methods=['GET', 'POST'])
@agent.route('/my_account', methods=['GET', 'POST'])
@login_required()
def my_account():
    if request.method == 'POST' and current_user.urole == 'Admin':
        my_data = Admin.query.get(current_user.id)
        print(my_data, file=sys.stderr)
        my_data.user.email = request.form.get('email')
        my_data.first_name = request.form.get('first_name')
        my_data.middle_name = request.form.get('middle_name')
        my_data.last_name = request.form.get('last_name')
        my_data.license_no = request.form.get('phone_no')
        if not request.form.get('password') == "":
            if len(request.form.get('password')) < 5:
                flash('Пароль должен быть длиннее 4 символов.', category='error')
            else:
                my_data.user.password = generate_password_hash(request.form.get('password'), method='sha256')
        else:
            db.session.commit()
            flash("Информация обновлена успешно!")

    if request.method == 'POST' and current_user.urole == 'Agent':
        my_data = Agent.query.get(current_user.id)
        my_data.user.email = request.form.get('email')
        my_data.first_name = request.form.get('first_name')
        my_data.middle_name = request.form.get('middle_name')
        my_data.last_name = request.form.get('last_name')
        my_data.license_no = request.form.get('license_no')
        my_data.comission = request.form.get('comission')
        if not request.form.get('password') == "":
            if len(request.form.get('password')) < 5:
                flash('Пароль должен быть длиннее 4 символов.', category='error')
            else:
                my_data.user.password = generate_password_hash(request.form.get('password'), method='sha256')
        else:
            db.session.commit()
            flash("Информация обновлена успешно!")

    if request.method == 'POST' and current_user.urole == 'Client':
        my_data = Client.query.get(current_user.id)
        my_data.user.email = request.form.get('email')
        my_data.first_name = request.form.get('first_name')
        my_data.middle_name = request.form.get('middle_name')
        my_data.last_name = request.form.get('last_name')
        my_data.date_of_birth = request.form.get('date_of_birth')
        my_data.phone_no = request.form.get('phone_no')
        my_data.address = request.form.get('address')
        if not request.form.get('password') == "":
            if len(request.form.get('password')) < 5:
                flash('Пароль должен быть длиннее 4 символов.', category='error')
            else:
                my_data.user.password = generate_password_hash(request.form.get('password'), method='sha256')
        else:
            db.session.commit()
            flash("Информация обновлена успешно!")

    if current_user.urole == 'Admin':
        admins = Admin.query.filter_by(user_id=current_user.id).first()
        return render_template("admin/my_account.html", user=current_user, admins=admins, route="/Admin")
    elif current_user.urole == 'Agent':
        agents = Agent.query.filter_by(user_id=current_user.id).first()
        return render_template("agent/my_account.html", user=current_user, agents=agents, route="/Agent")
    else:
        clients = Client.query.filter_by(user_id=current_user.id).first()
        return render_template("client/my_account.html", user=current_user, clients=clients, route="/")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    from .models import User
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                current_user.role = user.urole
                flash('Вы успешно вошли! ' + str(current_user.role), category='success')
                user = current_user
                if current_user.role == 'Admin':
                    return redirect(url_for('admin.admin_homepage'))
                if current_user.role == 'Agent':
                    return redirect(url_for('agent.agent_homepage'))
                return redirect(url_for('auth.home'))
            else:
                flash("Неверный пароль!", category='error')
        else:
            flash("Неверный email!", category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required()
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    from . import db
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        middle_name = request.form.get('middleName')
        last_name = request.form.get('lastName')
        date_of_birth = request.form.get('dateOfBirth')
        phone_no = request.form.get('phoneNo')
        address = request.form.get('address')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        exists = User.query.filter_by(email=email).first()
        date = datetime.strptime(date_of_birth, '%Y-%m-%d')

        if len(email) < 5:
            flash('Проверьте правильность написания email.', category='error')
        elif exists:
            flash('Пользователь с таким email уже существует.', category='error')
        elif len(first_name) < 3:
            flash('Имя должно быть длиннее 2 символов.', category='error')
        elif len(last_name) < 3:
            flash('Фамилия должна быть длиннее 2 символов.', category='error')
        elif date < (datetime.now() - years * 110) or date > (datetime.now() - years * 18):
            flash('Вам должно быть больше 18 и меньше 110 лет.', category='error')
        elif len(phone_no) < 8:
            flash('Номер телефона должен быть длиннее 7 символов.', category='error')
        elif password1 != password2:
            flash('Пароли не совпадают.', category='error')
        elif len(password1) < 5:
            flash('Пароль должен быть длиннее 4 символов.', category='error')
        else:
            new_user = User(email=email, password=generate_password_hash(password1, method='sha256'), urole='Client')
            db.session.add(new_user)
            db.session.commit()
            db.session.refresh(new_user)
            new_client = Client(first_name=first_name, middle_name=middle_name, last_name=last_name, date_of_birth=date_of_birth, phone_no=phone_no, address=address, user_id=new_user.id)
            db.session.add(new_client)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Учётная запись создана!', category='success')
            return redirect(url_for('auth.home'))
    return render_template("sign_up.html", user=current_user)


@admin.route('/agents', methods=['GET', 'POST'])
@login_required('Admin')
def agents():
    if request.method == 'POST' and "form1-submit" in request.form:
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        middle_name = request.form.get('middleName')
        last_name = request.form.get('lastName')
        license_no = request.form.get('licenseNo')
        comission = request.form.get('comission')
        password = request.form.get('password')

        exists = User.query.filter_by(email=email).first()

        if len(email) < 5:
            flash('Проверьте правильность написания email.', category='error')
        elif exists:
            flash('Пользователь с таким email уже существует.', category='error')
        elif len(first_name) < 3:
            flash('Имя должно быть длиннее 2 символов.', category='error')
        elif len(last_name) < 3:
            flash('Фамилия должна быть длиннее 2 символов.', category='error')
        elif len(password) < 5:
            flash('Пароль должен быть длиннее 4 символов.', category='error')
        else:
            new_user = User(email=email, password=generate_password_hash(password, method='sha256'), urole='Agent')
            db.session.add(new_user)
            db.session.commit()
            db.session.refresh(new_user)
            new_agent = Agent(first_name=first_name, middle_name=middle_name, last_name=last_name, license_no=license_no, comission=float(comission), admin_id=1, user_id=new_user.id)
            db.session.add(new_agent)
            db.session.commit()
            flash('Учётная запись агента создана!', category='success')

    agents = Agent.query.all()
    return render_template("admin/agents.html", user=current_user, agents=agents, route="/Admin")

@admin.route('/agent_update', methods=['GET', 'POST'])
@login_required('Admin')
def update_agent():
    if request.method == 'POST':
        my_data = Agent.query.get(request.form.get('id'))
        my_data.user.email = request.form.get('email')
        if not request.form.get('password') == "":
            my_data.user.password = generate_password_hash(request.form.get('password'), method='sha256')
        my_data.first_name = request.form.get('firstName')
        my_data.middle_name = request.form.get('middleName')
        my_data.last_name = request.form.get('lastName')
        my_data.license_no = request.form.get('licenseNo')
        my_data.comission = request.form.get('comission')

        db.session.commit()
        flash("Информация об агенте обновлена успешно!")

    agents = Agent.query.all()
    return redirect(url_for('admin.agents'))


@admin.route('/agent_delete/<id>/', methods=['GET', 'POST'])
@login_required('Admin')
def delete_agent(id):
    my_data = Agent.query.get(id)
    my_data2 = User.query.get(id)
    db.session.delete(my_data)
    db.session.delete(my_data2)
    db.session.commit()
    flash("Агент удален успешно!")
    agents = Agent.query.all()
    return redirect(url_for('admin.agents'))

@admin.route('/clients', methods=['GET', 'POST'])
@login_required('Admin')
def clients():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        date_of_birth = request.form.get('date_of_birth')
        phone_no = request.form.get('phone_no')
        address = request.form.get('address')
        agent_id = request.form.get('agent_id')
        password = request.form.get('password')

        exists = User.query.filter_by(email=email).first()
        agent_exists = Agent.query.filter_by(user_id=agent_id).first()
        date = datetime.strptime(date_of_birth, '%Y-%m-%d')

        if len(email) < 5:
            flash('Проверьте правильность написания email.', category='error')
        elif exists:
            flash('Пользователь с таким email уже существует.', category='error')
        elif len(first_name) < 3:
            flash('Имя должно быть длиннее 2 символов.', category='error')
        elif len(last_name) < 3:
            flash('Фамилия должна быть длиннее 2 символов.', category='error')
        elif date < (datetime.now() - years * 110) or date > (datetime.now() - years * 18):
            flash('Вам должно быть больше 18 и меньше 110 лет.', category='error')
        elif len(phone_no) < 8:
            flash('Номер телефона должен быть длиннее 7 символов.', category='error')
        elif len(password) < 5:
            flash('Пароль должен быть длиннее 4 символов.', category='error')
        else:
            if not agent_exists:
                if agent_id == "":
                    pass
                else:
                    flash('Не удалось найти агента.', category='error')
                    return render_template("admin/clients.html", user=current_user, clients=clients, route="/Admin")

            if agent_id == "":
                agent_id = None

            new_user = User(email=email, password=generate_password_hash(password, method='sha256'), urole='Client')
            db.session.add(new_user)
            db.session.commit()
            db.session.refresh(new_user)
            new_client = Client(first_name=first_name, middle_name=middle_name, last_name=last_name, date_of_birth=date_of_birth, phone_no=phone_no, agent_id=agent_id, address=address, user_id=new_user.id)
            db.session.add(new_client)
            db.session.commit()
            flash('Учётная запись клиента создана!', category='success')

    clients = Client.query.all()
    return render_template("admin/clients.html", user=current_user, clients=clients, route="/Admin")

@admin.route('/client_update', methods=['GET', 'POST'])
@login_required('Admin')
def update_client():
    clients = Client.query.all()
    if request.method == 'POST':
        my_data = Client.query.get(request.form.get('id'))
        my_data.user.email = request.form.get('email')
        if not request.form.get('password') == "":
            my_data.user.password = generate_password_hash(request.form.get('password'), method='sha256')
        my_data.first_name = request.form.get('first_name')
        my_data.middle_name = request.form.get('middle_name')
        my_data.last_name = request.form.get('last_name')
        my_data.date_of_birth = request.form.get('date_of_birth')
        my_data.phone_no = request.form.get('phone_no')

        if request.form.get('agent_id') == "":
            my_data.agent_id = null()
        elif Agent.query.filter_by(user_id=request.form.get('agent_id')).first():
            my_data.agent_id = request.form.get('agent_id')
        else:
            flash('Не удалось найти агента.', category='error')

        my_data.address = request.form.get('address')

        db.session.commit()
        flash("Информация о клиенте обновлена успешно!")

        clients = Client.query.all()
        return redirect(url_for('admin.clients'))

@admin.route('/client_delete/<id>/', methods=['GET', 'POST'])
@login_required('Admin')
def delete_client(id):
    my_data = db.session.query(Client).filter_by(user_id=id).first()
    my_data2 = User.query.get(id)
    db.session.delete(my_data)
    db.session.delete(my_data2)
    db.session.commit()
    flash("Клиент удален успешно!")
    clients = Client.query.all()
    return redirect(url_for('admin.clients'))

@agent.route('/clients', methods=['GET', 'POST'])
@login_required('Agent')
def ag_clients():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        date_of_birth = request.form.get('date_of_birth')
        phone_no = request.form.get('phone_no')
        address = request.form.get('address')
        agent_id = request.form.get('agent_id')
        password = request.form.get('password')

        exists = User.query.filter_by(email=email).first()
        date = datetime.strptime(date_of_birth, '%Y-%m-%d')

        if len(email) < 5:
            flash('Проверьте правильность написания email.', category='error')
        elif exists:
            flash('Пользователь с таким email уже существует.', category='error')
        elif len(first_name) < 3:
            flash('Имя должно быть длиннее 2 символов.', category='error')
        elif len(last_name) < 3:
            flash('Фамилия должна быть длиннее 2 символов.', category='error')
        elif date < (datetime.now() - years * 110) or date > (datetime.now() - years * 18):
            flash('Вам должно быть больше 18 и меньше 110 лет.', category='error')
        elif len(phone_no) < 8:
            flash('Номер телефона должен быть длиннее 7 символов.', category='error')
        elif len(password) < 5:
            flash('Пароль должен быть длиннее 4 символов.', category='error')
        else:
            new_user = User(email=email, password=generate_password_hash(password, method='sha256'), urole='Client')
            db.session.add(new_user)
            db.session.commit()
            db.session.refresh(new_user)
            new_client = Client(first_name=first_name, middle_name=middle_name, last_name=last_name, date_of_birth=date_of_birth, phone_no=phone_no, agent_id=agent_id, address=address, user_id=new_user.id)
            db.session.add(new_client)
            db.session.commit()
            flash('Учётная запись клиента создана!', category='success')

    clients = Client.query.all()
    return render_template("agent/clients.html", user=current_user, clients=clients, route="/Agent")


@agent.route('/client_link/<id>/', methods=['GET', 'POST'])
@login_required('Agent')
def link_client(id):
    my_data = Client.query.get(id)

    if my_data.agent_id == current_user.id:
         my_data.agent_id = null()
         db.session.commit()
         flash("Клиент отвязан успешно!")
    else:
        my_data.agent_id = current_user.id
        db.session.commit()
        flash("Клиент привязан успешно!")

    clients = Client.query.all()
    return redirect(url_for('agent.ag_clients'))

@auth.route('/policies', methods=['GET', 'POST'])
@agent.route('/policies', methods=['GET', 'POST'])
@admin.route('/policies', methods=['GET', 'POST'])
@login_required()
def policies():
    if request.method == 'POST' and "form1-submit" in request.form:
        ptype = request.form.get('ptype')
        validity = request.form.get('validity')
        company_name = request.form.get('company_name')
        amount_sum = request.form.get('amount_sum')
        agent_id = request.form.get('agent_id')

        agent_exists = Agent.query.filter_by(user_id=agent_id).first()

        if not agent_exists:
            if agent_id == "":
                pass
            else:
                flash('Не удалось найти агента.', category='error')

        new_policy = Policy(ptype=ptype, validity=validity, company_name=company_name, amount_sum=float(amount_sum), agent_id=agent_id)
        db.session.add(new_policy)
        db.session.commit()
        flash('Новый полис успешно добавлен!', category='success')

    if request.method == 'POST' and "purchase-submit" in request.form:
        policy_id = request.form.get('purchase-submit')
        new_purchase = Purchase(policy_id=policy_id, client_id=current_user.id)
        db.session.add(new_purchase)
        db.session.commit()

    policies = Policy.query.all()
    if current_user.urole == 'Admin':
        policies = Policy.query.all()
        return render_template("admin/policies.html", user=current_user, policies=policies, route="/Admin")
    elif current_user.urole == 'Agent':
        return render_template("agent/policies.html", user=current_user, policies=policies, route="/Agent")
    else:
        owned_items = Purchase.query.filter_by(client_id=current_user.id).all()
        return render_template("client/policies.html", user=current_user, policies=policies, owned_items=owned_items, route="/")



@admin.route('/policy_update', methods=['GET', 'POST'])
@login_required('Admin', 'Agent')
def update_policy():
    if request.method == 'POST' and "form2-submit" in request.form:
        my_data = Policy.query.get(request.form.get('id'))
        if request.form.get('ptype'):
            my_data.ptype = request.form.get('ptype')
        if request.form.get('validity'):
            my_data.validity = request.form.get('validity')
        if request.form.get('company_name'):
            my_data.company_name = request.form.get('company_name')
        if request.form.get('amount_sum'):
            my_data.amount_sum = request.form.get('amount_sum')

        if request.form.get('agent_id') == "0":
            my_data.agent_id = null()
            db.session.commit()
            flash("Информация о полисе обновлена успешно!")
        elif Agent.query.filter_by(user_id=request.form.get('agent_id')).first():
            my_data.agent_id = request.form.get('agent_id')
            db.session.commit()
            flash("Информация о полисе обновлена успешно!")
        else:
            flash('Не удалось найти агента.', category='error')

    policies = Policy.query.all()
    if current_user.urole == 'Admin':
        return redirect(url_for('admin.policies'))
    else:
        return redirect(url_for('agent.policies'))

@admin.route('/policy_delete/<id>/', methods=['GET', 'POST'])
@login_required('Admin', 'Agent')
def delete_policy(id):
    my_data = db.session.query(Policy).filter_by(id=id).first()
    db.session.delete(my_data)
    db.session.commit()
    flash("Полис удален успешно!")
    policies = Policy.query.all()
    if current_user.urole == 'Admin':
        return redirect(url_for('admin.policies'))
    else:
        return redirect(url_for('agent.policies'))

@agent.route('/purchases', methods=['GET', 'POST'])
@admin.route('/purchases', methods=['GET', 'POST'])
@login_required('Admin', 'Agent')
def purchases():
    if request.method == 'POST' and "form1-submit" in request.form:
        purchase_date = request.form.get('purchase_date')
        policy_id = request.form.get('policy_id')
        client_id = request.form.get('client_id')

        client_exists = Client.query.filter_by(user_id=client_id).first()
        policy_exists = Policy.query.filter_by(id=policy_id).first()

        if not client_exists:
            flash('Не удалось найти клиента.', category='error')
        elif not policy_exists:
            flash('Не удалось найти полис.', category='error')
        else:
            new_purchase = Purchase(purchase_date=purchase_date, policy_id=policy_id, client_id=client_id)
            db.session.add(new_purchase)
            db.session.commit()
            flash('Новая покупка успешно создана!', category='success')

    purchases = Purchase.query.all()
    if current_user.urole == 'Admin':
        return render_template("admin/purchases.html", user=current_user, purchases=purchases, route="/Admin")
    else:
        policies = Policy.query.filter_by(agent_id=current_user.id).all()
        clients = Client.query.filter_by(agent_id=current_user.id).all()
        return render_template("agent/purchases.html", user=current_user, policies=policies, clients=clients, purchases=purchases, route="/Agent")

@admin.route('/purchase_update', methods=['GET', 'POST'])
@login_required('Admin')
def update_purchase():
    if request.method == 'POST' and "form2-submit" in request.form:
        my_data = Purchase.query.get(request.form.get('id'))
        my_data.purchase_date = request.form.get('purchase_date')
        my_data.policy_id = request.form.get('policy_id')
        my_data.client_id = request.form.get('client_id')

        db.session.commit()
        flash("Информация о полисе обновлена успешно!")

    purchases = Purchase.query.all()
    return redirect(url_for('admin.purchases'))

@admin.route('/purchase_delete/<id>/', methods=['GET', 'POST'])
@login_required('Admin')
def delete_purchase(id):
    my_data = db.session.query(Purchase).filter_by(id=id).first()
    db.session.delete(my_data)
    db.session.commit()
    flash("Покупка удалена успешно!")

    purchases = Purchase.query.all()
    return redirect(url_for('admin.purchases'))
