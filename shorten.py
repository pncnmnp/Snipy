import requests
import socket
import sys
import sqlite3
import string
from termcolor import colored
import datetime

"""
future features:
>> verify duplicate links [ done ]
>> auto expiry of url [ done ]
>> multi link url conversion
>> copy to clipboard [ done ]
>> spam detection
>> load balancer friendly
>> number of views [ done ]
"""

class urlShortner:
	def __init__(self):
		self.url = " "
		self.flag = False
		self.uid = 0
		self.base = "http://127.0.0.1:5000/"
		self.auto_expiry_t = ''
		self.t_base = ''

	def getUrl(self):
		self.url = input(colored('enter a url: ', 'white'))

	def urlValidity(self):
		if self.isInternetWorking() == False:
			print(colored('internet is down', 'red'))
			sys.exit(0)

		if self.isValid() >= 300:
			print(colored('either an invalid url or a client/server error has occured', 'red'))
			sys.exit(0)

	def isInternetWorking(self):
		hostname = 'www.google.com'
		try:
			host = socket.gethostbyname(hostname)
			# create_connection((host, port), timeout_value)
			s = socket.create_connection((host, 80), 2)
			return True

		except:
			return False

	def isValid(self):
		try:
			r = requests.get(self.url)
			return int(r.status_code)

		except:
			return False

	def dbFetchStore(self):
		conn = sqlite3.connect('./links.db')
		c = conn.cursor()

		if self.flag == False:
			c.execute('''CREATE TABLE IF NOT EXISTS links
						(uid INTEGER PRIMARY KEY, 
						old_link TEXT,
						new_link TEXT,
						tstamp TEXT,
						texpiry TEXT,
						views INTEGER)''')
			count_old = c.execute("SELECT COUNT(old_link) FROM links WHERE old_link=?", (self.url,)).fetchone()[0]
			count_new = c.execute("SELECT COUNT(new_link) FROM links WHERE new_link=?", (self.url,)).fetchone()[0]

			if count_old > 0:
				return (False, c.execute("SELECT new_link FROM links WHERE old_link=?", (self.url,)).fetchone()[0])
			elif count_new > 0:	
				return (False, self.url)

			c.execute("INSERT INTO links (old_link, new_link, tstamp, texpiry, views) VALUES (?,?,?,?,?)", (self.url, ' ', self.t_base, self.auto_expiry_t, 0))

			self.uid = c.execute("SELECT uid FROM links WHERE old_link=?", (self.url,)).fetchone()[0]
			conn.commit()
			conn.close()

			return (True, None)

		elif self.flag == True:
			c.execute("UPDATE links SET new_link=? WHERE uid=?", (self.base, self.uid))

			conn.commit()
			conn.close()

	def shortenUrl(self):
		uid = self.uid

		keys = string.ascii_lowercase+string.ascii_uppercase+string.digits
		mapping = {key: keys[key] for key in range(len(keys))}

		digits, rem = [], 0

		while uid > 0:
			rem = uid%62
			digits.append(rem)
			uid = int(uid/62)
		digits.reverse()

		for digit in digits:
			self.base += mapping[digit-1]
		self.flag = True

		print(colored("shortened link: ", "white"), colored(self.base, "red"))

	def has_expired(self, url):
		conn = sqlite3.connect('./links.db')
		c = conn.cursor()

		values = c.execute("SELECT uid, tstamp, texpiry FROM links WHERE new_link=?", (url,)).fetchone()
		is_expired = False

		try:
			if values[2] != 'None':
				if datetime.datetime.strptime(values[2], "%d,%m,%y,%H,%M") < datetime.datetime.now():
					is_expired = True

			if is_expired:
				c.execute("DELETE FROM links WHERE uid=?", (values[0],))

			conn.commit()
			conn.close()

			return is_expired

		except:
			conn.commit()
			conn.close()

			return is_expired

	def execution(self):
		self.getUrl()
		self.urlValidity()
		self.dbFetchStore() # for fetching uid
		self.shortenUrl()
		self.dbFetchStore() # for storing shortened link

if __name__ == '__main__':
	obj = urlShortner()
	obj.execution()