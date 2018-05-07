# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 17:05:19 2018

@author: suganthi.c
"""

from tkinter import *
from tkinter import messagebox, filedialog
import csv
import visa
import re
import math
import itertools
from functools import partial
import time
import smtplib
import yagmail
import os

class MyApp(Frame):
    
    def __init__(self,master):
        self.master = master
        Frame.__init__(self,self.master)
        self.master.grid()
        self.step_buttons = []
        self._step_selected = None
        self.new_btn = Button()
        self.delayfinal = 0
        self.stepbtntexts = []
        self.btnstrings = []
        self.allbtns = []
        self.savetext = ""
        self.inputValue = ""
        self.readvalue = ""
        self.currentdriver = ""
        self.pwrterminal = ""
        self.stepdubbtn = None
        self.saveentry = []
        self.saveentrydict = {}
        self.readwrite = ""
        self.saveheader = []
        self.entryline = ""
        self.saving = ""
        num = 0
        self.destroy= lambda num=num : self.destroywidgets(num)
        self.currentpath = os.path.dirname(__file__)
        self.datestr = time.strftime("%Y-%m-%d")
        self.hourstr = time.strftime("%Y-%m-%d-%H")
        self.minstr = time.strftime("%Y-%m-%d-%H%M")
        """Uncomment below (6)lines from 53 to 58, if you want to run the application with instrument"""
#        self.timestr = time.strftime("%Y-%m-%d-%H%M%S")
#        self.rm = visa.ResourceManager()
#        self.device=self.rm.list_resources()
#        print("Instrument USB Address is " ,self.device) 
#        self.inst = self.rm.open_resource(self.device[0])
#        print(self.inst.query("*IDN?"))   
        self.appOutline()

    """Here is where the application is designed with widgets inside"""
    def appOutline(self):
        top = self.winfo_toplevel()
        self.menuBar = Menu(top)
        top["menu"] = self.menuBar
        self.subMenu1 = Menu(self.menuBar)
        self.menuBar.add_cascade(label = "File", menu = self.subMenu1)
        self.subMenu1.add_command( label = "Load Test Input(CSV)",command = self.readCSV)
        self.subMenu2 = Menu(self.menuBar)
        self.menuBar.add_cascade(label = "Tools", menu = self.subMenu2)
        self.subMenu2.add_command( label = "Reload",command = self.menuFunc)
        self.subMenu3 = Menu(self.menuBar)
        self.menuBar.add_cascade(label = "Help", menu = self.subMenu3)
        self.subMenu3.add_command( label = "Help",command = self.menuFunc)
        self.masterframe1 = Frame(self.master,width=600,height=450)
        self.masterframe1.grid(sticky=N,padx=20)
        self.masterframe2 = Frame(self.master,width=600,height=100)
        self.masterframe2.grid(sticky=S,padx=20)
        self.masterframe3 = Frame(self.master,width=600,height=100)
        self.masterframe3.grid(sticky=S,padx=20)
        self.addtabbutton = Button(self.masterframe2,text="Add Step", width=10, command=self.popup2, bg="sienna1")
        self.addtabbutton.grid(row=0,column=0,sticky=EW)
        self.runallbutton = Button(self.masterframe2,text="Run All", width=10, command=self.process_all, bg="sienna1",state=DISABLED)
        self.runallbutton.grid(row=0,column=1,sticky=EW)
        self.runselbutton = Button(self.masterframe2,text="Run Selected", width=15, command=self.process_selected, bg="sienna1",state=DISABLED)
        self.runselbutton.grid(row=0,column=2,sticky=EW)
        self.savesequence = Button(self.masterframe2,text="Save Sequence", width=15, bg="sienna1",state=DISABLED)
        self.savesequence.grid(row=0,column=3,sticky=EW)
        self.opensequence = Button(self.masterframe2,text="Open Sequence", width=15, command=self.openseq, bg="sienna1",state=NORMAL)
        self.opensequence.grid(row=0,column=4,sticky=EW)
        self.clearbutton = Button(self.masterframe2,text="Clear All", width=10, command=self.clearall, bg="sienna1",state=NORMAL)
        self.clearbutton.grid(row=0,column=5,sticky=EW)
        
    """Clicking on "Load Test Input(CSV)" will redirect to below function"""
    def readCSV(self):
        self.destroy(1)
        try:
            self.filename = filedialog.askopenfilename()
            f = open(self.filename,"r")
            self.read = csv.reader(f, delimiter = "\n")
            for row in enumerate(self.read):
                self.allbtns.append(row)
                for x,btn in enumerate(row,start=1):                
                    if x%2 == 0:
                        self.new_btn = Button(self.masterframe1, text=btn, bg="burlywood1")
                        self.new_btn.pack(fill=X,padx=50)
                        self.new_btn.configure(command=partial(self.colorchange, self.new_btn))
                    else:
                        self.new_btn = Label(self.masterframe1, text=btn+1, bg="deepskyblue2",fg="white")
                        self.new_btn.pack(fill=X,padx=50)
    
                    btn = str(btn)
                    self.btn1= btn[btn.find("(")+1:btn.rfind(")")]
                    self.commacount = self.btn1.count(',')
                    btnstrings = str(self.btn1).split(',')
                    self.btnstrings.append(btnstrings)
                    self.step_buttons.append(self.new_btn)
            self.btnstrings1 = [strgs for strgs in self.btnstrings if strgs != ['']]
            self.runallbutton.config(state=NORMAL,command=self.process_all)
            self.addtabbutton.config(state=DISABLED)
        except FileNotFoundError:
            self.destroy(3)
            self.reportmsg=Label(self.masterframe3,text="Error: Select a csv file")
            self.reportmsg.grid()
            messagebox.showerror("Error", "Select a csv file")
            print("Please provide input csv file!!")
    
    """Here is the prompt to save the sequence that we added as steps -func: saveseq, saveseqsubmit"""
    def saveseq(self):
        self.saveseqpopup = Toplevel(self.master)
        Label(self.saveseqpopup,text="Enter file name you want to save:").pack()
        self.saveseqentry = Entry(self.saveseqpopup)
        self.saveseqentry.pack()
        self.saveseqentry.focus()
        Label(self.saveseqpopup,text="(File gets saved as csv only. Don't add any extensions to filename)").pack()
        Button(self.saveseqpopup,text="Submit",command=self.saveseqsubmit).pack()
    
    def saveseqsubmit(self):
        self.saveseqfilename = self.saveseqentry.get()
        self.saveseqpopup.destroy()
        if len(self.saveseqfilename) == 0:
            print("File name not provided")
            messagebox.showerror("error","File name should be given")
        else:
            print("Saving filename is {}.csv".format(self.saveseqfilename))
            self.saving = self.currentpath+r"/outputs/sequences_to_open/"
            if not os.path.exists(self.saving):
                    os.mkdir(self.saving)
            self.saveseqfile = self.saving+self.saveseqfilename+r".csv"
            with open(self.saveseqfile,'a',newline='') as csvfile:
                writer = csv.writer(csvfile,dialect='excel')
                for item in self.stepbtntexts:
                    writer.writerow([item])
    
    """Here is the prompt to open the sequence we saved"""
    def openseq(self):
        self.filename = filedialog.askopenfilename()
        self.destroy(1)
        self.destroy(3)
        try:
            f = open(self.filename,"r")
            self.read = csv.reader(f, delimiter = "\n")
            for row in enumerate(self.read):
                self.allbtns.append(row)
                for x,btn in enumerate(row,start=1):                
                    if x%2 == 0:
                        self.new_btn = Button(self.masterframe1, text=btn, bg="burlywood1")
                        self.new_btn.pack(fill=X,padx=50)
                        self.new_btn.configure(command=partial(self.colorchange, self.new_btn))
                    else:
                        pass
                    btn = str(btn)
                    self.btn1= btn[btn.find("(")+1:btn.rfind(")")]
                    self.commacount = self.btn1.count(',')
                    btnstrings = str(self.btn1).split(',')
                    self.btnstrings.append(btnstrings)
                    self.step_buttons.append(self.new_btn)
            self.btnstrings1 = [strgs for strgs in self.btnstrings if strgs != ['']]
            self.runallbutton.config(state=NORMAL,command=self.process_all)
            self.addtabbutton.config(state=DISABLED)
        
        except FileNotFoundError:
            self.destroy(3)
            self.reportmsg=Label(self.masterframe3,text="Error: Select a csv file")
            self.reportmsg.grid()
            messagebox.showerror("Error", "Select a csv file")
            print("Please provide input csv file!!")
    
    """This function will clear all the steps appearing in main UI"""
    def clearall(self):
        self.destroy(1)
        self.runallbutton.config(state=DISABLED)
        self.addtabbutton.config(state=NORMAL)
    
    """Use this function to configure any Menu Options such as Reload and Help"""
    def menuFunc(self):
        messagebox.showinfo("info","Functionalities to be configured")
        print("Functionalities to be configured")
    
    """This common function is dynamically used at many places"""
    def destroywidgets(self,num):
        if num == 1:
            for widget in self.masterframe1.winfo_children():
                widget.destroy()
        elif num == 2:
            for widget in self.masterframe2.winfo_children():
                widget.destroy()
        elif num == 3:
            for widget in self.masterframe3.winfo_children():
                widget.destroy()
        elif num == 4:
            for widget in self.frame1.winfo_children():
                widget.destroy()
        elif num == 5:
            for widget in self.top_frm.winfo_children():
                widget.destroy()
        elif num == 6:
            for widget in self.ctr.winfo_children():
                widget.destroy()
        elif num == 7:
            for widget in self.ctr_left.winfo_children():
                widget.destroy()
        elif num == 8:
            for widget in self.ctr_mid.winfo_children():
                widget.destroy()
        elif num == 9:
            for widget in self.ctr_right.winfo_children():
                widget.destroy()
        elif num == 10:
            for widget in self.ctr_right_up.winfo_children():
                widget.destroy()
        elif num == 11:
            for widget in self.ctr_right_btm.winfo_children():
                widget.destroy()
        elif num == 12:
            for widget in self.btm_frm.winfo_children():
                widget.destroy()
            
    """Secondary window is configured in below function """
    def popup2(self):
        self.destroy(3)
        self.childpopup = Toplevel(self.master)
        self.childpopup.title("Driver's tab")
        self.childpopup.geometry('{}x{}'.format(550,400))
        self.captionInput=StringVar()
        self.frame1 = Frame(self.childpopup,width=550,height=400)
        self.frame1.grid(padx=0)
        self.top_frm = Frame(self.frame1, width=500, height=100)
        self.top_frm.grid(row=0,column=0)              
        self.top_frm_lbl = Label(self.top_frm,text="Caption of the driver's action: ")
        self.top_frm_lbl.grid(row=0,column=0,sticky=NW,ipadx=5)
        self.top_frm_entry = Entry(self.top_frm,textvariable=self.captionInput)
        self.top_frm_entry.grid(row=0,column=1,sticky=EW,padx=5)
        self.top_frm_entry.focus()
        self.ctr = Frame(self.frame1,width=500,height=200)
        self.ctr.grid(row=1,column=0)
        self.ctr_left = Frame(self.ctr, width=100, height=200)
        self.ctr_mid = Frame(self.ctr, width=150, height=200)
        self.ctr_right = Frame(self.ctr, width=250, height=200)
        self.ctr_left.grid(row=1,column=0)
        self.ctr_mid.grid(row=1,column=1)
        self.ctr_right.grid(row=1,column=2)
        self.ctr_right_up = Frame(self.ctr_right,width=225,height=100)
        self.ctr_right_btm = Frame(self.ctr_right,width=225,height=100)
        self.ctr_right_up.grid(row=0,column=0)
        self.ctr_right_btm.grid(row=1,column=0)
        self.btm_frm = Frame(self.frame1,width=500,height=100)
        self.btm_frm.grid(row=2,column=0,sticky=S,padx=30)
        self.savebtn = Button(self.btm_frm,text="Save",width=10,command=self.saveprompt)
        self.savebtn.grid(row=1,column=0,sticky=SE)
        self.closebtn = Button(self.btm_frm,text="Close",width=10,command=self.closebutton)
        self.closebtn.grid(row=1,column=1,sticky=SE)
        self.lbl1 = Label(self.ctr_left,text="List of Driver Categories:",fg="RoyalBlue2",font=("none",10,"bold"))
        self.lbl1.grid(row=0,column=0)
        """ Add the category of drivers to the below list if you want to add more """
        self.drivernames = ["Power Supplies","Digital Multimeter","Software Drivers","Protocol Drivers","Custom Drivers","Others"]
        for i in range(len(self.drivernames)):
            self.driverButtons=Button(self.ctr_left,bg="tomato",text=self.drivernames[i],command=lambda i=i : self.drivercategories(i))
            self.driverButtons.grid(row=i+1,column=0,sticky=EW,padx=5)
        
    """ Configuring the steps on selection of any driver """
    def drivercategories(self,driverid):
        """ Add the corresponding sub-categories of drivers if you want to add more """
        self.pwrsply = ["3631 Driver", "3634 Driver"]
        self.multimeter = ["34401 Driver", "34461 Driver"]
        self.swdrivers = ["Delay running"]
        self.others = ["Request New Driver"]
        self.destroy(8)
        self.lbl2 = Label(self.ctr_mid,text="Sub-Categories of Drivers: ",fg="RoyalBlue2",font=("none",10,"bold"))
        self.lbl2.grid(row=0,column=0)
        self.drivercategory = self.drivernames[driverid]
        print(self.drivercategory)
        if driverid == 0:
            for j in range(len(self.pwrsply)):
                Button(self.ctr_mid,bg="pink3",text=self.pwrsply[j],command=lambda j=j : self.powersupplyfunc(j)).grid(row=j+1,column=0,sticky=EW,padx=5)
        elif driverid == 1:
            for k in range(len(self.multimeter)): 
                Button(self.ctr_mid,bg="pink3",text=self.multimeter[k],command= lambda k=k : self.multimeterfunc(k)).grid(row=k+1,column=0,sticky=EW,padx=5)
        elif driverid == 2:
            for m in range(len(self.swdrivers)):
                Button(self.ctr_mid,bg="pink3",text=self.swdrivers[m],command=lambda m=m : self.swdriversfunc(m)).grid(row=m+1,column=0,sticky=EW,padx=5)
        elif driverid == 5:
            for n in range(len(self.others)):
                Button(self.ctr_mid,bg="pink3",text=self.others[n],command=lambda n=n : self.othersfunc(n)).grid(row=n+1,column=0,sticky=EW,padx=5)
            
    """ Configuring the steps on selection of any sub-categories of driver """
    """ This function corresponds to selection of "Power Supply" category """
    def powersupplyfunc(self,id):
        self.destroy(10)
        self.destroy(11)
        if id == 0:
            self.currentdriver = self.pwrsply[id]
            Label(self.ctr_right_up,text="Front panel of {}".format(self.pwrsply[id]),justify=LEFT,font=("none",10,"bold"),fg="RoyalBlue2").grid(row=0,column=0,ipadx=20)
            self.var=IntVar()
            Label(self.ctr_right_up,text="Select Read/Write option",justify=LEFT,fg="blue").grid(row=1,column=0,ipadx=20)
            self.radiobut1 = Radiobutton(self.ctr_right_up,text="Read",variable=self.var,value=1,command=self.radioSel)
            self.radiobut1.grid(row=2,column=0,sticky=N,columnspan=1)
            self.radiobut2 = Radiobutton(self.ctr_right_up,text="Write",variable=self.var,value=2,command=self.radioSel)
            self.radiobut2.grid(row=3,column=0,sticky=N,columnspan=1)
        elif id == 1:
            self.currentdriver = self.pwrsply[id]
            Label(self.ctr_right_up,text="Front panel of {}".format(self.pwrsply[id]),justify=LEFT,font=("none",10,"bold"),fg="RoyalBlue2").grid(row=0,column=0,ipadx=20)
            self.var=IntVar()
            Label(self.ctr_right_up,text="Select Read/Write option",justify=LEFT,fg="blue").grid(row=1,column=0,ipadx=20)
            self.radiobut1 = Radiobutton(self.ctr_right_up,text="Read",variable=self.var,value=1,command=self.radioSel)
            self.radiobut1.grid(row=2,column=0,sticky=N,columnspan=1)
            self.radiobut2 = Radiobutton(self.ctr_right_up,text="Write",variable=self.var,value=2,command=self.radioSel)
            self.radiobut2.grid(row=3,column=0,sticky=N,columnspan=1)
        
    def radioSel(self):
        self.destroy(11)
        self.radVal = self.var.get()
        self.var1=IntVar()
        Label(self.ctr_right_up,text="Select the terminal: ",justify=LEFT,fg="blue").grid(row=4,column=0)
        if self.radVal == 1:
            self.readwrite = self.radiobut1["text"]
            print("Selected Option is {}".format(self.readwrite))
            self.radiobut3 = Radiobutton(self.ctr_right_btm,text="P6V",variable=self.var1,value=1,command=self.radioSel1)
            self.radiobut3.grid(row=0,column=0,sticky=N)
            self.radiobut4 = Radiobutton(self.ctr_right_btm,text="P25V",variable=self.var1,value=2,command=self.radioSel1)
            self.radiobut4.grid(row=1,column=0,sticky=N)
        else:
            self.readwrite = self.radiobut2["text"]
            print("Selected Option is {}".format(self.readwrite))
            self.radiobut3 = Radiobutton(self.ctr_right_btm,text="P6V",variable=self.var1,value=1,command=self.radioSel1)
            self.radiobut3.grid(row=0,column=0,sticky=N)
            self.radiobut4 = Radiobutton(self.ctr_right_btm,text="P25V",variable=self.var1,value=2,command=self.radioSel1)
            self.radiobut4.grid(row=1,column=0,sticky=N)

    def radioSel1(self):
        self.radVal1 = self.var1.get()
        self.var2=IntVar()
        if self.radVal1 == 1:
            self.pwrterminal = self.radiobut3["text"]
            print("Terminal is {}".format(self.pwrterminal))
        else:
            self.pwrterminal = self.radiobut4["text"]
            print("Terminal is {}".format(self.pwrterminal))
        Label(self.ctr_right_btm,text="Do you want to Read the value?",fg="blue").grid(row=2,column=0)
        self.radiobut5 = Radiobutton(self.ctr_right_btm,text="Yes",variable=self.var2,value=1,command=self.radioSel2)
        self.radiobut5.grid(row=3,column=0,sticky=N)
        self.radiobut6 = Radiobutton(self.ctr_right_btm,text="No",variable=self.var2,value=2,command=self.radioSel2)
        self.radiobut6.grid(row=4,column=0,sticky=N)
        self.readimmdbutt = Button(self.ctr_right_btm,text="Read Immediate",command=self.readimmd)
    
    def radioSel2(self):
        self.radVal2 = self.var2.get()
        if self.radVal2 == 1:
            self.readimmdbutt.grid(row=5,column=0)
            self.readimmdbutt.config(state=NORMAL)
            self.readtext = Text(self.ctr_right_btm,height=1,width=10)
            self.readtext.grid(row=6,column=0)
            self.readtext.config(state=DISABLED)
        else:
            self.readimmdbutt.config(state=DISABLED)
            self.savetext = r" (" +self.currentdriver+ ", Power supply is set for " + str(self.readwrite)+" operation at the output " + str(self.pwrterminal) + " terminal)"
            print(self.savetext)
            self.savebtn.config(command=self.savebutton)
            
    def processpowersupply(self):
        self.savetext = r" (" +self.currentdriver+ ", Power supply is set at " + str(self.readvalue) + "V for " + str(self.readwrite)+" operation at the output " + str(self.pwrterminal) + " terminal)"
        print(self.savetext)
        self.savebtn.config(command=self.savebutton)
        
    def readimmd(self):
        self.readimmdwid = Toplevel(self.childpopup)
        self.readimmdwid.title("Read from user")
        self.readimmdwid.geometry("100x100")
        Label(self.readimmdwid,text="Input").pack()
        self.readentry=IntVar()
        self.readentry=Entry(self.readimmdwid)
        self.readentry.pack()
        self.readentry.focus()
        Button(self.readimmdwid,text="Save",command=self.redirect).pack()
        
    def redirect(self):
        self.readtext.config(state=NORMAL)
        self.readvalue=self.readentry.get()
        self.readtext.insert(END,self.readvalue)
        self.readtext.config(state=DISABLED)
        print("Read Immediate: {}".format(self.readvalue))
        self.readimmdwid.destroy()
        self.processpowersupply()
    
    """ This function corresponds to selection of "Digital Multimeter" category"""
    def multimeterfunc(self,id):
        self.destroy(10)
        self.destroy(11)
        if id == 0:
            self.currentdriver = self.multimeter[id]
            Label(self.ctr_right_up,text="Front panel of {}".format(self.multimeter[id]),justify=LEFT,font=("none",10,"bold"),fg="RoyalBlue2").grid(row=0,column=0,ipadx=20)
            self.mulvar=IntVar()
            Label(self.ctr_right_up,text="Select Read/Write option",justify=LEFT,fg="blue").grid(row=1,column=0,ipadx=20)
            self.mulradiobut1 = Radiobutton(self.ctr_right_up,text="Read",variable=self.mulvar,value=1,command=self.mulradioSel)
            self.mulradiobut1.grid(row=2,column=0,sticky=N,columnspan=1)
            self.mulradiobut2 = Radiobutton(self.ctr_right_up,text="Write",variable=self.mulvar,value=2,command=self.mulradioSel)
            self.mulradiobut2.grid(row=3,column=0,sticky=N,columnspan=1)
        elif id == 1:
            self.currentdriver = self.multimeter[id]
            Label(self.ctr_right_up,text="Front panel of {}".format(self.multimeter[id]),justify=LEFT,font=("none",10,"bold"),fg="RoyalBlue2").grid(row=0,column=0,ipadx=20)
        
    def mulradioSel(self):
        self.destroy(11)
        self.mulvarval = self.mulvar.get()
        self.mulvar1 = IntVar()
        Label(self.ctr_right_up,text="Select parameter: ",justify=LEFT,fg="blue").grid(row=4,column=0)
        if self.mulvarval == 1:
            print("You chose {}".format(self.mulradiobut1["text"]))
            self.mulradiobut3 = Radiobutton(self.ctr_right_btm,text="Voltage",variable=self.mulvar1,value=1,command=self.mulradioSel1)
            self.mulradiobut3.grid(row=0,column=0,sticky=NW)
            self.mulradiobut4 = Radiobutton(self.ctr_right_btm,text="Current",variable=self.mulvar1,value=2,command=self.mulradioSel1)
            self.mulradiobut4.grid(row=1,column=0,sticky=NW)
            self.mulradiobut5 = Radiobutton(self.ctr_right_btm,text="Resistance",variable=self.mulvar1,value=3,command=self.mulradioSel1)
            self.mulradiobut5.grid(row=2,column=0,sticky=NW)
        else:
            print("You chose {}".format(self.mulradiobut2["text"]))
            self.mulradiobut3 = Radiobutton(self.ctr_right_btm,text="Auto zero",variable=self.mulvar1,value=1,command=self.mulradioSel2)
            self.mulradiobut3.grid(row=0,column=0,sticky=NW)
            self.mulradiobut4 = Radiobutton(self.ctr_right_btm,text="Null",variable=self.mulvar1,value=2,command=self.mulradioSel2)
            self.mulradiobut4.grid(row=1,column=0,sticky=NW)
            self.mulradiobut5 = Radiobutton(self.ctr_right_btm,text="2/4 wire",variable=self.mulvar1,value=3,command=self.mulradioSel2)
            self.mulradiobut5.grid(row=2,column=0,sticky=NW)
            self.mulradiobut6 = Radiobutton(self.ctr_right_btm,text="Reset",variable=self.mulvar1,value=4,command=self.mulradioSel2)
            self.mulradiobut6.grid(row=3,column=0,sticky=NW)
            self.mulradiobut7 = Radiobutton(self.ctr_right_btm,text="Resolution",variable=self.mulvar1,value=5,command=self.mulradioSel2)
            self.mulradiobut7.grid(row=4,column=0,sticky=NW)
        
    def mulradioSel1(self):
        pass
        self.mulvar1val = self.mulvar1.get()
        if self.mulvar1val == 1:
            print("Parameter is {}".format(self.mulradiobut3["text"]))
            self.inst.write("CONFIGURE:VOLTAGE:DC")
            time.sleep(0.2)
            self.inst.write("INIT")
            time.sleep(0.2)
            print("The Measured Current is:",self.inst.query("READ?"))
        elif self.mulvar1val == 2:
            print("Parameter is {}".format(self.mulradiobut4["text"]))
            self.inst.write("CONFIGURE:CURRENT:DC")
            time.sleep(0.2)
            self.inst.write("INIT")
            time.sleep(0.2)
            print("The Measured Current is:",self.inst.query("READ?"))
        else:
            print("Parameter is {}".format(self.mulradiobut5["text"]))
            self.inst.write("CONFIGURE:RESISTANCE")
            time.sleep(0.2)
            self.inst.write("INIT")
            time.sleep(0.2)
            print("The Measured Current is:",self.inst.query("READ?"))
        Button(self.ctr_right,text="Read value: ",command=self.readimmd).grid(row=8,column=0)
        self.readtext = Text(self.ctr_right,height=1,width=10)
        self.readtext.grid(row=9,column=0)
        self.readtext.config(state=DISABLED)
        self.rm.close()
        
    def mulradioSel2(self):
        pass
        self.mulvar1val = self.mulvar1.get()
        if self.mulvar1val == 1:
            print("Parameter is {}".format(self.mulradiobut3["text"]))
            self.inst.write("ZERO:AUTO ONCE")
        elif self.mulvar1val == 2:
            print("Parameter is {}".format(self.mulradiobut4["text"]))
            self.inst.write("CALCulate:FUNCtion NULL")    #select the Null math operation 
            time.sleep(0.2)
            self.inst.write("CALCulate:STATe ON")
        elif self.mulvar1val == 3:
            print("Parameter is {}".format(self.mulradiobut5["text"]))
            self.inst.write("SENSe:FUNCtion RESistance")
        elif self.mulvar1val == 4:
            print("Parameter is {}".format(self.mulradiobut6["text"]))
            self.inst.write("*RST")
        else:
            print("Parameter is {}".format(self.mulradiobut7["text"]))
            self.inst.write("SENSe:FUNCtion FRESistance")
        self.rm.close()
        
    """ This function corresponds to selection of "Software Drivers" category"""
    def swdriversfunc(self,id):
        self.destroy(10)
        self.destroy(11)
        self.delayvar = IntVar()
        if id == 0:
            self.currentdriver = self.swdrivers[id]
            Label(self.ctr_right_up,text=self.swdrivers[id],justify=LEFT,font=("none",10,"bold"),fg="RoyalBlue2").grid(row=0,column=0,ipadx=20)
            self.delayradio1 = Radiobutton(self.ctr_right_up,text="Hours",variable=self.delayvar,value=1,command=self.delayfunc)
            self.delayradio1.grid(row=1,column=0,ipadx=10)
            self.delayradio2 = Radiobutton(self.ctr_right_up,text="Minutes",variable=self.delayvar,value=2,command=self.delayfunc)
            self.delayradio2.grid(row=2,column=0,ipadx=10)
            self.delayradio3 = Radiobutton(self.ctr_right_up,text="Seconds",variable=self.delayvar,value=3,command=self.delayfunc)
            self.delayradio3.grid(row=3,column=0,ipadx=10)
        else:
            pass
            
    def delayfunc(self):
        self.delayvarvalue = self.delayvar.get()
        self.delayentryvar = StringVar()
        self.delayent = Entry(self.ctr_right_btm,textvariable=self.delayentryvar,width=15)
        self.delayent.grid(row=0,column=0)
        self.delayent.focus()
        Button(self.ctr_right_btm,text="Save Delay",command=self.delayfunc1).grid(row=1,column=0)
        self.delval = Text(self.ctr_right_btm, height=1, width=10)
        self.delval.grid(row=2,column=0)
        Label(self.ctr_right_btm,text="(in secs)").grid(row=2,column=1)
        self.delval.config(state=DISABLED)
            
    def delayfunc1(self):
        try:
            self.delayentry = self.delayent.get()
            print(self.delayentry)
            if self.delayvarvalue == 1:
                self.delayfinal = int(self.delayentry)*3600
            elif self.delayvarvalue == 2:
                self.delayfinal = int(self.delayentry)*60
            else:
                self.delayfinal = int(self.delayentry)
            self.delval.config(state=NORMAL)
            self.delval.insert(END,self.delayfinal)
            self.delval.config(state=DISABLED)
            print("Delay is {}sec".format(self.delayfinal))
            self.savetext="( Delay timing running for {} sec)".format(self.delayfinal)
            self.savebtn.config(command=self.savebutton)
        except ValueError:
            print("Only positive integers are allowed!!")
            messagebox.showerror("error","Enter only positive integers(numbers) !!")
    
    """ This function corresponds to selection of "Others" category. Configure functionality """
    def othersfunc(self,id):
        pass
    
    """ Here is where the "Save" button of secondary window is configured, which saves the process"""
    def savebutton(self):
        self.inputValue = self.top_frm_entry.get()
        self.saving = self.currentpath+r"/outputs/"
        if not os.path.exists(self.saving):
                os.mkdir(self.saving)
        self.savingparams = self.saving+r"/particulars/"
        if not os.path.exists(self.savingparams):
                os.mkdir(self.savingparams)
        self.file_path = self.saving+r"sequence_"+self.minstr+r".csv"
        self.savetexts_file_path = self.savingparams+r"sequences_particulars"+r".csv"

        if len(self.inputValue) == 0:
            print("Caption is missing !!")
            messagebox.showerror("Error", "Caption is missing !!")
        else:
            self.savetext = self.inputValue+self.savetext
            print(self.savetext)
            self.saveentry = [self.inputValue,self.drivercategory,self.currentdriver,self.readwrite,self.readvalue,self.pwrterminal]
            self.saveentrydict = {"Caption Input":self.inputValue,"Driver Catrgory":self.drivercategory,"Driver sub-category":self.currentdriver,"Read/Write Operation":self.readwrite,"Value-in Volts(if Write)":self.readvalue,"Terminal":self.pwrterminal}
            print(self.saveentry)
            self.saveheader = ["Caption Input","Driver Catrgory","Driver sub-category","Read/Write Operation","Value-in Volts(if Write)","Terminal"]
            with open(self.savetexts_file_path,'a',newline='') as csvfile:
                writer = csv.DictWriter(csvfile,fieldnames=self.saveheader)
                fileEmpty = os.stat(self.savetexts_file_path).st_size == 0
                if fileEmpty:
                    writer.writeheader()
                writer.writerow(self.saveentrydict)
            with open(self.file_path,'a',newline='') as csvfile:
                writer = csv.writer(csvfile,dialect='excel')
                writer.writerow([self.savetext])
            self.childpopup.destroy()
            self.stepbtn = Button(self.masterframe1, text=self.savetext, relief=RAISED,bg="burlywood2")
            self.stepbtn.configure(command=partial(self.colorchange, self.stepbtn))
            self.stepbtn.grid(ipadx=10,sticky=EW)
            self.stepbtntexts.append(self.stepbtn["text"])
            self.step_buttons.append(self.stepbtn)
            self.runallbutton.config(state=NORMAL) 
            self.savesequence.config(state=NORMAL,command=self.saveseq)
            self.stepbtn.bind('<Double-Button-1>',lambda event:self.dubclick(event,self.stepbtn))

    """ Configuration of double clicking is done here, which opens up secondary window"""
    def dubclick(self,event,step):
        self.stepdubbtn = step
        if self.stepdubbtn == step:
            self.popup2()
        else:
            pass

    def colorchange(self,button):
        if self._step_selected == button:
            button.config(bg="burlywood2")
            self._step_selected = None
            self.runselbutton.config(state=DISABLED)
        else:
            for btn in self.step_buttons:
                btn.config(bg="burlywood2")
            button.config(bg="white")
            self._step_selected = button
            self.runselbutton.config(state=NORMAL)
        self.destroy(3)

    """ "Close" button of secondary window is configured here"""
    def closebutton(self):
        self.childpopup.destroy()
    
    """ "Run all" button in primary window is configured here"""
    def process_all(self):
        self.destroy(3)
        print("Processing all: ")
        self.stepbtn=[]
        self.timestr = time.strftime("%Y-%m-%d-%H%M%S")
        self.saving = self.currentpath+r"/outputs/"
        if not os.path.exists(self.saving):
                os.mkdir(self.saving)
        self.steps_processedfile = self.saving+r"steps_processed_"+self.hourstr+".csv"
        writer = csv.writer(open(self.steps_processedfile, 'a'),delimiter=",")
        for btn in self.step_buttons:
            btn.config(bg="white")
            btn.update()
            print(" Processing {}...".format(btn["text"]))
            time.sleep(5)
            btn.config(bg="burlywood2")
            writer.writerow(["Processed {}...".format(btn["text"])])
            self.stepbtn.append(btn["text"])
        self.msg=Label(self.masterframe3,text="Info: Running All completed !!")
        self.msg.grid(sticky=EW)
        messagebox.showinfo("info","Running All completed !!")
        
    """ "Run selected" button in primary window is configured here"""
    def process_selected(self):
        self.destroy(3)
        self.saving = self.currentpath+r"/outputs/"
        if not os.path.exists(self.saving):
                os.mkdir(self.saving)
        print("Processing selected: ")
        print("  Processing {}...".format(self._step_selected["text"]))
        self.eachstep_processedfile = self.saving+r"eachstep_processed_"+self.minstr+".csv"
        writer = csv.writer(open(self.eachstep_processedfile, 'a'),delimiter=",")
        writer.writerow(["Processed {}...".format(self._step_selected["text"])])
    
    def saveprompt(self):
        print("Cannot Save!! Enter details to record. ")
        messagebox.showwarning("warning","Cannot Save !! Enter details to record ! ")
            
if __name__ == "__main__":
    widget = Tk()
    MyApp(widget)
    widget.title("HAND CARRY LAB")
    widget.geometry('{}x{}+{}+{}'.format(700,650,0,0))
    widget.mainloop()
