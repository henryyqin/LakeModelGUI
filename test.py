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

# Data Analytics
import pandas as pd
import numpy as np
import matplotlib

# Imports for plotting
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import datetime as dt
from matplotlib import dates as mdates
from statistics import mean
plt.style.use('seaborn-whitegrid')
matplotlib.use('TkAgg')  # Necessary for Mac Mojave


#Miscellaneous imports
import os
from os.path import basename
import webbrowser
import copy
import subprocess
import multiprocessing
from subprocess import PIPE, Popen
from tkinter.ttk import Label
from PIL import Image, ImageTk

#===========GENERAL FUNCTIONS========================================
def callback(url):
    webbrowser.open_new(url)

def initialize_global_variables():
    """
    Reads global_vars.txt to initialize global variables with pre-existing values
    from previous runs of the GUI
    """
    with open("global_vars.txt", "r") as start:
        lines = start.readlines()
        global INPUT
        if len(lines) >= 1:
            INPUT = lines[0]
        if len(lines) >= 2:
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

def get_output_data(time, data, column):
    """
    Retrieves data from surf.dat from years where lake is at equilibrium
    Inputs
    - time: an empty array which is populated with day #'s
    - data: an empty array which is populated with a certain column of data from surf.dat
    - column: the specific column of data in surf.dat which should populate "data"
    """
    with open("ERA-HIST-Tlake_surf.dat") as file:
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

def plot_setup(frame, figure, title, x_axis, y_axis):
    """
    Creates a blank plot on which a graph can be displayed
    Inputs
    - frame: the page in the GUI where the plot is located
    - figure: the figure on which the plot is located
    - title: the title displayed on the plot
    - x_axis: the x-axis label
    - y_axis: the y-axis label
    """
    plt = figure.add_subplot(111)
    canvas = FigureCanvasTkAgg(figure, frame)
    canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
    plt.set_title(title, fontsize=12)
    plt.set_xlabel(x_axis)
    plt.set_ylabel(y_axis)

def plot_draw(frame, figure, title, x_axis, y_axis, x_data, y_data, plot_type, colors, widths, labels, error_lines=None, overlay=False):
    """
    Creates plot(s) based on input parameters
    Inputs
    - frame: the page in the GUI where the plot is located
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
    if not overlay:
        figure.clf()
    plt = figure.add_subplot(111)
    plt.set_title(title)
    plt.set_xlabel(x_axis)
    plt.set_ylabel(y_axis)
    i = 0
    for line in y_data:
        if "normal" in plot_type:
            plt.plot_date(x_data, line, linestyle="solid", color=colors[i], linewidth=widths[i], label=labels[i])

        if "scatter" in plot_type:
            plt.scatter(x_data, line, color=colors[i])
        if "monthly" in plot_type:
            date_format = mdates.DateFormatter('%b,%Y')
            plt.xaxis.set_major_formatter(date_format)
        i+=1
    if error_lines != None:
        plt.fill_between(x_data, error_lines[0], error_lines[1], facecolor='grey', edgecolor='none', alpha=0.20)
    plt.legend()
    canvas = FigureCanvasTkAgg(figure, frame)
    canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
    canvas.draw()


def convert_to_monthly(time):
    """
    Converts timeseries x-axis into monthly units with proper labels
    Input:
    - time: an array of day numbers (15, 45, 75, etc.)
    """
    global START_YEAR
    start_date = dt.date(START_YEAR, 1, 1)
    dates = []
    for day in time:
        new_date = start_date + dt.timedelta(days=day-1)
        dates.append(new_date)
    return dates

def convert_to_annual(data):
    """
    Converts timeseries data into annually averaged data with proper axis labels
    Input:
    - data: the y-axis of the timeseries data
    """
    global START_YEAR
    start_date = dt.date(START_YEAR, 7, 2)
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
TITLE_FONT = ("Courier New", 12) #43
LARGE_FONT = ("Courier New", 12) #26
MED_FONT = ("Consolas", 8) #12
f = ("Consolas", 8) #12
f_slant = ("Consolas", 8, "italic") #12
START_YEAR = None
INPUT = None
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
        #self.minsize(600, 300)
        # self.wm_iconbitmap('icon.ico')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others

        self.frames = {}
        self.pages = [StartPage, PageEnvModel]
        for F in self.pages:
            page_name = F.__name__
            frame = F(parent=self)
            self.frames[page_name] = frame

        self.show_frame(["StartPage", "PageEnvModel"], "StartPage")

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



class StartPage(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
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
        label = tk.Label(self.scrollable_frame,
                         text="PRYSMv2.0: Lake PSM",
                         fg="black",
                         font=TITLE_FONT)
        label.pack(pady=(40, 20), padx=10)

        # background image
        photo = PhotoImage(file="resize_640.png")
        label = tk.Label(self.scrollable_frame, image=photo, anchor=tk.CENTER)
        label.image = photo  # keep a reference!
        label.pack(pady=2, padx=10)

        lake_label = tk.Label(self.scrollable_frame,
                              text="Aerial view of Lake Tanganyika",
                              font=f_slant)
        lake_label.pack(pady=(0, 10), padx=10)

        descrip = tk.Label(self.scrollable_frame,
                           text="A graphical user interface for Climate Proxy System Modeling Tools in Python",
                           font=MED_FONT,
                           anchor=tk.CENTER,
                           justify="center")
        descrip.pack(pady=1, padx=10)

        authors = tk.Label(self.scrollable_frame,
                           text="By: Henry Qin, Xueyan Mu, Vinay Tummarakota, and Sylvia Dee",
                           font=MED_FONT,
                           justify="center")
        authors.pack(pady=1, padx=10)

        website = tk.Label(self.scrollable_frame,
                           text="Getting Started Guide",
                           fg="SlateBlue2",
                           cursor="hand2",
                           font=MED_FONT,
                           justify="center")
        website.pack(pady=1, padx=10)
        website.bind("<Button-1>", lambda e: callback(
            "https://docs.google.com/document/d/1RHYEXm5AjXO3NppNxDLPmPnHPr8tQIaT_jH7F7pU2ic/edit?usp=sharing"))

        paper = tk.Label(self.scrollable_frame,
                         text="Original Paper, 2018",
                         fg="SlateBlue2",
                         cursor="hand2",
                         font=MED_FONT)
        paper.pack(pady=1, padx=10)
        paper.bind("<Button-2>", lambda e: callback(
            "https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2018PA003413"))

        github = tk.Label(self.scrollable_frame,
                          text="Github",
                          fg="SlateBlue2",
                          cursor="hand2",
                          font=MED_FONT)
        github.pack(pady=1, padx=10)
        github.bind("<Button-1>", lambda e: callback("https://github.com/henryyqin/LakeModelGUI"))

        # Leads to Run Lake Env Model
        envModelButton = tk.Button(self.scrollable_frame, text="Run Lake Environment Model", font=f,
                                   command=lambda: self.parent.show_frame(["StartPage"], "PageEnvModel"))
        envModelButton.pack(ipadx=43, ipady=3, pady=(10, 5))

        # Leads to PageEnvTimeSeries
        envTimeSeriesButton = tk.Button(self.scrollable_frame, text="Plot Environment Time Series", font=f,
                                        command=lambda: self.parent.show_frame(["StartPage"], "PageEnvTimeSeries"))
        envTimeSeriesButton.pack(ipadx=30, ipady=3, pady=(2,5))


        # Leads to PageEnvSeasonalCycle
        envTimeSeriesButton = tk.Button(self.scrollable_frame, text="Plot Environment Seasonal Cycle", font=f,
                                        command=lambda: self.parent.show_frame(["StartPage"], "PageEnvSeasonalCycle"))
        envTimeSeriesButton.pack(ipadx=37, ipady=3, pady=(2,5))


        # Leads to PageCarbonate
        carbButton = tk.Button(self.scrollable_frame, text="Run Carbonate Model", font=f,
                    command=lambda: self.parent.show_frame(["StartPage"], "PageCarbonate"))
        carbButton.pack(ipadx=37, ipady=3, pady=(2,5))


        # Leads to PageGDGT
        gdgtButton = tk.Button(self.scrollable_frame, text="Run GDGT Model", font=f,
                               command=lambda: self.parent.show_frame(["StartPage"], "PageGDGT"))
        gdgtButton.pack(ipadx=37, ipady=3, pady=(2,5))


        # Leads to PageLeafwax
        leafwaxButton = tk.Button(self.scrollable_frame, text="Run Leafwax Model", font=f,
                                  command=lambda: self.parent.show_frame(["StartPage"], "PageLeafwax"))
        leafwaxButton.pack(ipadx=37, ipady=3, pady=(2,5))


        # Leads to PageBioturbation
        bioButton = tk.Button(self.scrollable_frame, text="Run Bioturbation Model", font=f,
                              command=lambda: self.parent.show_frame(["StartPage"], "PageBioturbation"))
        bioButton.pack(ipadx=37, ipady=3, pady=(2,50))

"""
Page to run the environment model
"""
class PageEnvModel(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        s = ttk.Style()
        s.configure('new.TFrame', background='#FFFFFF')
        self.scrollable_frame = ttk.Frame(canvas, style='new.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        x0 = self.scrollable_frame.winfo_screenwidth() / 2
        y0 = self.scrollable_frame.winfo_screenheight() / 2
        print(x0, y0)
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        rowIdx = 1

        # Title
        label = tk.Label(self.scrollable_frame, text="Run Lake Environment Model", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3)

        rowIdx += 3

        # Instructions for uploading .txt and .inc files
        tk.Label(self.scrollable_frame,
                text="1) Upload a text file to provide input data for the lake model\n2) Enter lake-specific and simulation-specific parameters\n3) If parameters are left empty, default parameters for Lake Tanganyika will be used",
                font=f, justify="left"
                 ).grid(row=rowIdx,  columnspan=1, rowspan=1, pady=15, ipady=0, sticky="W")
        rowIdx += 3

        # Allows user to upload .txt data.
        tk.Label(self.scrollable_frame, text="Click to upload your .txt file:", font=f).grid(
            row=rowIdx, column=0, pady=10, sticky="W")
        graphButton = tk.Button(self.scrollable_frame, text="Upload .txt File", font=f,
                                command=self.uploadTxt)
        graphButton.grid(row=rowIdx, column=0, padx=340,
                         ipadx=10, ipady=3, sticky="W")
        rowIdx += 1

        # Shows the name of the current uploaded file, if any.
        tk.Label(self.scrollable_frame, text="Current File Uploaded:", font=f).grid(
            row=rowIdx, column=0, sticky="W")
        self.currentTxtFileLabel = tk.Label(self.scrollable_frame, text="No file", font=f)
        self.currentTxtFileLabel.grid(
            row=rowIdx, column=0, columnspan=2, ipady=3, padx=340, pady=(2,10), sticky="W")
        rowIdx+=1

        # Autofill buttons
        malawiButton = tk.Button(self.scrollable_frame, text="Autofill Malawi Parameters", font=f,
                                 command=lambda: self.fill("Malawi", param_containers))
        malawiButton.grid(row=rowIdx, column=0, ipadx=30, ipady=3, sticky="W")

        tanganyikaButton = tk.Button(self.scrollable_frame, text="Autofill Tanganyika Parameters", font=f,
                                     command=lambda: self.fill("Tanganyika", param_containers))
        tanganyikaButton.grid(row=rowIdx, column=0, padx=340, ipadx=30, ipady=3, sticky="W")

        rowIdx += 3

        # Entries for .inc file
        parameters = ["Obliquity", "Latitude (Negative For South)", "Longitude (Negative For West)",
              "Local Time Relative To Gmt In Hours", "Depth Of Lake At Sill In Meters",
              "Elevation Of Basin Bottom In Meters", "Area Of Catchment+Lake In Hectares",
              "Neutral Drag Coefficient", "Shortwave Extinction Coefficient (1/M)",
              "Fraction Of Advected Air Over Lake", "Albedo Of Melting Snow", "Albedo Of Non-Melting Snow",
              "Prescribed Depth In Meters", "Prescribed Salinity In Ppt", "D18o Of Air Above Lake",
              "Dd Of Air Above Lake", "Temperature To Initialize Lake At In INIT_LAKE Subroutine",
              "Dd To Initialize Lake At In INIT_LAKE Subroutine",
              "D18o To Initialize Lake At In INIT_LAKE Subroutine", "Number Of Years For Spinup",
              "True For Explict Boundry Layer Computations; Presently Only For Sigma Coord Climate Models",
              "Sigma Level For Boundary Flag", "True For Variable Lake Depth", "True For Variable Ice Cover",
              "True For Variable Salinity", "True For Variable D18o", "True For Variable Dd",
              "Height Of Met Inputs", "Start Year"]
        param_values = []
        param_containers = []
        tk.Label(self.scrollable_frame, text="Lake-Specific Parameters", font=LARGE_FONT).grid(
            row=rowIdx, column=0, pady=10, sticky="W")
        tk.Label(self.scrollable_frame, text="Simulation-Specific Parameters", font=LARGE_FONT).grid(
            row=rowIdx, column=0, pady=10, padx=750, sticky="W")
        rowIdx += 1

        # List entries for lake-specific parameters
        for i in range(rowIdx, rowIdx + 19):
            tk.Label(self.scrollable_frame, text=parameters[i - rowIdx], font=f).grid(
                row=i, column=0, sticky="W")
            p = tk.Entry(self.scrollable_frame)
            p.grid(row=i, column=0, padx=550, sticky="W")
            param_values.append(p)
            param_containers.append(p)

        # List entries for simulation-specific parameters
        for i in range(rowIdx + 19, rowIdx + 29):
            tk.Label(self.scrollable_frame, text=parameters[i - rowIdx], font=f).grid(
                row=i - 19, column=0, padx=750, sticky="W")
            if i in [rowIdx + 19, rowIdx + 21, rowIdx + 27, rowIdx + 28]:
                p = tk.Entry(self.scrollable_frame)
                p.grid(row=i - 19, column=0, padx=1300, sticky="W")
                param_containers.append(p)
            else:
                p = tk.IntVar()
                c = tk.Checkbutton(self.scrollable_frame, variable=p)
                c.grid(row=i - 19, column=0, padx=1300, sticky="W")
                param_containers.append(c)
            param_values.append(p)

        rowIdx += 19

        # Submit entries for .inc file
        submitButton = tk.Button(self.scrollable_frame, text="Submit Parameters", font=f,
                                 command=lambda: self.editInc([p.get() for p in param_values], parameters))
        submitButton.grid(row=rowIdx, column=0, padx=1300, ipadx=3, ipady=3, sticky="W")
        rowIdx += 1


        # Button to run the model (Mac/Linux only)
        runButton = tk.Button(
            self.scrollable_frame, text="Run Model", font=f,command=self.compileModel)
        runButton.grid(row=rowIdx, column=0, padx=1300, ipadx=30, ipady=3, sticky="W")
        rowIdx+=1

        csvButton = tk.Button(self.scrollable_frame, text='Download CSV', font=f, command=lambda: self.download_csv())
        csvButton.grid(row=rowIdx, column=0, padx=1300, ipadx=30, ipady=3, sticky="W")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", font=f,
                               command=lambda: self.parent.show_frame(["PageEnvModel"], "StartPage"))
        # previousPageB.pack(anchor = "w", side = "bottom")
        homeButton.grid(row=rowIdx, column=0, ipadx=25,
                        ipady=3, pady=3, sticky="W")
        rowIdx += 1
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
            if len(new) == 0:
                new.append(INPUT + "\n")
            else:
                new[0] = INPUT + "\n"
            write_to_file(vars, new)

        base = basename(self.txtfilename)
        nonbase = (self.txtfilename.replace("/", "\\")).replace(base, '')[:-1]
        self.currentTxtFileLabel.configure(text=base)

        # Modify the Fortran code to read the input text file
        with open("env_heatflux.f90", "r+") as f:
            new = f.readlines()
            if self.txtfilename != "":
                if nonbase == os.getcwd():
                    new[19] = "      !data_input_filename = '" + base + "'\n"
                else:
                    new[19] = "      !data_input_filename = '" + self.txtfilename + "'\n"
            write_to_file(f, new)

        # Modify the include file to read the input text file
        with open("Malawi.inc", "r+") as f:
            new = f.readlines()
            if self.txtfilename != "":
                if nonbase == os.getcwd():
                    new[
                        55] = "      character(38) :: datafile='" + base + "' ! the data file to open in FILE_OPEN subroutine\n"
                    new[56] = "      character(38) :: datafile='" + base + "'\n"
                else:
                    new[
                        55] = "      character(38) :: datafile='" + self.txtfilename + "' ! the data file to open in FILE_OPEN subroutine\n"
                    new[56] = "      character(38) :: datafile='" + self.txtfilename + "'\n"
            write_to_file(f, new)

    """
    Checks whether a string represents a valid signed/unsigned floating-point number

    Inputs:
    - str: a string that should represent a floating-point number
    Returns: 
    - True if str represents a float, False otherwise
    """

    def check_float(self, str):
        try:
            float(str)
            return True
        except:
            return False

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
                if not self.check_float(parameters[i]):
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
            if len(new) <= 1:
                new.append(str(START_YEAR))
            else:
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
            rows = [28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 41, 42, 44, 45, 57, 58, 59, 62, 63, 64, 65, 66, 67,
                    68, 69, 70]
            for i in range(len(parameters) - 1):
                if len(str(parameters[i])) != 0:
                    if i == 20 or (i > 21 and i < 27):
                        if parameters[i] == 1:
                            new[rows[i]] = "      parameter (" + names[i] + " = .true.)   ! " + comments[i] + "\n"
                        else:
                            new[rows[i]] = "      parameter (" + names[i] + " = .false.)   ! " + comments[i] + "\n"
                    else:
                        new[rows[i]] = "      parameter (" + names[i] + " = " + parameters[i] + ")   ! " + comments[
                            i] + "\n"
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
        else:
            values = ["23.4", "-6.30", "29.5", "+3", "999", "733.", "23100000.",
                      "2.0e-3", "0.065", "0.3", "0.4", "0.7", "570", "0.0", "-14.0", "-96.",
                      "23.0", "24.0", "3.7", "10", 0, "0.9925561", 0, 0, 0, 0, 0, "5.0", "1979"]
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
    Compiles the Fortran model by executing Cygwin commands to run gfortran
    """
    def compileModel(self):
        response = tk.messagebox.askyesno(title="Run Model", message="Running the model will take several minutes, and "
                                                                     "GUI functionality will temporarily stop. You will receive a notification "
                                                                     "once the model has finished. Do you wish to proceed?")
        #user agrees to run the model
        if response == 1:
            cygwin1 = Popen(['bash'], stdin=PIPE, stdout=PIPE)
            result1 = cygwin1.communicate(input=b"gfortran -o 'TEST1' env_heatflux.f90")
            print(result1)
            self.runModel()
            tk.messagebox.showinfo(title="Run Model", message="Model has completed running. You will find "
                                                              "surface_output.dat located in your "
                                                              "current working directory.")
        #user does not agree to run the model
        else:
            pass

    """
    Executes the file created by compiling the Fortran model in gfortran
    """
    def runModel(self):
        cygwin2 = Popen(['bash'], stdin=PIPE, stdout=PIPE)
        result2 = cygwin2.communicate(input=b"./TEST1.exe")
        print(result2)


    """
    Downloads 'surface_output.dat' as a CSV to the user's desired location
    """
    def download_csv(self):
        read_file = pd.read_csv("ERA-HIST-Tlake_surf.dat")
        export_file_path = fd.asksaveasfilename(defaultextension='.csv')
        read_file.to_csv(export_file_path, index=None)


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()


