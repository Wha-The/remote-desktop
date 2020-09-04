# Client Setup
from __future__ import division
print("Loading Client package...")
import wx
import keyboard,socket,json,time,numpy,base64,ast,json,threading,struct,pyautogui,datetime
from PIL import Image
FPS = 20


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

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

CURRENTSOCKETINFO = {"sock":None,"unProcessedEvents":{"keyboard":[],"mouse":[]},"server_screen_size":[]}
clienttempscreenshotpath = "./client_temporary_screenshot.jpg"

def update(client_socket):
	"""
	while client_socket:
		updateUnprocessedEvents()
		time.sleep(0.03)
	"""


def getmillisec():
	c = datetime.datetime.now()
	return (c.day * 24 * 60 * 60 + c.second) * 1000 + c.microsecond / 1000.0

disconnected = Image.open("./disconnected.png")
Client_Screen_Size = pyautogui.size()
def get_image():
	client_socket = CURRENTSOCKETINFO["sock"]
	if client_socket:
		try:
			data = recv_msg(client_socket)
		except:
			return disconnected
		date,starttime = data.split("|??|")
		starttime = int(starttime)


		print ("Recieved:",len(data)," Took %dms to recieve"%(getmillisec()-starttime))
		open(clienttempscreenshotpath,"wb").write(data)
		screen = Image.open(clienttempscreenshotpath)
		screen = screen.resize(Client_Screen_Size)
		return screen

def pil_to_wx(image):
	width, height = image.size
	buffer = image.convert('RGB').tobytes()
	bitmap = wx.BitmapFromBuffer(width, height, buffer)
	return bitmap

def updateUnprocessedEvents():
	sendData = dumps( {"events":CURRENTSOCKETINFO["unProcessedEvents"]} ).encode()
	#print("About to be sent: ",sendData)
	send_msg(CURRENTSOCKETINFO["sock"],sendData)
	CURRENTSOCKETINFO["unProcessedEvents"]={"keyboard":[],"mouse":[]}
class Panel(wx.Panel):
	def __init__(self, parent):
		super(Panel, self).__init__(parent, -1)
		self.SetSize(CURRENTSOCKETINFO["server_screen_size"])
		self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
		self.Bind(wx.EVT_PAINT, self.on_paint)
		self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		self.Bind(wx.EVT_KEY_UP, self.onKeyUp)

		self.Bind(wx.EVT_MOUSE_EVENTS, self.mouseEvent)

		self.update()
	def mouseEvent(self,event):
		validMouseEvents = ["LeftDClick","LeftDown","LeftUp","MiddleDClick","MiddleDown","MiddleUp","RightDClick","RightDown","RightUp"]
		thisEvent = [i for i in validMouseEvents if event.__getattribute__(i)()]
		try:
			thisEvent = thisEvent[0]
		except IndexError:
			thisEvent = None
		if event.GetButton == wx.MOUSE_BTN_NONE:
			CURRENTSOCKETINFO["unProcessedEvents"]["mouse"].append({"event":"Move","pos":event.GetLogicalPosition()})
		elif not thisEvent: return
		CURRENTSOCKETINFO["unProcessedEvents"]["mouse"].append({"event":thisEvent})
		updateUnprocessedEvents()


	def update(self):
		self.Refresh()
		self.Update()

		wx.CallLater(FPS, self.update)
	def create_bitmap(self):
		image = get_image()
		bitmap = pil_to_wx(image)
		return bitmap
	def on_paint(self, event):
		bitmap = self.create_bitmap()
		dc = wx.AutoBufferedPaintDC(self)
		dc.DrawBitmap(bitmap, 0, 0)
	def onKeyDown(self, event):
		keycode = event.GetRawKeyCode()
		appendData={"type":"DOWN","code":keycode}
		print "KEY DOWN!: ",appendData
		CURRENTSOCKETINFO["unProcessedEvents"]["keyboard"].append(appendData)

		updateUnprocessedEvents()
		event.Skip()
	def onKeyUp(self, event):
		keycode = event.GetRawKeyCode()
		appendData={"type":"UP","code":keycode}
		print "KEY UP!: ",appendData
		CURRENTSOCKETINFO["unProcessedEvents"]["keyboard"].append(appendData)
		updateUnprocessedEvents()

		event.Skip()


class Frame(wx.Frame):
	def __init__(self):
		style = wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER & ~wx.MAXIMIZE_BOX
		super(Frame, self).__init__(None, -1, 'Remote Desktop', style=style)
		panel = Panel(self)
		self.SetFocus()
		self.ShowFullScreen(True)
		self.Fit()
	

def Run():
	global disconnected

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	s.connect(("8.8.8.8", 80))
	host = raw_input("Host: ") or s.getsockname()[0]
	s.close()
	port = 9736
	try:
		client_socket = socket.socket()  # instantiate
		client_socket.connect((host, port))  # connect to the server
	except socket.error:
		print "No Server with the IP '"+host+"' is found.Please Try again"
		return Run()

	message = {"host":str(host)}
	send_msg(client_socket,dumps(message).encode())  # send message
	CURRENTSOCKETINFO["sock"]=client_socket

	serverdata = loads(recv_msg(client_socket).decode())
	server_screen_size = serverdata["monitor_size"]
	CURRENTSOCKETINFO["server_screen_size"] = server_screen_size
	disconnected = disconnected.resize(Client_Screen_Size,Image.ANTIALIAS)
	updateThread = threading.Thread(target=update,args=(client_socket,))
	updateThread.start()
	app = wx.PySimpleApp()
	frame = Frame()
	frame.Center()
	frame.Show()
	app.MainLoop()


	return
print("Client package finished loading")