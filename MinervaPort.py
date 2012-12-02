#!/usr/bin/python2


from StringIO import StringIO
import requests
import os
import sys
import wx
import time
from threading import Thread

cookie=""
isThreadRunning=""

def getSalt():
    global cookie
	r = requests.get('https://minerva.ugent.be/secure/index.php?external=true', verify=False)
	lines = r.text.split("\n")
	cookie = r.cookies
	
	for line in lines:
	    if "authentication_salt" in line:
			return line.split("\"")[5]

def Login(username, password, salt):
	global cookie
	postdata = {'login' : str(username), 'password': str(password), 'authentication_salt': str(salt), 'submitAuth': 'Log in'}
	r = requests.post("https://minerva.ugent.be/secure/index.php?external=true", data=postdata, cookies=cookie, verify=False)
	cookie = r.cookies
	if '<div id="CBINFO_ext" class="course course0 visible" >' in r.text:
		return True
	else:
		return False

def getCourses(courseid, coursename):
	global cookie
	r = requests.get("https://minerva.ugent.be/index.php", cookies=cookie, verify=False)
	lines = r.text.split("\n")
	cookie = r.cookies
	
	courses = []
	for line in lines:
	    if "course_home.php?cidReq=" in line:
		if "class=\"course course0" not in line:
		    courses.append(line)

	tempcourse = ""

	for i in courses:
	    if "class=\"course course0" not in i:
		temp = i.split("\"")[1]
		if temp != "":
		    courseid.append(temp)
		    coursename.append(i.split("<")[5].split(">")[1])

def recursiveCourseDownloader(line, coursename):
	global cookie
	extension = ""
	if "http://minerva.ugent.be" in line:
		line = line.replace("http://minerva.ugent.be","")
 	if "downloadfolder" in line:
		extension = ".zip"
	
	url = str(line.split("\"")[15]).replace("amp;","")
	filename = url.split("path=%2F")[1]

	print "downloading: " + filename+extension
	r = requests.get("http://minerva.ugent.be"+url , cookies=cookie, verify=False)
	cookie = r.cookies
	with open(coursename+"/"+filename+extension, "wb") as code:
		code.write(r.content)

def courseDownloader(courseid, coursename):
	global cookie
	if not os.path.exists(coursename):
    		os.mkdir(coursename)
	
	r = requests.get("http://minerva.ugent.be/main/document/document.php?cidReq="+courseid, cookies=cookie, verify=False)
	cookie = r.cookies
	lines = r.text.split("\n")

	for line in lines:
		if "action=download" in line:
			recursiveCourseDownloader(line, coursename)
			if (not isThreadRunning):
				return



def MinervaSyncer(username, password, button):
	salt = getSalt()
	returnvalue = Login(username,password,salt)
	
	if not returnvalue:
		wx.MessageBox('Incorrect username and/or password', 'Error', wx.OK | wx.ICON_ERROR)
		return
	
	courseid = []
	coursename = []
	getCourses(courseid, coursename) #dit nog recursief maken
	
	for i in range(0,courseid.__len__()):
		courseDownloader(courseid[i],coursename[i])
		if(not isThreadRunning):
			return
	
	button.Enable()
	return "Successfully synced with the directory!"

class LoginDialog(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, -1, "Minerva Syncer V0.1")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.InitUI()
		self.SetSize((200,100))
		self.Centre()
		self.Fit()
		self.Show()
	
	def InitUI(self):
		hbox = wx.BoxSizer(wx.VERTICAL)
		fgs = wx.FlexGridSizer(2, 2, hgap=5, vgap=10)
		
		self.txt_username = wx.TextCtrl(self, 1)
		lbl_username = wx.StaticText(self,-1, "Username:")
		fgs.Add(lbl_username)
		fgs.Add(self.txt_username)
		
		self.txt_password = wx.TextCtrl(self, 1, style=wx.TE_PASSWORD)
		lbl_password = wx.StaticText(self,-1, "Password:")
		fgs.Add(lbl_password)
		fgs.Add(self.txt_password)
		
		"""
		fgs.Add(wx.StaticText(self,-1, label="Login:"))
		fgs.Add(wx.TextCtrl(self))
		fgs.Add(wx.StaticText(self,-1, label="Password:"))
		fgs.Add(wx.TextCtrl(self, style=wx.TE_PASSWORD))
		"""

		hbox.Add(fgs)
		self.SetSizer(hbox)
		
		self.button = wx.Button(self, -1, label="Sync")
		self.Bind(wx.EVT_BUTTON, self.OnSubmit, self.button)
		hbox.Add(self.button,0,wx.ALIGN_CENTER)
		
		#hbox.Add(wx.Button(self, label="Login"), 1, wx.ALIGN_CENTER)
		
	
	def OnSubmit(self, event):
		global isThreadRunning
		username=self.txt_username.GetValue()
		password=self.txt_password.GetValue()
		if username != "" and password != "":
			#print username + " | " + password
			t = Thread(target=MinervaSyncer, args=(username,password,self.button,))
			isThreadRunning=True
			t.start()
			self.button.Disable()
			#MinervaSyncer(username, password)
	
	def OnClose(self, event):
		global isThreadRunning
		if(isThreadRunning):
			isThreadRunning=False
			self.Destroy()
			#self.Destroy()
			#sys.exit(1)
		else:
			self.Destroy()
		
		
app = wx.App(False)

frame = LoginDialog()

app.MainLoop()
