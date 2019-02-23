from flask import Flask, redirect, request, render_template
import sqlite3
import shorten
import datetime

"""
To run server :
	export FLASK_APP=redirection.py
	flask run
"""

"""
While coding 'auto expiry of url', I faced a dilemma.
There were 2 choices:
>>	I can check if a url is expired after user requests it.
	That would be 2 checks, one when @app.route('/<name>') matches with url,
	other when url entered is duplicate
>>	Check after every @app.route('/') request

2nd option is surely simpler and privacy friendly, but adds unnecessary load on server.
1st option is better both in terms of link analytics and less load on server.
After much thought, I choose the 1st option.
"""

error_400 = "ERROR 400: link does not exist<br/>looks like you have gone crazy 😜"
error_500 = "ERROR 500: internal server error<br/>looks like i have gone crazy 😭"

app = Flask(__name__)

@app.route('/<name>', methods=['GET'])
def direct(name):
	base = shorten.urlShortner().base

	# To check for expired urls in database
	s_exp_obj = shorten.urlShortner()
	expired = s_exp_obj.has_expired(base+name)

	if expired:
		return error_400

	conn = sqlite3.connect('./links.db')
	c = conn.cursor()

	error = None
	try:
		meta = c.execute("SELECT old_link, views FROM links WHERE new_link=?", (base+name,)).fetchone()
		# updating the view count
		c.execute("UPDATE links SET views=? WHERE old_link=?", (meta[1]+1, meta[0]))

		conn.commit()
		conn.close()

		return redirect(meta[0], code=302)

	except:
		return error_400

@app.route('/', methods=['POST', 'GET'])
def index():
	error = True
	if request.method == 'POST':
		if request.form['query']:
			# try:
			s_obj = shorten.urlShortner()
			url = request.form['query']

			# comment the code  below if you hate the easter egg
			if len(set(url.split('/')).intersection(set(['goo.gl', 'bit.ly', 't.co']))) > 0:
				return render_template('index.html', yoda_says="You must unlearn what you have learned! ", mortal_taunt="Shoo away cunning mortal!")

			# get the current and expiry time
			s_obj.t_base = (datetime.datetime.now()).strftime("%d,%m,%y,%H,%M")
			if request.form['time'] != '':
				s_obj.auto_expiry_t = (datetime.datetime.now() + datetime.timedelta(minutes = int(request.form['time']))).strftime("%d,%m,%y,%H,%M")
			else:
				s_obj.auto_expiry_t = 'None'

			# for custom url
			if len(url.split(',')) > 1:
				s_obj.url = (url.split(',')[0]).strip()

				validity = s_obj.isValid(s_obj.url)

				if validity == False:
					return render_template('index.html', other="link is invalid")

				s_obj.base += (url.split(',')[1]).strip()

				if s_obj.isCustomUrl() == False:
					check = s_obj.dbFetchStore()

					if check[0] == True:
						s_obj.flag = True
						true_check(s_obj)
						return render_template('index.html', name=s_obj.base)

					elif check[0] == False:
						expired = false_check(s_obj, check[1])

						if expired:
							return error_400

						# if not expired, yet link is duplicate
						return render_template('index.html', other="link is already shortened: ", val=check[1])

				elif s_obj.isCustomUrl() == True:
						return render_template('index.html', other="link is already shortened: ", val=s_obj.base)

			s_obj.url = url.strip()
			validity = s_obj.isValid(url)

			if validity == False:
				return render_template('index.html', other="link is invalid")

			# if check is True: link is not duplicate
			# if check is False: link is duplicate
			check = s_obj.dbFetchStore() # for fetching uid

			if check[0] == True:
				true_check(s_obj)
				return render_template('index.html', name=s_obj.base)

			elif check[0] == False:
				expired = false_check(s_obj, check[1])

				if expired:
					return error_400

				# if not expired, yet link is duplicate
				return render_template('index.html', other="link is already shortened: ", val=check[1])
			# except:
			# 	return error_500

	return render_template('index.html', error=error)

def true_check(s_obj):
	# To check whether custom url is used
	if s_obj.flag == False:
		s_obj.shortenUrl()
	s_obj.dbFetchStore() # for storing shortened link

def false_check(s_obj, link):
	# To check for expired urls in database
	base = shorten.urlShortner().base
	s_exp_obj = shorten.urlShortner()
	return s_exp_obj.has_expired(link)

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)