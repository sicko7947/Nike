import datetime,threading,random
from termcolor import cprint, colored
import colorama


class Logger():

	def __init__(self):
		colorama.init()

	def __timestamp(self):
		now = str(datetime.datetime.now())
		now = now.split(' ')[1]
		threadname = threading.currentThread().getName()
		threadname = str(threadname).replace('Thread', 'Task')
		now = '[' + str(now) + ']' + '[' + str(threadname) + ']'
		return now

	def log(self, text):
		print("{} {}".format(self.__timestamp(), text))
		return

	def success(self, text):
		print("{} {}".format(self.__timestamp(), colored(text, "green")))
		return

	def warn(self, text):
		print("{} {}".format(self.__timestamp(), colored(text, "yellow")))
		return

	def error(self, text):
		print("{} {}".format(self.__timestamp(), colored(text, "red")))
		return

	def status(self, text):
		print("{} {}".format(self.__timestamp(), colored(text, "magenta")))
		return

class ProxyManager():

	def __init__(self):
		self.proxies = []
		with open('proxy.txt') as f:
			for item in f.read().splitlines():
				if not item == '':
					item = item.split(":")
					if len(item) == 4:
						proxyDict = {
							'http': 'http://{}:{}@{}:{}'.format(item[2], item[3], item[0], item[1]),
							'https': 'https://{}:{}@{}:{}'.format(item[2], item[3], item[0], item[1])
						}
						self.proxies.append(proxyDict)
					elif len(item) == 2:
						proxyDict = {
							'http': 'http://{}:{}'.format(item[0], item[1]),
							'https': 'https://{}:{}'.format(item[0], item[1])
						}
						self.proxies.append(proxyDict)
					else:
						pass
			f.close()

	def get_proxy(self):
		return random.choice(self.proxies)
