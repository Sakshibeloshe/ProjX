from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    expertise = db.Column(db.String(255))  # Comma-separated
    interests = db.Column(db.String(255))
    about_me = db.Column(db.Text)
    profile_image = db.Column(db.LargeBinary)

    projects = db.relationship('UserProject', back_populates='user')

class Project(db.Model):
    __tablename__ = 'Projects'
    project_id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    project_info = db.Column(db.Text)
    keywords = db.Column(db.String(255))  # Comma-separated
    status = db.Column(db.String(50))  # 'Ongoing' or 'Completed'

    roles = db.relationship('Role', back_populates='project')
    members = db.relationship('UserProject', back_populates='project')

class Role(db.Model):
    __tablename__ = 'Roles'
    role_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('Projects.project_id'))
    role_name = db.Column(db.String(100), nullable=False)
    requirements = db.Column(db.Text)
    status = db.Column(db.String(50))  # 'Available' or 'Filled'

    project = db.relationship('Project', back_populates='roles')

class UserProject(db.Model):
    __tablename__ = 'UserProject'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    project_id = db.Column(db.Integer, db.ForeignKey('Projects.project_id'))
    role_id = db.Column(db.Integer, db.ForeignKey('Roles.role_id'))
    is_leader = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='projects')
    project = db.relationship('Project', back_populates='members')
