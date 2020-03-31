from myproject import app, db, login_manager
from flask import render_template, redirect, request, url_for, flash,abort
from flask_login import login_user, login_required, logout_user, current_user
from flask_user import roles_required
from myproject.models import User , Students, Teachers,  Branchs, Subjects
from myproject.forms import UpdateUserForm
from werkzeug.security import generate_password_hash, check_password_hash
from myproject.picture_handler import add_profile_pic


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load.""" 
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('login'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome_user.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    

    if current_user.is_authenticated:
        return redirect(url_for('index'))



    if request.method == 'POST':
       email = request.form['email']
       password1 = request.form['password']
       usertype = request.form['optradio']
       user = User.query.filter_by(email=email).first()
       
       
       if user.user_type == usertype and usertype == 'student':
           if user and user.check_password(password=password1):
               login_user(user)
               next_page = request.args.get('next')
               return redirect(next_page or url_for('student_info'))
       
       elif user.user_type == usertype and usertype == 'teacher':
           if user and user.check_password(password=password1):
               login_user(user)
               next_page = request.args.get('next')
               return redirect(next_page or url_for('teacher_info'))
       
       elif user.user_type == usertype and usertype == 'admin':
           if user and user.check_password(password=password1):
               login_user(user)
               next_page = request.args.get('next')
               return redirect(next_page or url_for('admin_dashboard'))
       else:
           flash('your user type opption is not correct')
       
    flash('Enter your login details')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['psw']
        rpsw = request.form['rpsw']
        usertype = request.form['optradio']
        if User.query.filter_by(email=email).first():
            flash('Email address already register')
            return render_template('register.html')
        
        elif User.query.filter_by(username=username).first():
            flash('username already taken')
            return render_template('register.html')


        elif password == rpsw:
             user = User(email=email, username=username, password=password, user_type=usertype)
             db.session.add(user)
             db.session.commit()
             flash('Thanks for registering! Now you can login!')
             return redirect(url_for('login'))
        else:
            flash('please enter same password')
            return render_template('register.html')
    return render_template('register.html')


    ##############################################################
    ##################### admin section #########################
@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if request.method == 'POST':
        branch = request.form['branch']
        tid = request.form['t_id']
        teacher = Teachers.query.filter_by(branch=branch).all()
        if teacher != None:
            return render_template('admin/dashboard.html', teacher=teacher)
        
        else:
            teacher = Teachers.query.filter_by(t_id=tid).first()
            return render_template('admin/dashboard.html', teacher=teacher)

    return render_template('admin/dashboard.html')


###################### student Page #############################
###############################################################

@app.route('/student_dashboard')
@login_required
def student_dashboard():
     return render_template('student/dashboard.html')


@app.route("/account", methods=['GET', 'POST'])
@login_required
def student_account():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        address = request.form['address']
        branch = request.form['branch']
        sem = request.form['sem']
        sec = request.form['sec']

        if Students.query.filter_by(usn=current_user.s_user.usn).first():
            current_user.s_user.first_name = request.form['firstname']
            current_user.s_user.last_name = request.form['lastname']
            current_user.s_user.address = request.form['address']
            current_user.s_user.branch = request.form['branch']
            current_user.s_user.dept.sem = request.form['sem']
            current_user.s_user.dept.sec = request.form['sec']
            current_user.username = request.form['username']
            current_user.email = request.form['email']
            db.session.commit()
            flash("update Successfully")
            return redirect(url_for('student_account'))


    elif request.method == 'GET':
        username = current_user.username
        email = current_user.email
        usn = current_user.s_user.usn
        firstn = current_user.s_user.first_name
        lastn = current_user.s_user.last_name
        address = current_user.s_user.address
        branch = current_user.s_user.dept.branch_id
        sem = current_user.s_user.dept.sem
        sec = current_user.s_user.dept.sec
        return render_template('user1.html', username=username, email=email, usn=usn, firstn=firstn, lastn=lastn, branch=branch, sem=sem, sec=sec)


@app.route('/student_info', methods=['GET', 'POST'])
@login_required
def student_info():
    if request.method == 'POST':
        usn = request.form['usn']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        address = request.form['address']
        branch = request.form['branch']
        sem = request.form['sem']
        sec = request.form['sec']

      
        
        if  Students.query.filter_by(usn=usn).first():
            flash("already submitted")
            return render_template('student/tables.html')

        else:
            student = Students(usn=usn, first_name=firstname, last_name=lastname,user_id=current_user.id, address=address)
            branch = Branchs(branch_id=branch, sem=sem, sec=sec, usns=usn)
            db.session.add(student)
            db.session.add(branch)
            db.session.commit()
            flash("Information Add Successfully")
            return redirect(url_for('student_dashboard'))
    
    return render_template('student/tables.html')
        
@app.route('/assignment')
@login_required
def assignment():
     return render_template('student/assignment.html')
    
    


@app.route('/<username>')
def user_dashboard(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('student/dashboard.html', user=user)

##################################################################################################
######################### student page End #######################################################



##################################################################################################
########################## teacher coding area ###################################################

@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
     return render_template('teacher/dashboard.html')


@app.route("/teacher_account", methods=['GET', 'POST'])
@login_required
def teacher_account():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        address = request.form['address']
        branch = request.form['branch']

        if Teachers.query.filter_by(t_id=current_user.t_user.t_id).first():
            current_user.t_user.first_name = request.form['firstname']
            current_user.t_user.last_name = request.form['lastname']
            current_user.t_user.address = request.form['address']
            current_user.t_user.branch = request.form['branch']
            current_user.username = request.form['username']
            current_user.email = request.form['email']
            db.session.commit()
            flash("update Successfully")
            return redirect(url_for('teacher_account'))

    elif request.method == 'GET':
        username = current_user.username
        email = current_user.email
        t_id = current_user.t_user.t_id
        firstn = current_user.t_user.first_name
        lastn = current_user.t_user.last_name
        address = current_user.t_user.address
        branch = current_user.t_user.branch
        return render_template('teacher/user2.html', username=username, email=email, t_id=t_id, firstn=firstn, lastn=lastn, branch=branch)


@app.route('/teacher_info', methods=['GET', 'POST'])
@login_required
def teacher_info():
    if request.method == 'POST':
        t_id = request.form['t_id']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        address = request.form['address']
        branch = request.form['branch']

        if Teachers.query.filter_by(t_id=t_id).first():
            flash("already submitted")
            return render_template('teacher/tables.html')

        else:
            teacher = Teachers(t_id = t_id, first_name = firstname,last_name=lastname, user_id=current_user.id, address=address,branch=branch)
            db.session.add(teacher)
            db.session.commit()
            flash("Information Add Successfully")
            return redirect(url_for('teacher_dashboard'))

    return render_template('teacher/tables.html')




@app.route('/compiler')
def compiler():
    return render_template('compiler.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
