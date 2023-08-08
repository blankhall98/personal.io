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

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="Default Name")
    professional_title = db.Column(db.String(100), default="Default Title")
    description = db.Column(db.String(500), default="Default Description")
    email = db.Column(db.String(100), default="default@example.com")
    cellphone = db.Column(db.String(20), default="123-456-7890")
    instagram = db.Column(db.String(100), default="default_instagram")
    facebook = db.Column(db.String(100), default="default_facebook")
    linkedin = db.Column(db.String(100), default="default_linkedin")

# login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/login', methods=['GET', 'POST'])
def login():
    contact_info = Contact.query.first()
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
            
    return render_template('login.html', form=form, contact=contact_info)

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
    contact_info = Contact.query.first()
    return render_template('dashboard.html', contact=contact_info)

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
@app.route('/edit_contact', methods=['GET', 'POST'])
@login_required
def edit_contact():
    # Assuming there's only one row for the user's contact information.
    contact_info = Contact.query.first()

    # If the contact_info doesn't exist, create a default one.
    if not contact_info:
        contact_info = Contact()
        db.session.add(contact_info)
        db.session.commit()

    if request.method == 'POST':
        contact_info.name = request.form['name']
        contact_info.professional_title = request.form['professional_title']
        contact_info.description = request.form['description']
        contact_info.email = request.form['email']
        contact_info.cellphone = request.form['cellphone']
        contact_info.instagram = request.form['instagram']
        contact_info.facebook = request.form['facebook']
        contact_info.linkedin = request.form['linkedin']
        db.session.commit()

        flash('Contact information updated successfully!', 'success')
        return redirect(url_for('edit_contact'))

    return render_template('edit_contact.html', contact=contact_info)

# main route
@app.route('/main')
def main():
    contact_info = Contact.query.first()
    return render_template('base.html',contact=contact_info)

@app.route('/')
def index():
    contact_info = Contact.query.first()
    return render_template('index.html',contact=contact_info)

# education route
@app.route('/education')
def education():
    contact_info = Contact.query.first()
    return render_template('education.html',contact=contact_info)

# projects route
@app.route('/projects')
def projects():
    contact_info = Contact.query.first()
    return render_template('projects.html', contact=contact_info)

# contact route
@app.route('/contact')
def contact():
    contact_info = Contact.query.first()
    if not contact_info:
        # Handle this case as you see fit; e.g., render a different template or redirect.
        return "No contact information available."
    return render_template('contact.html', contact=contact_info)


# run app
if __name__ == '__main__':
    app.run(debug=True)