from bitarray import bitarray
import mmh3

class Safe_Browsing_API:
	"""
	bloom filter implementation of safe browsing API
	"""
	def __init__(self):
		self.n = 20000 # bit array size
		self.bit_arr = bitarray(self.n)
		self.bit_arr.setall(0)
		self.k = 5 # no of hash functions to be applied
		
	def store(self, url):
		"""
		url is the malicious link to be stored in bitarray
		"""
		seed = [11, 13, 17, 19, 23]
		for hashing in range(self.k):
			self.bit_arr[mmh3.hash(url, seed[hashing])%self.n] = 1

	def check(self, url):
		"""
		returns True if url is malicious
		"""
		seed = [11, 13, 17, 19, 23]
		for hashing in range(self.k):
			if self.bit_arr[mmh3.hash(url, seed[hashing])%self.n] == 0:
				return False
		return True