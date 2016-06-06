import web
import brotli
import fastlz
import os
import time
import requests
from multiprocessing import Process
import json

def write(payload, status):
    return json.dumps({"payload": payload, "status": status})

def notfound():
    return web.notfound("404")

def new_request(request):
    web.header("Content-Type", "application/json")
    web.header("Access-Control-Allow-Origin", "*")
	# web.header("charset", "utf-8")

def call_backup(agent_ip):
	r = requests.post("%s/backup/scan" % agent_ip)


urls = (
	"/user/register", "user_register",
	"/user/update", "user_update",
	"/user/new", "user_new",
	"/user/upload", "user_upload"
)

class user_register:
	def POST(self):
		new_request(self)

		data = web.input()

		try:
			user_hash = data["user_hash"]
			agent_ip = data["agent_ip"]
		except KeyError:
			return write({"error": "User hash or agent ip not provided. "}, 400)

		if os.path.isdir("%s/%s" % (path, user_hash)):
			print "exists"
		else:
			print "create"
			os.mkdir("%s/%s" % (path, user_hash))
			f = open("%s/%s/user.conf" % (path, user_hash), "w")
			f.write("agent_ip = \"%s\"\n" % agent_ip)
			f.close()

		Process(target=call_backup, args=(agent_ip,)).start()

		return

class user_update:
	def POST(self):
		new_request(self)
		data = web.input()

		try:
			user_hash = data["user_hash"]
			new_structure = data["structure"]
		except KeyError:
			return write({"error": "User hash or structure not provided. "}, 400)

		if os.path.isdir("%s/%s" % (path, data["user_hash"])):

			try:
				f = open("%s/%s/structure.json" % (path, data["user_hash"]), "r")
				old_structure = json.load(f)
				f.close()

				for keys in old_structure.keys():
					print keys

			except IOError:
				f = open("%s/%s/structure.json" % (path, data["user_hash"]), "w")
				f.write(data["structure"])
				f.close()
		else:
			return write({"error": "User not registered. "}, 403)

class user_new:
	def POST(self):
		new_request(self)
		data = web.input()

		try:
			user_hash = data["user_hash"]
			new_structure = data["structure"]
		except KeyError:
			return write({"error": "User hash or structure not provided. "}, 400)

		if os.path.isdir("%s/%s" % (path, data["user_hash"])):
			f = open("%s/%s/structure.json" % (path, data["user_hash"]))
			f.write(data["structure"])
			f.close()
		else:
			return write({"error": "User not registered. "}, 403)



path = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
	app = web.application(urls, globals())
	app.notfound = notfound
	app.run()
