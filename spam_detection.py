import requests
import json

# uncomment this to increase the var scope
# api_key = ''

# To test safe browsing API use the link:
# https://testsafebrowsing.appspot.com/

# safe browsing API documentation:
# https://developers.google.com/safe-browsing/v4/lookup-api

def isSpam(filename, url_to_check):
	"""
	returns False with None if not spam
	returns True with threatType if spam
	returns "cannot be determined" if API request error
	"""
	api_key = ''
	with open(filename, 'r') as f:
		api_key = f.readlines()
	
	url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

	config = {'client': {'clientId': "mycompany", 'clientVersion': "0.1"},
			'threatInfo': {'threatTypes': ["MALWARE", "SOCIAL_ENGINEERING"],
							'platformTypes': ["ANY_PLATFORM"],
							'threatEntryTypes': ["URL"],
							'threatEntries': [{'url': url_to_check}]}}
	params = {'key': api_key}

	try:
		r = requests.post(url, params=params, json=config)

		if r.json() == {}:
			return (False, None)
		return (True, r.json()['matches'][0]['threatType'])
	except:
		return "cannot be determined"

if __name__ == '__main__':
	"""
	[ for command line testing ]
	"""
	filename = input('Enter filename: ')
	url_to_check = input('Enter url to check: ')
	isSpam(filename, url_to_check)