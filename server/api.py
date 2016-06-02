import web
import brotli
import fastlz

def write(payload, status):
    return json.dumps({"payload": payload, "status": status})

def notfound():
    return web.notfound("404")

def new_request(request):
    web.header("Content-Type", "application/json")
    web.header("Access-Control-Allow-Origin", "*")
	# web.header("charset", "utf-8")


urls = (
    "/structure/new", "structure_new"
)

class structure_new:
	def POST(self):
		new_request(self)
		data = web.input()

		comp_struct = data["structure"]

		structure = fastlz.decompress(comp_struct)

		f = open("structure.json", "w")
		f.write(structure)
		f.close()



if __name__ == "__main__":
	app = web.application(urls, globals())
	app.notfound = notfound
	app.run()
