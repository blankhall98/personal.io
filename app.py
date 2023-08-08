# imports
from flask import Flask, render_template, request, redirect, url_for, flash, session 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm
from flask_sqlalchemy import SQLAlchemy

# flask app
app = Flask(__name__)

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'xxaladinxx'
db = SQLAlchemy(app)

# data tables
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

# login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))  # Redirect to home if user is already logged in
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # Check if user exists and the password is correct
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))  # Redirect to dashboard page after successful login
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
            
    return render_template('login.html', form=form)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# logout route
@app.route('/logout')
def logout():
    logout_user()  # Logs out the current logged in user
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# edit main information route
@app.route('/edit_main_information')
@login_required
def edit_main_information():
    return render_template('edit_main_information.html')

# edit education route
@app.route('/edit_education')
@login_required
def edit_education():
    return render_template('edit_education.html')

# edit projects route
@app.route('/edit_projects')
@login_required
def edit_projects():
    return render_template('edit_projects.html')

# edit contact route
@app.route('/edit_contact')
@login_required
def edit_contact():
    return render_template('edit_contact.html')

# main route
@app.route('/')
def index():
    return render_template('index.html')

# education route
@app.route('/education')
def education():
    return render_template('education.html')

# projects route
@app.route('/projects')
def projects():
    return render_template('projects.html')

# contact route
@app.route('/contact')
def contact():
    return render_template('contact.html')


# run app
if __name__ == '__main__':
    app.run(debug=True)