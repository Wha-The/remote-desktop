# Server Setup
from __future__ import division
import Queue
print("Loading Server package...")
import datetime

def getmillisec():
    c=datetime.datetime.now()
    return int( (c.day*24*60*60+c.second)*1000+c.microsecond/1000.0)

import keyboard,socket,pyautogui,numpy,time,base64,ast,json,threading,struct,mouse
FPS = 20

keycodes = {
	8:14,
	91:91,
	18:56,
	17:29,
	46:83,
	16:45,
}


def send_msg(sock, msg,bucket=None):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('I>', len(msg)) + msg
    try:
    	sock.sendall(msg)
    except socket.error:
    	if bucket:
    		bucket.put("cant connect")

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def dumps(data):
	return base64.b64encode(json.dumps(data))
def loads(data):
	strdata = base64.b64decode(data)
	return json.loads(strdata)
temporaryscreenshotpath = "./temporaryscreenshot.jpg"

def recievingKeyboardThreadFunc(conn):
	data = loads(recv_msg(conn).decode())
	while data:
		print data
		for evt in data["events"]["keyboard"]:
			print evt
			try:
				scan_code = keyboard.key_to_scan_codes( chr(evt["code"]) )[0]
			except ValueError:
				try:
					scan_code = keycodes[evt["code"]]
				except IndexError:
					continue
			if evt["type"]=="DOWN":
				keyboard.press(scan_code)
			else:
				keyboard.release(scan_code)
		for evt in data["events"]["mouse"]:
			print "MOUSEEVENT:",evt
			if evt=="Move":
				newPos = evt["pos"]
				mouse.move(newPos[0],newPos[1],duration=0.15)
			elif evt=="LeftDown":
				mouse.press()
			elif evt == "LeftUp":
				mouse.release()
		try:
			recieved = recv_msg(conn).decode()
		except socket.error:
			break
		data = loads(recieved)



def Run():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	host = s.getsockname()[0]

	print "Your Server IP is",host
	port = 9736
	server_socket = socket.socket()  # get instance
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.close()
	# look closely. The bind() function takes tuple as argument
	server_socket.bind((host, port))  # bind host address and port together

	# configure how many client the server can listen simultaneously
	while True:
		bucket = Queue.Queue()
		print "Waiting for client to be online..."
		server_socket.listen(2)
		conn, address = server_socket.accept()  # accept new connection
		print("Connection from ",address)
		data = recv_msg(conn).decode()
		if data:
			data=loads(data)
			send_msg(conn,dumps({"message":"OK","monitor_size":pyautogui.size()}).encode())
		# data = clientdata
		"""
		data = conn.recv(1024*1024*10).decode()
		if data:
			data=loads(data)
		"""
		success=True
		recievingKeyboardThread = threading.Thread(target=recievingKeyboardThreadFunc,args=(conn,))
		recievingKeyboardThread.start()
		while success:
			try:
				bucket.get(block=False)
			except Queue.Empty:
				pass
			else:
				break

			# process data
			starttime = getmillisec()
			pyautogui.screenshot(temporaryscreenshotpath)
			stoptime = getmillisec()
			print("Took %dms to take the screenshot"%(stoptime-starttime))
			starttime = getmillisec()
			aboutToBeSent = open(temporaryscreenshotpath,'rb').read()
			#print("AboutToBeSent: ",len(aboutToBeSent))
			stoptime = getmillisec()
			print("Took %dms to read screenshot"%(stoptime-starttime))
			sendThread = threading.Thread(target=send_msg,args=(conn,aboutToBeSent+"|??|"+str(getmillisec()),bucket) )
			sendThread.start()

			
		conn.close()
print("Server package finished loading")