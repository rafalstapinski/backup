import os
import json
import brotli
import fastlz
import requests
import time
import web
import logging
import random
from config import conf


# def path_to_dict(path):
#     d = {'n': os.path.basename(path)}
#     # path
#     if os.path.isdir(path):
#         d['t'] = "d"
#         d['c'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
#     else:
# 		d['t'] = "f"
# 		d["m"] = time.ctime(os.path.getmtime(path))
#     return d
#
# # applications =  brotli.compress(json.dumps(path_to_dict('/Applications/')))
# user = fastlz.compress(json.dumps(path_to_dict("/Users/rafalstapinski/")))
#
# url = "http://localhost:8080/structure/new"
#
# f = {"structure": ("structure.lz", user)}
#
# r = requests.post(url, files=f)
#

def write(payload, status):
    return json.dumps({"payload": payload, "status": status})

def notfound():
    return web.notfound("404")

def new_request(request):
    web.header("Content-Type", "application/json")
    web.header("Access-Control-Allow-Origin", "*")
	# web.header("charset", "utf-8")

class backup_begin:
	def POST(self):
		new_request(self)

		backup_structure = []

		for d in conf.backup_dirs:
			#backup_structure.append(path_to_dict(config["backup_dirs"][d]))
			print d

urls = (
	"/backup/begin", "backup_begin"
)



if __name__ == "__main__":

	path = os.path.dirname(os.path.realpath(__file__))
	logging.basicConfig(filename="default.log", level=logging.DEBUG)

	try:
		user_hash = conf.user_hash

	except AttributeError:

		f = open("%s/config.py" % path, "a")
		user_hash = "%064x" % random.getrandbits(256)
		f.write("\tuser_hash = \"%s\"\n" % user_hash)
		f.close()

	try:

		my_ip = requests.get('http://jsonip.com').json()
		#for some reason referencing ["ip"] in above doesn't work
		my_port = "18563"
		# f = open("%s/default.conf" % path, "a")
		# f.write("my_ip = \"%s\"\n" % my_ip)
		# f.write("my_port = \"%s\"\n" % my_port)
		# f.close()

		try:

			my_ip["ip"] = "http://localhost"

			#overwrite for testing since behind proxy and all

			requests.post("%s/user/register" % conf.server_ip, data = {"user_hash": user_hash, "agent_ip": "%s:%s" % (my_ip["ip"], my_port)})

		except Exception as e:

			print e

	except Exception as e:
		#for some reason this is causing program to exit, but isn't printing or logging
		# logging.critical("Could not get public IP. ")
		# print "could not get public ip"
        # exit()

		pass


	app = web.application(urls, globals())
	app.notfound = notfound
	app.run()
