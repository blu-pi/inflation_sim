import pickle
from tkinter import filedialog, messagebox
from typing import Union

from market.economy import Economy

from tkinter import *
from tkinter.ttk import *
import os

from typing import TYPE_CHECKING

if TYPE_CHECKING:
   from market.input.sim_args import ArgDict

#The original core code in this file is adapted from https://gist.github.com/cowlicks/21dd1b1938a9474f56cf
#Obviously, many additions and modifications were made.

class InfoHandle:

    infoDict = {}

    @staticmethod
    def readInfoFile() -> None:
        print(os.getcwd())
        info_file = open("util/arg_info.txt")
        section_title = None
        for line in info_file:
            if "#section" in line:
                section_title = line.split()[-1]
                InfoHandle.infoDict.update({section_title : {}})
            elif "#argument" in line:
                temp = line.replace("#argument","").strip().split(":")
                arg_name = temp[0]
                arg_desc = temp[1]
                InfoHandle.infoDict[section_title].update({arg_name : arg_desc})
        info_file.close()
    
    @staticmethod
    def showInfo(section_name, arg_name):
        arg_desc = InfoHandle.infoDict[section_name][arg_name]
        title = f"{section_name}, {arg_name} description"
        messagebox.showinfo(title=title, message=arg_desc)

class entry_field:
    def __init__(self, parent, colName, default, section_name):

        self.default = default
        self.restriction = type(default)
        self.colName = colName

        self.frame = Frame(parent)
        self.frame.pack(side = TOP)
        
        self.label = Label(self.frame, text = colName)
        self.label.configure(width = 20)
        self.label.pack(side = LEFT)

        self.entry = Entry(self.frame)
        self.entry.pack(side = LEFT)

        if self.restriction == int:
            self.value = lambda : self.getIntVal()
        elif self.restriction == float:
            self.value = lambda : self.entry.getdouble()
        else:
            self.value = lambda : self.entry.get() #unrestricted string

        self.holdButton = Button(self.frame, command = lambda:InfoHandle.showInfo(section_name,colName))
        self.holdButton.configure(text = 'Info')
        self.holdButton.pack(side = RIGHT)

    def getIntVal(self) -> Union[int,None]: #safe way to get int from entry box
        try:
            val = int(self.entry.get())
        except ValueError:
            val = None
        return val

class drop_down:
    def __init__(self, parent, colName, default_value, section_name) -> None:
        self.restriction = default_value

        self.frame = Frame(parent)
        self.frame.pack(side = TOP)
        
        self.label = Label(self.frame, text = colName)
        self.label.configure(width = 20)
        self.label.pack(side = LEFT)

        self.variable = StringVar(parent)
        self.variable.set(self.restriction[0]) # default value

        self.option_menu = OptionMenu(self.frame, self.variable, self.restriction[0], *self.restriction)
        self.option_menu.pack(side = LEFT)
        self.value = lambda : self.variable.get()

        self.holdButton = Button(self.frame, command = lambda:InfoHandle.showInfo(section_name,colName))
        self.holdButton.configure(text = 'Info')
        self.holdButton.pack(side = RIGHT)

class tick_box:
    def __init__(self, parent, colName, section_name) -> None:
        self.frame = Frame(parent)
        self.frame.pack(side = TOP)
        
        self.label = Label(self.frame, text = colName)
        self.label.configure(width = 20)
        self.label.pack(side = LEFT)

        var = BooleanVar()
        self.check_button = Checkbutton(self.frame, variable=var, onvalue=True, offvalue=False)
        self.check_button.pack(side = LEFT)
        self.value = lambda : var.get()

        self.holdButton = Button(self.frame, command = lambda:InfoHandle.showInfo(section_name,colName))
        self.holdButton.configure(text = 'Info')
        self.holdButton.pack(side = RIGHT)

class App:

    user_input = {} #ugly but honestly tkinter is ugly so idc >=/

    def __init__(self, parent, args : list[tuple]) -> None:
        parent.winfo_toplevel().title("Parameter Input")
        InfoHandle.readInfoFile()
        self.parent = parent
        self.sections = args.copy()
        self.default_args = args
        i = 0
        for section in self.sections:
            section_str = section[0]
            section_data = section[1]
            self.sections[i] = (section_str, Section(self.parent, section_data, section_str))
            i += 1

    
        # Next button.
        self.nextButton = Button(parent, command = self.getAllInput)
        self.nextButton.configure(text = 'Start Simulation!')
        self.nextButton.pack(side = LEFT)

        self.loadButton = Button(parent, command = self.makeLoadScreen)
        self.loadButton.configure(text = 'Load simulation config')
        self.loadButton.pack(side = BOTTOM)
    
    def makeLoadScreen(self) -> None:
        """Not implemented, WIP"""
        #TODO adapt to new context and implement
        folder_selected = filedialog.askdirectory()
        if folder_selected != "":
            fileObj = open(folder_selected + '/args.obj', 'rb')
            args = pickle.load(fileObj)
            fileObj.close()
            args["from_file"] = True
            sim = Economy(**args)
        #TODO else case? 

    def initSim(self) -> None:
        #close input UI?
        for args in self.default_args:
            key : str = args[0]
            default_vals : ArgDict = args[1]
            default_vals.joinConts(App.user_input[key])
            final_vals = default_vals #for clarity
            App.user_input[key] = final_vals
        sim = Economy(App.user_input)
    
    def getAllInput(self) -> list:
        for section in self.sections:
            section_str = section[0]
            section_obj = section[1]
            assert(isinstance(section_obj, Section))
            App.user_input.update({section_str : section_obj.nextItem()}) 
        self.initSim()


class Section:
    def __init__(self, parent, columns, title):
        self.myParent = parent
        self.columns = columns
        self.title = title
        #self.colNames = get_colNames(COLUMNS)

        self.Container = Frame(parent)
        self.Container.pack()
        
        self.entrycont = Frame(self.Container)
        self.entrycont.pack(side = TOP)

        self.title_label = Label(self.entrycont,text=self.title,font=('Arial', 18))
        self.title_label.pack()

        self.make_buttons(self.myParent, self.columns)

        # Next/esc container
        self.next_esc = Frame(self.Container)
        self.next_esc.pack(side = BOTTOM)

        # Escape the window.
        self.Container.bind('<Escape>', self.quit)

    def quit(self, event):
        self.myParent.destroy()
        print('herp')

    # Make data entry buttons.
    def make_buttons(self, parent, column_names):
        self.factory = {}
        column_names = column_names.conts
        if isinstance(column_names,dict):
            #new functionality
            for key in column_names:
                colName = key
                default_value = column_names[key]
                self.factory[colName] = self.gen_entry_obj(colName, default_value)
        else:
            print("critical error") #can't really happen idk TODO remove after debug

    def gen_entry_obj(self, colName, default_value):
        # if ".." in entry_restrictions:
        #     return entry_field(self.entrycont, colName, entry_restrictions)
        # if entry_restrictions == "STRING":
        #     return entry_field(self.entrycont, colName) #unrestricted
        # if entry_restrictions == [True,False]:
        #     return tick_box(self.entrycont, colName)
        # return drop_down(self.entrycont, colName, entry_restrictions)
        default_type = type(default_value)
        if default_type in [int, float, str]:
            return entry_field(self.entrycont, colName, default_value, self.title)
        if default_type == bool:
            return tick_box(self.entrycont, colName, self.title)
        if default_type == list:
            return drop_down(self.entrycont, colName, default_value, self.title)

    # Next button handeler.
    def nextItem(self) -> dict:
        # get data from buttons
        data = {}
        for colName in self.columns.conts:
            #data.append(self.factory[colName].value())
            val = self.factory[colName].value()
            if val not in ["",None]: #don't pass params that aren't needed.
                data.update({colName : val})
        return data