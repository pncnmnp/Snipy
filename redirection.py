from flask import Flask, redirect, request, render_template
import sqlite3
import shorten

"""
to run server :
	export FLASK_APP=redirection.py
	flask run
"""

app = Flask(__name__)

@app.route('/<name>', methods=['GET'])
def direct(name):
	base = shorten.urlShortner().base

	conn = sqlite3.connect('./links.db')
	c = conn.cursor()

	error = None
	try:
		link = c.execute("SELECT old_link FROM links WHERE new_link=?", (base+name,)).fetchone()[0]

		conn.commit()
		conn.close()

		return redirect(link, code=302)

	except:
		return "ERROR 404: link does not exist"

@app.route('/', methods=['POST', 'GET'])
def index():
	error = None
	if request.method == 'POST':
		if request.form['query']:
			s_obj = shorten.urlShortner()
			url = request.form['query']
			s_obj.url = url;
			check = s_obj.dbFetchStore() # for fetching uid
			if check[0] == True:
				s_obj.shortenUrl()
				s_obj.dbFetchStore() # for storing shortened link

				return render_template('index.html', name=s_obj.base)

			elif check[0] == False:
				return render_template('index.html', other="link is already shortened: ", val=check[1])
			
	return render_template('index.html', error=error)

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)