import pickle
from tkinter import filedialog
from typing import Union

from market.economy import Economy
from tkinter import *
from tkinter.ttk import *

#The original core code in this file is adapted from https://gist.github.com/cowlicks/21dd1b1938a9474f56cf
#Obviously, many additions and modifications were made.

#TODO totally broken right now. Needs to be fully adapted for current project.

class info_window:

    def __init__(self, text) -> None:
        pass #TODO complete (low priority)

class entry_field:
    def __init__(self, parent, colName, default = None):

        self.default = default
        self.restriction = type(default)

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

        self.holdButton = Button(self.frame, command = self.hold)
        self.holdButton.configure(text = 'Info')
        self.holdButton.pack(side = RIGHT)

    def getIntVal(self) -> Union[int,None]: #safe way to get int from entry box
        try:
            val = int(self.entry.get())
        except ValueError:
            val = None
        return val

    def hold(self):
        print('derp')

class drop_down:
    def __init__(self, parent, colName, default_value) -> None:
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

        self.holdButton = Button(self.frame, command = self.hold)
        self.holdButton.configure(text = 'Info')
        self.holdButton.pack(side = RIGHT)
    
    def hold(self):
        print('derp') 

class tick_box:
    def __init__(self, parent, colName) -> None:
        self.frame = Frame(parent)
        self.frame.pack(side = TOP)
        
        self.label = Label(self.frame, text = colName)
        self.label.configure(width = 20)
        self.label.pack(side = LEFT)

        var = BooleanVar()
        self.check_button = Checkbutton(self.frame, variable=var, onvalue=True, offvalue=False)
        self.check_button.pack(side = LEFT)
        self.value = lambda : var.get()

        self.holdButton = Button(self.frame, command = self.hold)
        self.holdButton.configure(text = 'Info')
        self.holdButton.pack(side = RIGHT)
    
    def hold(self):
        print('derp') 

class App:

    global_output = {} #ugly but honestly tkinter is ugly so idc >=/

    def __init__(self, parent, args : list[tuple]) -> None:
        parent.winfo_toplevel().title("Parameter Input")
        self.parent = parent
        self.sections = args
        #self.sections_str = sections_str
        #self.sections = {}
        #self.columns = columns

        # i = 0
        # for column in self.columns:
        #     self.sections[sections_str[i]] = Section(self.parent, column, sections_str[i])
        #     i += 1
        print(self.sections)
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
        #TODO passing parameters needs cleanup + fix. Make standardised config class mayhaps?
        sim = Economy(**App.global_output)
    
    def getAllInput(self) -> list:
        for section in self.sections:
            section_str = section[0]
            section_obj = section[1]
            assert(isinstance(section_obj, Section))
            App.global_output.update({section_str : section_obj.nextItem()}) 
        self.initSim()


class Section:
    def __init__(self, parent, columns, title):
        self.myParent = parent
        self.columns = columns
        self.title = title + " arguments:"
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
        print(column_names)
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
        print(f"val: {default_value}, type: {default_type}")
        if default_type in [int, float, str]:
            return entry_field(self.entrycont, colName, default_value)
        if default_type == bool:
            return tick_box(self.entrycont, colName)
        if default_type == list:
            return drop_down(self.entrycont, colName, default_value)

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