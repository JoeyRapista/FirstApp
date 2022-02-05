from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] =  'postgres://nqjexbxaealyfr:4acaf994ed492839ad40d2c4e1fc6ae55a677b3a30796bb3b8424a10e7fab3b8@ec2-35-153-35-94.compute-1.amazonaws.com:5432/d2d707k9e6uoq3'

app.config['SECRET_KEY'] = "secretkeythatnoonewantstoknow"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = Loginform()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash("Logged in successfully")
				return redirect(url_for('dashboard'))
			else:
				flash("Wrong credentials, Try Again!")
	return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You logged out")
	return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard(): 
	return render_template('dashboard.html')

class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255))
	content = db.Column(db.Text)
	author = db.Column(db.String(255))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(255))

class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(200), nullable=False, unique=True)
	name = db.Column(db.String(200), nullable=False)
	email = db.Column(db.String(200), nullable=False, unique=True)
	favorite_color = db.Column(db.String(200))
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	password_hash = db.Column(db.String(128))

	@property
	def password(self):
		raise AttributeError('Password incorrect')


	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<Name %r>' % self.name

class Loginform(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Login")

class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	favorite_color = StringField("Favorite color")
	password_hash=PasswordField("Enter Password", validators=[DataRequired(), EqualTo('password_hash2', message='Password must Match!')])
	password_hash2=PasswordField("Confirm Password", validators=[DataRequired()])
	submit = SubmitField("Submit")


class NamerForm(FlaskForm):
	name = StringField("What is you name", validators=[DataRequired()])
	#password = PasswordField("Enter Password", validators=[DataRequired()])
	submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
	email = StringField("What is you email", validators=[DataRequired()]) 
	password_hash = PasswordField("What is you password", validators=[DataRequired()]) 
	submit = SubmitField("Submit")


class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()]) 
	content = StringField("Content", validators=[DataRequired()], widget=TextArea()) 
	author = StringField("Author", validators=[DataRequired()]) 
	slug = StringField("Slug", validators=[DataRequired()]) 
	submit = SubmitField("Submit")


@app.route('/add-post', methods=['GET','POST'])
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		post = Posts(title = form.title.data, content = form.content.data, author = form.author.data, slug = form.slug.data)
		form.title.data = ''
		form.content.data = ''
		form.author.data = ''
		form.slug.data = ''
		db.session.add(post)
		db.session.commit()

		flash("Post Created Successfully!")
	return render_template("add_post.html", form = form)

@app.route('/posts')
def posts():
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts = posts)

@app.route('/post/<int:id>') 
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template("post.html", post = post)

@app.route('/post/delete/<int:id>') 
def delete_post(id):
	post = Posts.query.get_or_404(id) 
	try:
		db.session.delete(post) 
		db.session.commit()
		flash("Deleted Successfully!")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts = posts)
	except:
		flash("Something wrong deleting post!")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts = posts)
	 

@app.route('/post/edit/<int:id>', methods=['GET', 'POST']) 
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data
		db.session.add(post)
		db.session.commit()
		flash("Post has been Updated!")
		return redirect(url_for('post', id=post.id))
	form.title.data = post.title
	form.author.data = post.author
	form.slug.data = post.slug 
	form.content.data = post.content
	return render_template("edit_post.html", form = form)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == 'POST':
		name_to_update.name = request.form['name']
		name_to_update.username = request.form['username']
		name_to_update.email = request.form['email']
		name_to_update.favorite_color = request.form['favorite_color']
		try:
			db.session.commit()
			flash("User Updated Successfully!")
			return render_template("update.html",
				form=form, name_to_update=name_to_update)
		except:
			flash("Something is wrong")
			return render_template("update.html",
				form=form, name_to_update=name_to_update)
	else:
		return render_template("update.html",
			form=form, name_to_update=name_to_update)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm() 
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		username = Users.query.filter_by(username=form.username.data).first()
		if user is None and username is None:
			hased_pw = generate_password_hash(form.password_hash.data, "sha256")
			user = Users(name=form.name.data, username=form.username.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hased_pw)
			db.session.add(user)
			db.session.commit()
			
			name = form.name.data
			form.name.data = ''
			form.username.data=''
			form.email.data=''
			form.favorite_color.data=''
			form.password_hash.data=''
			form.password_hash2.data=''
			flash("User added successfully")
		else:
			flash("No duplicate of email and username, choose another username or email")
	user_list = Users.query.order_by(Users.date_added)
	return render_template("add_user.html", form = form, name=name, userlist=user_list)

@app.route('/') 
def index():
	dogs = ["yt", "browny", "blacky"]
	user_lists = Users.query.order_by(Users.date_added)
	return render_template("index.html", dogs = dogs, user_lists =  user_lists)
 
@app.route('/users')
def users():
	user_list = Users.query.order_by(Users.date_added)
	return render_template("users.html", userlist=user_list)

@app.route('/delete/<int:id>')
def delete(id):
		user_to_delete = Users.query.get_or_404(id)
		name = None
		form = UserForm() 

		try:   
			db.session.delete(user_to_delete)
			db.session.commit()
			flash("User Deleted Successfully")

			
			user_list = Users.query.order_by(Users.date_added)
			return render_template("add_user.html", 
				form = form, 
				name=name, 
				userlist=user_list)	
		except:
			flash("Problem Deleting the record")
			user_list = Users.query.order_by(Users.date_added)
			return render_template("add_user.html", 
				form = form, 
				name=name, 
				userlist=user_list)	

@app.route('/about')
def about():
	return render_template("about.html")


@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():

	email = None
	password = None
	user = None
	passed = None 
	form = PasswordForm()


	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		form.email.data=''
		form.password_hash.data='' 
		user = Users.query.filter_by(email=email).first()

		passed = check_password_hash(user.password_hash, password)

	return render_template("test_pw.html", 
	email = email,
	password = password, 
	passed = passed,
	user = user, 
	form = form)


@app.route('/name', methods=['GET', 'POST'])
def name():

	name = None
	form = NamerForm()
	if form.validate_on_submit():
		name = form.name.data
		form.name.data=''
		flash("Form Submited Successfully")
	return render_template("name.html", 
	name = name,
	form = form)


#error pages
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500


