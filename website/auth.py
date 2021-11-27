from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")


@auth.route('/logout')
def logout():
    pass


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        middleName = request.form.get('middleName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 5:
            flash('Проверьте правильность написания email.', category='error')
        elif len(firstName) < 3:
            flash('Имя должно быть длиннее 2 символов.', category='error')
        elif len(middleName) < 3:
            flash('Отчество должно быть длиннее 2 символов.', category='error')
        elif len(lastName) < 2:
            flash('Фамилия должна быть длиннее 2 символов.', category='error')
        elif password1 != password2:
            flash('Пароли не совпадают.', category='error')
        elif len(password1) < 5:
            flash('Пароль должен быть длиннее 4 символов.', category='error')
        else:
            flash('Учётная звпись создана!', category='success')
    return render_template("sign_up.html")
