from flask import Flask, redirect, request, render_template
import sqlite3
import shorten
import datetime
import spam_detection

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
spam_msg_malware = "Warning—The web-site you are trying to shorten may harm your computer. This page appears to contain malicious code that could be downloaded to your computer without your consent."
spam_msg_phishing = "Warning—The web-site you are trying to shorten may be Deceptive. Attackers on site may trick you into doing something dangerous like installing software or revealing your personal information (for example, passwords, phone numbers, or credit cards)."
spam_msg_2 = "This service uses Google's safe browsing API."
spam_msg_3 = "Google works to provide the most accurate and up-to-date information about unsafe web resources. However, Google cannot guarantee that its information is comprehensive and error-free: some risky sites may not be identified, and some safe sites may be identified in error."

# Note: for testing purposes my api key was in a different directory
# Remove '../' and replace it with './' to reference to current directory's api_key.txt file
# Don't forget to add your API KEY in api_key.txt
api_key_file = "../api_key.txt"

app = Flask(__name__)

@app.route('/<name>', methods=['GET'])
def direct(name):
	"""
	returns the redirected link
	checks for expired links
	updates the view count
	"""
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
	"""
	returns index.html with appropriate response
	initializes timestamps
	checks for custom url
	The following detection takes place here:
	>> spam
	>> expired url 
	>> url validity
	>> duplicate url
	"""
	error = True
	if request.method == 'POST':
		if request.form['query']:
			try:
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

					# check if link is spam or not
					isSpam = spam_detection.isSpam(api_key_file, s_obj.url)
					if isSpam[0]:
						if isSpam[1] == "MALWARE":
							return render_template('index.html', mw_1=spam_msg_malware, mw_2=spam_msg_2, mw_3=spam_msg_3)
						elif isSpam[1] == "SOCIAL_ENGINEERING":
							return render_template('index.html', mw_1=spam_msg_phishing, mw_2=spam_msg_2, mw_3=spam_msg_3)

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

				# check if link is spam or not
				isSpam = spam_detection.isSpam(api_key_file, s_obj.url)
				if isSpam[0]:
					if isSpam[1] == "MALWARE":
						return render_template('index.html', mw_1=spam_msg_malware, mw_2=spam_msg_2, mw_3=spam_msg_3)
					elif isSpam[1] == "SOCIAL_ENGINEERING":
						return render_template('index.html', mw_1=spam_msg_phishing, mw_2=spam_msg_2, mw_3=spam_msg_3)

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
			except:
				return error_500

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