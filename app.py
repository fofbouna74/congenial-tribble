from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask_login import current_user


# ✅ Instanciation Flask et config
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ton_secret_key_ici'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Initialisation des extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ✅ ROUTES
@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Ce nom d'utilisateur existe déjà.")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Inscription réussie, tu peux maintenant te connecter.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Connexion réussie !')
            return redirect(url_for('tasks'))  # à venir
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.")

    return render_template('login.html')

@app.route('/tasks')
@login_required
def tasks():
    return f"<h1>Bienvenue {current_user.username} sur la page des tâches.</h1>"


# 👇 Important : bloc main à la fin
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    print("\n✅ Routes enregistrées par Flask :")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint} ➜ {rule}")

    app.run(debug=True)
