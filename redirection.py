from flask import Flask, redirect, request, render_template
import sqlite3
import shorten

app = Flask(__name__)

@app.route('/<name>', methods=['POST', 'GET'])
def direct(name):
	base = shorten.urlShortner().base

	conn = sqlite3.connect('./links.db')
	c = conn.cursor()

	link = c.execute("SELECT old_link FROM links WHERE new_link=?", (base+name,)).fetchone()[0]

	conn.commit()
	conn.close()

	return redirect(link, code=302)

@app.route('/', methods=['POST', 'GET'])
def index():
	error = None
	if request.method == 'POST':
		if request.form['query']:
			s_obj = shorten.urlShortner()
			url = request.form['query']
			s_obj.url = url;
			s_obj.dbFetchStore() # for fetching uid
			s_obj.shortenUrl()
			s_obj.dbFetchStore() # for storing shortened link

			return render_template('index.html', name=s_obj.base)
	return render_template('index.html', error=error)

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)