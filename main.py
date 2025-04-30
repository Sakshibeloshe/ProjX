#from flask import Flask, render_template, request
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Add this if not already present


# Configure the MySQL database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123@localhost/proj'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    prn=db.Column(db.Integer)
    department = db.Column(db.String(100))
    expertise = db.Column(db.String(255))  # comma-separated
    interests = db.Column(db.String(255))
    about_me = db.Column(db.Text)
    profile_image = db.Column(db.LargeBinary)


class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'))
    role_name = db.Column(db.String(100))
    requirements = db.Column(db.Text)
    status = db.Column(db.String(20))


class Project(db.Model):
    __tablename__ = 'projects'
    project_id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    keywords = db.Column(db.String(255))
    status = db.Column(db.Enum('Ongoing','Completed'), default='Ongoing')
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    roles = db.relationship('Role', backref='project', cascade='all, delete')
    members = db.relationship('ProjectMembership', backref='membership_project', cascade='all, delete')

class ProjectMembership(db.Model):
    __tablename__ = 'project_members'
    
    # Composite primary key
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'))
    is_leader = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship backrefs
    project = db.relationship('Project', backref=db.backref('memberships', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('projects', lazy='dynamic'))
    role = db.relationship('Role', backref=db.backref('memberships', lazy='dynamic'))


class ProjectUpdate(db.Model):
    __tablename__ = 'project_updates'

    update_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    update_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional: backref to project if needed
    project = db.relationship('Project', backref=db.backref('updates', lazy=True, cascade="all, delete"))


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            return redirect(url_for('search_projects'))  # or wherever you want to go
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        department = request.form['department']
        age = int(request.form['age'])
        prn=int(request.form['prn'])
        expertise = request.form['expertise']  # comma-separated string
        interests = request.form['interests']  # comma-separated string
        about_me = request.form.get('about_me', '')

        new_user = User(
            name=name,
            email=email,
            username=username,
            password=password,
            department=department,
            age=age,
            prn=prn,
            expertise=expertise,
            interests=interests,
            about_me=about_me
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/search_projects')
def search_projects():
    keyword = request.args.get('keyword')
    status = request.args.get('status')
    role = request.args.get('role')
    name = request.args.get('name')


    query = Project.query

    if keyword:
        query = query.filter(Project.keywords.like(f"%{keyword}%"))
    if status:
        query = query.filter(Project.status == status)
    if name:
        query = query.filter(Project.project_name.like(f"%{name}%"))

    projects = query.all()

    #  Get all keywords from DB and split by comma
    all_keyword_strings = db.session.query(Project.keywords).all()
    keyword_list = []

    for item in all_keyword_strings:
        if item[0]:
            keyword_list.extend([kw.strip() for kw in item[0].split(',')])

    # Get unique keywords
    unique_keywords = sorted(set(keyword_list))

    statuses = ['Ongoing', 'Completed', 'Upcoming']

    unique_roles = [row.role_name for row in db.session.query(Role.role_name).distinct().all()]


    return render_template('project_search.html', projects=projects, statuses=statuses, 
                           available_keywords=unique_keywords, roles= unique_roles)


@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')  # Or your login route

    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    user = User.query.get(user_id)
    if user:
        user.name = request.form.get('name')
        user.age = request.form.get('age')
        user.department = request.form.get('department')
        user.education = request.form.get('education')
        user.email = request.form.get('email')
        user.contact = request.form.get('contact')
        user.prn = request.form.get('prn')

        db.session.commit()
        return redirect(url_for('profile'))
    return "User not found", 404

@app.route('/delete_profile', methods=['POST'])
def delete_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    # Check if user has created any projects
    user_projects = Project.query.filter_by(created_by=user_id).first()
    if user_projects:
        return "Cannot delete profile: You are the creator of one or more projects. Please delete or transfer them first.", 400

    # If no projects, delete memberships and the user
    ProjectMembership.query.filter_by(user_id=user_id).delete()
    db.session.delete(User.query.get(user_id))
    db.session.commit()
    session.clear()
    return redirect('/signup')




from flask import render_template, request, redirect, session
from datetime import datetime

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('project_name')
        desc = request.form.get('description')
        keywords = request.form.get('keywords')
        status = request.form.get('status', 'Ongoing')  # Default to Ongoing if missing
        created_by = session.get('user_id')

        if not name or not created_by:
            return "Missing required fields", 400

        # Add project to DB
        new_proj = Project(
            project_name=name,
            description=desc,
            keywords=keywords,
            status=status,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        db.session.add(new_proj)
        db.session.commit()

        project_id = new_proj.project_id

        # Save roles
        roles = request.form.getlist('roles[]')
        requirements = request.form.getlist('role_requirements[]')
        statuses = request.form.getlist('role_status[]')

        for r, req, stat in zip(roles, requirements, statuses):
            role = Role(project_id=project_id, role_name=r, requirements=req, status=stat)
            db.session.add(role)

        # Save members
        usernames = request.form.getlist('member_usernames[]')
        member_roles = request.form.getlist('member_roles[]')
        leads = request.form.getlist('is_lead[]')
        admins = request.form.getlist('is_admin[]')

        for uname, mrole, is_lead, is_admin in zip(usernames, member_roles, leads, admins):
            user = User.query.filter_by(username=uname).first()
            if user:
                member = ProjectMembership(
                    project_id=project_id,
                    user_id=user.user_id,
                    role=mrole,
                    is_lead=(is_lead.lower() == "true"),
                    is_admin=(is_admin.lower() == "true")
                )
                db.session.add(member)

        db.session.commit()
        return redirect('/search_projects')

    # For GET requests, show the form
    return render_template('add_project.html')

@app.route('/project/<int:project_id>')
def view_project(project_id):
    # Retrieve the project by ID
    project = Project.query.get_or_404(project_id)

    # Retrieve members and roles associated with the project
    memberships = ProjectMembership.query.filter_by(project_id=project_id).all()
    roles = Role.query.filter_by(project_id=project_id).all()

    # Retrieve updates associated with the project
    updates = ProjectUpdate.query.filter_by(project_id=project_id).all()

    # Pass project, memberships, roles, and updates to the template
    return render_template('project_detail.html', project=project, memberships=memberships, roles=roles, updates=updates)





if __name__ == '__main__':
    app.run(debug=True)
