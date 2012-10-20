from StringIO import StringIO
import pycurl
import os

print "insert username:"
username = str(raw_input())
print "insert password:"
password = str(raw_input())
print username, ":", password

#salt bemachtigen---------------------------------------
c = pycurl.Curl()
cookie = "tempcookies"
c.setopt(pycurl.URL, "https://minerva.ugent.be/secure/index.php?external=true")
c.setopt(pycurl.SSL_VERIFYPEER, False)
c.setopt(pycurl.COOKIEFILE, cookie)
storagebuffer = StringIO()
c.setopt(pycurl.WRITEFUNCTION, storagebuffer.write)
c.perform()
c.close()


html = storagebuffer.getvalue()
lines = html.split("\n")
for line in lines:
    if "authentication_salt" in line:
        salt = line.split("\"")[5]

#inloggen---------------------------------------
  
c = pycurl.Curl()
c.setopt(pycurl.URL,"https://minerva.ugent.be/secure/index.php?external=true")
c.setopt(pycurl.SSL_VERIFYPEER, False)
c.setopt(pycurl.COOKIEJAR, cookie)
c.setopt(pycurl.COOKIEFILE, cookie)


postdata = ""
postdata += "login="
postdata += username
postdata += "&password="
postdata += password
postdata += "&authentication_salt="
postdata += salt
postdata += "&submitAuth=Log in"

c.setopt(pycurl.POST, 1)
c.setopt(pycurl.POSTFIELDS, postdata)

c.perform()
c.close()

#minerva site downloaden----------------------------------------------------------------------------
#mss hier een wait van een seconde insteken ?
c = pycurl.Curl()
c.setopt(pycurl.URL,"https://minerva.ugent.be/index.php")
c.setopt(pycurl.SSL_VERIFYPEER, False)
c.setopt(pycurl.COOKIEJAR, cookie)
c.setopt(pycurl.COOKIEFILE, cookie)
storagebuffer.flush()
c.setopt(pycurl.WRITEFUNCTION, storagebuffer.write)
c.perform()
c.close()

courses = []
html = storagebuffer.getvalue()
lines = html.split("\n")
for line in lines:
    if "course_home.php?cidReq=" in line:
        if "class=\"course course0" not in line:
            courses.append(line)

courseid = []
coursename = []
tempcourse = ""

for i in courses:
    if "class=\"course course0" not in i:
        temp = i.split("\"")[1]
        if temp != "":
            courseid.append(temp)
            coursename.append(i.split("<")[5].split(">")[1])

#----------elk vak zijn documenthtml downloaden-------------------------------------------------------------
for i in range(0,courseid.__len__()):
    if not os.path.exists(coursename[i]):
        os.mkdir(coursename[i])
    c = pycurl.Curl()
    url = "http://minerva.ugent.be/main/document/document.php?cidReq="
    url += courseid[i]
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.SSL_VERIFYPEER, False)
    c.setopt(pycurl.COOKIEJAR, cookie)
    c.setopt(pycurl.COOKIEFILE, cookie)
    storagebuffer.flush()
    c.setopt(pycurl.WRITEFUNCTION, storagebuffer.write)
    c.perform()
    c.close()
    html = ""
    html = storagebuffer.getvalue()
    
    #-------------alle folders en files downloaden op die html
    lines = []
    lines = html.split("\n")
    for line in lines:
        if "action=download" in line:
            extension = ""
            if "http://minerva.ugent.be" in line:
                line = line.replace("http://minerva.ugent.be","")
            if "downloadfolder" in line:
                extension = ".zip"
            url = ""
            filename = ""
            url = str(line.split("\"")[15]).replace("amp;","")
            filename = url.split("path=%2F")[1]
            fp = open(coursename[i]+"/"+filename+extension, "wb")
            
            c = pycurl.Curl()
            c.setopt(pycurl.URL, "http://minerva.ugent.be"+url)
            c.setopt(pycurl.SSL_VERIFYPEER, False)
            c.setopt(pycurl.COOKIEJAR, cookie)
            c.setopt(pycurl.COOKIEFILE, cookie)
            c.setopt(pycurl.WRITEDATA, fp)
            c.perform()
            c.close()
            fp.close()
            print filename +" is downloaded"

print "DONE"