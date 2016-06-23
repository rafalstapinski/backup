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
import hashlib
import mimetypes

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def path_to_dict(path):
	d = {"name": path, "mtime": os.path.getmtime(path)}
	if os.path.isdir(path):
		d["type"] = "directory"
		d["children"] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
	else:
		d["md5"] = md5(path)
		d["type"] = "file"
	return d

def write(payload, status):
    return json.dumps({"payload": payload, "status": status})

def notfound():
    return web.notfound("404")

def new_request(request):
    web.header("Content-Type", "application/json")
    web.header("Access-Control-Allow-Origin", "*")
	# web.header("charset", "utf-8")

class backup_scan:
	def POST(self):
		new_request(self)

		print "starting backup scan"

		backup_structure = []

		for d in conf.backup_dirs:
			backup_structure.append(path_to_dict(d))

		requests.post("%s/user/update" % conf.server_ip, data = {"user_hash": conf.user_hash, "structure": json.dumps(backup_structure)})

class backup_send:
	def POST(self):
		new_request(self)

		data = web.input()

		try:
			filename = data["filename"]
			checksum = data["checksum"] # to make sure its from actual backup agent not fishing for files
		except KeyError:
			return write({"error": "No filename or checksum provided. "}, 400)

		print data["filename"], data["checksum"]

		if md5(data["filename"]) == data["checksum"]:
			requests.post("%s/user/upload" % conf.server_ip, files = {"myfile": open(data["filename"], "rb")}, data={"user_hash": conf.user_hash, "checksum": data["checksum"]})
			return write({"message": "File will be posted to server. "}, 200)
		else:
			return write({"error": "Checksum was incorrect, no auth. "}, 403)


urls = (
	"/backup/scan", "backup_scan",
	"/backup/send", "backup_send"
)

if __name__ == "__main__":

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
