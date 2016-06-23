import logging
import os

logging.basicConfig(filename="default.log", level=logging.DEBUG)

class conf:

	server_ip = "http://localhost:8080"
	backup_dirs = ["/Users/rafalstapinski/GitHub/ensur"]
	path = os.path.dirname(os.path.realpath(__file__))
	user_hash = "6059a8aaab72ce2c3f023c95a48e8cc8409ded5ca24c92b25d7e9a5edf125b0b"
