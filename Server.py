from tkinter import *
import socket
import threading
import time
import sqlite3
import datetime
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style
from Crypto.Cipher import AES

class Server(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.form = []
        self.KEY = b'\x82#\x8e\x91\xf9\xafJqJ\xdbQ\x94\xee\xb1\xde\x87'
        self.interface()

        
    def interface(self):
        #Set the title background colour and height and width
        self.parent.title("Server")
        self.parent.configure(bg='grey75')
        self.parent.geometry("600x400+400+200")
        self.pack(fill=BOTH, expand=True)

        #Configure the grid at index 0 with the weights 1
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0,weight=1)

        self.lbl = Label(self, text="Connections",background="black",width=300,foreground="white")
        self.lbl.grid(row=0,sticky=N)

        #Shows the IP addresses which have connected
        self.connections = Message(self, text=None,width=300,background="grey70")
        self.connections.grid(row=1,sticky=NSEW)

        self.button = Button(self, text="Start Server",command=self.switch)
        self.button.grid(row=2)

        #Turn access from multiple threads off and connects to the database file
        self.conn = sqlite3.connect("Form.db", check_same_thread=False)
        self.c = self.conn.cursor()
        self.create_table()

        self.check()

        
        ax.clear()

        #Set values and labels for the axis
        ax.plot_date(self.form,self.number,"-")
        ax.set_title('Filled out')
        ax.set_xlabel('Dates')
        ax.set_ylabel('Entries')

        #Creates the canvas and passes in axis information
        self.canvas = FigureCanvasTkAgg(fig, master=self.parent)
        self.canvas.show()
        self.canvas.get_tk_widget().pack()

    def switch(self):
        #Checks to see if the server is on or not
        if self.button.cget("text") == "Start Server":
            #Calls the function server if the server is initially off
            self.t = threading.Thread(target=self.server,daemon=True)
            self.t.start()
            self.button.configure(text="Exit Server")
        else:
            self.parent.destroy()
            self.c.close()
            self.conn.close()
            
    def pad(self,msg):
        #Adds extra characters as AES encryption supports minimum of 16 bytes
        return msg + "0" * (16 - len(msg)% 16)

    def server(self):
        #Create a socket object
        #address family - AF_INET
        #Connection type - SOCK_STREAM
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 9999
        host = socket.gethostname()
        #Bind the socket to address
        server_socket.bind((host, port))
        #Listen for connections made to the socket
        server_socket.listen(5)

        while True:
            _pass =True
            #When there is a connection
            clientsocket, addr = server_socket.accept()
            self.ip, self.port = addr

            #Database query to select the IP and time
            self.c.execute('SELECT IP,Time FROM Form')
            data = self.c.fetchall()

            #Get current time
            localtime = datetime.datetime.now()
            localtime = localtime.strftime("%M %H %d %m %Y")

            #For every entry in database
            for data in data:
                time_one = datetime.datetime.strptime(localtime, "%M %H %d %m %Y")
                replaced = data[1].replace("/", " ")
                time_two = datetime.datetime.strptime(replaced, "%M %H %d %m %Y")
                diff = time_one-time_two
                #Check if ip is the same and the time difference is less than 120s
                if self.ip == data[0] and diff.seconds<120 :
                    print("pass", time_one, time_two)
                    _pass=False                    
                else:
                    _pass=True
                    
            if _pass:
                #Update text showing connections
                self.text = self.connections.cget("text")+"Got a connection from %s  Port %s \n" % (self.ip,self.port)
                self.connections.configure(text=self.text)

                #Creates an AES object
                cipher = AES.new(self.KEY)
                #Encrypt the padded message and send to client
                encoded = cipher.encrypt(self.pad("yoo"))
                clientsocket.send(encoded)

                #Find how many addresses have connected
                self.length = self.connections.cget("text").count('\n')

                self.data_entry()
                self.check()
                self.update_line()
            else:
                clientsocket.send("boo".encode())


    def check(self):
        #If there are many connections cut out older connections
        if self.length == 6:
            text=self.connections.cget("text")
            k = len(self.text) // self.length
            self.connections.configure(text=text[k:])

    def create_table(self):
        #Creates a table for the database
        self.c.execute('CREATE TABLE IF NOT EXISTS Form(Ip TEXT, Port INTEGER, Time TEXT)')

    def data_entry(self):
        #Inserts new entry into the database
        localtime = datetime.datetime.now()
        localtime=localtime.strftime("%M/%H/%d/%m/%Y")
        self.c.execute('INSERT INTO Form (Ip,Port,Time) VALUES(?,?,?)',(self.ip,self.port,localtime))
        self.conn.commit()

    def update_line(self):
        #Updates the graph line
        ax.clear()
        ax.plot_date(self.form, self.number,"-")
        self.canvas.draw()

    def check(self):
        #Connects to the database file
        conn = sqlite3.connect("Form.db", check_same_thread=False)
        c = conn.cursor()
        #Database query to select the time 
        c.execute('SELECT TIME FROM Form')
        
        entry = [0]
        number = [0]
        self.form = []

        #Find the number of entries within  dates stored on the database
        for dates in c.fetchall():
            new = dates[0][6:]
            if new == entry[-1]:
                number[-1]+=1
            else:
                entry.append(new)
                number.append(1)
        #List slicing to remove 0   
        entry = entry[1:]
        self.number=number[1:]
        #Converts each string to number and appends to form
        for date in entry:
            self.form.append(matplotlib.dates.datestr2num(date))


#TkAgg 	Agg backend used for rendering to a Tk canvas 
matplotlib.use('TkAgg')
style.use('seaborn-paper')

#Keeps track of child axis
fig = Figure()
#Creates a 1x1 grid 
ax = fig.add_subplot(111)
hl= ax.plot([],[])

#Instance of tk interpreter
root = Tk()
app = Server(root)
root.mainloop()
