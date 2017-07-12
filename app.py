#!/usr/bin/python
#coding=utf-8

__author__ = 'magiclyde'

import os, random, string
from flask import Flask, request, redirect, render_template, \
url_for, make_response, abort, session
from werkzeug import secure_filename

app = Flask(__name__)

@app.errorhandler(401)
def unauthorized(error):
	return render_template('unauthorized.html'), 401


@app.errorhandler(404)
def page_not_found(error):
	return render_template('page_not_found.html'), 404


@app.route('/', methods = ['GET', 'POST'])
def index():
	guest = request.cookies.get('username') or 'guest'
	resp = make_response(render_template('index.html'))
	resp.set_cookie('username', guest)
	return resp


@app.route('/home', methods = ['GET', 'POST'])
def home():
	username = session.get('username')
	if (not username):
		return redirect(url_for('signin'))

	length = 16
	session['csrf_token'] = csrf_token = ''.join(random.sample(string.ascii_letters, length))
	resp = make_response(render_template('home.html'))
	resp.set_cookie('username', username)
	return resp


@app.route('/signin', methods = ['GET'])
def signin_form():
	if (session.get('username')):
		return redirect(url_for('home'))

	length = 16
	session['csrf_token'] = csrf_token = ''.join(random.sample(string.ascii_letters, length))
	return render_template('signin.html', csrf_token = csrf_token)


@app.route('/signin', methods = ['POST'])
def signin():
	csrf_token = request.form['csrf_token']
	if csrf_token != session.get('csrf_token'):
		abort(401)

	username = request.form['username']
	if username == 'magiclyde' and request.form['password'] == 'qazwsx':
		session['username'] = request.form['username']
		return redirect(url_for('home'))

	return '<h3>Bad username or password.</h3>'


@app.route('/logout', methods = ['POST'])
def logout():
	csrf_token = request.form['csrf_token']
	if csrf_token != session.get('csrf_token'):
		abort(401)

	username = session.get('username')
	if (not username):
		return redirect(url_for('signin'))

	session.pop('username', None)
	return redirect(url_for('index'))


@app.route('/user/<username>', methods = ['GET'])
def show_user_profile(username):
	current_user = session.get('username')
	if (username != current_user and current_user != 'admin'):
		abort(401)

	avatar = session.get('avatar') or 'default.png'
	return render_template('user.html', name = username, avatar = avatar)


def allow_file(filename):
	ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
	username = session.get('username')
	if (not username):
		return redirect(url_for('signin'))

	if request.method == 'POST':
		f = request.files['upload_file']
		if f and allow_file(f.filename):
			filename = secure_filename(f.filename)
			f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			session['avatar'] = filename
			return redirect(url_for('show_user_profile', username = username ))

	return render_template('upload.html')


@app.route('/search', methods = ['GET', 'POST'])
def search():
	searchword = request.args.get('q', '')
	return render_template('search.html', searchword = searchword)


if __name__ == '__main__':
	app.config['UPLOAD_FOLDER'] = 'static/upload'
	app.secret_key = os.urandom(24)
	app.debug = True
	app.run(host='0.0.0.0')