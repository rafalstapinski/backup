import web
import brotli
import fastlz
import os
import time
import requests
from multiprocessing import Process
import json
from config import conf
import urllib

def write(payload, status):
    return json.dumps({"payload": payload, "status": status})

def notfound():
    return web.notfound("404")

def new_request(request):
    web.header("Content-Type", "application/json")
    web.header("Access-Control-Allow-Origin", "*")
	# web.header("charset", "utf-8")

def call_backup(agent_ip):
	r = requests.post("s/%s/backup/scan" % agent_ip)

def start_backup(tba, tbd, agent_ip, user_hash):

	print tba
	print tbd
	print agent_ip

	for filename in tba:
		r = requests.post("s/%s/backup/send" % agent_ip, data={"filename": filename, "checksum": tba[filename][1]})
		print r.json()

def get_files(structure, files):

	for o in structure:

		if o["type"] == "file":
			files[o["name"]] = [o["mtime"], o["md5"]]
		else:
			get_files(o["children"], files)

	return files

def write_file(user_hash, checksum, s):

	f = open("s/%s/files/%s" % (user_hash, checksum), "w")
	f.write(s["myfile"].file.read())
	f.close()

urls = (
	"/user/register", "user_register",
	"/user/update", "user_update",
	"/user/new", "user_new",
	"/user/upload", "user_upload"
)

class user_upload:
	def POST(self):
		new_request(self)

		data = web.input()

		try:
			f = web.input(myfile={})

			user_hash = data["user_hash"]

			Process(target=write_file, args=(data["user_hash"], data["checksum"], f)).start()

		except KeyError:
			print "file was not provided"
			return write({"error": "File was not provided. "})


class user_register:
	def POST(self):
		new_request(self)

		data = web.input()

		try:
			user_hash = data["user_hash"]
			agent_ip = data["agent_ip"]
		except KeyError:
			return write({"error": "User hash or agent ip not provided. "}, 400)

		if os.path.isdir("s/%s/%s" % (conf.path, user_hash)):
			pass
			# probably update agent ip anyway
		else:
			print "create"
			os.mkdir("s/%s/%s" % (conf.path, user_hash))
			os.mkdir("s/%s/%s/files" % (conf.path, user_hash))
			f = open("s/%s/%s/user.json" % (conf.path, user_hash), "w")
			user = {"agent_ip": data["agent_ip"]}
			f.write(json.dumps(user))
			f.close()

		Process(target=call_backup, args=(agent_ip,)).start()

		return #write

class user_update:
	def POST(self):
		new_request(self)
		data = web.input()

		try:
			user_hash = data["user_hash"]
			new_structure = json.loads(data["structure"])
		except KeyError:
			return write({"error": "User hash or structure not provided. "}, 400)

		if os.path.isdir("s/%s/%s" % (conf.path, data["user_hash"])):

			try:
				f = open("s/%s/%s/structure.json" % (conf.path, data["user_hash"]), "r")
				old_structure = json.loads(f.read())
				f.close()

				f = open("s/%s/%s/user.json" % (conf.path, data["user_hash"]), "r")
				user = json.loads(f.read())
				f.close()

				# eventually move to structure comparison and checksum comparison for more efficiency

				old_files = get_files(old_structure, {})
				new_files = get_files(new_structure, {})

				old_keys = old_files.keys()
				new_keys = new_files.keys()

				tba = {}
				tbd = []

				for n in new_keys:
					if n not in old_keys:
						tba[n] = new_files[n]
					elif new_files[n] > old_files[n]:
						tba[n] = new_files[n]
				for o in old_keys:
					if o not in new_keys:
						tbd.append(o)

				print user["agent_ip"]

				Process(target=start_backup, args=(tba, tbd, user["agent_ip"], data["user_hash"])).start()

				return #write

			except IOError:
				f = open("s/%s/%s/structure.json" % (conf.path, data["user_hash"]), "w")
				f.write(data["structure"])
				f.close()

				f = open("s/%s/%s/user.json" % (conf.path, data["user_hash"]), "r")
				agent_ip = json.loads(f.read())["agent_ip"]
				f.close()

				Process(target=start_backup, args=(get_files(json.loads(data["structure"]), {}), [], agent_ip, data["user_hash"])).start()

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

		if os.path.isdir("s/%s/%s" % (conf.path, data["user_hash"])):
			f = open("s/%s/%s/structure.json" % (conf.path, data["user_hash"]))
			f.write(data["structure"])
			f.close()
		else:
			return write({"error": "User not registered. "}, 403)

if __name__ == "__main__":
	app = web.application(urls, globals())
	app.notfound = notfound
	app.run()
