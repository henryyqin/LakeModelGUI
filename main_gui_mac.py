
import os
import pathlib
os.chdir(pathlib.Path(__file__).parent.absolute()) # changes working directory to the current file path
print(pathlib.Path().absolute())

import sys

#tkinter imports
import tkinter as tk
from tkinter import Canvas, Image, PhotoImage, font
import tkinter.filedialog as fd
from tkinter import ttk

# Sensor Model Scripts
import sensor_carbonate as carb
import sensor_gdgt as gdgt
import sensor_leafwax as leafwax

#Archive Model Scripts
import lake_archive_bioturb as bio
import lake_archive_compact as comp

# Data Analytics
import numpy as np
from numpy import genfromtxt
import pandas as pd
import matplotlib

# Imports for plotting
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import datetime as dt
from matplotlib import dates as mdates
from statistics import mean
plt.style.use('seaborn-whitegrid')
matplotlib.use('TkAgg')  # Necessary for MacOS Mojave


# Imports for Observation Model
from rpy2.robjects import FloatVector
from rpy2.robjects.vectors import StrVector
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()


#Miscellaneous imports
import os
#os.chdir("/Users/henryqin/Desktop/LakeModelGUI/dist/main_gui_mac") #pyinstaller test
print(os.getcwd())
from os.path import basename
import webbrowser
import copy
import subprocess
import multiprocessing
from subprocess import PIPE, Popen
from tkinter.ttk import Label
from PIL import Image, ImageTk
from tkinter.filedialog import asksaveasfilename

#tkinter imports
import tkinter as tk
from tkinter import Canvas, Image, PhotoImage, font
import tkinter.filedialog as fd
from tkinter import ttk

from tkinter.ttk import Label
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#plt.style.use('seaborn-whitegrid')
matplotlib.use('TkAgg')  # Necessary for MacOS Mojave
import sys

#===========GENERAL FUNCTIONS========================================
def callback(url):
    webbrowser.open_new(url)

# def download_graph(time, proxy, filetype): #self.days, self.gdgt_proxy, '.png'
#         df = pd.DataFrame({"Time": time, "Pseudoproxy": proxy})
#         export_file_path = fd.asksaveasfilename(defaultextension=filetype) #ex: .csv or .png
#         df.to_csv(export_file_path, index=None)

def check_float(str):
    """
    Returns True if the input string represents a floating point number
    Input:
    - str: a string that should represent a floating-point number
    """
    try:
        float(str)
        return True
    except:
        return False

def initialize_global_variables():
    """
    Reads global_vars.txt to initialize global variables with pre-existing values
    from previous runs of the GUI
    """
    with open("global_vars.txt", "r") as start:
        lines = start.readlines()
        global INPUT
        INPUT = lines[0]
        global START_YEAR
        START_YEAR = int(lines[1])

def write_to_file(file, data):
    """
    Writes data to a file
    Inputs
    - file: the file that is overwritten
    - data: the data which must be contained by the file
    """
    file.seek(0)
    file.truncate()
    file.writelines(data)
    file.close()

def get_output_data(time, data, column, filename):
    """
    Retrieves data from surf.dat from years where lake is at equilibrium
    Inputs
    - time: an empty array which is populated with day #'s
    - data: an empty array which is populated with a certain column of data from surf.dat
    - column: the specific column of data in surf.dat which should populate "data"
    - filename: the file which contains the desired data
    """
    with open(filename) as file:
        lines = file.readlines()
        cur_row = lines[len(lines) - 1].split()
        next_row = lines[len(lines) - 2].split()
        i = 2
        while int(float(cur_row[0])) > int(float(next_row[0])):
            data.insert(0, float(cur_row[column]))
            time.insert(0, int(float(cur_row[0])))
            cur_row = copy.copy(next_row)
            i += 1
            next_row = lines[len(lines) - i].split()
        data.insert(0, float(cur_row[column]))
        time.insert(0, int(float(cur_row[0])))

def uploadTxt(type, frame, file_label, sample=None, file_types=None):
    """
    Allows the user to upload sample data or data of their own choice
    Inputs:
    - type: indicates where the file is sample data or user-uploaded
    - frame: the frame in which the upload text feature is located
    - file_label: an object within the frame which indicates the filename
    - sample: the name of the sample file
    - file_types: the type of the file to be uploaded
    """
    if type == "sample":
        # Upload example file
        file_label.configure(text=basename(sample))
        frame.txtfilename = sample
    else:
        # Open the file choosen by the user
        frame.txtfilename = fd.askopenfilename(
            filetypes=file_types)
        file_label.configure(text=basename(frame.txtfilename))

def plot_setup(frame, axes, figure, title, x_axis, y_axis):
    """
    Creates a blank plot on which a graph can be displayed
    Inputs
    - frame: the page in the GUI where the plot is located
    - axes: the axes which allow plotting capabilities
    - figure: the figure on which the plot is located
    - title: the title displayed on the plot
    - x_axis: the x-axis label
    - y_axis: the y-axis label
    """
    canvas = FigureCanvasTkAgg(figure, frame)
    canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=9, sticky="e")
  
    axes.set_title(title, fontsize=12)
    axes.set_xlabel(x_axis)
    axes.set_ylabel(y_axis)

def plot_draw(frame, axes, figure, title, x_axis, y_axis, x_data, y_data, plot_type, colors, widths, labels,
              error_lines=None, overlay=False):
    """
    Creates plot(s) based on input parameters
    Inputs
    - frame: the page in the GUI where the plot is located
    - axes: the axes which allow plotting capabilities
    - figure: the figure on which the plot is located
    - title: the title displayed on the plot
    - x_axis: the x-axis label
    - y_axis: the y-axis label
    - x_data: the set of x-coordinates
    - y_data: an array of each set of y-coordinates
    - plot_type: a string containing the type of plot(s) desired
    - colors: the colors of the lines in the plot
    - widths: the width of the lines in the plot
    - labels: the labels for the legend
    - error_lines: an array with 2 values that demarcates the CI, None if no CI is necessary for plot
    - overlay: indicates whether this plot should be overlaid on pre-existing plots, False by default
    """
    canvas = FigureCanvasTkAgg(figure, frame)
    canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
    canvas.get_tk_widget().configure(highlightcolor='white smoke', highlightthickness=40)
    if not overlay:
        plt.cla()
    axes.set_title(title)
    axes.set_xlabel(x_axis)
    axes.set_ylabel(y_axis)
    i = 0
    for line in y_data:
        if "normal" in plot_type:
            if "monthly" in plot_type:
                date_format = mdates.DateFormatter('%b,%Y')
                axes.xaxis.set_major_formatter(date_format)
                axes.plot_date(x_data, line, linestyle="solid", color=colors[i], linewidth=widths[i], label=labels[i],
                               marker=None)
            elif "month-only" in plot_type:
                date_format = mdates.DateFormatter('%b')
                axes.xaxis.set_major_formatter(date_format)
                axes.plot_date(x_data, line, linestyle="solid", color=colors[i], linewidth=widths[i], label=labels[i])
            elif "non-month" in plot_type:
                axes.plot(x_data, line, linestyle="solid", color=colors[i], linewidth=widths[i], label=labels[i])
            else:
                axes.plot_date(x_data, line, linestyle="solid", color=colors[i], linewidth=widths[i], label=labels[i])
        if "scatter" in plot_type:
            axes.scatter(x_data, line, color=colors[i])
            pass
        i += 1
    if error_lines != None:
        axes.fill_between(x_data, error_lines[0], error_lines[1], facecolor='grey', edgecolor='none', alpha=0.20)
    axes.legend()


def convert_to_monthly(time, start=None):
    """
    Converts timeseries x-axis into monthly units with proper labels
    Input:
    - time: an array of day numbers (15, 45, 75, etc.)
    """
    start_date = None
    if start==None:
        global START_YEAR
        start_date = dt.date(START_YEAR, 1, 1)
    else:
        start_date = dt.date(start, 1, 1)
    dates = []
    for day in time:
        new_date = start_date + dt.timedelta(days=day-1)
        dates.append(new_date)
    return dates

def convert_to_annual(data, start=None):
    """
    Converts timeseries data into annually averaged data with proper axis labels
    Input:
    - data: the y-axis of the timeseries data
    """
    start_date = None
    if start==None:
        global START_YEAR
        start_date = dt.date(START_YEAR-1, 7, 2)
    else:
        start_date = dt.date(start - 1, 7, 2)
    all_year_avgs = []
    for column in data:
        years = []
        year_data = []
        year_avgs = []
        for i in range(len(column)):
            year_data.append(column[i])
            if (i + 1) % 12 == 0:
                year_avgs.append(mean(year_data))
                years.append(start_date+dt.timedelta(days=365*((i+1)/12)))
                year_data.clear()
        all_year_avgs.append(year_avgs)
    return years, all_year_avgs

#================GLOBAL VARIABLES==================================================
TITLE_FONT = ("Courier New", 35) #43
LARGE_FONT = ("Courier New", 22) #26
MED_FONT = ("Consolas", 12) #12
f = ("Consolas", 11) #12
f_slant = ("Consolas", 12, "italic") #12
START_YEAR = None
INPUT = None
PARAMETERS = []
initialize_global_variables()

"""
Creates a GUI object
"""
class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title_font = TITLE_FONT
        # title of window
        self.title("Lake Model GUI")
        self.geometry("2500x1600")
        #self.minsize(600, 300)
        # self.wm_iconbitmap('icon.ico')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others

        self.frames = {}
        self.pages = [StartPage, PageEnvModel, PageEnvTimeSeries, PageEnvSeasonalCycle,
                      PageCarbonate, PageGDGT, PageLeafwax, PageObservation, PageBioturbation,
                      PageCompaction]
        for F in self.pages:
            page_name = F.__name__
            frame = F(parent=self)
            self.frames[page_name] = frame

        self.show_frame(["StartPage", "PageEnvModel", "PageEnvTimeSeries", "PageEnvSeasonalCycle",
                         "PageCarbonate","PageGDGT","PageLeafwax", "PageObservation", "PageBioturbation",
                         "PageCompaction"], "StartPage")

        self.protocol('WM_DELETE_WINDOW', self.close_app)

    def show_frame(self, old_pages, new_page):
        '''Show a frame for the given page name'''
        for old_page in old_pages:
            old = self.frames[old_page]
            old.destroy()
            self.frames.pop(old_page)

        for F in self.pages:
            if F.__name__ == new_page:
                new = F(parent=self)
                self.frames[new_page] = new

    def close_app(self):
        sys.exit()

"""
Home/Title Page
"""
class StartPage(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(  bg='white',
                scrollregion=canvas.bbox("all")
            )
        )
        x0 = self.scrollable_frame.winfo_screenwidth() / 2
        y0 = self.scrollable_frame.winfo_screenheight() / 2
        canvas.create_window((x0,y0), window=self.scrollable_frame, anchor="center")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        label = tk.Label(self.scrollable_frame, bg="white smoke",
                        text="PRYSMv2.0: Lake PSM", 
                        fg= "black", 
                        font= TITLE_FONT)
        label.pack(pady=10, padx=10)

        #background image
        photo=PhotoImage(file="resize_490.png")
        label = Label(self.scrollable_frame,image = photo, anchor=tk.CENTER)
        label.image = photo # keep a reference!
        label.pack(pady=2, padx=10)


        lake_label = tk.Label(self.scrollable_frame, bg="white smoke", 
                            text="Aerial view of Lake Tanganyika",
                            font=f_slant)
        lake_label.pack(pady=(0, 10), padx=10)


        descrip = tk.Label(self.scrollable_frame, bg="white smoke", 
                            text="A graphical user interface for Climate Proxy System Modeling Tools in Python",
                            font=MED_FONT, 
                            anchor=tk.CENTER,
                            justify="center")
        descrip.pack(pady=0, padx=10)


        authors = tk.Label(self.scrollable_frame, bg="white smoke", 
                            text="By: Henry Qin, Xueyan Mu, Vinay Tummarakota, and Sylvia Dee",
                            font=MED_FONT, 
                            justify="center")
        authors.pack(pady=3, padx=10)


        website = tk.Label(self.scrollable_frame, bg="white smoke", 
                            text="Getting Started Guide", 
                            fg="SlateBlue2", 
                            cursor="hand2", 
                            font=MED_FONT, 
                            justify="center")
        website.pack(pady=0, padx=10)
        website.bind("<Button-1>", lambda e: callback(
            "https://docs.google.com/document/d/1vMu0Oq28dl5XCFVTw6FQYwND3VMWl8S2lWzDw1RC5oY/edit?usp=sharing"))


        paper = tk.Label(self.scrollable_frame, bg="white smoke", 
                        text="Original Paper, 2018", 
                        fg="SlateBlue2", 
                        cursor="hand2", 
                        font=MED_FONT)
        paper.pack(pady=0, padx=10)
        paper.bind("<Button-2>", lambda e: callback(
            "https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2018PA003413"))


        github = tk.Label(self.scrollable_frame, bg="white smoke", 
                        text="Github", 
                        fg="SlateBlue2", 
                        cursor="hand2", 
                        font=MED_FONT)
        github.pack(pady=(0, 5), padx=10)
        github.bind("<Button-1>", lambda e: callback("https://github.com/henryyqin/LakeModelGUI"))

        buttonText = ["Run Lake Environment Model", "Plot Environment Time Series", "Plot Environment Seasonal Cycle",
                      "Run Carbonate Model", "Run GDGT Model", "Run Leafwax Model", "Run Observation Model",
                      "Run Bioturbation Model", "Run Compaction Model"]

        pageNames = ["PageEnvModel", "PageEnvTimeSeries", "PageEnvSeasonalCycle",
                     "PageCarbonate", "PageGDGT", "PageLeafwax", "PageObservation", "PageBioturbation",
                     "PageCompaction"]

        for i in range(len(buttonText)):
            page = pageNames[i]
            button = tk.Button(self.scrollable_frame, text=buttonText[i], font=f,
                               command=lambda page=page: self.parent.show_frame(["StartPage"], page))
            button.pack(ipadx=37, ipady=3, pady=(2,3))

"""
Page to run the environment model
"""
class PageEnvModel(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self, borderwidth=0, bg="white smoke")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        s = ttk.Style()
        s.configure('new.TFrame', background='white smoke')
        self.scrollable_frame = ttk.Frame(canvas, style='new.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        rowIdx = 1

        # Title
        label = tk.Label(self.scrollable_frame, text="Run Lake Environment Model", font=LARGE_FONT, bg="white smoke")
        label.grid(sticky="W")

        rowIdx += 1

        # Instructions for uploading .txt and .inc files
        tk.Label(self.scrollable_frame, bg="white smoke", 
                 text="1) Upload a text file to provide input data for the lake model\n2) Enter lake-specific and simulation-specific parameters\n3) If parameters are left empty, default parameters for Lake Tanganyika will be used",
                 font=f, justify="left"
                 ).grid(row=rowIdx, rowspan=1, pady=12, sticky="W")
        rowIdx += 3

        # Allows user to upload .txt data.
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Click to upload your .txt file:", font=f).grid(
            row=rowIdx, pady=1, sticky="W")
        graphButton = tk.Button(self.scrollable_frame, text="Upload .txt File", font=f,
                                command=self.uploadTxt)
        graphButton.grid(row=rowIdx, padx=200,
                         ipadx=10, sticky="W")
        rowIdx += 1

        # Shows the name of the current uploaded file, if any.
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Current File Uploaded:", font=f).grid(
            row=rowIdx, sticky="W")
        self.currentTxtFileLabel = tk.Label(self.scrollable_frame, bg="white smoke",  text="No file", font=f)
        self.currentTxtFileLabel.grid(
            row=rowIdx,columnspan=2, padx=200, pady=(1, 12), sticky="W")
        rowIdx += 1

        # Autofill buttons
        malawiButton = tk.Button(self.scrollable_frame, text="Autofill Malawi Parameters", font=f,
                                 command=lambda: self.fill("Malawi", param_containers))
        malawiButton.grid(row=rowIdx, ipadx=10, ipady=3, sticky="W")

        tanganyikaButton = tk.Button(self.scrollable_frame, text="Autofill Tanganyika Parameters", font=f,
                                     command=lambda: self.fill("Tanganyika", param_containers))
        tanganyikaButton.grid(row=rowIdx, padx=200, ipadx=10, ipady=3, sticky="W")

        refillButton = tk.Button(self.scrollable_frame, text="Autofill Previously Saved Parameters", font=f,
                                 command=lambda: self.fill("Refill", param_containers))
        refillButton.grid(row=rowIdx, padx=430, ipadx=10, ipady=3, sticky="W")

        clearButton = tk.Button(self.scrollable_frame, text="Clear Parameters", font=f,
                                command=lambda: self.fill("Clear", param_containers))
        clearButton.grid(row=rowIdx, padx=700, ipadx=10, ipady=3, sticky="W")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", fg="blue", font=MED_FONT, bg="azure", 
                               command=lambda: self.parent.show_frame(["PageEnvModel"], "StartPage"))
        # previousPageB.pack(anchor = "w", side = "bottom")
        homeButton.grid(row=rowIdx, padx=900, ipadx=10, ipady=3, sticky="W")
        rowIdx += 3

        # Entries for .inc file
        parameters = ["Obliquity", "Latitude (Negative For South)", "Longitude (Negative For West)",
                      "Local Time Relative To Gmt In Hours", "Depth Of Lake At Sill In Meters",
                      "Elevation Of Basin Bottom In Meters", "Area Of Catchment+Lake In Hectares",
                      "Neutral Drag Coefficient", "Shortwave Extinction Coefficient (1/M)",
                      "Fraction Of Advected Air Over Lake", "Albedo Of Melting Snow", "Albedo Of Non-Melting Snow",
                      "Prescribed Depth In Meters", "Prescribed Salinity In Ppt", "\u0394¹⁸o Of Air Above Lake",
                      "\u0394d Of Air Above Lake", "Temperature To Initialize Lake At In INIT_LAKE Subroutine",
                      "Dd To Initialize Lake At In INIT_LAKE Subroutine",
                      "\u0394¹⁸o To Initialize Lake At In INIT_LAKE Subroutine", "Number Of Years For Spinup",
                      "Check Mark For Explict Boundary Layer Computations;\nPresently Only For Sigma Coord Climate Models",
                      "Sigma Level For Boundary Flag", "Check Mark For Variable Lake Depth",
                      "Check Mark For Variable Ice Cover",
                      "Check Mark For Variable Salinity", "Check Mark For Variable \u0394¹⁸o",
                      "Check Mark For Variable \u0394d",
                      "Height Of Met Inputs", "Start Year"]
        param_values = []
        param_containers = []
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Lake-Specific Parameters", font=LARGE_FONT).grid(
            row=rowIdx, pady=10, sticky="W")
        tk.Label(self.scrollable_frame, bg="white smoke", text="Simulation-Specific Parameters", font=LARGE_FONT).grid(
            row=rowIdx, pady=10, padx=600, sticky="W")
        rowIdx += 1

        # List entries for lake-specific parameters
        for i in range(rowIdx, rowIdx + 19):
            tk.Label(self.scrollable_frame, bg="white smoke", text=parameters[i - rowIdx], font=f).grid(
                row=i, column=0, sticky="W")
            p = tk.Entry(self.scrollable_frame, bd=1)
            p.grid(row=i, column=0, ipady=1, ipadx=0, padx=350, sticky="W")
            
            param_values.append(p)
            param_containers.append(p)

        # List entries for simulation-specific parameters
        for i in range(rowIdx + 19, rowIdx + 29):
            tk.Label(self.scrollable_frame, bg="white smoke",  text=parameters[i - rowIdx], font=f).grid(
                row=i - 19, column=0, padx=600, sticky="W")
            if i in [rowIdx + 19, rowIdx + 21, rowIdx + 27, rowIdx + 28]:
                p = tk.Entry(self.scrollable_frame, bd=1)
                p.grid(row=i - 19, column=0, padx=950, sticky="W")
                param_containers.append(p)
            else:
                p = tk.IntVar()
                c = tk.Checkbutton(self.scrollable_frame, variable=p)
                c.grid(row=i - 19, column=0, padx=950, sticky="W")
                param_containers.append(c)
            param_values.append(p)

        rowIdx += 16

        # Submit entries for .inc file
        submitButton = tk.Button(self.scrollable_frame, text="Save Parameters", font=f,
                                 command=lambda: self.editInc([p.get() for p in param_values], parameters))
        submitButton.grid(row=rowIdx, padx=950, ipadx=10, ipady=3, sticky="W")
        rowIdx += 1

        # Button to run the model (Mac/Linux only)
        runButton = tk.Button(
            self.scrollable_frame, text="Run Model", font=f, command=lambda: self.runModel(runButton))
        runButton.grid(row=rowIdx, padx=950, ipadx=10, ipady=3, sticky="W")
        rowIdx += 1


        csvButton = tk.Button(self.scrollable_frame, text='Download CSV', font=f, command=self.download_csv)
        csvButton.grid(row=rowIdx, padx=950, ipadx=10, ipady=3, sticky="W")




    """
    Allows the user to upload an input text file to be read by the lake model code
    """

    def uploadTxt(self):
        # Open the file choosen by the user
        self.txtfilename = fd.askopenfilename(
            filetypes=(('text files', 'txt'),))
        global INPUT
        INPUT = self.txtfilename
        with open("global_vars.txt", "r+") as vars:
            new = vars.readlines()
            new[0] = INPUT + "\n"
            write_to_file(vars, new)

        base = basename(self.txtfilename)
        nonbase = (self.txtfilename.replace(base, ''))[:-1]
        self.currentTxtFileLabel.configure(text=base)

        # Modify the Fortran code to read the input text file
        with open("env_heatflux.f90", "r+") as f:
            new = f.readlines()
            if self.txtfilename != "":
                if nonbase == os.getcwd():
                    new[18] = "      !data_input_filename = '" + base + "'\n"
                else:
                    new[18] = "      !data_input_filename = '" + self.txtfilename + "'\n"
            write_to_file(f, new)

        # Modify the include file to read the input text file
        with open("Malawi.inc", "r+") as f:
            new = f.readlines()
            if self.txtfilename != "":
                if nonbase == os.getcwd():
                    new[
                        55] = "      character(38) :: datafile='" + base + "' ! the data file to open in FILE_OPEN subroutine\n"
                else:
                    new[
                        55] = "      character(38) :: datafile='" + self.txtfilename + "' ! the data file to open in FILE_OPEN subroutine\n"
            write_to_file(f, new)

    """
    Checks if any parameter value is invalid

    Inputs: 
    - parameters: the values for the model parameters
    Returns: 
    - True if all parameters are valid, False otherwise
    """

    def validate_params(self, parameters):
        for i in range(len(parameters)):
            # Checks whether numerical values are indeed numerical
            if (i <= 21 or i == 27) and (not parameters[i] == ""):
                if not check_float(parameters[i]):
                    tk.messagebox.showerror(title="Run Lake Model", message="Non-numerical value was entered as a value"
                                                                            " for a numerical parameter.")
                    return False
            if (i == 28):
                try:
                    int(parameters[i])
                except:
                    tk.messagebox.showerror(title="Run Lake Model", message="Years must be integer values")
                    return False
        global START_YEAR
        START_YEAR = int(parameters[28])
        with open("global_vars.txt", "r+") as vars:
            new = vars.readlines()
            new[1] = str(START_YEAR)
            write_to_file(vars, new)
        return True

    """
    Edits the parameters in the .inc file based on user input

    Inputs: 
    - parameters: the values for the model parameters
    - comments: the comments in the Fortran code associated with each parameter
    """

    def editInc(self, parameters, comments):
        if not self.validate_params(parameters):
            return
        with open("Malawi.inc", "r+") as f:
            new = f.readlines()
            # names of the parameters that need to be modified
            names = ["oblq", "xlat", "xlon", "gmt", "max_dep", "basedep", "b_area", "cdrn", "eta", "f", "alb_slush",
                     "alb_snow", "depth_begin", "salty_begin", "o18air", "deutair", "tempinit", "deutinit", "o18init",
                     "nspin", "bndry_flag", "sigma", "wb_flag", "iceflag", "s_flag", "o18flag", "deutflag", "z_screen"]
            # line numbers in the .inc file that need to be modified
            rows = [28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 41, 42, 44, 45, 56, 57, 58, 61, 62, 63, 64, 65, 66, 67,
                    68, 69]
            global PARAMETERS
            PARAMETERS = copy.copy(parameters)
            for i in range(len(parameters) - 1):
                if len(str(parameters[i])) != 0:
                    comments[i] = comments[i].replace("\u0394", "D")
                    comments[i] = comments[i].replace("¹⁸", "18")
                    comments[i] = comments[i].replace("Check Mark", "true")
                    comments[i] = comments[i].replace("\n", "")
                    if i == 20 or (i > 21 and i < 27):
                        if parameters[i] == 1:
                            new[rows[i]] = "      parameter (" + names[i] + " = .true.)   ! " + comments[i] + "\n"
                        else:
                            new[rows[i]] = "      parameter (" + names[i] + " = .false.)   ! " + comments[i] + "\n"
                    else:
                        new[rows[i]] = "      parameter (" + names[i] + " = " + parameters[i] + ")   ! " + comments[i] + "\n"
            write_to_file(f, new)

    """
    Fills in parameter values with either Malawi or Tanganyika parameters
    """

    def fill(self, lake, containers):
        if lake == "Malawi":
            values = ["23.4", "-12.11", "34.22", "+3", "292", "468.", "2960000.",
                      "1.7e-3", "0.04", "0.1", "0.4", "0.7", "292", "0.0", "-28.",
                      "-190.", "-4.8", "-96.1", "-11.3", "10", 0, "0.96", 0, 1,
                      0, 0, 0, "5.0", "1979"]
        elif lake=="Tanganyika":
            values = ["23.4", "-6.30", "29.5", "+3", "999", "733.", "23100000.",
                      "2.0e-3", "0.065", "0.3", "0.4", "0.7", "570", "0.0", "-14.0", "-96.",
                      "23.0", "24.0", "3.7", "10", 0, "0.9925561", 0, 0, 0, 0, 0, "5.0", "1979"]
        elif lake=="Refill":
            values = copy.copy(PARAMETERS)
        else:
            values = [""]*20
            values.extend([0,"",0,0,0,0,0,""])
        for i in range(len(values)):
            if i == 20 or (i > 21 and i < 27):
                containers[i].deselect()
                if values[i] == 1:
                    containers[i].select()
                else:
                    containers[i].deselect()
            else:
                containers[i].delete(0, tk.END)
                containers[i].insert(0, values[i])

    """
    Disables run model button and creates separate process for lake model
    """

    def runModel(self, btn):
        response = tk.messagebox.askyesno(title="Warning", message="Running the model will take several minutes, and the GUI may close "
                                                                     "once the model finishes running. If this occurs, you will need to "
                                                                     "re-open the GUI to download the output. Do you wish to proceed?")
        if response == 1:
            btn["state"]="disabled"
            model_process = multiprocessing.Process(target=self.computeModel(btn))
            model_process.start()
        else:
            pass


    """
    Compiles a Fortran wrapper and runs the model
    """

    def computeModel(self,btn):
        # Runs f2py terminal command then (hopefully) terminates (takes a bit)
        subprocess.run(
            ['f2py', '-c', '-m', 'lakepsm', 'env_heatflux.f90'])
        # imports the wrapper
        import lakepsm

        # Run Environment Model (Crashes eventually)
        lakepsm.lakemodel()



    def check_file(self, file, past_size, progress, btn):
        current_size = os.path.getsize(file)
        if past_size != current_size or current_size==0:
            self.after(60000, lambda: self.check_file(file, current_size, progress, btn))
        else:
            btn["state"]="normal"
            progress.stop()
        return None

    """
    Downloads 'surface_output.dat' as a CSV to the user's desired location
    """
    def download_csv(self):
        read_file = genfromtxt('ERA-HIST-Tlake_surf.dat', delimiter='.')
        export_file_path = fd.asksaveasfilename(defaultextension='.csv')
        read_file.to_csv(export_file_path, index=None)


"""
Page to plot environment model time series
"""

class PageEnvTimeSeries(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self, bg="#ECECEC", bd=25)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        s = ttk.Style()
        s.configure('new.TFrame', bg="white smoke")
        self.scrollable_frame = ttk.Frame(canvas, style='new.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        rowIdx = 1
        #Title
        label = tk.Label(
            self.scrollable_frame, bg="white smoke", text="Environment Model Time Series", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0,5))
        rowIdx += 3

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Current File Uploaded:", font=f).grid(
            row=rowIdx + 2, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, bg="white smoke",  text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx + 2, column=1, columnspan=2, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Click to load data", font=f).grid(
            row=rowIdx, column=0, pady=10, sticky="W")
        graphButton = tk.Button(self.scrollable_frame, text="Upload example file", font=f,
                                command=lambda: uploadTxt("sample", self, self.currentFileLabel,
                                                          sample="samples/ERA-HIST-Tlake_surf.dat"))
        rowIdx += 1
        graphButton.grid(row=rowIdx, column=0, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        # Upload own text file
        graphButton = tk.Button(self.scrollable_frame, text="Upload own .dat File", font=f,
                                command=lambda: uploadTxt("user_file", self, self.currentFileLabel,
                                                          file_types=(("dat files", "dat"),)))
        graphButton.grid(row=rowIdx, column=1, pady=10,padx=(0, 50), 
                         ipadx=30, ipady=3, sticky="W")
  
        rowIdx += 4

        # Empty graph, default
        self.f, self.axis = plt.subplots(1,1, figsize=(7, 4.5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis, self.f, "Time Series", "Time", "Lake Surface Temperature")

        button_text = ["Graph Surface Temperature", "Graph Mixing Depth", "Graph Evaporation",
                       "Graph Latent Heat (QEW)",
                       "Graph Sensible Heat (QHW)", "Graph Downwelling\nShortwave Radiation (SWW)",
                       "Graph Upwelling\nLongwave Raditation (LUW)", "Graph Max\nMixing Depth"]

        button_params = [(1, 'Surface Temperature'), (2, 'Mixing Depth'), (3, 'Evaporation'),
                         (4, 'Latent Heat Flux (QEW)'),
                         (5, 'Sensible Heat (QHW)'), (6, 'Downwelling Shortwave Radiation (SWW)'),
                         (7, 'Upwelling Longwave Raditation (LUW)'), (8, 'Max Mixing Depth')]

        for i in range(len(button_text)):
            col = button_params[i][0]
            name = button_params[i][1]
            tk.Button(self.scrollable_frame, text=button_text[i], font=f,
                      command=lambda col=col, name=name: self.generate_env_time_series(col, name)).grid(
                row=rowIdx, column=0, pady=5, ipadx=25, ipady=5, sticky="W")
            rowIdx += 1

        # Save as PNG and CSV
        
        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")
        
        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", fg="blue", font=MED_FONT, bg="azure",
            command=lambda: self.parent.show_frame(["PageEnvTimeSeries"], "StartPage"))        
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")


    """
    Plots the multiple values of a specific variable for each day of the year as a scatterplot

    Inputs:
     - column, an int that corresponds to the column of the desired variable to be plotted
     - varstring, a string that is the name and unit of the variable
    """

    # extracts data from .dat file and plots data based on given column number
    # only takes data after the lake has reached equilibriam, e.g. when the days stop repeating
    def generate_env_time_series(self, column, varstring):
        self.days = []  # x-axis
        self.yaxis = []  # y-axis

        get_output_data(self.days, self.yaxis, column, self.txtfilename)

        self.months = convert_to_monthly(self.days)
        plot_draw(self.scrollable_frame, self.axis, self.f, varstring + " over Time", "Month", varstring, self.months, [self.yaxis],
                  "normal monthly", ["#b22222"], [1], ["Monthly Data"])

        self.years, self.yaxes = convert_to_annual([self.yaxis])
        plot_draw(self.scrollable_frame, self.axis, self.f, varstring + " over Time", "Year", varstring, self.years, self.yaxes,
                  "normal", ["#000000"], [3], ["Annually Averaged Data"], overlay=True)

    # Numpy 1.15.4
    """
    def download_csv(self):
        data = np.array([self.days, self.yaxis]).T

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            fmt = ",".join(["%s"] * (data.shape[1]-1))
            with open(file, 'wb') as f:
                f.write(b'Time,Data\n')
                np.savetxt(f, data, fmt=fmt, delimiter=",")

            tk.messagebox.showinfo("Success", "Saved Data")
    """
    # Numpy 1.17.0 and up
    def download_csv(self):
        data = np.array([self.days, self.yaxis]).T

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            fmt = ",".join(["%s"] * (data.shape[1]-1))
            np.savetxt(file, data, fmt=fmt, header="Time (Days),Temperature (" + u"\N{DEGREE SIGN}" + "C)", comments='', delimiter=',')

        tk.messagebox.showinfo("Success", "Saved Data")


    def download_png(self):
        file = asksaveasfilename(initialfile="Figure.png", defaultextension=".png")
        if file:
            self.f.savefig(file)
            tk.messagebox.showinfo("Sucess", "Saved graph")

"""
Page to plot seasonal cycle
"""


class PageEnvSeasonalCycle(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self, bg="#ECECEC", bd=25)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        s = ttk.Style()
        s.configure('new.TFrame', bg="white smoke")
        self.scrollable_frame = ttk.Frame(canvas, style='new.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        rowIdx = 1
        # Title
        label = tk.Label(
            self.scrollable_frame, bg="white smoke", text="Environment Model Seasonal Cycle", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0,5))
        rowIdx += 3

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Current File Uploaded:", font=f).grid(
            row=rowIdx + 2, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, bg="white smoke",  text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx + 2, column=1, columnspan=2, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Click to load data", font=f).grid(
            row=rowIdx, column=0, pady=10, sticky="W")
        graphButton = tk.Button(self.scrollable_frame, text="Upload example file", font=f,
                                command=lambda: uploadTxt("sample", self, self.currentFileLabel,
                                                          sample="samples/ERA-HIST-Tlake_surf.dat"))
        rowIdx += 1
        graphButton.grid(row=rowIdx, column=0, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        # Upload own text file
        graphButton = tk.Button(self.scrollable_frame, text="Upload own .dat File", font=f,
                                command=lambda: uploadTxt("user_file", self, self.currentFileLabel,
                                                          file_types=(("dat files", "dat"),)))
        graphButton.grid(row=rowIdx, column=1, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        rowIdx += 4

        # Empty graph, default
        self.f, self.axis = plt.subplots(1, 1, figsize=(7, 4.5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis, self.f, "Seasonal Cycle", "Day of the Year",
                   "Lake Surface Temperature")

        # Graph button for each variable

        button_text = ["Graph Surface Temperature", "Graph Mixing Depth", "Graph Evaporation",
                       "Graph Latent Heat (QEW)",
                       "Graph Sensible Heat (QHW)", "Graph Downwelling\nShortwave Radiation (SWW)",
                       "Graph Upwelling\nLongwave Raditation (LUW)", "Graph Max\nMixing Depth"]

        button_params = [(1, 'Surface Temperature'), (2, 'Mixing Depth'), (3, 'Evaporation'),
                         (4, 'Latent Heat Flux (QEW)'),
                         (5, 'Sensible Heat (QHW)'), (6, 'Downwelling Shortwave Radiation (SWW)'),
                         (7, 'Upwelling Longwave Raditation (LUW)'), (8, 'Max Mixing Depth')]

        for i in range(len(button_text)):
            col = button_params[i][0]
            name = button_params[i][1]
            tk.Button(self.scrollable_frame, text=button_text[i], font=f,
                      command=lambda col=col, name=name: self.generate_env_seasonal_cycle(col, name)).grid(
                row=rowIdx, column=0, pady=5, ipadx=25, ipady=5, sticky="W")
            rowIdx += 1

        # Save as PNG and CSV
        
        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")
        
        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", fg="blue", font=MED_FONT, bg="azure",
            command=lambda: self.parent.show_frame(["PageEnvSeasonalCycle"], "StartPage"))        
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")

    """
    Plots the average of a specific variable for each day of the year as a scatterplot

    Inputs:
     - column, an int that corresponds to the column of the desired variable to be plotted
     - varstring, a string that is the name and unit of the variable
    """

    # Treating 375 as part of the year for now
    # Treating everything >375 to be 15, 45, etc.
    def generate_env_seasonal_cycle(self, column, varstring):
        self.days = []  # x-axis
        self.yaxis = []  # y-axis

        get_output_data(self.days, self.yaxis, column, self.txtfilename)

        # At this point, self.days and self.yaxis are identical to the ones in envtimeseries

        self.ydict = {}  # dictionary to store the y values for each day from 15 to 375
        for day in self.days:  # 15, 45, ...
            # if the day is not a key, then make an empty list
            if day % 360 not in self.ydict:
                self.ydict[day % 360] = []
            self.ydict[day % 360].append(self.yaxis[int((day - 15) / 30)])  # (day - 15)/30 gets the correct index

        # After yval array is formed for each xval, generate the axtual yaxis data
        self.seasonal_yaxis = []  # actual plotting data for y
        self.seasonal_days = []
        global START_YEAR
        start = dt.date(START_YEAR, 1, 1)
        for i in range(15, 346, 30):
            date = start+dt.timedelta(days=(i-1))
            self.seasonal_days.append(date)
            self.seasonal_yaxis.append(mean(self.ydict[i]))

        plot_draw(self.scrollable_frame, self.axis, self.f, varstring + " Seasonal Cycle", "Day of the Year", "Average", self.seasonal_days,
                  [self.seasonal_yaxis], "normal month-only", ["#000000"], [3], ["Monthly Averaged Data"])

    # Numpy 1.15.4
    """
    def download_csv(self):
        data = np.array([self.seasonal_days, self.seasonal_yaxis]).T

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            fmt = ",".join(["%s"] * (data.shape[1]-1))
            with open(file, 'wb') as f:
                f.write(b'Time,Data\n')
                np.savetxt(f, data, fmt=fmt, delimiter=",")

            tk.messagebox.showinfo("Success", "Saved Data")
    """

    # Numpy 1.17.0 and up
    
    def download_csv(self):
        data = np.array([self.seasonal_days, self.seasonal_yaxis]).T

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            fmt = ",".join(["%s"] * (data.shape[1]-1))
            np.savetxt(file, data, fmt=fmt, header="Date,Temperature (" + u"\N{DEGREE SIGN}" + "C)", comments='', delimiter=',')

        tk.messagebox.showinfo("Success", "Saved Data")
    

    def download_png(self):
        file = asksaveasfilename(initialfile="Figure.png", defaultextension=".png")
        if file:
            self.f.savefig(file)
            tk.messagebox.showinfo("Sucess", "Saved graph")
"""
Page to run carbonate sensor model and plot data
"""


class PageCarbonate(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self, bg="#ECECEC", bd=25)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        s = ttk.Style()
        s.configure('new.TFrame', bg="white smoke")
        self.scrollable_frame = ttk.Frame(canvas, style='new.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        rowIdx = 1

        #Title
        label = tk.Label(
            self.scrollable_frame, bg="white smoke", text="Carbonate Sensor Model", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0,5))

        rowIdx += 3

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Current File Uploaded:", font=f).grid(
            row=rowIdx + 2, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, bg="white smoke",  text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx + 2, column=0, padx=(150, 0), columnspan=1, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Click to load data", font=f).grid(
            row=rowIdx, column=0, pady=10, sticky="W")
        graphButton = tk.Button(self.scrollable_frame, text="Upload example file", font=f,
                                command=lambda: uploadTxt("sample", self, self.currentFileLabel,
                                                          sample="samples/ERA-HIST-Tlake_surf.dat"))
        rowIdx += 1
        graphButton.grid(row=rowIdx, column=0, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        # Upload own text file
        graphButton = tk.Button(self.scrollable_frame, text="Upload own .dat File", font=f,
                                command=lambda: uploadTxt("user_file", self, self.currentFileLabel,
                                                          file_types=(("dat files", "dat"),)))
        graphButton.grid(row=rowIdx, column=0, pady=10, padx=(200, 50), 
                         ipadx=30, ipady=3, sticky="E")
        rowIdx += 4

        self.model = tk.StringVar()
        self.model.set("ONeil")
        model_names = ["ONeil", "Kim-ONeil", "ErezLuz", "Bemis", "Lynch"]
        for name in model_names:
            tk.Radiobutton(self.scrollable_frame, text=name, bg="white smoke", font=MED_FONT, value=name, variable=self.model).grid(
                row=rowIdx, column=0,
                pady=1,
                ipadx=20, ipady=5,
                sticky="W")
            rowIdx += 1
        tk.Button(self.scrollable_frame, text="Generate Graph of Carbonate Proxy Data", font=MED_FONT, command=self.generate_graph).grid(
            row=rowIdx, column=0, pady=(10, 5),
            ipadx=20, ipady=5, sticky="W")

        # Save as PNG and CSV
        
        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")
        
        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", fg="blue", font=MED_FONT, bg="azure",
            command=lambda: self.parent.show_frame(["PageCarbonate"], "StartPage"))        
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")

        self.f, self.axis = plt.subplots(1,1, figsize=(7, 4.5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis, self.f, "SENSOR", "Time", "Simulated Carbonate Data")

    """
    Create time series data for carbonate sensor
    """

    def generate_graph(self):
        surf_tempr = []
        self.days = []
        get_output_data(self.days, surf_tempr, 1, self.txtfilename)
        self.LST = np.array(surf_tempr, dtype=float)
        self.d180w = -2
        self.carb_proxy = carb.carb_sensor(self.LST, self.d180w, model=self.model.get())

        self.months = convert_to_monthly(self.days)
        plot_draw(self.scrollable_frame, self.axis, self.f, "SENSOR", "Month", "Simulated Carbonate Data", self.months, [self.carb_proxy],
                  "normal monthly", ["#b22222"], [1], ["Monthly Data"])

        self.years, self.yaxis = convert_to_annual([self.carb_proxy])
        plot_draw(self.scrollable_frame, self.axis, self.f, "SENSOR", "Year", "Simulated Carbonate Data", self.years, self.yaxis,
                  "normal", ["#000000"], [3], ["Annually Averaged Data"], overlay=True)
        
    # Numpy 1.15.4
    """
    def download_csv(self):
        data = np.array([self.days, self.carb_proxy]).T

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            fmt = ",".join(["%s"] * (data.shape[1]-1))
            with open(file, 'wb') as f:
                f.write(b'Time,Pseudoproxy\n')
                np.savetxt(f, data, fmt=fmt, delimiter=",")

            tk.messagebox.showinfo("Success", "Saved Data")
    """

    # Numpy 1.17.0 and up
    def download_csv(self):
        data = np.array([self.days, self.carb_proxy]).T

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            fmt = ",".join(["%s"] * (data.shape[1]-1))
            np.savetxt(file, data, fmt=fmt, header="Time,Pseudoproxy", comments='', delimiter=',')

        tk.messagebox.showinfo("Success", "Saved Data")


    def download_png(self):
        file = asksaveasfilename(initialfile="Figure.png", defaultextension=".png")
        if file:
            self.f.savefig(file)
            tk.messagebox.showinfo("Success", "Saved graph")
"""
Page to run GDGT Model and plot data
"""


class PageGDGT(tk.Frame):


    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self, bg="#ECECEC", bd=25)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        s = ttk.Style()
        s.configure('new.TFrame', bg="white smoke")
        self.scrollable_frame = ttk.Frame(canvas, style='new.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        rowIdx = 1
        #Title
        label = tk.Label(
            self.scrollable_frame, bg="white smoke", text="Run GDGT Sensor Model", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0,5))

        rowIdx += 3

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Current File Uploaded:", font=f).grid(
            row=rowIdx + 2, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, bg="white smoke",  text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx + 2, column=1, columnspan=2, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Click to load data", font=f).grid(
            row=rowIdx, column=0, pady=10, sticky="W")
        graphButton = tk.Button(self.scrollable_frame, text="Upload example file\n(for Non-MBT Models)", font=f,
                                command=lambda: uploadTxt("sample", self, self.currentFileLabel,
                                                          sample="samples/ERA-HIST-Tlake_surf.dat"))
        rowIdx += 1
        graphButton.grid(row=rowIdx, column=0, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        # Upload own text file
        graphButton = tk.Button(self.scrollable_frame, text="Upload own .dat File", font=f,
                                command=lambda: uploadTxt("user_file", self, self.currentFileLabel,
                                                          file_types=(("dat files", "dat"),)))
        graphButton.grid(row=rowIdx, column=1, pady=10,
                         ipadx=30, ipady=3,padx=(0, 50), sticky="W")
        rowIdx += 4

        self.model = tk.StringVar()
        self.model.set("TEX86-tierney")
        model_names = ["TEX86-tierney", "TEX86-powers", "TEX86-loomis", "MBT-R", "MBT-J"]
        for name in model_names:
            tk.Radiobutton(self.scrollable_frame, bg="white smoke", text=name, value=name, font=MED_FONT, variable=self.model).grid(row=rowIdx, column=0,
                                                                                                 pady=5,
                                                                                                 ipadx=20, ipady=5,
                                                                                                 sticky="W")
            rowIdx += 1
        rowIdx += 1

        tk.Button(self.scrollable_frame, text="Generate Graph of GDGT Proxy Data", font=MED_FONT, command=self.generate_graph).grid(
            row=rowIdx, column=0, pady=20, ipadx=20, ipady=5, sticky="W")

        # Save as PNG and CSV
        
        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")
        
        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", fg="blue", font=MED_FONT, bg="azure",
            command=lambda: self.parent.show_frame(["PageGDGT"], "StartPage"))        
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")

        self.f, self.axis = plt.subplots(1, 1, figsize=(7, 4.5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis, self.f, "SENSOR", "Time", "Simulated GDGT Data")

    """
    Create time series data for GDGT sensor
    """

    def generate_graph(self):
        surf_tempr = []
        self.days = []
        get_output_data(self.days, surf_tempr, 1, self.txtfilename)
        self.LST = np.array(surf_tempr, dtype=float)

        # unchanged
        climate_input = INPUT.replace("\n", "")
        air_tempr = []
        if "MBT" in self.model.get():
            with open(climate_input, 'r') as data:
                self.days = []
                airtemp_yr = []
                for line in data:
                    line_vals = line.split()
                    airtemp_yr.append(line_vals[2])
                    self.days.append(int(float((line_vals[1]))))
                air_tempr.append(airtemp_yr)
            air_tempr = np.array(air_tempr[0], dtype=float)

        self.MAAT = air_tempr
        self.beta = 1. / 50.
        self.gdgt_proxy = gdgt.gdgt_sensor(self.LST, self.MAAT, self.beta, model=self.model.get())

        self.months = convert_to_monthly(self.days)
        plot_draw(self.scrollable_frame, self.axis, self.f, "Leafwax Model", "Month", "Simulated GDGT Data", self.months,
                  [self.gdgt_proxy],
                  "normal monthly", ["#b22222"], [1], ["Monthly Data"])

        self.years, self.yaxis = convert_to_annual([self.gdgt_proxy])
        plot_draw(self.scrollable_frame, self.axis, self.f, "Leafwax Model", "Year", "Simulated GDGT Data", self.years,
                  self.yaxis,
                  "normal", ["#000000"], [3], ["Annually Averaged Data"], overlay=True)

    # Numpy 1.15.4
    """
    def download_csv(self):
        data = np.array([self.days, self.gdgt_proxy]).T

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            fmt = ",".join(["%s"] * (data.shape[1]-1))
            with open(file, 'wb') as f:
                f.write(b'Time,Pseudoproxy\n')
                np.savetxt(f, data, fmt=fmt, delimiter=",")

            tk.messagebox.showinfo("Success", "Saved Data")
    """

    # Numpy 1.17.0 and up
    def download_csv(self):
        data = np.array([self.days, self.gdgt_proxy]).T

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            fmt = ",".join(["%s"] * (data.shape[1]-1))
            np.savetxt(file, data, fmt=fmt, header="Time,Pseudoproxy", comments='', delimiter=',')

        tk.messagebox.showinfo("Success", "Saved Data")


    def download_png(self):
        file = asksaveasfilename(initialfile="Figure.png", defaultextension=".png")
        if file:
            self.f.savefig(file)
            tk.messagebox.showinfo("Sucess", "Saved graph")



"""
Page to run leafwax sensor model and plot data
"""


class PageLeafwax(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self, bg="#ECECEC", bd=25)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        s = ttk.Style()
        s.configure('new.TFrame', bg="white smoke")
        self.scrollable_frame = ttk.Frame(canvas, style='new.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        rowIdx = 1
        #Title
        label = tk.Label(
            self.scrollable_frame, bg="white smoke", text="Run Leafwax Model", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0, 5))

        rowIdx += 1

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Current File Uploaded:", font=f).grid(
            row=rowIdx + 2, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, bg="white smoke",  text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx + 2, column=1, columnspan=2, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Click to load data", font=f).grid(
            row=rowIdx, column=0, pady=10, sticky="W")
        graphButton = tk.Button(self.scrollable_frame, text="Upload example file", font=f,
                                command=lambda: uploadTxt("sample", self, self.currentFileLabel,
                                                          sample="samples/IsoGSM_dDP_1953_2012.txt"))
        rowIdx += 1
        graphButton.grid(row=rowIdx, column=0, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        # Upload own text file
        graphButton = tk.Button(self.scrollable_frame, text="Upload own .txt File", font=f,
                                command=lambda: uploadTxt("user_file", self, self.currentFileLabel,
                                                          file_types=(("text files", "txt"),)))
        graphButton.grid(row=rowIdx, column=1, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        rowIdx += 2
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Start Year:", font=f).grid(
            row=rowIdx, column=0, sticky="W")
        start = tk.Entry(self.scrollable_frame)
        start.grid(row=rowIdx, column=1, padx=(0, 50), sticky="W")

        rowIdx+=2
        self.f, self.axis = plt.subplots(1,1, figsize=(7, 4.5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis, self.f, "SENSOR", "Time", "Simulated Leafwax Data")

        tk.Button(self.scrollable_frame, text="Graph Leafwax Proxy Data", font=f, command=lambda: self.generate_graph(start.get())).grid(
            row=rowIdx, column=0, ipadx=20, ipady=5, sticky="W")


        # Save as PNG and CSV
        
        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")
        
        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", fg="blue", font=MED_FONT, bg="azure",
            command=lambda: self.parent.show_frame(["PageLeafwax"], "StartPage"))        
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")

    """
    Create time series data for leafwax sensor
    """

    def generate_graph(self, start_year):
        try:
            int(start_year)
        except:
            tk.messagebox.showerror(title="Run Leafwax Model", message="Year must be a positive integer value")
            return
        if int(start_year) < 0:
            tk.messagebox.showerror(title="Run Leafwax Model", message="Year must be a positive integer value")
            return
        start_year = int(start_year)
        self.dDp = np.loadtxt(self.txtfilename)
        self.fC_3 = 0.7  # fraction of C3 plants
        self.fC_4 = 0.3  # fraction of C4 plants
        self.eps_c3 = -112.8  # pm 34.7
        self.eps_c4 = -124.5  # pm 28.2

        # define the error range on the epsilon (apparent fractionation) measurement:
        self.eps_c3_err = 34.7
        self.eps_c4_err = 28.2

        self.leafwax_proxy = leafwax.wax_sensor(self.dDp, self.fC_3, self.fC_4, self.eps_c3, self.eps_c4)

        # add uncertainties in apparent fractionation via monte-carlo resampling process:
        self.delta_d_wax_mc, self.Q1, self.Q2 = leafwax.wax_uncertainty(self.dDp, self.fC_3, self.fC_4, self.eps_c3,
                                                                        self.eps_c4, self.eps_c3_err, self.eps_c4_err)
        # where Q1 is the 2.5th percentile, Q2 is the 97.5th percentile of the 1000 MC realizations
        self.days = []
        with open(self.txtfilename) as input:
            for i in range(len(input.readlines())):
                self.days.append(30 * i + 15)
        self.months = convert_to_monthly(self.days, start=start_year)
        plot_draw(self.scrollable_frame, self.axis, self.f, "Leafwax Model", "Month", "Simulated Leafwax Data", self.months, [self.leafwax_proxy],
                  "normal monthly", ["#b22222"], [1], ["Monthly Data"])

        self.years, self.leafwax_array = convert_to_annual([self.leafwax_proxy, self.Q1, self.Q2], start=start_year)
        plot_draw(self.scrollable_frame, self.axis, self.f, "Leafwax Model", "Year", "Simulated Leafwax Data", self.years, [self.leafwax_array[0]],
                  "normal", ["#000000"], [3], ["Annually Averaged Data"], error_lines=self.leafwax_array[1:], overlay=True)

    """
    def download_csv(self):
        df = pd.DataFrame({"Time": self.days, "Pseudoproxy": self.leafwax_proxy, "95% CI Lower Bound": self.Q1,
                           "95% CI Upper Bound": self.Q2})

        export_file_path = fd.asksaveasfilename(defaultextension='.csv')
        df.to_csv(export_file_path, index=None)
    
    
    # Numpy 1.15.4
    def download_csv(self):
        data = np.array([self.days, self.leafwax_proxy, self.Q1, self.Q2]).T

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            fmt = ",".join(["%s"] + ["%s"] + ["%s"] * (data.shape[1]-1))
            with open(file, 'wb') as f:
                f.write(b'Time,Pseudoproxy,95% CI Lower Bound,95% CI Upper Bound\n')
                np.savetxt(f, data, fmt=fmt, delimiter=",")

            tk.messagebox.showinfo("Success", "Saved Data")
    """
    # Numpy 1.17.0 and up
    def download_csv(self):
        data = np.array([self.days, self.leafwax_proxy, self.Q1, self.Q2]).T

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            fmt = ",".join(["%s"] + ["%s"] * (data.shape[1]-1))
            np.savetxt(file, data, fmt=fmt, header="Time,Pseudoproxy,95% CI Lower Bound,95% CI Upper Bound", comments='', delimiter=',')

        tk.messagebox.showinfo("Success", "Saved Data")


    def download_png(self):
        file = asksaveasfilename(initialfile="Figure.png", defaultextension=".png")
        if file:
            self.f.savefig(file)
            tk.messagebox.showinfo("Sucess", "Saved graph")



"""
Page to run observation model and plot data
"""

class PageObservation(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self, bg="#ECECEC", bd=25)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        s = ttk.Style()
        s.configure('new.TFrame', bg="white smoke")
        self.scrollable_frame = ttk.Frame(canvas, style='new.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)


    def populate(self):
        rowIdx = 1

        # Title
        label = tk.Label(
            self.scrollable_frame, bg="white smoke", text="Run Observation Model", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0,5))
        rowIdx += 2

        # Instructions for uploading file
        tk.Label(self.scrollable_frame, bg="white smoke", 
                 text=
                 """WARNING: Long running time\nInstructions for input file:\n1) The first row must be 'DP, AGE, SD'\n2) Ages must be in BP
                 """, font=f, justify="left"
                 ).grid(row=rowIdx, column=0, columnspan=1, rowspan=1, pady=10, ipady=0, sticky="W")
        rowIdx += 2

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Current File Uploaded:", font=f).grid(
            row=rowIdx, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, bg="white smoke",  text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx, column=1, columnspan=2, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Click to load data", font=f).grid(
            row=rowIdx, column=0, pady=10, sticky="W")
        graphButton = tk.Button(self.scrollable_frame, text="Upload example file", font=f,
                                command=lambda: uploadTxt("sample", self, self.currentFileLabel,
                                                          sample="samples/TEX86_cal.csv"))
        rowIdx += 1
        graphButton.grid(row=rowIdx, column=0, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        # Upload own text file
        graphButton = tk.Button(self.scrollable_frame, text="Upload own .csv File", font=f,
                                command=lambda: uploadTxt("user_file", self, self.currentFileLabel,
                                                          file_types=(("csv files", "csv"),)))
        graphButton.grid(row=rowIdx, column=1, pady=10, padx=(0, 50), 
                         ipadx=30, ipady=3, sticky="W")
        rowIdx += 2


        self.f, self.axis = plt.subplots(1,1, figsize=(7, 4.5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis, self.f, "Observation Model", "Age (cal years BP)", "Depth in Core (cm)")


        tk.Button(self.scrollable_frame, text="Graph Observation Model", font=MED_FONT, command=lambda: self.generate_graph()).grid(
            row=rowIdx, column=0, pady=1,
            ipadx=20, ipady=5, sticky="W")

        # Save as PNG and CSV
        
        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")
        
        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", fg="blue", font=MED_FONT, bg="azure",
            command=lambda: self.parent.show_frame(["PageObservation"], "StartPage"))        
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")


    """
    Plot observation model
    """

    def generate_graph(self):
        # R packages
        utils = importr("utils")
        utils.chooseCRANmirror(ind=1)
        packnames = ('Bchron', 'stats', 'graphics')
        utils.install_packages(StrVector(packnames))
        Bchron = importr('Bchron')
        r = robjects.r

        # Read in the data (csv file must be in the same directory as executable)
        data = np.genfromtxt(self.txtfilename, delimiter=',', names=True, dtype=None)
        year = data['AGE']
        depth = data['DP']
        sds = data['SD']
        calCurves = np.repeat('normal', len(year))
        nyears = year[-1]
        d = depth[-1]
        ages = FloatVector(year)
        sd = FloatVector(sds)
        positions = FloatVector(depth)
        calCurves = StrVector(calCurves)
        predictPositions = r.seq(0, d, by=d / nyears)
        extractDate = year[0]


        # Runs the actual model (takes several minutes)
        self.ages = Bchron.Bchronology(ages=ages, ageSds=sd, positions=positions,
                          calCurves=calCurves, predictPositions=predictPositions, extractDate=extractDate)

        # Creating arrays for plotting
        thetaPredict = self.ages[4]
        thetaPredict = np.array(thetaPredict)
        depths = np.array(predictPositions)
        self.depth_horizons = depths[:-1]
        chrons = thetaPredict[:, :-1]
        self.chronsQ = np.quantile(chrons.transpose(), [0.025, 0.5, 0.975], axis=1)

        # Actual Plotting
        self.axis.fill_betweenx(self.depth_horizons, self.chronsQ[0], self.chronsQ[2],
                          facecolor='Silver', edgecolor='Silver', lw=0.0) # horizontal fill between 2.5% - 97.5% of data

        self.axis.plot(self.chronsQ[1], self.depth_horizons, color="black", lw=0.75) # median line
        self.axis.scatter(data['AGE'], data['DP'], marker="s") # squares
        self.axis.legend(['Median', '95% CI', 'Dated Positions'])
        self.axis.invert_xaxis()
        self.axis.invert_yaxis()
        self.axis.set_xlabel('Age (cal years BP)')
        self.axis.set_ylabel('Depth (mm)')

        canvas = FigureCanvasTkAgg(self.f, self.scrollable_frame)
        canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        canvas.draw()

    def download_csv(self):
        df = pd.DataFrame({"Depth": self.depth_horizons, "Age (95% CI Lower Bound)": self.chronsQ[0],
                        "Age (95% CI Median)": self.chronsQ[0], "Age (95% CI Upper Bound)": self.chronsQ[2]})
        #export_file_path = fd.asksaveasfilename(defaultextension='.csv')
        #df.to_csv(export_file_path, index=None)


        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            df.to_csv(file, index=False)
            tk.messagebox.showinfo("Success", "Saved Data")

    """
    def download_csv(self):
        data = np.array([self.depth_horizons, self.chronsQ[0], self.chronsQ[0], self.chronsQ[2]]).T

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            fmt = ",".join(["%s"] * (data.shape[1]-1))
            with open(file, 'wb') as f:
                f.write(b'Depth,Age (95% CI Lower Bound),Age (95% CI Median),Age (95% CI Upper Bound)\n')
                np.savetxt(f, data, fmt=fmt, delimiter=",")

            tk.messagebox.showinfo("Success", "Saved Data")
    
    # Numpy 1.17.0 and up
    def download_csv(self):
        data = np.array([self.depth_horizons, self.chronsQ[0], self.chronsQ[0], self.chronsQ[2]]).T

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            fmt = ",".join(["%s"] + ["%s"] * (data.shape[1]-1))
            np.savetxt(file, data, fmt=fmt, header="Depth,Age (95% CI Lower Bound),Age (95% CI Median),Age (95% CI Upper Bound)", comments='', delimiter=',')

        tk.messagebox.showinfo("Success", "Saved Data")
    """

    def download_png(self):
        file = asksaveasfilename(initialfile="Figure.png", defaultextension=".png")
        if file:
            self.f.savefig(file)
            tk.messagebox.showinfo("Sucess", "Saved graph")


"""
Page to run bioturbation archive model and plot data
"""
class PageBioturbation(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self, bg="#ECECEC", bd=25)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        s = ttk.Style()
        s.configure('new.TFrame', bg="white smoke")
        self.scrollable_frame = ttk.Frame(canvas, style='new.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        rowIdx = 1
        #Title
        label = tk.Label(
            self.scrollable_frame, bg="white smoke", text="Run Bioturbation Model", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0,5))
        rowIdx += 3

        # Instructions for uploading .txt and .inc files
        tk.Label(self.scrollable_frame, bg="white smoke", 
                 text=
                """1) Upload a .csv file with a column "Pseudoproxy",\n containing pseudoproxy timeseries data. \n2) Enter parameters for bioturbation\n3) You cannot leave parameters empty
                """, font=f, justify="left"
                 ).grid(row=rowIdx, columnspan=3, rowspan=1, pady=10, ipady=0, sticky="W")
        rowIdx += 3

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Current File Uploaded:", font=f).grid(
            row=rowIdx + 2, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, bg="white smoke",  text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx + 2, column=1, columnspan=2, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, bg="white smoke",  text="Click to load data", font=f).grid(
            row=rowIdx, column=0, pady=10, sticky="W")
        graphButton = tk.Button(self.scrollable_frame, text="Upload example file", font=f,
                                command=lambda: uploadTxt("sample", self, self.currentFileLabel,
                                                          sample="samples/leafwax_timeseries.csv"))
        rowIdx += 1
        graphButton.grid(row=rowIdx, column=0, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        # Upload own text file
        graphButton = tk.Button(self.scrollable_frame, text="Upload own .csv File", font=f,
                                command=lambda: uploadTxt("user_file", self, self.currentFileLabel,
                                                          file_types=(("csv files", "csv"),)))
        graphButton.grid(row=rowIdx, column=1, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        rowIdx += 4


        
        parameters = ["Start Year:", "End Year:", "Mixed Layer Thickness Coefficient:", "Abundance:",
                      "Number of Carriers:"]
        param_values = []
        for i in range(rowIdx, rowIdx + 5):
            tk.Label(self.scrollable_frame, bg="white smoke",  text=parameters[i - rowIdx], font=f).grid(
                row=i, column=0, sticky="W")
            p = tk.Entry(self.scrollable_frame)
            p.grid(row=i, column=1, sticky="W", padx=(20, 50))
            param_values.append(p)
        rowIdx += 5
        tk.Button(self.scrollable_frame, text="Generate Graph", font=MED_FONT,
                  command=lambda: self.run_bioturb_model([p.get() for p in param_values])).grid(
            row=rowIdx, column=0, sticky="W")

       
        # Save as PNG and CSV
        
        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")
        
        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", fg="blue", font=MED_FONT, bg="azure",
            command=lambda: self.parent.show_frame(["PageBioturbation"], "StartPage"))        
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")

        
        self.f, self.axis = plt.subplots(1, 1, figsize=(7, 4.5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis, self.f, "ARCHIVE", "Year", "Bioturbated Sensor Data")

    """
    Returns false is any parameter value is invalid
    """

    def validate_params(self, params):
        for p in params:
            if not p:
                tk.messagebox.showerror(title="Run Bioturbation Model", message="Not all parameters were entered.")
                return False
        if not (params[0].isdigit() and params[1].isdigit()):
            tk.messagebox.showerror(title="Run Bioturbation Model",
                                    message="Years must be positive integers")
            return False
        if int(params[0]) < 0 or int(params[1]) < 0:
            tk.messagebox.showerror(title="Run Bioturbation Model",
                                    message="Years must be positive integers")
            return False
        for i in range(2, 5):
            if not check_float(params[i]):
                tk.messagebox.showerror(title="Run Bioturbation Model",
                                        message=str(params[i]) + " should be a numeric value")
                return False
            if i == 5 and not params[i].isdigit():
                tk.messagebox.showerror(title="Run Bioturbation Model",
                                        message=str(params[i]) + " should be an integer")
                return False
        # convert parameters to integers for further validation
        params_copy = copy.deepcopy(params)
        params_copy = [float(p) for p in params_copy]
        if params_copy[0] >= params_copy[1]:
            tk.messagebox.showerror(title="Run Bioturbation Model",
                                    message="Start year cannot be greater than or equal to end year")
            return False
        return True

    def run_bioturb_model(self, params):
        # check whether csv file can be opened
        try:
            pseudoproxy = pd.read_csv(self.txtfilename)["Pseudoproxy"]
        except:
            tk.messagebox.showerror(title="Run Bioturbation Model", message="Error with reading csv file")

        year = []
        self.days, self.iso = convert_to_annual([pseudoproxy])
        if not self.validate_params(params):
            return
        self.age = int(params[1]) - int(params[0])
        self.mxl = np.ones(self.age) * float(params[2])
        self.abu = np.ones(self.age) * float(params[3])
        self.numb = int(params[4])
        # Run the bioturbation model
        self.oriabu, self.bioabu, self.oriiso, self.bioiso = bio.bioturbation(self.abu, self.iso[0], self.mxl, self.numb)

        # Plot the bioturbation model
        self.bio1 = self.bioiso[:, 0]
        self.bio2 = self.bioiso[:, 1]
        self.ori = self.oriiso[:, 0]
        plot_draw(self.scrollable_frame, self.axis, self.f, "ARCHIVE", "Year", "Bioturbated Sensor Data", self.days, [self.bio1, self.bio2, self.ori],
                  "normal", ["#b22222", "#b22222", "#000000"], [2,2,2], ["Bioturbated 1", "Bioturbated 2", "Original"])

    # Numpy 1.15.4
    """
    def download_csv(self):
        df = pd.DataFrame({"Time": self.days, "Pseudoproxy": self.ori,
                           "Bioturbated Carrier 1": self.bio1, "Bioturbated Carrier 2": self.bio2})
        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            df.to_csv(file, index=False)
            tk.messagebox.showinfo("Success", "Saved Data")
    """

    # Numpy 1.17.0 and up
    def download_csv(self):
        data = np.array([self.days, self.ori, self.bio1, self.bio2]).T

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            fmt = ",".join(["%s"] + ["%s"] * (data.shape[1]-1))
            np.savetxt(file, data, fmt=fmt, header="Time,Pseudoproxy,Bioturbated Carrier 1,Bioturbated Carrier 2", comments='', delimiter=',')

        tk.messagebox.showinfo("Success", "Saved Data")

    def download_png(self):
        file = asksaveasfilename(initialfile="Figure.png", defaultextension=".png")
        if file:
            self.f.savefig(file)
            tk.messagebox.showinfo("Sucess", "Saved graph")

class PageCompaction(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self, bg="#ECECEC", bd=25)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        s = ttk.Style()
        s.configure('new.TFrame', bg="white smoke")
        self.scrollable_frame = ttk.Frame(canvas, style='new.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        rowIdx = 1
        # Title
        label = tk.Label(
            self.scrollable_frame, bg="white smoke", text="Run Compaction Model", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(1, 20))
        rowIdx += 3

        parameters = ["Sedimentation Rate (cm/kyr):","# of Years", "Porosity (\u03d5)"]
        param_values = []
        for i in range(rowIdx, rowIdx + 3):
            tk.Label(self.scrollable_frame, bg="white smoke",  text=parameters[i - rowIdx], font=f).grid(
                row=i, column=0, sticky="W")
            p = tk.Entry(self.scrollable_frame)
            p.grid(row=i, column=1, padx=(20, 50), sticky="W")
            param_values.append(p)
        rowIdx += 3
        tk.Button(self.scrollable_frame, text="Generate Graph", font=MED_FONT,
                  command=lambda: self.run_compaction_model([p.get() for p in param_values])).grid(
            row=rowIdx, column=0, pady=(10, 5),
            ipadx=20, ipady=5, sticky="W")


        # Save as PNG and CSV

        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")

        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", fg="blue", font=MED_FONT, bg="azure",
                               command=lambda: self.parent.show_frame(["PageCompaction"], "StartPage"))
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")


        self.f, self.axis = plt.subplots(1, 2, figsize=(9, 5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis[0], self.f, "ARCHIVE", "Year", "Compaction Data")
        plot_setup(self.scrollable_frame, self.axis[1], self.f, "ARCHIVE", "Year", "Compaction Data")

    def validate_params(self, params):
        if not check_float(params[0]):
            tk.messagebox.showerror(title="Run Compaction Model", message="Floating point value was not entered for sedimentation rate")
            return False
        if not params[1].isdigit():
            tk.messagebox.showerror(title="Run Compaction Model", message="Integer value was not entered for year")
            return False
        if int(params[1]) < 0:
            tk.messagebox.showerror(title="Run Compaction Model",
                                    message="Positive integer value was not entered for year")
            return False
        if not check_float(params[2]):
            tk.messagebox.showerror(title="Run Compaction Model", message="Floating point value was not entered for porosity")
            return False
        return True

    def run_compaction_model(self, params):
        if not self.validate_params(params):
            return
        sbar = float(params[0])
        year = int(params[1])
        phi_0 = float(params[2])
        self.z, self.phi, self.h, self.h_prime = comp.compaction(sbar, year, phi_0)
        plot_draw(self.scrollable_frame, self.axis[0], self.f, "Porosity ($\phi$) Profile in Sediment Core", "Depth (m)",
                  r'Porosity Profile ($\phi$) (unitless)', self.z, [self.phi],
                  "normal non-month", ["#000000"], [3], ["Porosity Profile"])
        plot_draw(self.scrollable_frame, self.axis[1], self.f, "Depth Scale w/Compaction in Sediment Core", "Depth (m)", "Sediment Height (m)",
                  self.z, [self.h_prime, self.h], "normal non-month", ["#000000", "#b22222"], [3, 3],
                  ["Compcated Layer", "Non-Compacted Original Layer"])

    def download_csv(self):
        df = pd.DataFrame({"Depth (m)": self.z, r'Porosity Profile ($\phi$) (unitless)':self.phi,
                           "Compacted Layer": self.h.prime,"Non-Compacted Original Layer": self.h})
        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            df.to_csv(file, index=False)
            tk.messagebox.showinfo("Success", "Saved Data")

    def download_png(self):
        file = asksaveasfilename(initialfile="Figure.png", defaultextension=".png")
        if file:
            self.f.savefig(file)
            tk.messagebox.showinfo("Sucess", "Saved graph")


if __name__ == "__main__":
    app = SampleApp()
    app.config(highlightcolor="white smoke")
    app.mainloop()