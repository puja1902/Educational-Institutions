from myproject import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

# By inheriting the UserMixin we get access to a lot of built-in attributes
# which we will be able to call in our views!
# is_authenticated()
# is_active()
# is_anonymous()
# get_id()

# The user_loader decorator allows flask-login to load the current user
# and grab their id.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):

    # Create a table in the db
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    profile_image = db.Column(db.String(20), default='default_profile.png')
    email = db.Column(db.String(64),  unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.String(64), index=True)
    roles = db.relationship('Role', secondary='user_roles')
    s_user = db.relationship('Students', backref='students', uselist=False)
    t_user = db.relationship('Teachers', backref='teachers', uselist=False)
   
    def __init__(self, email, username, password, user_type):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.user_type = user_type
        

    def check_password(self,password):
        # https://stackoverflow.com/questions/23432478/flask-generate-password-hash-not-constant-output
        return check_password_hash(self.password_hash,password)


# Define the Role data-model

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    # Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

    def __init__(self, user_id, role_id):
        self.user_id=user_id
        self.role_id=role_id

class Students(db.Model):

    __tablename__ = 'student'

    
    usn = db.Column(db.String(40), primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(140))
    last_name = db.Column(db.String(140))
    address = db.Column(db.String(240))
    branch = db.Column(db.String(140))
    dept = db.relationship('Branchs', backref='branch', uselist=False)

   
    

    def __init__(self, usn, first_name, last_name, address,  user_id):
        self.usn = usn
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.user_id = user_id


class Teachers(db.Model):
    __tablename__ = 'teacher'

    t_id = db.Column(db.String(40), primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(140))
    last_name = db.Column(db.String(140))
    branch = db.Column(db.String(140))
    address = db.Column(db.String(240))
    

    def __init__(self, t_id, first_name, last_name, address, branch, user_id):
        self.t_id = t_id
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.branch = branch
        self.user_id = user_id


class Branchs(db.Model):

    __tablename__ = 'branch'

    branch_id = db.Column(db.String(40), primary_key=True, unique=True)
    sem = db.Column(db.String(140))
    sec = db.Column(db.String(140))
    usns = db.Column(db.String(140), db.ForeignKey('student.usn'), nullable=False)
    sub = db.relationship('Subjects', backref='subject', lazy='dynamic')
    atten = db.relationship('Attendance', backref='attendance', lazy='dynamic')

    def __init__(self, branch_id , sem , sec,usns):
        self.branch_id = branch_id
        self.sem = sem
        self.sec = sec
        self.usns = usns

class Subjects(db.Model):

    __tablename__ = 'subject'

    sub_id = db.Column(db.String(40), primary_key=True, unique=True)
    sub_name = db.Column(db.String(140))
    Branch = db.Column(db.String(140), db.ForeignKey('branch.branch_id'), nullable=False)

    def __init__(self , sub_id, sub_name, branch):
        self.sub_id = sub_id
        self.sub_name = sub_name
        self.Branch = branch


class Attendance(db.Model):

    __tablename__='attendance'

    day = db.Column(db.String(140), primary_key=True, unique=True)
    time = db.Column(db.String(140))
    Subject = db.Column(db.String(140))
    branch = db.Column(db.String(140), db.ForeignKey('branch.branch_id'), nullable=False)
    sem = db.Column(db.String(140))
    sec = db.Column(db.String(140))

    def __init__(self, day, time, subject, branch, sem, sec):
        self.day = day
        self.time = time
        self.Subject = subject
        self.branch = branch
        self.sem = sem
        self.sec = sec
 
