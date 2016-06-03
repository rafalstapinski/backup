import os
import json
import brotli
import fastlz
import requests
import time
import web
import logging
import random


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

path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(filename="default.log", level=logging.DEBUG)

try:
	config = {}
	execfile("%s/default.conf" % path, config)

	try:
		user_hash = config["user_hash"]
	except KeyError:
		f = open("%s/default.conf" % path, "a")
		user_hash = "%064x" % random.getrandbits(256)
		f.write("user_hash = \"%s\"\n" % user_hash)
		f.close()

	try:
		my_ip = requests.get('http://jsonip.com').json()
		print my_ip["ip"]
		my_port = "18563"
		f = open("%s/default.conf" % path, "a")
		f.write("my_ip = \"&s\"\n" % my_ip)
		f.write("my_port = \"%s\"\n" % my_port)
		f.close()

		try:
			print config["server_ip"]
			r = requests.post("%s/user/register" % config["server_ip"], data = {"user_hash": user_hash, "agent_ip": "%s:%s" % (my_ip, my_port)})
		except Exception as e:
			print e

	except Exception as e:
		logging.critical("Could not get public IP. ")
        exit()

except IOError as e:
	logging.critical("Could not find config file default.conf in same directory. ")
	exit()

if __name__ == "__main__":

	app = web.application(urls, globals())
	app.notfound = notfound
	app.run()
