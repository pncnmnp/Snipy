import requests
import socket
import sys
import sqlite3
import string
from termcolor import colored

class urlShortner:
	def __init__(self):
		self.url = " "
		self.flag = False
		self.uid = 0
		self.base = "https://par.th/"

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
						new_link TEXT)''')
			c.execute("INSERT INTO links (old_link, new_link) VALUES (?,?)", (self.url, ' '))

			self.uid = c.execute("SELECT uid FROM links WHERE old_link=?", (self.url,)).fetchone()[0]

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

	def execution(self):
		self.getUrl()
		self.urlValidity()
		self.dbFetchStore() # for fetching uid
		self.shortenUrl()
		self.dbFetchStore() # for storing shortened link

obj = urlShortner()
obj.execution()