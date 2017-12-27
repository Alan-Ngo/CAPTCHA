# CAPTCHA test implemented in a windows application
#
#CAPITALISED - Constants
#CapitalisedWords - Classes
#lowercase - Functions
#
#Different classes - ConnectServer, Captcha, Form, StartPage, PageOne

#---------------------------------------------------------------------------------------------------------#
from Crypto.Cipher import AES
from tkinter import Frame, Entry, BOTH, Label, Message, Button, Tk,Canvas, S, YES, CENTER, END
import tkinter.messagebox
from tkinter import ttk
from matplotlib.font_manager import findSystemFonts
import random, string, socket, datetime, threading
from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageFont
from pymouse import PyMouse

#Constants
FONT = ("Verdana Bold", 12)
QUESTIONS = ("What is your name?", "What is your age?", "Where are you from?")
SYMMETRIC_KEY = b'\x82#\x8e\x91\xf9\xafJqJ\xdbQ\x94\xee\xb1\xde\x87'

class ConnectServer():
    def server(self):
        #Use of try and except
        try:
            #Set the return of the function connect to encoded_data
            encoded_data = self.connect()
            #Create an AES object
            cipher = AES.new(SYMMETRIC_KEY)
            #Decode the encrypted data and set it to the variable decoded
            decoded = cipher.decrypt(encoded_data).decode("utf-8")
            #Remove the padding
            message =  self.remove_pad(decoded)
            if message == "yoo":
                return True
        except:
            #Shows an error box
            tkinter.messagebox.showinfo("Error", "Connection to server failed")

    def connect(self):
        #Create a socket object
        #address family - AF_INET
        #Connection type - SOCK_STREAM
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Get it will IPv4 address format
        host = socket.gethostname()
        port = 9999
        #Connect to host via port
        sock.connect((host, port))
        #max data revieved is 1024 bytes
        data = sock.recv(1024)
        sock.close()
        return data

    def remove_pad(self,decoded):
        #Remove the padding added during the server
        pad_length = decoded.count("0")
        return decoded[:- pad_length]

class Captcha(ConnectServer):
    def __init__(self, canvas, entry):
        self.characters = []
        self.canvas = canvas
        self.entry = entry
        self.rand_string = ""
        self.captcha_on = False
        self.mouse_bool = False
        self.time_on = False

    def show_cap(self):
        self.captcha_on = True
        self.rand_string = ""
        self.characters = []
        
        #Gets a random integer from 5-7
        loops = random.randint(5, 7)
        #Creates an image with sizes 612 by 200
        img = Image.new('RGB', (612, 200))
        #calls CAPTCHA recursion
        self.captcha(loops, img, 100, 50)

        self.canvas.pack()
        self.entry.pack()

        #Used for testing purposes - prints answer
        print(self.rand_string)

    def captcha(self, loops, img, inx, iny):
        CONSTANT = 2
        if loops <= 0:
            return 1

        else:
            #Creates a draw object
            img_ob = ImageDraw.Draw(img)
            #Retrieve a random character
            self.rand_string += random.choice(string.ascii_letters + string.digits)
            #Creates a function
            ran_colour = lambda: random.randint(100, 255)

            size = random.randint(50, 70)

            #Goes through system fonts and selects a random font
            fonts = findSystemFonts(None, "ttf")
            font = fonts[random.randint(0, len(fonts) - 1)]
            #Load true type font file and create a font object
            font = ImageFont.truetype(font, size)

            #Shift coordinates for next character
            inx += random.randint(size//CONSTANT, size // CONSTANT+10)

            #randomly determine if it should shift upwards of downwards in y axis
            if size >= 60:
                iny += random.randint(5, 10)
            else:
                iny -= random.randint(5, 10)

            #Creates the text with random colours and font
            img_ob.text((inx,iny), self.rand_string[-1], (ran_colour(),ran_colour(),ran_colour()), font=font)

            #Rotate the image
            rotate_img = img.rotate(random.randint(-10, 10))

            #Adds filter
            img.paste(rotate_img.filter(ImageFilter.SMOOTH_MORE))
            
            self.tk_img = ImageTk.PhotoImage(img)

            #Multidimesional lists
            self.characters.append([inx, iny, self.rand_string])
            self.canvas.create_image((300,100), image=self.tk_img)

            #Calls itself with shifted coordinates
            return self.captcha(loops-1, img, self.characters[-1][0], self.characters[-1][1])
        
    def start_time(self):
        self.time_on = True
        #Get current time and set format of the time
        localtime = datetime.datetime.now()
        localtime = localtime.strftime("%M %H %m %d %Y")
        self.start = datetime.datetime.strptime(localtime, "%M %H %d %m %Y")
        
    
    def time_diff(self):
        #Gets current time and sets format
        localtime = datetime.datetime.now()
        localtime = localtime.strftime("%M %H %d %m %Y")
        #print(localtime)
        end = datetime.datetime.strptime(localtime, "%M %H %d %m %Y")

        #Find the time difference
        difference = end - self.start
        return difference

    def mouse_check(self):
        #Calls mosue object
        m = PyMouse()
        mouseLoc = [(0,0)]
        
        mouseLoc.append(m.position())
        
        while True:
            #If there is a difference in position checks if the mouse has skipped more than 60 pixels in the x and y axis
            for i in range(2):
                if m.position()[i]-mouseLoc[-1][i] != 0:
                    if abs(m.position()[i] - mouseLoc[-1][i]) >= 100:
                        print("computer")
                        self.mouse_bool = True
                    mouseLoc.append(m.position())

    def check(self):
        if self.captcha_on:
            if self.time_on:
                #Time completed is less than 60 seconds
                if self.time_diff().seconds<60:
                    if self.server():
                        print("Passed")
                        return True
                else:
                    print("Took too long")
                    self.show_cap()
                    self.start_time()
                    return
                    
            #If input box = answer
            if self.entry.get() == self.rand_string:
                if self.server():
                    print("Passed")
                    return True
                else:
                    print("Server connect failed")
            else:
                print("Wrong entry")
                self.show_cap()
                self.start_time()

        else:
            #If has failed mouse test
            if self.mouse_bool == True:
                self.show_cap()
                self.start_time()
                self.mouse_bool = False
                return

            else:
                if self.server():
                    print("Passed with no text captcha")
                    return True

class Form(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        #Make columns and rows have  a weight  of 1
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

        self.parent.title("Form")

        self.frames = {}
        
        for Page in (StartPage, PageOne):
            #Calls the classes StartPage and PageOne
            frame = Page(self.parent, self)
            #Stores the class objects in self.frames
            self.frames[Page] = frame
            frame.grid(row=0, column=0, sticky="NESW")

            self.show_frame(StartPage)

    def show_frame(self, page):
        #Shows a frame object by raising the frame
        frame = self.frames[page]
        frame.tkraise()

class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.button_names = []
        self.configure(bg="SkyBlue2")

        #Open the banner image and display
        open_img = Image.open("image.png")
        banner = ImageTk.PhotoImage(open_img)
        self.label = Label(self, image=banner, bg="SkyBlue2")
        self.label.pack(pady=10, padx=10, fill=BOTH)
        self.label.image = banner

        self.controller = controller

        #Uses for loop to create questions and entry box
        for question in QUESTIONS:
            self.questions = Message(self, text=question, width=200, bg="SkyBlue2", fg="black", font=FONT)
            self.questions.pack()

            self.entry = Entry(self)
            self.entry.pack(fill=BOTH)
            #Appends an object to button_names
            self.button_names.append(self.entry)

            self.space = Message(self, text=None, width=200, bg="SkyBlue2")
            self.space.pack()

        #Submit button displayed
        button = Button(self, text="Submit", bg="white", relief="solid", command=self.check_entry)
        button.pack()
            
        #Creates a canvas(hidden) to show image
        self.canvas = Canvas(self, width=600, height=200, bg="white")
        self.canvas.pack(expand=YES, fill=BOTH)
        self.canvas.pack_forget()

        #Creates a entry box(hidden) to retrieve input
        self.entry = Entry(self)
        self.entry.pack_forget()

        self.ob = Captcha(self.canvas,self.entry)

        #Creates and starts a thread, calls ob object's function mouse_check
        self.t = threading.Thread(target=self.ob.mouse_check)
        self.t.start()

    def check_entry(self):
        #If not empty and passed tests
        #Clear boxes and show PageOne
        if not self.empty():
            if self.ob.check():
                self.clear()
                self.entry.pack_forget()
                self.canvas.pack_forget()
                self.ob.captcha_on = False
                self.controller.show_frame(PageOne)
        else:
            tkinter.messagebox.showinfo("Error", "Boxes are empty")

    def clear(self):
        #Delete entries from start to end
        self.entry.delete(0, END)
        for i in range(len(self.button_names)):
            self.button_names[i].delete(0, END)

    def empty(self):
        #Loops through button names to determine if any of the entries are empty
        for i in range(len(QUESTIONS)):
            if self.button_names[i].get() == "":
                return True

class PageOne(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.configure(bg="SkyBlue2")
        
        label = Label(self, text="You passed the captcha test", font=FONT)
        label.pack(pady=10, padx=10)

        #Button to return back to StartPage
        button = Button(self, text="Back to Form", command=lambda: controller.show_frame(StartPage))
        button.pack()

#Tk class initialised
root = Tk()
app = Form(root)

style = ttk.Style()
style.theme_use("clam")
root.mainloop()
