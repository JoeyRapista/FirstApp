from flask import Flask, render_template

app = Flask(__name__)

@app.route('/') 
def index():
	dogs = ["yt", "browny", "blacky"]
	return render_template("index.html", dogs = dogs)
 
@app.route('/user/<name>')
def user(name):
	return render_template("user.html", name = name)

#error pages
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500