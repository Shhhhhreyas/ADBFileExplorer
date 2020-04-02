from Tkinter import *
import tkMessageBox
from PIL import ImageTk, Image
import subprocess
import time
import os

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))


output_file = open('output_file.txt', 'w+')
error_file = open('error_file.txt','w+')
procId = subprocess.Popen('adb shell',stdin = subprocess.PIPE, stdout = output_file, stderr = error_file,shell=True)
procId.stdin.write('su\n')
time.sleep(1)
content = []
population = []
location = "/"

window = Tk()
window.title("root")
window.geometry("1366x768")

img = Image.open("folder.png")
img = img.resize((70,70), Image.ANTIALIAS)
folder = ImageTk.PhotoImage(img)
img = Image.open("file.png")
img = img.resize((60,60), Image.ANTIALIAS)
file = ImageTk.PhotoImage(img)
img = Image.open("backButton.jpg")
img = img.resize((30,30), Image.ANTIALIAS)
goBack = ImageTk.PhotoImage(img)
img = Image.open("refresh.png")
img = img.resize((30,30), Image.ANTIALIAS)
re = ImageTk.PhotoImage(img)
img = Image.open("go.png")
img = img.resize((30,30), Image.ANTIALIAS)
go = ImageTk.PhotoImage(img)
img = Image.open("home.png")
img = img.resize((30,30), Image.ANTIALIAS)
goHome = ImageTk.PhotoImage(img)

explorer = Canvas(window, borderwidth=3,height=768,width=1366)
frame = Frame(explorer)
vsb = Scrollbar(window, orient="vertical", command=explorer.yview)
hsb = Scrollbar(window,orient="horizontal",command=explorer.xview)
explorer.configure(yscrollcommand=vsb.set,xscrollcommand=hsb.set)
vsb.pack(side="right", fill="y")
hsb.pack(side="bottom",fill="x")
explorer.pack(side="left", fill="both", expand=True)
explorer.create_window((4,4), window=frame, anchor="nw")
frame.bind("<Configure>", lambda event, canvas=explorer: onFrameConfigure(explorer))

def populate():
	global content
	del content[:]
	content = doLs(content)
	clearGrid()
	nrow=1
	ncolumn=1
	for dr in content:
		if("/" in dr or "@" in dr):
			create_folder(dr.replace("/","").replace("@",""),nrow,ncolumn)
		else:
			create_file(dr.replace("*",""),nrow,ncolumn)
		ncolumn=ncolumn+1
		if(ncolumn==9):
			nrow = nrow+1
			ncolumn = 1

def back():
	runcmd("cd ../")
	populate()
	set_text("",True,False)

def refresh():
	populate()

def goToLocation(event=None):
	path = (e1.get()).rstrip()
	command = 'cd '+path
	runcmd(command)
	populate()
	if(not path.endswith('/')):
		path = path+'/'
	set_text(path,False,True)

def home():
	runcmd('cd /')
	populate()
	set_text('/',False,False,home=True)



def doLs(content):
	output_file.truncate(0)
	print('ls -F')
	try:
		procId.stdin.write('ls -F\n')
	except IOError:
		print("Shell closed")
		return
	time.sleep(0.1)
	with open('output_file.txt', 'r') as content_file:
		for line in content_file:
			content.append(line.rstrip())
	return content

def runcmd(command):
	print(command)
	try:
		procId.stdin.write(command+'\n')
	except IOError:
		print("Shell closed")
		return
	time.sleep(0.1)

def copyFile(file):
	runcmd('cp '+location + file + ' /sdcard/ADM/'+file)
	os.system('adb pull /sdcard/ADM/'+file+' '+file)
	time.sleep(0.1)
	runcmd('rm /sdcard/ADM/'+file)

def clearGrid():
	global population
	for i in population:
		i.destroy()
	del population[:]

def click(event):
	row = event.widget.grid_info()["row"]
	column = event.widget.grid_info()["column"]
	clicked = content[((row-1)*8 + column)-1]

	if("/" in clicked or "@" in clicked):
		path = clicked.replace("/","").replace("@","")
		command = "cd "+ path
		runcmd(command)
		populate()
		set_text(path,False,False)
		return
	elif("*" not in clicked and "=" not in clicked and "|" not in clicked and ">" not in clicked and "/" not in clicked and "@" not in clicked):
		result = ''
		result = tkMessageBox.askquestion("Copy", "Do you want to copy this file to PC?", icon='warning')
    	if result == 'yes':
        	copyFile(clicked)
        	tkMessageBox.showinfo(title="Copy", message="Done!")
    	else:
        	return


def onClose():
	runcmd("exit")
	runcmd("exit")
	window.destroy()

def set_text(text,back,goToLoc,home=False):
	global location
	if(not back):
		e1.delete(0,END)
		location = location + text + '/'
		e1.insert(0,location)
		window.title(text)

	else:
		res = location.rsplit('/',2)
		location = res[0]+'/'
		e1.delete(0,END)
		e1.insert(0,location)
		title = ""
		try:
			title = res[0].rsplit('/',1)[1]
		except IndexError:
			title="root"
		window.title(title)
		return

	if(goToLoc):
		e1.delete(0,END)
		e1.insert(0,text)
		res = text.rsplit('/',2)
		window.title(res[1])
		location = text

	if(home):
		location = '/'
		e1.delete(0,END)
		e1.insert(0,'/')
		window.title('root')
	return

def create_folder(label,nrow,ncolumn):
	panel = Label(frame, text=label,image = folder,compound='top')
	panel.grid(row = nrow, column = ncolumn)
	panel.bind("<Button-1>", click)
	population.append(panel)

def create_file(label,nrow,ncolumn):
	panel = Label(frame, text=label,image = file,compound='top')
	panel.grid(row = nrow, column = ncolumn)
	panel.bind("<Button-1>", click)
	population.append(panel)


btnBack = Button(explorer, image = goBack,command=back)
btnBack.grid(row=1,column=2,columnspan=1,rowspan=1)
btnRefresh = Button(explorer, image = re,bg="white",command=refresh)
btnRefresh.grid(row=1,column=8,columnspan=1,rowspan=1)
btnGo = Button(explorer, image = go,bg="white",command=goToLocation)
btnGo.grid(row=1,column=7,columnspan=1,rowspan=1)
btnHome = Button(explorer, image = goHome,bg="white",command=home)
btnHome.grid(row=1,column=1,columnspan=1,rowspan=1)
URL = Label(explorer, text='Location: ').grid(row = 1, column = 3)
e1 = Entry(explorer, bg="white",width=100)
e1.grid(row = 1, column = 4, columnspan = 3)
e1.insert(0,location)
e1.bind('<Return>', goToLocation)


populate()



window.protocol("WM_DELETE_WINDOW", onClose)
window.mainloop()