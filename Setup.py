#written and tested with python3
#author: Bogdan Spuze
#company: Toolker
#date: 10.10.2019

#imports section
import logging
from configparser import ConfigParser
import shutil
import os
#from tkinter import *
#from tkinter import filedialog      
import tkinter as tk
import tkinter.filedialog as TKFileDiag
from tkinter import messagebox

#globals section
LOG_FILE_NAME = "setup_logs.txt"
LOG_LEVEL = logging.DEBUG
#logging.debug('This is a debug message')
#logging.info('This is an info message')
#logging.warning('This is a warning message')
#logging.error('This is an error message')
#logging.critical('This is a critical message')


SETUP_CONFIG_FILE_NAME = "config_setup.ini"
APP_CONFIG_FILE_NAME = "config.ini"

GENERIC_INFO_NOTE = "INFO: Move mouse over fields to get extra info."

#inits & config
logging.basicConfig(filename=LOG_FILE_NAME, level=LOG_LEVEL, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

config = ConfigParser()
config.read(SETUP_CONFIG_FILE_NAME)
app_config = ConfigParser()
if os.path.isfile(APP_CONFIG_FILE_NAME):
    app_config.read(APP_CONFIG_FILE_NAME)

scroll_count = 0

#def callback_file():
#    name=filedialog.askopenfilename(initialdir = ".",title = "choose your file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
#    return name


class CreateToolTip(object):
    '''
    create a tooltip for a given widget
    '''
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)
    def enter(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 35
        y += self.widget.winfo_rooty() + 30
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background='yellow', relief='solid', borderwidth=1,
                       font=("times", "10", "normal"))
        label.pack(ipadx=1)
    def close(self, event=None):
        if self.tw:
            self.tw.destroy()



class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)

        self.canvas = tk.Canvas(self, borderwidth=0)          #place canvas on self
        self.viewPort = tk.Frame(self.canvas)                    #place a frame on the canvas, this frame will hold the child widgets 
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas.create_window((0,0), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        
        

    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))  
    
    def _on_mousewheel(self, event):
        global scroll_count
        def delta(event):
            if event.num == 5 or event.delta < 0:
                return 2 
            return -2 

        scroll_count += delta(event)
        self.canvas.yview_scroll(scroll_count, "units")



class GenericFolderPath(tk.Frame):
    def callback_folder_path(self):
        path = TKFileDiag.askdirectory(title="Please select a directory")
        self.text_field.delete(0, tk.END)
        self.text_field.insert(0, path)

    def __init__(self, parent, label, text_field_value, label_note):
        super().__init__(parent)
        self.pack(fill=tk.X)
        self.parent = parent

        label_note = "INFO: "+label_note
        
        frame = tk.Frame(self)
        frame.pack(fill=tk.X, side=tk.TOP, expand=True, padx=5, pady=10)

        frame2 = tk.Frame(self)
        frame2.pack(in_=frame, fill=tk.X, side=tk.TOP, expand=True, padx=5, pady=2)
        
        self.label = tk.Label(self, text=label, width=40, anchor='w')
        self.label.pack(in_=frame2, side=tk.LEFT, padx=5, pady=5)
        
        self.text_field=tk.Entry(width=50)
        self.text_field.delete(0, tk.END)
        self.text_field.insert(0, text_field_value)

        self.text_field.pack(in_=frame2, side=tk.LEFT, fill=tk.X, padx=5)

        text_filed_tooltip = CreateToolTip(self.text_field, label_note)

        self.button = tk.Button(text="Browse", command=self.callback_folder_path)
        self.button.pack(in_=frame2, side=tk.LEFT, padx=5, pady=5)



class GenericFilePath(tk.Frame):
    def callback_file_path(self):
        if self.filter != "*":
            path = TKFileDiag.askopenfilename(title="Please select a " + self.filter +" file")
        else:
            path = TKFileDiag.askopenfilename(title="Please select a file")
        self.text_field.delete(0, tk.END)
        self.text_field.insert(0, path)

    def __init__(self, parent, label, text_field_value, label_note, filter_by):
        super().__init__(parent)
        self.pack(fill=tk.X)

        self.filter=filter_by

        label_note = "INFO: "+label_note

        frame = tk.Frame(self)
        frame.pack(fill=tk.X, side=tk.TOP, expand=True, padx=5, pady=10)

        frame2 = tk.Frame(self)
        frame2.pack(in_=frame, fill=tk.X, side=tk.TOP, expand=True, padx=5, pady=2)
        
        self.label = tk.Label(self, text=label, width=40 , anchor='w')
        self.label.pack(in_=frame2, side=tk.LEFT, padx=5, pady=5)
        
        self.text_field=tk.Entry(width=50)
        self.text_field.delete(0, tk.END)
        self.text_field.insert(0, text_field_value)

        self.text_field.pack(in_=frame2, side=tk.LEFT, fill=tk.X, padx=5)

        text_filed_tooltip = CreateToolTip(self.text_field, label_note)

        self.button = tk.Button(text="Browse", command=self.callback_file_path)
        self.button.pack(in_=frame2, side=tk.LEFT, padx=5, pady=5)


class GenericTextBox(tk.Frame):
    def __init__(self, parent, label, text_field_value, label_note):
        super().__init__(parent)
        self.pack(fill=tk.X)

        frame = tk.Frame(self)
        frame.pack(fill=tk.X, side=tk.TOP, expand=True, padx=5, pady=10)
        
        label_note = "INFO: "+label_note
        
        frame2 = tk.Frame(self)
        frame2.pack(in_=frame, fill=tk.X, side=tk.TOP, expand=True, padx=5, pady=2)
        
        self.label = tk.Label(self, text=label, width=40, anchor='w')
        self.label.pack(in_=frame2, side=tk.LEFT , padx=5, pady=5)

        
        self.text_field=tk.Entry(width=30)
        self.text_field.delete(0, tk.END)
        self.text_field.insert(0, text_field_value)

        self.text_field.pack(in_=frame2, side=tk.LEFT, fill=tk.X, padx=5)

        text_filed_tooltip = CreateToolTip(self.text_field, label_note)



class App(tk.Tk):
    def write_app_config(self, config):
        file_app_config = open(APP_CONFIG_FILE_NAME, 'w')
        config.write(file_app_config)
        file_app_config.close()

    def print_callback(self):
        new_app_config = ConfigParser()
        i=0
        for each_section in config.sections():
            new_app_config.add_section(each_section)
            for (each_key, each_val) in config.items(each_section):
                label = self.entries[i].label.cget("text")
                value = self.entries[i].text_field.get()
                each_key_well_put=each_key.replace("_"," ").capitalize()
                if each_section in label and each_key_well_put in label:
                    new_app_config.set(each_section,each_key,value)
                else:
                    messagebox.showerror("Config Save Error", "Config values don't match. Please delete config.ini and retry.")
                i+=1
        self.write_app_config(new_app_config)
        messagebox.showinfo("Config Saved", "Configuration file saved successfully")
    
    def read_config_create_ui(self, parent):
        i=0
        for each_section in config.sections(): 
            for (each_key, each_val) in config.items(each_section):
                current_app_config_value = ""
                try:
                    current_app_config_value = app_config.get(each_section,each_key)
                except:
                    current_app_config_value = ""
                
                object_label_well_put=each_section+": "+each_key.replace("_"," ").capitalize()

                self.config_values.append([each_section+"_"+each_key,current_app_config_value])
    
                values = each_val.split("/./")
                if "file_path" in values[0]:
                    filter_by="*"
                    if len(values[2])>0:
                        filter_by=values[2]
                    self.entries.append(GenericFilePath(parent, object_label_well_put, current_app_config_value, values[1], filter_by))
                if "folder_path" in values[0]:
                    self.entries.append(GenericFolderPath(parent, object_label_well_put, current_app_config_value, values[1]))
                if "text_box" in values[0]:
                    self.entries.append(GenericTextBox(parent, object_label_well_put, current_app_config_value, values[1]))
                i+=1    

    def __init__(self):
        super().__init__()

        self.title("Config App")
        self.geometry("1200x900")

        #dummy_frame = tk.Frame(self, width=1800, height=1600)
        #dummy_frame.pack(side="top", fill="both", expand=True)
        
        frame = ScrollFrame(self)
        
        self.mainFraim = frame.viewPort 
        
        self.entries = []
        self.config_values=[]
        #call the fields to add

        self.read_config_create_ui(self.mainFraim)

        print_button = tk.Button(text="Save Config", command=self.print_callback)
        print_button.pack(in_=self.mainFraim, side=tk.LEFT, padx=5, pady=5)

        close_button = tk.Button(text="Close", command=self.destroy)
        close_button.pack(in_=self.mainFraim, side=tk.LEFT, padx=5, pady=5)

        frame.pack(side="top", fill="both", expand=True)
    




if __name__ == "__main__":
    App().mainloop()