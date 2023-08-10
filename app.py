# imports
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

# flask app
app = Flask(__name__)

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://database:mwF3G88QOyApHkVnqnkRJIAdixA5Q2Gt@dpg-cja36oq683bs7391qgl0-a.oregon-postgres.render.com/database_x133'
app.config['SECRET_KEY'] = 'xxaladinxx'
db = SQLAlchemy(app)

# uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_files', methods=['POST','GET'])
@login_required
def upload_files():
    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture.filename == '':
            return redirect(request.url)
        if profile_picture and allowed_file(profile_picture.filename):
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_picture_path = filename
        else:
            profile_picture_path = None
    else:
        profile_picture_path = None

    if 'cv' in request.files:
        cv = request.files['cv']
        if cv.filename == '':
            return redirect(request.url)
        if cv and allowed_file(cv.filename):
            filename = secure_filename(cv.filename)
            cv.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cv_path = filename
        else:
            cv_path = None
    else:
        cv_path = None

    description = request.form.get('description')

    info = Info.query.first()
    if not info:
        new_info = Info(description=description, profile_picture_path=profile_picture_path, cv_path=cv_path)
        db.session.add(new_info)
    else:
        info.description = description
        if profile_picture_path:
            info.profile_picture_path = profile_picture_path
        if cv_path:
            info.cv_path = cv_path

    db.session.commit()

    return redirect(url_for('dashboard'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# data tables
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500), default="Default Description")
    profile_picture_path = db.Column(db.String(100), default="default_profile_picture")
    cv_path = db.Column(db.String(100), default="default_cv")

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

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    education_type = db.Column(db.String(50))  # institution or course
    name = db.Column(db.String(150))
    duration = db.Column(db.String(100))
    reference_contact = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    collaborators = db.Column(db.String(150), nullable=True)
    evidence = db.Column(db.String(120), nullable=True)



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
@app.route('/edit_main_information',methods=['GET', 'POST'])
@login_required
def edit_main_information():
    contact_info = Contact.query.first()
    return render_template('edit_main_information.html',contact=contact_info)

# edit education route
@app.route('/edit_education')
@login_required
def edit_education():
    educations = Education.query.all()
    contact_info = Contact.query.first()
    return render_template('edit_education.html',contact=contact_info,educations=educations)

@app.route('/add_education', methods=['GET', 'POST'])
@login_required  # assuming you want this page to be accessible only when logged in
def add_education():
    contact_info = Contact.query.first()
    if request.method == 'POST':
        education_type = request.form.get('education_type')
        name = request.form.get('name')
        duration = request.form.get('duration')
        reference_contact = request.form.get('reference_contact')
        description = request.form.get('description')

        new_education = Education(education_type=education_type, name=name, duration=duration,
                                  reference_contact=reference_contact, description=description)
        db.session.add(new_education)
        db.session.commit()

        flash('Education added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_education.html',contact=contact_info)


@app.route('/update_education/<int:education_id>', methods=['GET', 'POST'])
@login_required
def update_education(education_id):
    contact_info = Contact.query.first()
    education = Education.query.get_or_404(education_id)

    if request.method == 'POST':
        education.education_type = request.form.get('education_type')
        education.name = request.form.get('name')
        education.duration = request.form.get('duration')
        education.reference_contact = request.form.get('reference_contact')
        education.description = request.form.get('description')

        db.session.commit()
        flash('Education updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('update_education.html', education=education,contact=contact_info)

@app.route('/delete_education/<int:education_id>', methods=['GET','POST'])
@login_required
def delete_education(education_id):
    education = Education.query.get_or_404(education_id)

    db.session.delete(education)
    db.session.commit()
    flash('Education deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

# edit projects route
@app.route('/edit_projects')
@login_required
def edit_projects():
    projects = Project.query.all()
    contact_info = Contact.query.first()
    return render_template('edit_projects.html',projects=projects,contact=contact_info)

@app.route('/dashboard/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    contact_info = Contact.query.first()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        duration = request.form.get('duration')
        collaborators = request.form.get('collaborators')

        evidence_filename = None
        evidence_file = request.files.get('evidence')
        if evidence_file and evidence_file.filename != '':
            evidence_filename = secure_filename(evidence_file.filename)
            evidence_file.save(os.path.join(app.config['UPLOAD_FOLDER'], evidence_filename))

        # Create a new project instance and add to the database
        project = Project(
            title=title,
            description=description,
            duration=duration,
            collaborators=collaborators,
            evidence=evidence_filename
        )

        db.session.add(project)
        db.session.commit()

        flash('Project added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('project_form.html',contact=contact_info)

@app.route('/dashboard/update_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def update_project(project_id):
    contact_info = Contact.query.first()
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.duration = request.form.get('duration')
        project.collaborators = request.form.get('collaborators')

        evidence_file = request.files.get('evidence')
        if evidence_file and evidence_file.filename != '':
            if project.evidence:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], project.evidence))
                
            evidence_filename = secure_filename(evidence_file.filename)
            evidence_file.save(os.path.join(app.config['UPLOAD_FOLDER'], evidence_filename))
            project.evidence = evidence_filename

        db.session.commit()

        flash('Project updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('update_project.html', project=project, contact=contact_info)

@app.route('/dashboard/projects/delete/<int:project_id>', methods=['POST','GET'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    db.session.delete(project)
    db.session.commit()

    flash('Project deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


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
    info = Info.query.first()
    if info:
        profile_picture_url = url_for('uploaded_file', filename=info.profile_picture_path) if info.profile_picture_path else None
        cv_url = url_for('uploaded_file', filename=info.cv_path) if info.cv_path else None
        description = info.description
    else:
        profile_picture_url, cv_url, description = None, None, None
    return render_template('index.html', profile_picture_url=profile_picture_url, cv_url=cv_url, description=description,contact=contact_info)

# education route
@app.route('/education')
def education():
    contact_info = Contact.query.first()
    educations = Education.query.all()
    return render_template('education.html',contact=contact_info,educations=educations)

# projects route
@app.route('/projects')
def projects():
    contact_info = Contact.query.first()
    projects = Project.query.all()
    return render_template('projects.html', contact=contact_info,projects=projects)

# contact route
@app.route('/contact')
def contact():
    contact_info = Contact.query.first()
    if not contact_info:
        # Handle this case as you see fit; e.g., render a different template or redirect.
        return "No contact information available."
    info = Info.query.first()
    if info:
        profile_picture_url = url_for('uploaded_file', filename=info.profile_picture_path) if info.profile_picture_path else None
    else:
        profile_picture_url = None
    return render_template('contact.html', contact=contact_info, profile_picture_url=profile_picture_url)


# run app
if __name__ == '__main__':
    #create database
    with app.app_context():
        db.create_all()
        #personalized user
        username = 'cvsofia7'
        password = 'Luisbalamnikobenito7'
        existing_user = User.query.filter_by(username = username).first()
        if existing_user is None:
            owner = User(username = username, password = password)
            db.session.add(owner)
            db.session.commit()
    # run app
    app.run(debug=True)