import requests
import json

# uncomment this to increase the var scope
# api_key = ''

def isSpam(filename, url_to_check):
	api_key = ''
	with open(filename, 'r') as f:
		api_key = f.readlines()
	
	url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

	payload = {'client': {'clientId': "mycompany", 'clientVersion': "0.1"},
			'threatInfo': {'threatTypes': ["MALWARE", "SOCIAL_ENGINEERING"],
							'platformTypes': ["ANY_PLATFORM"],
							'threatEntryTypes': ["URL"],
							'threatEntries': [{'url': url_to_check}]}}
	params = {'key': api_key}

	try:
		r = requests.post(url, params=params, json=payload)

		if r.json() == {}:
			return (False, None)
		return (True, r.json()['matches'][0]['threatType'])
	except:
		return "cannot be determined"

if __name__ == '__main__':
	filename = input('Enter filename: ')
	url_to_check = input('Enter url to check: ')
	isSpam(filename, url_to_check)