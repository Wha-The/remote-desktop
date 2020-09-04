import sys,subprocess,os,zipfile,shutil,json
importSuccess = False
ignoreUpdates=True
latestzip="lastest.zip"

class FatalError(Exception):pass
def install_package(package):return subprocess.check_call([sys.executable, "-m", "pip", "install", package])
specialpackagenames = {"wx":"wxpython","pil":"pillow",}
try:
	import requests,socket
except ImportError:
	install_package("requests")
	install_package("socket")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
host = s.getsockname()[0]

print "Your IP is",host

print("Checking for updates...")
data = requests.get("https://github.com/Wha-The/remote-desktop/archive/master.zip").content
lastest_update = os.path.exists(latestzip)and open(latestzip,'rb').read()
if data!=lastest_update:
	chooseToUpdate=not ignoreUpdates and raw_input("Update found, would you like to install it? (y/n)").lower()=="y"
	if chooseToUpdate:
		open(latestzip,'wb').write(data)
		with zipfile.ZipFile(latestzip, 'r') as zip_ref:
			zip_ref.extractall(".")
		directories = [name for name in os.listdir(".") if os.path.isdir(name)]
		if len(directories)>=1:
			for i in os.listdir(os.path.join(".",directories[0])):
				shutil.move(os.path.join(os.path.join(".",directories[0]),i),os.path.join(".",i))
			os.rmdir(directories[0])

		print("Updated, please restart RD")
		quit()
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
print("--------------------------------------------------------------------")
print "Your IP is",host
if (len(sys.argv)>=2 and sys.argv[1]or raw_input("Run (S)erver/(C)lient? ")).lower()=="s":
	print("Launching Server...")
	Server.Run()
else:
	print("Launching Client...")
	Client.Run()
