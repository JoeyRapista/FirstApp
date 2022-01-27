from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = "secretkeythatnoonewantstoknow"

db = SQLAlchemy(app)
migrate = Migrate(app, db)



class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200), nullable=False)
	email = db.Column(db.String(200), nullable=False, unique=True)
	favorite_color = db.Column(db.String(200))
	date_added = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<Name %r>' % self.name

class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	favorite_color = StringField("Favorite color")
	submit = SubmitField("Submit")


class NamerForm(FlaskForm):
	name = StringField("What is you name", validators=[DataRequired()])
	#password = PasswordField("Enter Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == 'POST':
		name_to_update.name = request.form['name']
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
		if user is None:
			user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data = ''
		form.email.data=''
		form.favorite_color.data=''
		flash("User added successfully")
	user_list = Users.query.order_by(Users.date_added)
	return render_template("add_user.html", form = form, name=name, userlist=user_list)
	

@app.route('/') 
def index():
	dogs = ["yt", "browny", "blacky"]
	return render_template("index.html", dogs = dogs)
 
@app.route('/users')
def users():
	user_list = Users.query.order_by(Users.date_added)
	return render_template("users.html", user_list=user_list)


@app.route('/about')
def about():
	return render_template("about.html")


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


