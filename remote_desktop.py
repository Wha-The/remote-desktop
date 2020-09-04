import sys,subprocess
importSuccess = False
class FatalError(Exception):pass
def install_package(package):return subprocess.check_call([sys.executable, "-m", "pip", "install", package])
specialpackagenames = {"wx":"wxpython","pil":"pillow",}
while not importSuccess:
	try:import Server,Client
	except ImportError as e:
		package = str(e).split("No module named ")[1].lower()
		try:package=specialpackagenames[package]
		except KeyError:pass
		print "Package %s not found, installing package... "%package
		try:status_code = install_package(package)
		except:raise FatalError("Cannot install dependent module "+package+" (Unknown Error)")
		else:
			if status_code != 0:raise FatalError("Cannot install dependent module "+package+" (Error: pip return status != 0)")
			else:print "Sucessfully installed package "+package
	else:importSuccess = True
print("-------------------------------------------------------------------")
if (len(sys.argv)>=2 and sys.argv[1]or raw_input("Run (S)erver/(C)lient? ")).lower()=="s":
	print("Launching Server...")
	Server.Run()
else:
	print("Launching Client...")
	Client.Run()