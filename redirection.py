from flask import Flask, redirect
import sqlite3
import shorten

app = Flask(__name__)

@app.route('/<name>')
def direct(name):
	base = shorten.urlShortner().base

	conn = sqlite3.connect('./links.db')
	c = conn.cursor()

	link = c.execute("SELECT old_link FROM links WHERE new_link=?", (base+name,)).fetchone()[0]

	conn.commit()
	conn.close()

	return redirect(link, code=302)

@app.route('/')
def index():
	return ("welcome to test site")

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)