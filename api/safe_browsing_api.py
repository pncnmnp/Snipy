from bitarray import bitarray
import mmh3
from hashlib import sha1

class Safe_Browsing_API:
	"""
	bloom filter ( non counting ) implementation of safe browsing API
	NOTE: This method is not for production. You will 
	be better off using Google's Safe Browsing API.
	This method can be useful with some custom links or 
	misused urls of your shortening service.
	"""
	def __init__(self):
		self.n = 20000 # bit array size
		self.bit_arr = bitarray(self.n)
		self.bit_arr.setall(0)
		self.k = 5 # no of hash functions to be applied
		self.sha1 = [] # to store sha1 hashes for removal purposes

	def store(self, url, remove=False):
		"""
		url   : is the malicious link to be stored in bitarray
		remove: to make a link temporary and remove it later,
		        use remove = True
		        default: remove = False
		"""
		# seed is kept local to prevent tampering
		seed = [11, 13, 17, 19, 23]
		for hashing in range(self.k):
			self.bit_arr[mmh3.hash(url, seed[hashing])%self.n] = 1

		if remove == True:
			hash_sha1 = sha1(url.encode("UTF-8")).hexdigest()
			self.sha1.append(hash_sha1[:10])

	def check(self, url, wasTemp=False):
		"""
		returns True if url is malicious
		url    : is the malicious link to be stored in bitarray
		wasTemp: initialize it to True if while storing the url,
		         'remove' variable was True
		         default: wasTemp = False
		"""
		# seed is kept local to prevent tampering
		seed = [11, 13, 17, 19, 23]
		for hashing in range(self.k):
			if self.bit_arr[mmh3.hash(url, seed[hashing])%self.n] == 0:
				return False
		
		if wasTemp == False:
			return True

		elif wasTemp == True:
			hash_sha1 = sha1(url.encode("UTF-8")).hexdigest()
			if hash_sha1[:10] in self.sha1:
				return True
			return False

	def remove(self, url):
		"""
		removes an url temporarily blocked from list
		returns True if link removed, False if link does not exist
		"""
		try:
			hash_sha1 = sha1(url.encode("UTF-8")).hexdigest()
			self.sha1.remove(hash_sha1[:10])
			return True
		except (ValueError, AttributeError) as error:
			return False

	def load_links(self, file):
		"""
		loads file containing malicious links and adds them to bitarray
		"""
		links = []
		with open(file) as f:
			links = f.readlines()
		for link in links:
			self.store(link)
