# tkinter imports
import tkinter as tk
from tkinter import Canvas, Image, PhotoImage, font
import tkinter.filedialog as fd
from tkinter import ttk

# Sensor Model Scripts
import sensor_carbonate as carb
import sensor_gdgt as gdgt
import sensor_leafwax as leafwax

# Archive Model Scripts
import lake_archive_bioturb as bio
import lake_archive_compact as comp

# Data Analytics
import pandas as pd
import numpy as np
import matplotlib

# Imports for plotting
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from statistics import mean

plt.style.use('seaborn-whitegrid')
matplotlib.use('TkAgg')  # Necessary for Mac

# Imports for Observation Model
from rpy2.robjects import FloatVector
from rpy2.robjects.vectors import StrVector
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import rpy2.robjects.numpy2ri

rpy2.robjects.numpy2ri.activate()

# Miscellaneous imports
import os
import sys
from os.path import basename
import webbrowser
import copy
from subprocess import PIPE, Popen
from tkinter.ttk import Label
from tkinter.filedialog import asksaveasfilename

# ===========GENERAL FUNCTIONS========================================
def callback(url):
    """
    Opens a website URL on the user's default browser

    Input:
    - url: the URL link for a website
    """
    webbrowser.open_new(url)

def check_float(str):
    """
    Determines whether the input string represents a floating point number

    Input:
    - str: a string that should represent a floating-point number
    Returns:
    - True if the string is a float-point number, False otherwise
    """
    try:
        float(str)
        return True
    except:
        tk.messagebox.showerror(title="Run Model", message="Value entered was not a floating-point number")
        return False


def initialize_global_variables():
    """
    Reads global_vars.txt to initialize global variables with pre-existing values
    from previous runs of the GUI
    """
    with open("global_vars.txt", "r") as start:
        lines = start.readlines()
        global INPUT
        if len(lines) >=1:
            INPUT = lines[0]
            global START_YEAR
            if len(lines) >=2:
                START_YEAR = int(lines[1])

def write_to_file(file, data):
    """
    Writes data to a specified file
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
    Retrieves data from a lake model output file for years that are not nspin data
    Inputs
    - time: an empty array which the function populates with day #'s
    - data: an empty array which the function populates with a certain column of data from the lake model output file
    - column: the specific column of data in the lake model output file which should populate "data"
    - filename: the lake model output file which contains the desired data
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
    - type: indicates whether the file is sample data or user-uploaded
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
    Inputs:
    - frame: the page in the GUI where the plot is located
    - axes: the axes which allow plotting capabilities
    - figure: the figure on which the plot is placed
    - title: the title displayed on the plot
    - x_axis: the x-axis label
    - y_axis: the y-axis label
    """
    canvas = FigureCanvasTkAgg(figure, frame)
    canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=9, sticky="nw")
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
    - figure: the figure on which the plot is placed
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
    if not overlay:
        plt.cla()
    axes.set_title(title)
    axes.set_xlabel(x_axis)
    axes.set_ylabel(y_axis)
    i = 0
    for line in y_data:
        if "no-marker" in plot_type:
            axes.plot(x_data, line, linestyle="solid", color=colors[i], linewidth=widths[i], label=labels[i])
        else:
            axes.plot(x_data, line, linestyle="solid", color=colors[i], linewidth=widths[i], label=labels[i], marker="o")
        i += 1
    if error_lines != None:
        axes.fill_between(x_data, error_lines[0], error_lines[1], facecolor='grey', edgecolor='none', alpha=0.20)
    axes.legend()


def convert_to_monthly(time, start=None):
    """
    Converts timeseries x-axis into monthly units with proper labels

    Inputs:
    - time: an array of day numbers (15, 45, 75, etc.)
    - start: a user-specified value for the start of the time axis, None by default
    Returns:
    - dates: a range of months encapsulating the time array
    """
    start_year = copy.copy(start)
    if start_year == None:
        global START_YEAR
        start_year = copy.copy(START_YEAR)
    months = [0,1/12,2/12,3/12,4/12,5/12,6/12,7/12,8/12,9/12,10/12,11/12]
    dates = []
    for i in range(len(time)):
        if (i+1)%12==0:
            start_year += 1
        month_year = months[(i+1)%12]+start_year
        dates.append(month_year)
    return dates

def convert_to_annual(data, start=None):
    """
    Converts timeseries data into annually averaged data with proper axis labels

    Input:
    - data: the y-axis (or axes) of the timeseries data
    - start: a user-specified value for the start of the time axis, None by default
    Returns:
    - years: a range of years encapsulating the data
    - all_year_avgs: a y-axis (or axes) that contain(s) yearly averaged data
    """
    start_year = copy.copy(start)
    if start==None:
        global START_YEAR
        start_year = copy.copy(START_YEAR)
    start_year+=0.5
    years = []
    for i in range(len(data[0])):
        if (i+1)%12==0:
            years.append(start_year)
            start_year+=1
    all_year_avgs = []
    for column in data:
        year_data = []
        year_avgs = []
        for i in range(len(column)):
            year_data.append(column[i])
            if (i + 1) % 12 == 0:
                year_avgs.append(mean(year_data))
                year_data.clear()
        all_year_avgs.append(year_avgs)
    return years, all_year_avgs


# ================GLOBAL VARIABLES==================================================
TITLE_FONT = ("Courier New", 43)  # 43
LARGE_FONT = ("Courier New", 26)  # 26
MED_FONT = ("Consolas", 12)  # 12
f = ("Consolas", 12)  # 12
f_slant = ("Consolas", 12, "italic")  # 12
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
                         "PageCarbonate", "PageGDGT", "PageLeafwax", "PageObservation", "PageBioturbation",
                         "PageCompaction"], "StartPage")
        self.protocol('WM_DELETE_WINDOW', self.close_app)

    def show_frame(self, old_pages, new_page):
        """
        Shows a particular frame of the GUI to the user
        Inputs:
        - old_pages: the pages that should be hidden from the user
        - new_page: the page that should be visible to the user
        """
        for old_page in old_pages:
            old = self.frames[old_page]
            old.destroy()
            self.frames.pop(old_page)

        for F in self.pages:
            if F.__name__ == new_page:
                new = F(parent=self)
                self.frames[new_page] = new

    def close_app(self):
        """
        Closes the GUI and ends any associated command line processes
        """
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
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        x0 = self.scrollable_frame.winfo_screenwidth() / 2
        y0 = self.scrollable_frame.winfo_screenheight() / 2
        canvas.create_window((x0, y0), window=self.scrollable_frame, anchor="center")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        """
        Populates this frame of the GUI with labels, buttons, and other features
        """
        label = tk.Label(self.scrollable_frame,
                         text="PRYSMv2.0: Lake PSM",
                         fg="black",
                         font=TITLE_FONT)
        label.pack(pady=(40, 20), padx=10)

        # background image
        photo = PhotoImage(file="resize_640.png")
        label = Label(self.scrollable_frame, image=photo, anchor=tk.CENTER)
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
            "https://docs.google.com/document/d/1vMu0Oq28dl5XCFVTw6FQYwND3VMWl8S2lWzDw1RC5oY/edit?usp=sharing"))

        paper = tk.Label(self.scrollable_frame,
                         text="Original Paper, 2018",
                         fg="SlateBlue2",
                         cursor="hand2",
                         font=MED_FONT)
        paper.pack(pady=1, padx=10)
        paper.bind("<Button-1>", lambda e: callback(
            "https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2018PA003413"))

        github = tk.Label(self.scrollable_frame,
                          text="Github",
                          fg="SlateBlue2",
                          cursor="hand2",
                          font=MED_FONT)
        github.pack(pady=1, padx=10)
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
            button.pack(ipadx=37, ipady=3, pady=(2, 5))


"""
Page to run the environment model
"""


class PageEnvModel(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self, bg="white", bd=50)
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

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        """
        Populates this frame of the GUI with labels, buttons, and other features
        """
        rowIdx = 1

        # Title
        label = tk.Label(self.scrollable_frame, text="Run Lake Environment Model", font=LARGE_FONT)
        label.grid(sticky="W")

        rowIdx += 1

        # Instructions for uploading .txt and .inc files
        tk.Label(self.scrollable_frame,
                 text="1) Upload a text file to provide input data for the lake model\n2) Enter lake-specific and simulation-specific parameters\n3) If parameters are left empty, default parameters for Lake Tanganyika will be used",
                 font=f, justify="left"
                 ).grid(row=rowIdx, columnspan=1, rowspan=1, pady=15, ipady=0, sticky="W")
        rowIdx += 3

        # Allows user to upload .txt data.
        tk.Label(self.scrollable_frame, text="Click to upload your .txt file:", font=f).grid(
            row=rowIdx, pady=10, sticky="W")
        graphButton = tk.Button(self.scrollable_frame, text="Upload .txt File", font=f,
                                command=self.uploadTxt)
        graphButton.grid(row=rowIdx, padx=340,
                         ipadx=10, ipady=3, sticky="W")
        rowIdx += 1

        # Shows the name of the current uploaded file, if any.
        tk.Label(self.scrollable_frame, text="Current File Uploaded:", font=f).grid(
            row=rowIdx, sticky="W")
        self.currentTxtFileLabel = tk.Label(self.scrollable_frame, text="No file", font=f)
        self.currentTxtFileLabel.grid(
            row=rowIdx, columnspan=2, ipady=3, padx=340, pady=(2, 10), sticky="W")
        rowIdx += 1

        # Autofill buttons
        malawiButton = tk.Button(self.scrollable_frame, text="Autofill Malawi Parameters", font=f,
                                 command=lambda: self.fill("Malawi", param_containers))
        malawiButton.grid(row=rowIdx, ipadx=30, ipady=3, sticky="W")

        tanganyikaButton = tk.Button(self.scrollable_frame, text="Autofill Tanganyika Parameters", font=f,
                                     command=lambda: self.fill("Tanganyika", param_containers))
        tanganyikaButton.grid(row=rowIdx, padx=340, ipadx=30, ipady=3, sticky="W")

        refillButton = tk.Button(self.scrollable_frame, text="Autofill Previously Saved Parameters", font=f,
                                 command=lambda: self.fill("Refill", param_containers))
        refillButton.grid(row=rowIdx, padx=720, ipadx=30, ipady=3, sticky="W")

        clearButton = tk.Button(self.scrollable_frame, text="Clear Parameters", font=f,
                                command=lambda: self.fill("Clear", param_containers))
        clearButton.grid(row=rowIdx, padx=1150, ipadx=30, ipady=3, sticky="W")

        rowIdx += 3

        # Entries for .inc file
        parameters = ["Obliquity", "Latitude (Negative For South)", "Longitude (Negative For West)",
                      "Local Time Relative To Gmt In Hours", "Depth Of Lake At Sill In Meters",
                      "Elevation Of Basin Bottom In Meters", "Area Of Catchment+Lake In Hectares",
                      "Neutral Drag Coefficient", "Shortwave Extinction Coefficient (1/M)",
                      "Fraction Of Advected Air Over Lake", "Albedo Of Melting Snow", "Albedo Of Non-Melting Snow",
                      "Prescribed Depth In Meters", "Prescribed Salinity In Ppt", "\u0394¹⁸o Of Air Above Lake",
                      "\u0394d Of Air Above Lake", "Temperature To Initialize Lake At In\nINIT_LAKE Subroutine",
                      "Dd To Initialize Lake At In\nINIT_LAKE Subroutine",
                      "\u0394¹⁸o To Initialize Lake At In\nINIT_LAKE Subroutine", "Number Of Years For Spinup",
                      "Check Mark For Explict Boundary Layer Computations;\nPresently Only For Sigma Coord Climate Models",
                      "Sigma Level For Boundary Flag", "Check Mark For Variable Lake Depth",
                      "Check Mark For Variable Ice Cover",
                      "Check Mark For Variable Salinity", "Check Mark For Variable \u0394¹⁸o",
                      "Check Mark For Variable \u0394d",
                      "Height Of Met Inputs", "Check Mark for Relative Humidity", "Start Year"]
        param_values = []
        param_containers = []
        tk.Label(self.scrollable_frame, text="Lake-Specific Parameters", font=LARGE_FONT).grid(
            row=rowIdx, pady=10, sticky="W")
        tk.Label(self.scrollable_frame, text="Simulation-Specific Parameters", font=LARGE_FONT).grid(
            row=rowIdx, pady=10, padx=720, sticky="W")
        rowIdx += 1

        # List entries for lake-specific parameters
        for i in range(rowIdx, rowIdx + 19):
            tk.Label(self.scrollable_frame, text=parameters[i - rowIdx], font=f).grid(
                row=i, column=0, sticky="W")
            p = tk.Entry(self.scrollable_frame)
            p.grid(row=i, column=0, padx=390, sticky="W")
            param_values.append(p)
            param_containers.append(p)

        # List entries for simulation-specific parameters
        for i in range(rowIdx + 19, rowIdx + 30):
            tk.Label(self.scrollable_frame, text=parameters[i - rowIdx], font=f).grid(
                row=i - 19, column=0, padx=720, sticky="W")
            if i in [rowIdx + 19, rowIdx + 21, rowIdx + 27, rowIdx + 29]:
                p = tk.Entry(self.scrollable_frame)
                p.grid(row=i - 19, column=0, padx=1120, sticky="W")
                param_containers.append(p)
            else:
                p = tk.IntVar()
                c = tk.Checkbutton(self.scrollable_frame, variable=p)
                c.grid(row=i - 19, column=0, padx=1120, sticky="W")
                param_containers.append(c)
            param_values.append(p)

        rowIdx += 19

        # Submit entries for .inc file
        submitButton = tk.Button(self.scrollable_frame, text="Save Parameters", font=f,
                                 command=lambda: self.editInc([p.get() for p in param_values], parameters))
        submitButton.grid(row=rowIdx, column=0, padx=1120, ipadx=30, ipady=3, sticky="W")
        rowIdx += 1

        # Button to run the model (Mac/Linux only)
        runButton = tk.Button(
            self.scrollable_frame, text="Run Model", font=f, command=self.compileModel)
        runButton.grid(row=rowIdx, column=0, padx=1120, ipadx=30, ipady=3, sticky="W")
        rowIdx += 1

        csvButton = tk.Button(self.scrollable_frame, text='Download CSV', font=f, command=self.download_csv)
        csvButton.grid(row=rowIdx, column=0, padx=1120, ipadx=30, ipady=3, sticky="W")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", font=f, bg="azure",
                               command=lambda: self.parent.show_frame(["PageEnvModel"], "StartPage"))
        # previousPageB.pack(anchor = "w", side = "bottom")
        homeButton.grid(row=rowIdx, column=0, ipadx=25,
                        ipady=3, pady=3, sticky="W")
        rowIdx += 1

    def uploadTxt(self):
        """
        Allows the user to upload an input .txt file for the lake model
        """
        # Open the file choosen by the user
        self.txtfilename = fd.askopenfilename(
            filetypes=(('text files', 'txt'),))
        global INPUT
        INPUT = self.txtfilename

        # Edit global_vars.txt to store the new input file for future access
        with open("global_vars.txt", "r+") as vars:
            new = vars.readlines()
            if len(new) >= 1:
                new[0] = INPUT + "\n"
            else:
                new.append(INPUT+"\n")
            write_to_file(vars, new)

        base = basename(self.txtfilename)
        nonbase = (self.txtfilename.replace("/", "\\")).replace(base, '')[:-1]
        self.currentTxtFileLabel.configure(text=base)
        print(nonbase, os.getcwd())


        # Modify the Fortran code to read the input text file
        with open("env_heatflux.f90", "r+") as f:
            new = f.readlines()
            if self.txtfilename != "":
                if nonbase == os.getcwd():
                    new[19] = "      !data_input_filename = '" + base + "'\n"
                else:
                    new[19] = "      !data_input_filename = '" + self.txtfilename + "'\n"
            if len(new[19]) > 132:
                tk.messagebox.showerror(title="Run Lake Model", message="File path is longer than Fortran character limit. "
                                                                       "Either move input file to same directory as GUI executable"
                                                                       " or move input file to a directory with a shorter file path.")
                return
            write_to_file(f, new)

        # Modify the include file to read the input text file
        with open("lake_environment.inc", "r+") as f:
            new = f.readlines()
            if self.txtfilename != "":
                if nonbase == os.getcwd():
                    new[55] = "      character("+str(len(base))+") :: datafile='" + base + "' ! the data file to open in FILE_OPEN subroutine\n"
                else:
                    new[55] = "      character("+str(len(self.txtfilename))+") :: datafile='" + self.txtfilename + "' ! the data file to open in FILE_OPEN subroutine\n"
            if len(new[55]) > 132:
                tk.messagebox.showerror(title="Run Lake Model",
                                        message="File path is longer than Fortran character limit. "
                                                "Either move input file to same directory as GUI executable"
                                                " or move input file to a directory with a shorter file path.")
                return False
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
            if (i == 29):
                try:
                    int(parameters[i])
                except:
                    tk.messagebox.showerror(title="Run Lake Model", message="Years must be integer values")
                    return False
        global START_YEAR
        START_YEAR = int(parameters[29])
        with open("global_vars.txt", "r+") as vars:
            new = vars.readlines()
            if len(new) >= 2:
                new[1] = str(START_YEAR)
            elif len(new) == 1:
                new.append(str(START_YEAR))
            else:
                new.append("No Input File Provided")
                new.append(str(START_YEAR))
            write_to_file(vars, new)
        return True

    def editInc(self, parameters, comments):
        """
        Edits the parameters in the .inc file based on user input

        Inputs:
        - parameters: the values for the model parameters
        - comments: the comments in the Fortran code associated with each parameter
        """
        if not self.validate_params(parameters):
            return
        with open("lake_environment.inc", "r+") as f:
            new = f.readlines()
            # names of the parameters that need to be modified
            names = ["oblq", "xlat", "xlon", "gmt", "max_dep", "basedep", "b_area", "cdrn", "eta", "f", "alb_slush",
                     "alb_snow", "depth_begin", "salty_begin", "o18air", "deutair", "tempinit", "deutinit", "o18init",
                     "nspin", "bndry_flag", "sigma", "wb_flag", "iceflag", "s_flag", "o18flag", "deutflag", "z_screen",
                     "rhflag"]
            # line numbers in the .inc file that need to be modified
            rows = [28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 41, 42, 44, 45, 56, 57, 58, 61, 62, 63, 64, 65, 66, 67,
                    68, 69, 70]
            global PARAMETERS
            PARAMETERS = copy.copy(parameters)
            for i in range(len(parameters)-1):
                if len(str(parameters[i])) != 0:
                    comments[i] = comments[i].replace("\u0394", "D")
                    comments[i] = comments[i].replace("¹⁸", "18")
                    comments[i] = comments[i].replace("Check Mark", "true")
                    comments[i] = comments[i].replace("\n", "")
                    if i == 20 or (i > 21 and i < 27) or i==28:
                        if parameters[i] == 1:
                            new[rows[i]] = "      parameter (" + names[i] + " = .true.)   ! " + comments[i] + "\n"
                        else:
                            new[rows[i]] = "      parameter (" + names[i] + " = .false.)   ! " + comments[i] + "\n"
                    else:
                        new[rows[i]] = "      parameter (" + names[i] + " = " + parameters[i] + ")   ! " + comments[i] + "\n"
            write_to_file(f, new)


    def fill(self, lake, containers):
        """
        Fills in parameter values with either Malawi or Tanganyika parameters

        Inputs:
        - lake: determines which lake's parameters should populate the GUI
        - containers: the GUI entries and checkboxes that should be populated
        """
        if lake == "Malawi":
            values = ["23.4", "-12.11", "34.22", "+3", "292", "468.", "2960000.",
                      "1.7e-3", "0.04", "0.1", "0.4", "0.7", "292", "0.0", "-28.",
                      "-190.", "-4.8", "-96.1", "-11.3", "10", 0, "0.96", 0, 1,
                      0, 0, 0, "5.0", 1, "1979"]
        elif lake == "Tanganyika":
            values = ["23.4", "-6.30", "29.5", "+3", "999", "733.", "23100000.",
                      "2.0e-3", "0.065", "0.3", "0.4", "0.7", "570", "0.0", "-14.0", "-96.",
                      "23.0", "24.0", "3.7", "10", 0, "0.9925561", 0, 0, 0, 0, 0, "5.0", 1, "1979"]
        elif lake == "Refill":
            values = copy.copy(PARAMETERS)
        else:
            values = [""] * 20
            values.extend([0, "", 0, 0, 0, 0, 0, "", 0, ""])
        for i in range(len(values)):
            if i == 20 or (i > 21 and i < 27) or i==28:
                containers[i].deselect()
                if values[i] == 1:
                    containers[i].select()
                else:
                    containers[i].deselect()
            else:
                containers[i].delete(0, tk.END)
                containers[i].insert(0, values[i])


    def compileModel(self):
        """
        Compiles the Fortran model by executing Cygwin commands to run gfortran
        """
        response = tk.messagebox.askyesno(title="Run Model", message="Running the model will take several minutes, and "
                                                                     "GUI functionality will temporarily stop. You will receive a notification "
                                                                     "once the model has finished. Do you wish to proceed?")
        #user agrees to run the model
        if response == 1:
            cygwin1 = Popen(['bash'], stdin=PIPE, stdout=PIPE, shell=True)
            result1 = cygwin1.communicate(input=b"gfortran -o 'TEST1' env_heatflux.f90")
            print(result1)
            self.after(10000, self.runModel)
        #user does not agree to run the model
        else:
            pass

    def runModel(self):
        """
        Executes the file created by compiling the Fortran model in gfortran
        """
        cygwin2 = Popen(['bash'], stdin=PIPE, stdout=PIPE, shell=True)
        result2 = cygwin2.communicate(input=b"./TEST1.exe")
        print(result2)
        tk.messagebox.showinfo(title="Run Model", message="Model has completed running. You will find "
                                                          "surface_output.dat located in your "
                                                          "current working directory.")

    def download_csv(self):
        """
        Downloads the newly generated lake model output file as a CSV to the user's desired location
        """
        read_file = pd.read_csv("ERA-HIST-Tlake_surf.dat")
        export_file_path = fd.asksaveasfilename(defaultextension='.csv')
        read_file.to_csv(export_file_path, index=None)


"""
Page to plot environment model time series
"""


class PageEnvTimeSeries(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self, bg="white", bd=50)
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

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        """
        Populates this frame of the GUI with labels, buttons, and other features
        """
        rowIdx = 1
        # Title
        label = tk.Label(
            self.scrollable_frame, text="Environment Model Time Series", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0, 5))
        rowIdx += 3

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, text="Current File Uploaded:", font=f).grid(
            row=rowIdx + 2, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx + 2, column=1, columnspan=2, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, text="Click to load data", font=f).grid(
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
        self.f, self.axis = plt.subplots(1, 1, figsize=(9, 5), dpi=100)
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
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", font=f, bg="azure",
                               command=lambda: self.parent.show_frame(["PageEnvTimeSeries"], "StartPage"))
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")


    def generate_env_time_series(self, column, varstring):
        """
        Plots timeseries data using the lake model output file

        Inputs:
         - column: an int that corresponds to the column of the desired variable to be plotted
         - varstring: a string that is the name and unit of the variable
        """
        self.days = []  # x-axis
        self.yaxis = []  # y-axis

        units = ["", "("+u"\N{DEGREE SIGN}"+"C)", "(m)", "(mm/day)", "", "", "", "", "(m)"]

        get_output_data(self.days, self.yaxis, column, self.txtfilename)
        self.months = convert_to_monthly(self.days)
        plot_draw(self.scrollable_frame, self.axis, self.f, varstring + " over Time ", "Month", varstring+" "+units[column], self.months,
                  [self.yaxis],
                  "no-marker", ["#b22222"], [1], ["Monthly Data"])
        self.years, self.yaxes = convert_to_annual([self.yaxis])
        plot_draw(self.scrollable_frame, self.axis, self.f, varstring + " over Time", "Year (C.E.)", varstring+" "+units[column], self.years,
                  self.yaxes,
                  "normal", ["#000000"], [3], ["Annually Averaged Data"], overlay=True)

    def download_csv(self):
        """
        Downloads data represented in the plot as a .csv file
        """
        df = pd.DataFrame({"Time": self.days, "yaxis": self.yaxis})
        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            df.to_csv(file, index=False)
            tk.messagebox.showinfo("Success", "Saved Data")

    def download_png(self):
        """
        Downloads the plot as a .png file
        """
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
        canvas = tk.Canvas(self, bg="white", bd=50)
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

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        """
        Populates this frame of the GUI with labels, buttons, and other features
        """
        rowIdx = 1
        # Title
        label = tk.Label(
            self.scrollable_frame, text="Environment Model Seasonal Cycle", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0, 5))
        rowIdx += 3

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, text="Current File Uploaded:", font=f).grid(
            row=rowIdx + 2, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx + 2, column=1, columnspan=2, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, text="Click to load data", font=f).grid(
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
        self.f, self.axis = plt.subplots(1, 1, figsize=(9, 5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis, self.f, "Seasonal Cycle", "Day of the Year",
                   "Average Surface Temperature")

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
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", font=f, bg="azure",
                               command=lambda: self.parent.show_frame(["PageEnvSeasonalCycle"], "StartPage"))
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")

    def generate_env_seasonal_cycle(self, column, varstring):
        """
        Plots seasonal cycle data using the lake model output file

        Inputs:
         - column: an int that corresponds to the column of the desired variable to be plotted
         - varstring: a string that is the name and unit of the variable
        """
        self.days = []  # x-axis
        self.yaxis = []  # y-axis

        units = ["", "("+u"\N{DEGREE SIGN}"+"C)", "(m)", "(mm/day)", "", "", "", "", "(m)"]

        get_output_data(self.days, self.yaxis, column, self.txtfilename)

        # At this point, self.days and self.yaxis are identical to the ones in envtimeseries

        self.ydict = {}
        for idx in range(len(self.days)):
            if idx % 12 not in self.ydict:
                self.ydict[idx] = []
            self.ydict[idx % 12].append(self.yaxis[idx])

        # After yval array is formed for each xval, generate the axtual yaxis data
        self.seasonal_yaxis = []  # actual plotting data for y
        self.seasonal_days = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        global START_YEAR

        for i in range(12):  # CHANGE (change how seasonal days are created) 15, 45, 75... 345
            self.seasonal_yaxis.append(mean(self.ydict[i]))

        plot_draw(self.scrollable_frame, self.axis, self.f, varstring + " Seasonal Cycle", "Month", "Average "+varstring+" "+units[column],
                  self.seasonal_days,
                  [self.seasonal_yaxis], "normal", ["#000000"], [3], ["Monthly Averaged Data"])

    def download_csv(self):
        """
        Downloads data represented in the plot as a .csv file
        """
        df = pd.DataFrame({"Time": self.seasonal_days, "Pseudoproxy": self.seasonal_yaxis})
        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            df.to_csv(file, index=False)
            tk.messagebox.showinfo("Success", "Saved Data")

    def download_png(self):
        """
        Downloads the plot as a .png file
        """
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
        canvas = tk.Canvas(self, bg="white", bd=50)
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

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        """
        Populates this frame of the GUI with labels, buttons, and other features
        """
        rowIdx = 1

        # Title
        label = tk.Label(
            self.scrollable_frame, text="Carbonate Sensor Model", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0, 5))

        rowIdx += 3

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, text="Current File Uploaded:", font=f).grid(
            row=rowIdx + 2, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx + 2, column=1, columnspan=2, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, text="Click to load data", font=f).grid(
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

        self.model = tk.StringVar()
        self.model.set("ONeil")
        model_names = ["ONeil", "Kim-ONeil", "ErezLuz", "Bemis", "Lynch"]
        for name in model_names:
            tk.Radiobutton(self.scrollable_frame, text=name, font=MED_FONT, value=name, variable=self.model).grid(
                row=rowIdx, column=0,
                pady=1,
                ipadx=20, ipady=5,
                sticky="W")
            rowIdx += 1
        tk.Button(self.scrollable_frame, text="Generate Graph of Carbonate Proxy Data", font=MED_FONT,
                  command=self.generate_graph).grid(
            row=rowIdx, column=0, pady=(10, 5),
            ipadx=20, ipady=5, sticky="W")
        rowIdx+=3
        tk.Label(self.scrollable_frame, text="Citations:", font=MED_FONT, justify="left").grid(row=rowIdx, column=0, sticky="W")

        rowIdx+=1
        citations = ["- O’Neil, J. R., Clayton, R. N., & Mayeda, T. K. (1969).\n"
                     "Oxygen isotope fractionation in divalent metal carbonates.\n"
                     "The Journal of Chemical Physics, 51(12), 5547–5558.",
                     "- Kim, S.-T., & O’Neil, J. R. (1997).\n"
                     "Equilibrium and nonequilibrium oxygen isotope effects in synthetic carbonates.\n"
                     "Geochimica et Cosmochimica Acta, 61(16), 3461–3475.",
                     "- Erez, J., & Luz, B. (1983).\n"
                     "Experimental paleotemperature equation for planktonic foraminifera.\n"
                     "Geochimica et Cosmochimica Acta, 47(6), 1025–1031.",
                     "- Bemis, B. E., Spero, H. J., Bijma, J., & Lea, D. W. (1998).\n"
                     "Reevaluation of the oxygen isotopic composition of planktonic foraminifera:\n"
                     "Experimental results and revised paleotemperature equations. Paleoceanography, 13(2), 150–160.",
                     "- Jean Lynch (No Citation)"]
        citationLinks = ["https://aip.scitation.org/doi/abs/10.1063/1.1671982",
                         "https://www.sciencedirect.com/science/article/pii/S0016703797001695",
                         "https://www.sciencedirect.com/science/article/abs/pii/0016703783902326",
                         "https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/98PA00070"]
        for i in range(len(citations)):
            citation = tk.Label(self.scrollable_frame,
                               text=citations[i],
                               fg="SlateBlue2",
                               cursor="hand2",
                               font=MED_FONT,
                               justify="left")
            citation.grid(row=rowIdx, column=0, columnspan=10, pady=5, sticky="W")
            if i < 4:
                link = citationLinks[i]
                citation.bind("<Button-1>", lambda e, link=link: callback(link))
            rowIdx+=1

        # Save as PNG and CSV

        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")

        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", font=f, bg="azure",
                               command=lambda: self.parent.show_frame(["PageCarbonate"], "StartPage"))
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")

        self.f, self.axis = plt.subplots(1, 1, figsize=(9, 5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis, self.f, "SENSOR", "Time", "Simulated Carbonate Data (\u03b4$^{18}O_{carb}$)")

    def generate_graph(self):
        """
        Plots simulated carbonate data using the lake model output file
        """
        surf_tempr = []
        self.days = []
        get_output_data(self.days, surf_tempr, 1, self.txtfilename)
        self.LST = np.array(surf_tempr, dtype=float)
        self.d180w = -2
        self.carb_proxy = carb.carb_sensor(self.LST, self.d180w, model=self.model.get())

        self.months = convert_to_monthly(self.days)
        plot_draw(self.scrollable_frame, self.axis, self.f, "SENSOR", "Year (C.E.)", "Simulated Carbonate Data (\u03b4$^{18}O_{carb}$)", self.months,
                  [self.carb_proxy],
                  "no-marker", ["#b22222"], [1], ["Monthly Data"])

        self.years, self.yaxis = convert_to_annual([self.carb_proxy])
        plot_draw(self.scrollable_frame, self.axis, self.f, "SENSOR", "Year (C.E.)", "Simulated Carbonate Data (\u03b4$^{18}O_{carb}$)", self.years,
                  self.yaxis,
                  "normal", ["#000000"], [3], ["Annually Averaged Data"], overlay=True)

    def download_csv(self):
        """
        Downloads data represented in the plot as a .csv file
        """
        df = pd.DataFrame({"Time": self.days, "Pseudoproxy": self.carb_proxy})
        file = asksaveasfilename(initialfile="CarbonateData.csv", defaultextension=".csv")
        if file:
            df.to_csv(file, index=False)
            tk.messagebox.showinfo("Success", "Saved Carbonate data")

    def download_png(self):
        """
        Downloads the plot as a .png file
        """
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
        canvas = tk.Canvas(self, bg="white", bd=50)
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

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        """
        Populates this frame of the GUI with labels, buttons, and other features
        """
        rowIdx = 1
        # Title
        label = tk.Label(
            self.scrollable_frame, text="Run GDGT Sensor Model", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0, 5))

        rowIdx += 3

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, text="Current File Uploaded:", font=f).grid(
            row=rowIdx + 2, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx + 2, column=1, columnspan=2, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, text="Click to load data", font=f).grid(
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
                         ipadx=30, ipady=3, sticky="W")
        rowIdx += 4

        self.model = tk.StringVar()
        self.model.set("TEX86-tierney")
        model_names = ["TEX86-tierney", "TEX86-powers", "TEX86-loomis", "MBT-R", "MBT-J"]
        for name in model_names:
            tk.Radiobutton(self.scrollable_frame, text=name, value=name, font=MED_FONT, variable=self.model).grid(
                row=rowIdx, column=0,
                pady=5,
                ipadx=20, ipady=5,
                sticky="W")
            rowIdx += 1
        rowIdx += 1

        tk.Button(self.scrollable_frame, text="Generate Graph of GDGT Proxy Data", font=MED_FONT,
                  command=self.generate_graph).grid(
            row=rowIdx, column=0, pady=20, ipadx=20, ipady=5, sticky="W")
        rowIdx += 3
        tk.Label(self.scrollable_frame, text="Citations:", font=MED_FONT, justify="left").grid(row=rowIdx, column=0,
                                                                                               sticky="W")

        rowIdx += 1
        citations = ["- Tierney, J. E., Russell, J. M., Huang, Y., Damsté, J. S. S., Hopmans, E. C., & Cohen, A. S. (2008).\n"
                     "Northern Hemisphere controls on tropical southeast African climate during the past 60,000 years.\n"
                     "Science, 322(5899), 252–255.",
                     "- Powers, L. A., Johnson, T. C., Werne, J. P., Castañeda, I. S., Hopmans, E. C., Damsté, J. S. S., & Schouten, S. (2011).\n"
                     "Organic geochemical records of environmental variability in Lake Malawi during the last 700 years,\n"
                     "part I: The TEX86 temperature record. Palaeogeography, Palaeoclimatology, Palaeoecology, 303(1), 133–139.",
                     "- Loomis, S. E., Russell, J. M., Ladd, B., Street-Perrott, F. A., & Damsté, J. S. S. (2012).\n"
                     "Calibration and application of the branched GDGT temperature proxy on East African lake sediments.\n"
                     "Earth and Planetary Science Letters, 357, 277–288.",
                     "- Russell, J. M., Hopmans, E. C., Loomis, S. E., Liang, J., & Damsté, J. S. S. (2018).\n"
                     "Distributions of 5-and 6-methyl branched glycerol dialkyl glycerol tetraethers (brGDGTs) in East African lake sediment:\n"
                     "Effects of temperature, pH, and new lacustrine paleotemperature calibrations. Organic Geochemistry, 117, 56–69.",
                     "- De Jonge, C., Hopmans, E. C., Zell, C. I., Kim, J.-H., Schouten, S., & Damsté, J. S. S. (2014).\n"
                     "Occurrence and abundance of 6-methyl branched glycerol dialkyl glycerol tetraethers in soils:\n"
                     "Implications for palaeoclimate reconstruction. Geochimica et Cosmochimica Acta, 141, 97–112."]
        citationLinks = ["https://arizona.pure.elsevier.com/en/publications/northern-hemisphere-controls-on-tropical-southeast-african-climat",
                         "http://www.pitt.edu/~jwerne/uploads/3/0/1/0/30101831/29.powersetal.p311.pdf",
                         "http://www.jsg.utexas.edu/sloomis/files/Loomis_2012_GDGT-Calibration.pdf",
                         "https://www.sciencedirect.com/science/article/pii/S0146638017304394",
                         "https://www.sciencedirect.com/science/article/abs/pii/S0016703714004141"]
        for i in range(len(citations)):
            citation = tk.Label(self.scrollable_frame,
                                text=citations[i],
                                fg="SlateBlue2",
                                cursor="hand2",
                                font=MED_FONT,
                                justify="left")
            citation.grid(row=rowIdx, column=0, columnspan=10, pady=5, sticky="W")
            link = citationLinks[i]
            citation.bind("<Button-1>", lambda e, link=link: callback(link))
            rowIdx += 1
        # Save as PNG and CSV

        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")

        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", font=f, bg="azure",
                               command=lambda: self.parent.show_frame(["PageGDGT"], "StartPage"))
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")

        self.f, self.axis = plt.subplots(1, 1, figsize=(9, 5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis, self.f, "SENSOR", "Time", "Simulated GDGT Data (brGDGT / $TEX_{86}$)")

    def generate_graph(self):
        """
        Plots simulated GDGT data using the lake model output file
        """
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
        plot_draw(self.scrollable_frame, self.axis, self.f, "SENSOR", "Month", "Simulated GDGT Data (brGDGT / $TEX_{86}$)", self.months,
                  [self.gdgt_proxy],
                  "no-marker", ["#b22222"], [1], ["Monthly Data"])

        self.years, self.yaxis = convert_to_annual([self.gdgt_proxy])
        plot_draw(self.scrollable_frame, self.axis, self.f, "SENSOR", "Year (C.E.)", "Simulated GDGT Data (brGDGT / $TEX_{86}$)", self.years,
                  self.yaxis,
                  "normal", ["#000000"], [3], ["Annually Averaged Data"], overlay=True)

    def download_csv(self):
        """
        Downloads data represented in the plot as a .csv file
        """
        df = pd.DataFrame({"Time": self.days, "Pseudoproxy": self.gdgt_proxy})
        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            df.to_csv(file, index=False)
            tk.messagebox.showinfo("Success", "Saved Data")

    def download_png(self):
        """
        Downloads the plot as a .png file
        """
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
        canvas = tk.Canvas(self, bg="white", bd=50)
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

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        """
        Populates this frame of the GUI with labels, buttons, and other features
        """
        rowIdx = 1
        # Title
        label = tk.Label(
            self.scrollable_frame, text="Run Leafwax Model", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0, 5))

        rowIdx += 1

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, text="Current File Uploaded:", font=f).grid(
            row=rowIdx + 2, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx + 2, column=1, columnspan=2, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, text="Click to load data", font=f).grid(
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
        tk.Label(self.scrollable_frame, text="Start Year:", font=f).grid(
            row=rowIdx, column=0, sticky="W")
        start = tk.Entry(self.scrollable_frame)
        start.grid(row=rowIdx, column=1, sticky="W")

        rowIdx += 2
        self.f, self.axis = plt.subplots(1, 1, figsize=(9, 5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis, self.f, "SENSOR", "Time", "Simulated Leafwax Data (\u03b4D$_{wax}$)")

        tk.Button(self.scrollable_frame, text="Graph Leafwax Proxy Data", font=f,
                  command=lambda: self.generate_graph(start.get())).grid(
            row=rowIdx, column=0, sticky="W")

        # Save as PNG and CSV

        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")

        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", font=f, bg="azure",
                               command=lambda: self.parent.show_frame(["PageLeafwax"], "StartPage"))
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")

    def generate_graph(self, start_year):
        """
        Plots simulated leafwax data using an input file of isotope ratios in precipitation

        Input:
        - start_year: the start year for the data collected on isotope ratios in precipitation
        """
        try:
            int(start_year)
        except:
            tk.messagebox.showerror(title="Run Leafwax Model", message="Year must be an integer value")
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
        plot_draw(self.scrollable_frame, self.axis, self.f, "SENSOR", "Month", "Simulated Leaf Wax Data (\u03b4D$_{wax}$)", self.months,
                  [self.leafwax_proxy],
                  "no-marker", ["#b22222"], [1], ["Monthly Data"])

        self.years, self.leafwax_array = convert_to_annual([self.leafwax_proxy, self.Q1, self.Q2], start=start_year)
        plot_draw(self.scrollable_frame, self.axis, self.f, "SENSOR", "Year (C.E.)", "Simulated Leaf Wax Data (\u03b4D$_{wax}$)", self.years,
                  [self.leafwax_array[0]],
                  "normal", ["#000000"], [3], ["Annually Averaged Data"], error_lines=self.leafwax_array[1:],
                  overlay=True)

    def download_csv(self):
        """
        Downloads data represented in the plot as a .csv file
        """
        df = pd.DataFrame({"Time": self.days, "Pseudoproxy": self.leafwax_proxy, "95% CI Lower Bound": self.Q1,
                           "95% CI Upper Bound": self.Q2})

        export_file_path = fd.asksaveasfilename(defaultextension='.csv')
        df.to_csv(export_file_path, index=None)

    def download_png(self):
        """
        Downloads the plot as a .png file
        """
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
        canvas = tk.Canvas(self, bg="white", bd=50)
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

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        """
        Populates this frame of the GUI with labels, buttons, and other features
        """
        rowIdx = 1

        # Title
        label = tk.Label(
            self.scrollable_frame, text="Run Observation Model", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0, 5))
        rowIdx += 3

        # Instructions for uploading file
        tk.Label(self.scrollable_frame,
                 text=
                 """WARNING: Long running time\nInstructions for input file:\n1) The first row must be 'DP, AGE, SD'\n2) Ages must be in BP
                 """, font=f, justify="left"
                 ).grid(row=rowIdx, column=0, columnspan=1, rowspan=1, pady=10, ipady=0, sticky="W")
        rowIdx += 3

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, text="Current File Uploaded:", font=f).grid(
            row=rowIdx + 2, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx + 2, column=1, columnspan=2, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, text="Click to load data", font=f).grid(
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
        graphButton.grid(row=rowIdx, column=1, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        rowIdx += 4

        self.f, self.axis = plt.subplots(1, 1, figsize=(10, 5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis, self.f, "Observation Model", "Age (cal years BP)",
                   "Depth in Core (cm)")

        tk.Button(self.scrollable_frame, text="Graph Observation Model", font=MED_FONT,
                  command=lambda: self.generate_graph()).grid(
            row=rowIdx, column=0, pady=1,
            ipadx=20, ipady=5, sticky="W")

        # Save as PNG and CSV

        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")

        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", font=f, bg="azure",
                               command=lambda: self.parent.show_frame(["PageObservation"], "StartPage"))
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")

    """
    Plot observation model
    """

    def generate_graph(self):
        """
        Utilizes rpy2 to generate a graph of the observation model output
        """
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
                                facecolor='Silver', edgecolor='Silver',
                                lw=0.0)  # horizontal fill between 2.5% - 97.5% of data

        self.axis.plot(self.chronsQ[1], self.depth_horizons, color="black", lw=0.75)  # median line
        self.axis.scatter(data['AGE'], data['DP'], marker="s")  # squares
        self.axis.legend(['Median', '95% CI', 'Dated Positions'])
        self.axis.invert_xaxis()
        self.axis.invert_yaxis()
        self.axis.set_xlabel('Age (cal years BP)')
        self.axis.set_ylabel('Depth (mm)')

        canvas = FigureCanvasTkAgg(self.f, self.scrollable_frame)
        canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        canvas.draw()

    def download_csv(self):
        """
        Downloads data represented in the plot as a .csv file
        """
        df = pd.DataFrame({"Depth": self.depth_horizons, "Age (95% CI Lower Bound)": self.chronsQ[0],
                           "Age (95% CI Median)": self.chronsQ[0], "Age (95% CI Upper Bound)": self.chronsQ[2]})

        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            df.to_csv(file, index=False)
            tk.messagebox.showinfo("Success", "Saved Data")

    def download_png(self):
        """
        Downloads the plot as a .png file
        """
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
        canvas = tk.Canvas(self, bg="white", bd=50)
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

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        """
        Populates this frame of the GUI with labels, buttons, and other features
        """
        rowIdx = 1
        # Title
        label = tk.Label(
            self.scrollable_frame, text="Run Bioturbation Model", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(0, 5))
        rowIdx += 3

        # Instructions for uploading .txt and .inc files
        tk.Label(self.scrollable_frame,
                 text=
                 """1) Upload a .csv file with a column "Pseudoproxy",\n containing pseudoproxy timeseries data. \n2) Enter parameters for bioturbation\n3) You cannot leave parameters empty
                 """, font=f, justify="left"
                 ).grid(row=rowIdx, columnspan=3, rowspan=1, pady=10, ipady=0, sticky="W")
        rowIdx += 3

        # Shows the name of the current uploaded file, if any.
        self.txtfilename = ""
        tk.Label(self.scrollable_frame, text="Current File Uploaded:", font=f).grid(
            row=rowIdx + 2, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self.scrollable_frame, text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx + 2, column=1, columnspan=2, pady=10, sticky="W")

        # Upload example file
        tk.Label(self.scrollable_frame, text="Click to load data", font=f).grid(
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
            tk.Label(self.scrollable_frame, text=parameters[i - rowIdx], font=f).grid(
                row=i, column=0, sticky="W")
            p = tk.Entry(self.scrollable_frame)
            p.grid(row=i, column=1, sticky="W")
            param_values.append(p)
        rowIdx += 5
        tk.Button(self.scrollable_frame, text="Generate Graph", font=f,
                  command=lambda: self.run_bioturb_model([p.get() for p in param_values])).grid(
            row=rowIdx, column=0, sticky="W")

        # Save as PNG and CSV

        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")

        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", font=f, bg="azure",
                               command=lambda: self.parent.show_frame(["PageBioturbation"], "StartPage"))
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")

        self.f, self.axis = plt.subplots(1, 1, figsize=(9, 5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis, self.f, "ARCHIVE", "Year (C.E.)", "Bioturbated Sensor Data")

    """
    Returns false is any parameter value is invalid
    """

    def validate_params(self, params, pseudoproxy):
        """
        Validates the user parameters entered in the GUI to ensure compatibility with the bioturbation model

        Inputs:
        - params: the parameters entered by the user
        - pseudoproxy: the sensor timeseries data (can be carbonate, GDGT, or leafwax)
        Returns:
        - True if all parameters are valid, False otherwise
        """
        # Check whether any parameters are empty
        for p in params:
            if not p:
                tk.messagebox.showerror(title="Run Bioturbation Model", message="Not all parameters were entered.")
                return False
        # Check whether years are integers
        try:
            int(params[0])
            int(params[1])
        except:
            tk.messagebox.showerror(title="Run Bioturbation Model",
                                    message="Years must be integers")
            return False
        # Check whether parameters are floating-point or integer values
        for i in range(2, 5):
            if not check_float(params[i]):
                tk.messagebox.showerror(title="Run Bioturbation Model",
                                        message=str(params[i]) + " should be a numeric value")
                return False
            if i == 5 and not params[i].isdigit():
                tk.messagebox.showerror(title="Run Bioturbation Model",
                                        message=str(params[i]) + " should be an integer")
                return False
        #ensure time period matches between sensor data and user-entered start year and end year
        if len(pseudoproxy)//12 != (int(params[1]) - int(params[0])):

            tk.messagebox.showerror(title="Run Bioturbation Model", message="Length of time between start year and end year"
                                                                            " does not match length of years in input .csv file")
            return False
        return True

    def run_bioturb_model(self, params):
        """
        Plots the output of the bioturbation model

        Input:
        - params: the user-entered parameters for the bioturbation model
        """
        # Check to see whether input .csv file contains a column titled "Pseudoproxy"
        try:
            pseudoproxy = pd.read_csv(self.txtfilename)["Pseudoproxy"]
        except:
            tk.messagebox.showerror(title="Run Bioturbation Model", message="Error with reading csv file")

        self.days, self.iso = convert_to_annual([pseudoproxy], start=int(params[0]))

        # Validate User-Entered Parameters
        if not self.validate_params(params, pseudoproxy):
            return
        self.age = int(params[1]) - int(params[0])
        self.mxl = np.ones(self.age) * float(params[2])
        self.abu = np.ones(self.age) * float(params[3])
        self.numb = int(params[4])

        # Run Bioturbation Model
        self.oriabu, self.bioabu, self.oriiso, self.bioiso = bio.bioturbation(self.abu, self.iso[0], self.mxl,
                                                                              self.numb)
        # Plot Bioturbation Model Output
        self.bio1 = self.bioiso[:, 0]
        self.bio2 = self.bioiso[:, 1]
        self.ori = self.oriiso[:, 0]
        plot_draw(self.scrollable_frame, self.axis, self.f, "ARCHIVE", "Year (C.E.)", "Bioturbated Sensor Data", self.days,
                  [self.bio1, self.bio2, self.ori],
                  "normal", ["#b22222", "#b22222", "#000000"], [2, 2, 2],
                  ["Bioturbated 1", "Bioturbated 2", "Original"])

    def download_csv(self):
        """
        Downloads data represented in the plot as a .csv file
        """
        df = pd.DataFrame({"Time": self.days, "Pseudoproxy": self.ori,
                           "Bioturbated Carrier 1": self.bio1, "Bioturbated Carrier 2": self.bio2})
        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            df.to_csv(file, index=False)
            tk.messagebox.showinfo("Success", "Saved Data")

    def download_png(self):
        """
        Downloads the plot as a .png file
        """
        file = asksaveasfilename(initialfile="Figure.png", defaultextension=".png")
        if file:
            self.f.savefig(file)
            tk.messagebox.showinfo("Sucess", "Saved graph")


class PageCompaction(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        canvas = tk.Canvas(self, bg="white", bd=50)
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

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.populate()
        self.pack(fill="both", expand=True)

    def populate(self):
        """
        Populates this frame of the GUI with labels, buttons, and other features
        """
        rowIdx = 1
        # Title
        label = tk.Label(
            self.scrollable_frame, text="Run Compaction Model", font=LARGE_FONT)
        label.grid(sticky="W", columnspan=3, pady=(1, 20))
        rowIdx += 3

        parameters = ["Sedimentation Rate (cm/kyr):", "# of Years", "Porosity (\u03d5)"]
        param_values = []
        for i in range(rowIdx, rowIdx + 3):
            tk.Label(self.scrollable_frame, text=parameters[i - rowIdx], font=f).grid(
                row=i, column=0, sticky="W")
            p = tk.Entry(self.scrollable_frame)
            p.grid(row=i, column=1, sticky="W")
            param_values.append(p)
        rowIdx += 3
        tk.Button(self.scrollable_frame, text="Generate Graph", font=f,
                  command=lambda: self.run_compaction_model([p.get() for p in param_values])).grid(
            row=rowIdx, column=0, sticky="W")

        # Save as PNG and CSV

        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")

        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", font=f, bg="azure",
                               command=lambda: self.parent.show_frame(["PageCompaction"], "StartPage"))
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")

        self.f, self.axis = plt.subplots(1, 2, figsize=(10, 5), dpi=100)
        plot_setup(self.scrollable_frame, self.axis[0], self.f, "ARCHIVE", "Depth (m)", "Compaction Data")
        plot_setup(self.scrollable_frame, self.axis[1], self.f, "ARCHIVE", "Depth (m)", "Compaction Data")

    def validate_params(self, params):
        """
        Validates the parameters entered by the user to ensure compatibility with the compaction model

        Input:
        - params: the parameters entered by the user
        Returns:
        - True if all user-entered parameters are valid, False otherwise
        """
        if not check_float(params[0]):
            tk.messagebox.showerror(title="Run Compaction Model",
                                    message="Floating point value was not entered for sedimentation rate")
            return False
        if not params[1].isdigit():
            tk.messagebox.showerror(title="Run Compaction Model", message="Integer value was not entered for year")
            return False
        if int(params[1]) < 0:
            tk.messagebox.showerror(title="Run Compaction Model",
                                    message="Positive integer value was not entered for year")
            return False
        if not check_float(params[2]):
            tk.messagebox.showerror(title="Run Compaction Model",
                                    message="Floating point value was not entered for porosity")
            return False
        if not (float(params[2]) > 0 and float(params[2]) < 1):
            tk.messagebox.showerror(title="Run Compaction Model",
                                    message="Porosity must be a value between 0 and 1 (exclusive)")
        return True

    def run_compaction_model(self, params):
        """
        Plots the output of the compaction model

        Input:
        - params: the user-entered parameters for the compaction model
        """
        # Validate User-Entered Parameters
        if not self.validate_params(params):
            return
        sbar = float(params[0])
        year = int(params[1])
        phi_0 = float(params[2])

        # Run Compaction Model
        self.z, self.phi, self.h, self.h_prime = comp.compaction(sbar, year, phi_0)
        self.axis[0].clear()
        self.axis[1].clear()

        # Plot Compaction Model Output
        plot_draw(self.scrollable_frame, self.axis[0], self.f, "Porosity ($\phi$) Profile in Sediment Core",
                  "Depth (m)",
                  r'Porosity Profile ($\phi$) (unitless)', self.z, [self.phi],
                  "no-marker", ["#000000"], [3], ["Porosity Profile"])
        plot_draw(self.scrollable_frame, self.axis[1], self.f, "Depth Scale w/Compaction in Sediment Core", "Depth (m)",
                  "Sediment Height (m)",
                  self.z, [self.h_prime, self.h], "no-marker", ["#000000", "#b22222"], [3, 3],
                  ["Compcated Layer", "Non-Compacted Original Layer"])

    def download_csv(self):
        """
        Downloads data represented in the plot as a .csv file
        """
        df = pd.DataFrame({"Depth (m)": self.z, r'Porosity Profile ($\phi$) (unitless)': self.phi,
                           "Compacted Layer": self.h_prime, "Non-Compacted Original Layer": self.h})
        file = asksaveasfilename(initialfile="Data.csv", defaultextension=".csv")
        if file:
            df.to_csv(file, index=False)
            tk.messagebox.showinfo("Success", "Saved Data")

    def download_png(self):
        """
        Downloads the plot as a .png file
        """
        file = asksaveasfilename(initialfile="Figure.png", defaultextension=".png")
        if file:
            self.f.savefig(file)
            tk.messagebox.showinfo("Sucess", "Saved graph")


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()