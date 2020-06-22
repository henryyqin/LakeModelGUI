#tkinter imports
import tkinter as tk
from tkinter import font as tkfont
import tkinter.filedialog as fd

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
from statistics import mean
plt.style.use('seaborn-whitegrid')
matplotlib.use('TkAgg')  # Necessary for Mac Mojave


#Miscellaneous imports
import os
from os.path import basename
import webbrowser
import copy
from subprocess import PIPE, Popen

LARGE_FONT = ("Verdana", 20)
MED_FONT = ("Verdana", 12)
f = ("Verdana", 8)

#===========GENERAL FUNCTIONS========================================
def callback(url):
    webbrowser.open_new(url)

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

def plot_draw(frame, figure, title, x_axis, y_axis, x_data, y_data, plot_type, error_lines=None):
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
    - error_lines: an array with 2 values that demarcates the CI, None if no CI is necessary for plot
    """
    figure.clf()
    plt = figure.add_subplot(111)
    plt.ticklabel_format(useOffset=False)
    plt.set_title(title)
    plt.set_xlabel(x_axis)
    plt.set_ylabel(y_axis)
    for line in y_data:
        if "normal" in plot_type:
            plt.plot(x_data, line, color="#ff6053", linewidth=3)
        if "scatter" in plot_type:
            plt.scatter(x_data, line, color="#ff6053")
    if error_lines != None:
        plt.fill_between(x_data, error_lines[0], error_lines[1], facecolor='grey', edgecolor='none', alpha=0.20)
    canvas = FigureCanvasTkAgg(figure, frame)
    canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
    canvas.draw()
#=======================================================================

"""
Creates a GUI object
"""
class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title_font = tkfont.Font(family='Verdana', size=24, weight="bold")
        # title of window
        self.title("Lake Model GUI")
        self.minsize(640, 400)
        # self.wm_iconbitmap('icon.ico')

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageEnvModel, PageEnvTimeSeries, PageEnvSeasonalCycle, PageCarbonate, PageLeafwax, PageGDGT,
                  PageBioturbation):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

"""
Home/Title Page
"""
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="PRYSM Models", font=("Verdana", 40))
        label.pack(pady=(200, 10), padx=10)

        descrip = tk.Label(self, text="A graphical user interface for Climate Proxy System Modeling Tools in Python",
                           font=("Helvetica", 18))
        descrip.pack(pady=10, padx=10)

        authors = tk.Label(self, text="By: Sylvia Dee, Henry Qin, Xueyan Mu, and Vinay Tummarakota",
                           font=("Helvetica", 18))
        authors.pack(pady=10, padx=10)

        website = tk.Label(self, text="Getting Started Guide", fg="blue", cursor="hand2", font=("Helvetica", 18))
        website.pack(pady=10, padx=10)
        website.bind("<Button-1>", lambda e: callback(
            "https://docs.google.com/document/d/1RHYEXm5AjXO3NppNxDLPmPnHPr8tQIaT_jH7F7pU2ic/edit?usp=sharing"))

        github = tk.Label(self, text="Github", fg="blue", cursor="hand2", font=("Helvetica", 18))
        github.pack(pady=10, padx=10)
        github.bind("<Button-1>", lambda e: callback("https://github.com/henryyqin/LakeModelGUI"))

        envModelButton = tk.Button(self, text="Run Lake Environment Model", font=f, command=lambda: controller.show_frame("PageEnvModel"))
        envModelButton.pack(ipadx=35, ipady=3, pady=(40, 5))

        # Leads to PageEnvTimeSeries
        envTimeSeriesButton = tk.Button(self, text="Plot Environment Time Series", font=f, command=lambda: controller.show_frame("PageEnvTimeSeries"))
        envTimeSeriesButton.pack(ipadx=35, ipady=3, pady=(5, 5))

        # Leads to PageEnvSeasonalCycle
        envTimeSeriesButton = tk.Button(self, text="Plot Environment Seasonal Cycle", font=f, command=lambda: controller.show_frame("PageEnvSeasonalCycle"))
        envTimeSeriesButton.pack(ipadx=35, ipady=3, pady=(5, 5))

        # Leads to PageCarbonate
        carbButton = tk.Button(self, text="Run Carbonate Model", font=f,
                    command=lambda: controller.show_frame("PageCarbonate"))
        carbButton.pack(ipadx=30, ipady=3, pady=(5, 5))

        # Leads to PageGDGT
        gdgtButton = tk.Button(self, text="Run GDGT Model", font=f, command=lambda: controller.show_frame("PageGDGT"))
        gdgtButton.pack(ipadx=30, ipady=3, pady=(5, 5))

        # Leads to PageLeafwax
        leafwaxButton = tk.Button(self, text="Run Leafwax Model", font=f, command=lambda: controller.show_frame("PageLeafwax"))
        leafwaxButton.pack(ipadx=30, ipady=3, pady=(5, 5))

        # Leads to PageBioturbation
        bioButton = tk.Button(self, text="Run Bioturbation Model", font=f, command=lambda: controller.show_frame("PageBioturbation"))
        bioButton.pack(ipadx=30, ipady=3, pady=(5, 5))


"""
Page to run the environment model
"""
class PageEnvModel(tk.Frame):

    def __init__(self, parent, controller):
        rowIdx = 1
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Label(self, text="Run Lake Environment Model", font=LARGE_FONT).grid(
            row=rowIdx, columnspan=3, rowspan=3, pady=5)
        rowIdx += 3

        # Instructions for uploading .txt and .inc files
        tk.Label(self,
                 text=
                 """
                 1) Upload a text file to provide input data for the lake model. Please make sure
                 the text file is either in the current directory or the file path is less than 132 
                 characters. \n
                 2) Enter lake-specific and simulation-specific parameters\n
                 3) If parameters are left empty, default parameters for Lake Tanganyika will be used instead
                 """, font=f, justify="left"
                 ).grid(row=rowIdx, columnspan=3, rowspan=3, pady=15)
        rowIdx += 3

        # Allows user to upload .txt data.
        tk.Label(self, text="Click to upload your .txt file:", font=f).grid(
            row=rowIdx, column=0, pady=10, sticky="W")
        graphButton = tk.Button(self, text="Upload .txt File", font=f,command=self.uploadTxt)
        graphButton.grid(row=rowIdx, column=1, pady=10, ipadx=30, ipady=3, sticky="W")
        rowIdx += 1

        # Shows the name of the current uploaded file, if any.
        tk.Label(self, text="Current File Uploaded:", font=f).grid(
            row=rowIdx, column=0, sticky="W")
        self.currentTxtFileLabel = tk.Label(self, text="No file", font=f)
        self.currentTxtFileLabel.grid(
            row=rowIdx, column=1, columnspan=2, pady=10, sticky="W")
        rowIdx += 3

        # Entries for .inc file
        parameters = ["obliquity", "latitude (negative for South)", "longitude (negative for West)",
                      "local time relative to gmt in hours", "depth of lake at sill in meters",
                      "Elevation of Basin Bottom in Meters", "Area of Catchment+Lake in Hectares",
                      "neutral drag coefficient", "shortwave extinction coefficient (1/m)",
                      "fraction of advected air over lake", "albedo of melting snow", "albedo of non-melting snow",
                      "prescribed depth in meters", "prescribed salinity in ppt", "d18O of air above lake",
                      "dD of air above lake", "temperature to initialize lake at in INIT_LAKE subroutine",
                      "dD to initialize lake at in INIT_LAKE subroutine",
                      "d18O to initialize lake at in INIT_LAKE subroutine", "number of years for spinup",
                      "true for explict boundry layer computations; presently only for sigma coord climate models",
                      "sigma level for boundary flag", "true for variable lake depth", "true for variable ice cover",
                      "true for variable salinity", "true for variable d18O", "true for variable dD",
                      "height of met inputs"]
        param_values = []
        param_containers = []
        tk.Label(self, text="Lake-Specific Parameters", font=LARGE_FONT).grid(
            row=rowIdx, column=0, sticky="W")
        tk.Label(self, text="Simulation-Specific Parameters", font=LARGE_FONT).grid(
            row=rowIdx, column=2, sticky="W")
        rowIdx += 1

        #List entries for lake-specific parameters
        for i in range(rowIdx, rowIdx + 19):
            tk.Label(self, text=parameters[i - rowIdx], font=f).grid(
                row=i, column=0, sticky="W")
            p = tk.Entry(self)
            p.grid(row=i, column=1, sticky="W")
            param_values.append(p)
            param_containers.append(p)

        #List entries for simulation-specific parameters
        for i in range(rowIdx + 19, rowIdx + 28):
            tk.Label(self, text=parameters[i - rowIdx], font=f).grid(
                row=i - 19, column=2, sticky="W")
            if i in [rowIdx+19, rowIdx+21, rowIdx+27]:
                p = tk.Entry(self)
                p.grid(row=i - 19, column=3, sticky="W")
                param_containers.append(p)
            else:
                p = tk.IntVar()
                c = tk.Checkbutton(self, variable=p)
                c.grid(row=i-19, column=3, sticky="W")
                param_containers.append(c)
            param_values.append(p)

        rowIdx += 19

        # Submit entries for .inc file
        malawiButton = tk.Button(self, text="Autofill Malawi Parameters", font=f,
                                 command = lambda: self.fill("Malawi", param_containers))
        malawiButton.grid(row=rowIdx, column=1, ipadx=30, ipady=3, sticky="W")

        tanganyikaButton = tk.Button(self, text="Autofill Tanganyika Parameters", font=f,
                                 command=lambda: self.fill("Tanganyika", param_containers))
        tanganyikaButton.grid(row=rowIdx, column=2, ipadx=30, ipady=3, sticky="W")

        submitButton = tk.Button(self, text="Submit Parameters", font=f,
                                 command=lambda: self.editInc([p.get() for p in param_values], parameters))
        submitButton.grid(row=rowIdx, column=3, ipadx=30, ipady=3, sticky="W")
        rowIdx += 1

        # Button to run the model (Mac/Linux only)
        runButton = tk.Button(
            self, text="Run Model", font=f, command=self.compileModel)
        runButton.grid(row=rowIdx, column=1, ipadx=30, ipady=3, sticky="W")
        rowIdx += 1

        # Return to Start Page
        homeButton = tk.Button(self, text="Back to start page", font=f,
                               command=lambda: controller.show_frame("StartPage"))
        # previousPageB.pack(anchor = "w", side = "bottom")
        homeButton.grid(row=rowIdx, column=3, ipadx=25,
                        ipady=3, pady=30, sticky="W")
        rowIdx += 1

    """
    Allows the user to upload an input text file to be read by the lake model code
    """
    def uploadTxt(self):
        # Open the file choosen by the user
        self.txtfilename = fd.askopenfilename(
            filetypes=(('text files', 'txt'),))
        base = basename(self.txtfilename)
        nonbase = (self.txtfilename.replace("/","\\")).replace(base,'')[:-1]
        self.currentTxtFileLabel.configure(text=base)

        # Modify the Fortran code to read the input text file
        with open("env_heatflux.f90", "r+") as f:
            new = f.readlines()
            if self.txtfilename != "":
                if nonbase == os.getcwd():
                    new[19] = "      !data_input_filename = '" + base + "'\n"
                else:
                    new[19] = "      !data_input_filename = '" + self.txtfilename + "'\n"
            f.seek(0)
            f.truncate()
            f.writelines(new)
            f.close()

        # Modify the include file to read the input text file
        with open("Malawi.inc","r+") as f:
            new = f.readlines()
            if self.txtfilename != "":
                if nonbase == os.getcwd():
                    new[55] = "      character(38) :: datafile='" + base + "' ! the data file to open in FILE_OPEN subroutine\n"
                    new[56] = "      character(38) :: datafile='" + base + "'\n"
                else:
                    new[55] = "      character(38) :: datafile='"+self.txtfilename+"' ! the data file to open in FILE_OPEN subroutine\n"
                    new[56] = "      character(38) :: datafile='" + self.txtfilename+"'\n"
            f.seek(0)
            f.truncate()
            f.writelines(new)
            f.close()

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
            rows = [28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 41, 42, 44, 45, 57, 58, 59, 62, 63, 64, 65, 66, 67, 68, 69, 70]
            for i in range(len(parameters)):
                if len(str(parameters[i])) != 0:
                    if i==20 or (i>21 and i<27):
                        if parameters[i]==1:
                            new[rows[i]] = "      parameter (" + names[i] + " = .true.)   ! " + comments[i] + "\n"
                        else:
                            new[rows[i]] = "      parameter (" + names[i] + " = .false.)   ! " + comments[i] + "\n"
                    else:
                        new[rows[i]] = "      parameter (" + names[i] + " = " + parameters[i] + ")   ! " + comments[i] + "\n"
            f.seek(0)
            f.truncate()
            f.writelines(new)
            f.close()

    """
    Fills in parameter values with either Malawi or Tanganyika parameters
    """
    def fill(self, lake, containers):
        if lake=="Malawi":
            values = ["23.4", "-12.11", "34.22", "+3", "292", "468.", "2960000.",
                      "1.7e-3", "0.04", "0.1", "0.4", "0.7", "292", "0.0", "-28.",
                      "-190.", "-4.8", "-96.1", "-11.3", "10", 0, "0.96", 0, 1,
                      0, 0, 0, "5.0"]
        else:
            values = ["23.4", "-6.30", "29.5", "+3", "999", "733.", "23100000.",
            "2.0e-3", "0.065", "0.3", "0.4", "0.7", "570", "0.0", "-14.0", "-96.",
            "23.0", "24.0", "3.7", "10", 0, "0.9925561", 0, 0, 0, 0, 0, "5.0"]
        for i in range(len(values)):
            if i==20 or (i>21 and i<27):
                containers[i].deselect()
                if values[i]==1:
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
Page to plot environment model time series
"""
class PageEnvTimeSeries(tk.Frame):

    def __init__(self, parent, controller):
        rowIdx = 1
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(
            self, text="Environment Model Time Series", font=LARGE_FONT)
        label.grid(row=rowIdx, columnspan=3, rowspan=3, pady=5, sticky="we")
        rowIdx += 3

        # Empty graph, default
        self.f = Figure(figsize=(10, 5), dpi=100)
        plot_setup(self, self.f, "Time Series", "Days", "Lake Surface Temperature")

        # Lake Surface Temperature
        LSTButton = tk.Button(self, text="Graph Surface Temperature", font=f,
                              command=lambda: self.generate_env_time_series(1, 'Surface Temperature'))  # 2nd column
        LSTButton.grid(row=rowIdx, column=1, pady=5,
                       ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Mixing Depth
        MDButton = tk.Button(self, text="Graph Mixing Depth", font=f,
                             command=lambda: self.generate_env_time_series(2, 'Mixing Depth'))  # 3rd column
        MDButton.grid(row=rowIdx, column=1, pady=5,
                      ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Evaporation Rate
        ERButton = tk.Button(self, text="Graph Evaporation", font=f,
                             command=lambda: self.generate_env_time_series(3, 'Evaporation'))  # 4th column
        ERButton.grid(row=rowIdx, column=1, pady=5,
                      ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Latent Heat Flux
        LHFButton = tk.Button(self, text="Graph Latent Heat (QEW)", font=f,
                              command=lambda: self.generate_env_time_series(4, 'Latent Heat Flux (QEW)'))  # 5th column
        LHFButton.grid(row=rowIdx, column=1, pady=5,
                       ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Sensible Heat Flux
        SHFButton = tk.Button(self, text="Graph Sensible Heat (QHW)", font=f,
                              command=lambda: self.generate_env_time_series(5, 'Sensible Heat (QHW)'))  # 6th column
        SHFButton.grid(row=rowIdx, column=1, pady=5,
                       ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Downwelling Shortwave Radiation (SWW)
        SWWButton = tk.Button(self, text="Graph Downwelling Shortwave Radiation (SWW)", font=f,
                              command=lambda: self.generate_env_time_series(6,
                                                                            'Downwelling Shortwave Radiation (SWW)'))  # 6th column
        SWWButton.grid(row=rowIdx, column=1, pady=5,
                       ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Upwelling Longwave Raditation (LUW)
        LUWButton = tk.Button(self, text="Graph Upwelling Longwave Raditation (LUW)", font=f,
                              command=lambda: self.generate_env_time_series(7,
                                                                            'Upwelling Longwave Raditation (LUW)'))  # 6th column
        LUWButton.grid(row=rowIdx, column=1, pady=5,
                       ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Max Mixing Depth
        MMDButton = tk.Button(self, text="Graph Max Mixing Depth", font=f,
                              command=lambda: self.generate_env_time_series(8, 'Max Mixing Depth'))  # 6th column
        MMDButton.grid(row=rowIdx, column=1, pady=5,
                       ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Lake Depth
        LDButton = tk.Button(self, text="Graph Lake Depth", font=f,
                             command=lambda: self.generate_env_time_series(9, 'Lake Depth'))  # 6th column
        LDButton.grid(row=rowIdx, column=1, pady=5,
                      ipadx=25, ipady=5, sticky="W")
        rowIdx += 10

        # Return to Start Page
        homeButton = tk.Button(self, text="Back to start page", font=f,
                               command=lambda: controller.show_frame("StartPage"))
        homeButton.grid(row=rowIdx, column=3, ipadx=25,
                        ipady=3, pady=3, sticky="E")

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

        get_output_data(self.days, self.yaxis, column)
        plot_draw(self, self.f, varstring+" over Time", "Days", varstring, self.days, [self.yaxis],
                  "scatter")

"""
Page to plot seasonal cycle
"""
class PageEnvSeasonalCycle(tk.Frame):

    def __init__(self, parent, controller):
        rowIdx = 1
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(
            self, text="Environment Model Seasonal Cycle", font=LARGE_FONT)
        label.grid(row=rowIdx, columnspan=3, rowspan=3, pady=5, sticky="we")
        rowIdx += 3

        # Empty graph, default
        self.f = Figure(figsize=(10, 5), dpi=100)
        plot_setup(self, self.f, "Seasonal Cycle", "Day of the Year", "")

        # Graph button for each variable

        # Lake Surface Temperature
        LSTButton = tk.Button(self, text="Graph Surface Temperature", font=f,
                              command=lambda: self.generate_env_seasonal_cycle(1, 'Surface Temperature'))  # 2nd column
        LSTButton.grid(row=rowIdx, column=1, pady=5,
                       ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Mixing Depth
        MDButton = tk.Button(self, text="Graph Mixing Depth", font=f,
                             command=lambda: self.generate_env_seasonal_cycle(2, 'Mixing Depth'))  # 3rd column
        MDButton.grid(row=rowIdx, column=1, pady=5,
                      ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Evaporation Rate
        ERButton = tk.Button(self, text="Graph Evaporation", font=f,
                             command=lambda: self.generate_env_seasonal_cycle(3, 'Evaporation'))  # 4th column
        ERButton.grid(row=rowIdx, column=1, pady=5,
                      ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Latent Heat Flux
        LHFButton = tk.Button(self, text="Graph Latent Heat (QEW)", font=f,
                              command=lambda: self.generate_env_seasonal_cycle(4,
                                                                               'Latent Heat Flux (QEW)'))  # 5th column
        LHFButton.grid(row=rowIdx, column=1, pady=5,
                       ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Sensible Heat Flux
        SHFButton = tk.Button(self, text="Graph Sensible Heat (QHW)", font=f,
                              command=lambda: self.generate_env_seasonal_cycle(5, 'Sensible Heat (QHW)'))  # 6th column
        SHFButton.grid(row=rowIdx, column=1, pady=5,
                       ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Downwelling Shortwave Radiation (SWW)
        SWWButton = tk.Button(self, text="Graph Downwelling Shortwave Radiation (SWW)", font=f,
                              command=lambda: self.generate_env_seasonal_cycle(6,
                                                                               'Downwelling Shortwave Radiation (SWW)'))  # 6th column
        SWWButton.grid(row=rowIdx, column=1, pady=5,
                       ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Upwelling Longwave Raditation (LUW)
        LUWButton = tk.Button(self, text="Graph Upwelling Longwave Raditation (LUW)", font=f,
                              command=lambda: self.generate_env_seasonal_cycle(7,
                                                                               'Upwelling Longwave Raditation (LUW)'))  # 6th column
        LUWButton.grid(row=rowIdx, column=1, pady=5,
                       ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Max Mixing Depth
        MMDButton = tk.Button(self, text="Graph Max Mixing Depth", font=f,
                              command=lambda: self.generate_env_seasonal_cycle(8, 'Max Mixing Depth'))  # 6th column
        MMDButton.grid(row=rowIdx, column=1, pady=5,
                       ipadx=25, ipady=5, sticky="W")
        rowIdx += 1

        # Lake Depth
        LDButton = tk.Button(self, text="Graph Lake Depth", font=f,
                             command=lambda: self.generate_env_seasonal_cycle(9, 'Lake Depth'))  # 6th column
        LDButton.grid(row=rowIdx, column=1, pady=5,
                      ipadx=25, ipady=5, sticky="W")
        rowIdx += 10

        # Return to Start Page
        homeButton = tk.Button(self, text="Back to start page", font=f,
                               command=lambda: controller.show_frame("StartPage"))
        homeButton.grid(row=rowIdx, column=3, ipadx=25,
                        ipady=3, pady=3, sticky="E")

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

        get_output_data(self.days, self.yaxis, column)

        # At this point, self.days and self.yaxis are identical to the ones in envtimeseries

        self.ydict = {}  # dictionary to store the y values for each day from 15 to 375
        for day in self.days:  # 15, 45, ...
            # if the day is not a key, then make an empty list
            if day % 390 not in self.ydict:
                self.ydict[day % 390] = []
            # otherwise append to that list
            else:
                self.ydict[day % 390].append(self.yaxis[int((day - 15) / 30)])  # (day - 15)/30 gets the correct index

        # After yval array is formed for each xval, generate the axtual yaxis data
        self.seasonal_yaxis = []  # actual plotting data for y
        self.seasonal_days = range(15, 376, 30)  # actual plotting data for x, count from 15 to 375 by 30's
        for day in self.seasonal_days:
            self.seasonal_yaxis.append(mean(self.ydict[day]))  # mean the values of each day

        plot_draw(self, self.f, varstring+" Seasonal Cycle", "Day of the Year", "Average", self.seasonal_days,
                  [self.seasonal_yaxis], "scatter")


"""
Page to run carbonate sensor model and plot data
"""
class PageCarbonate(tk.Frame):

    def __init__(self, parent, controller):
        rowIdx = 1
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(
            self, text="Carbonate Sensor Model", font=LARGE_FONT)
        label.grid(row=rowIdx, columnspan=3, rowspan=3, pady=5)

        rowIdx += 3

        self.model = tk.StringVar()
        self.model.set("ONeil")
        model_names = ["ONeil", "Kim-ONeil", "ErezLuz", "Bemis", "Lynch"]
        for name in model_names:
            tk.Radiobutton(self, text=name, font=MED_FONT, value=name, variable=self.model).grid(row=rowIdx, column=0,
                                                                                                 pady=1,
                                                                                                 ipadx=20, ipady=5,
                                                                                                 sticky="W")
            rowIdx += 1
        tk.Button(self, text="Submit Model", font=MED_FONT, command=self.run_carbonate_model).grid(
            row=rowIdx, column=0, pady=1,
            ipadx=20, ipady=5, sticky="W")
        rowIdx += 1

        tk.Button(self, text="Generate Graph of Carbonate Proxy Data", font=MED_FONT, command=self.generate_graph).grid(
            row=rowIdx, column=0, pady=1,
            ipadx=20, ipady=5, sticky="W")
        rowIdx += 1
        tk.Button(self, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_carb_data).grid(
            row=rowIdx, column=0, pady=1,
            ipadx=20, ipady=5, sticky="W")
        rowIdx += 1

        # Return to Start Page
        tk.Button(self, text="Back to start", font=f,
                  command=lambda: controller.show_frame("StartPage")).grid(
            row=rowIdx, column=0, sticky="W")

        self.f = Figure(figsize=(10, 5), dpi=100)
        plot_setup(self, self.f, "SENSOR", "Time", "Simulated Carbonate Data")

    """
    Create time series data for carbonate sensor
    """

    def run_carbonate_model(self):
        surf_tempr = []
        self.days = []
        get_output_data(self.days, surf_tempr, 1)
        self.LST = np.array(surf_tempr, dtype=float)
        self.d180w = -2
        self.carb_proxy = carb.carb_sensor(self.LST, self.d180w, model=self.model.get())

    def generate_graph(self):
        plot_draw(self, self.f, "SENSOR", "Time", "Simulated Carbonate Data", self.days, [self.carb_proxy],
                  "scatter")

    def download_carb_data(self):
        df = pd.DataFrame({"Time": self.days, "Pseudoproxy": self.carb_proxy})
        export_file_path = fd.asksaveasfilename(defaultextension='.csv')
        df.to_csv(export_file_path, index=None)


"""
Page to run GDGT Model and plot data
"""
class PageGDGT(tk.Frame):

    def __init__(self, parent, controller):
        rowIdx = 1
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(
            self, text="Run GDGT Sensor Model", font=LARGE_FONT)
        label.grid(row=rowIdx, columnspan=3, rowspan=3, pady=5)

        rowIdx += 3
        graphButton = tk.Button(self, text="Upload own .txt File", font=f,
                                command=self.uploadGDGTTxt)
        graphButton.grid(row=rowIdx, column=0, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        rowIdx += 1
        # Shows the name of the current uploaded file, if any.
        tk.Label(self, text="Current File Uploaded:", font=f).grid(
            row=rowIdx, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self, text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx, column=1, columnspan=2, pady=10, sticky="W")
        rowIdx += 3

        self.model = tk.StringVar()
        self.model.set("TEX86-tierney")
        model_names = ["TEX86-tierney", "TEX86-powers", "TEX86-loomis", "MBT-R", "MBT-J"]
        for name in model_names:
            tk.Radiobutton(self, text=name, value=name, variable=self.model).grid(row=rowIdx, column=0, sticky="W")
            rowIdx += 1
        tk.Button(self, text="Submit Model", command=self.run_gdgt_model).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx += 1

        tk.Button(self, text="Generate Graph of GDGT Proxy Data", command=self.generate_graph).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx += 1
        tk.Button(self, text="Save Graph Data as .csv", command=self.download_gdgt_data).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx += 1

        # Return to Start Page
        tk.Button(self, text="Back to start",
                  command=lambda: controller.show_frame("StartPage")).grid(
            row=rowIdx, column=0, sticky="W")

        self.f = Figure(figsize=(9, 5), dpi=100)
        plot_setup(self, self.f, "SENSOR", "Time", "Simulated GDGT Data")

    """
    Upload text file with air temperature data
    """

    def uploadGDGTTxt(self):
        # Open the file choosen by the user
        self.txtfilename = fd.askopenfilename(
            filetypes=(('text files', 'txt'),))
        self.currentFileLabel.configure(text=basename(self.txtfilename))

    """
    Create time series data for GDGT sensor
    """

    def run_gdgt_model(self):
        surf_tempr = []
        self.days = []
        get_output_data(self.days, surf_tempr, 1)
        self.LST = np.array(surf_tempr, dtype=float)

        # unchanged
        climate_input = self.txtfilename
        air_tempr = []
        with open(climate_input, 'r') as data:
            airtemp_yr = []
            for line in data:
                line_vals = line.split()
                airtemp_yr.append(line_vals[2])
            air_tempr.append(airtemp_yr)
        air_tempr = np.array(air_tempr[0], dtype=float)


        self.MAAT = air_tempr
        self.beta = 1. / 50.
        self.gdgt_proxy = gdgt.gdgt_sensor(self.LST, self.MAAT, self.beta, model=self.model.get())

    def generate_graph(self):
        plot_draw(self, self.f, "SENSOR", "Time", "Simulated GDGT Data", self.days, [self.gdgt_proxy],
                  "scatter")

    def download_gdgt_data(self):
        df = pd.DataFrame({"Time": self.days, "Pseudoproxy": self.gdgt_proxy})
        export_file_path = fd.asksaveasfilename(defaultextension='.csv')
        df.to_csv(export_file_path, index=None)


"""
Page to run leafwax sensor model and plot data
"""
class PageLeafwax(tk.Frame):
    def __init__(self, parent, controller):
        rowIdx = 1
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(
            self, text="Run Leafwax Model", font=LARGE_FONT)
        label.grid(row=rowIdx, columnspan=3, rowspan=3, pady=5)

        rowIdx += 3

        # Instructions for uploading file
        tk.Label(self,
                 text=
                 """
                 1) Upload a .txt file or choose the provided example .txt file
                 2) Enter error stuff? [IDK]
                 3) If parameters are left empty, [INSERT INSTRUCTIONS]
                 """, font=f, justify="left"
                 ).grid(row=rowIdx, columnspan=3, rowspan=3, pady=15)
        rowIdx += 3

        # Example file
        sample_input = 'IsoGSM_dDP_1953_2012.txt'
        dDp = np.loadtxt(sample_input)
        self.dDp = dDp

        # Upload example file
        tk.Label(self, text="Click to load data", font=f).grid(
            row=rowIdx, column=0, pady=10, sticky="W")
        graphButton = tk.Button(self, text="Upload example file", font=f,
                                command=lambda: self.uploadLeafwaxTxt("sample"))
        graphButton.grid(row=rowIdx, column=1, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        # Upload own text file
        graphButton = tk.Button(self, text="Upload own .txt File", font=f,
                                command=lambda: self.uploadLeafwaxTxt("user_file"))
        graphButton.grid(row=rowIdx, column=2, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        rowIdx += 1

        # Shows the name of the current uploaded file, if any.
        tk.Label(self, text="Current File Uploaded:", font=f).grid(
            row=rowIdx, column=0, sticky="W")
        self.currentFileLabel = tk.Label(self, text="No file", font=f)
        self.currentFileLabel.grid(
            row=rowIdx, column=1, columnspan=2, pady=10, sticky="W")

        rowIdx += 3

        self.f = Figure(figsize=(9, 5), dpi=100)
        plot_setup(self, self.f, "SENSOR", "Time", "Simulated Leafwax Data")

        tk.Button(self, text="Run Leafwax Model", font=f, command=self.run_leafwax_model).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx += 1
        tk.Button(self, text="Generate Graph of Leafwax Proxy Data", font=f, command=self.generate_graph).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx += 1
        tk.Button(self, text="Save Graph Data as .csv", font=f, command=self.download_leafwax_data).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx += 1
        # Return to Start Page
        tk.Button(self, text="Back to start", font=f,
                  command=lambda: controller.show_frame("StartPage")).grid(
            row=rowIdx, column=0, sticky="W")

    """
      Upload .txt file from user
      """

    def uploadLeafwaxTxt(self, type):
        if type == "sample":
            # Upload example file
            sample_input = 'IsoGSM_dDP_1953_2012.txt'
            self.currentFileLabel.configure(text=sample_input)
            self.txtfilename = sample_input
            self.dDp = np.loadtxt(sample_input)
        else:
            # Open the file choosen by the user
            self.txtfilename = fd.askopenfilename(
                filetypes=(('text files', 'txt'),))
            self.currentFileLabel.configure(text=basename(self.txtfilename))
            self.dDp = np.loadtxt(self.txtfilename)

    """
    Create time series data for leafwax sensor
    """

    def run_leafwax_model(self):

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

    def generate_graph(self):
        self.days = []
        with open(self.txtfilename) as input:
            for i in range(len(input.readlines())):
                self.days.append(30 * i + 15)

        plot_draw(self, self.f, "SENSOR", "Time", "Simulated Leaf Wax Data", self.days, [self.leafwax_proxy],
                  "scatter normal", error_lines=[self.Q1, self.Q2])

    def download_leafwax_data(self):
        df = pd.DataFrame({"Time": self.days, "Pseudoproxy": self.leafwax_proxy, "95% CI Lower Bound": self.Q1,
                           "95% CI Upper Bound": self.Q2})
        export_file_path = fd.asksaveasfilename(defaultextension='.csv')
        df.to_csv(export_file_path, index=None)


"""
Page to run bioturbation archive model and plot data
"""
class PageBioturbation(tk.Frame):
    def __init__(self, parent, controller):
        rowIdx = 1
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(
            self, text="Run Bioturbation Model", font=LARGE_FONT)
        label.grid(row=rowIdx, columnspan=3, rowspan=3, pady=5)
        rowIdx += 3
        # Instructions for uploading .txt and .inc files
        tk.Label(self,
                 text=
                 """
                 1) Upload a .csv file with a column "Pseudoproxy" containing pseudoproxy timeseries data. \n
                 2) Enter parameters for bioturbation\n
                 3) You cannot leave parameters empty
                 """, font=f, justify="left"
                 ).grid(row=rowIdx, columnspan=3, rowspan=3, pady=15)
        rowIdx += 3
        tk.Label(self, text="Current File Uploaded:", font=f).grid(
            row=rowIdx, column=0, sticky="W")
        self.currentTxtFileLabel = tk.Label(self, text="No file", font=f)
        self.currentTxtFileLabel.grid(
            row=rowIdx, column=1, columnspan=2, pady=10, sticky="W")
        rowIdx += 1
        tk.Button(self, text="Upload Data", command=self.upload_csv, font=f).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx += 1
        parameters = ["Start Year:", "End Year:", "Mixed Layer Thickness Coefficient:", "Abundance:",
                      "Number of Carriers:"]
        param_values = []
        for i in range(rowIdx, rowIdx + 5):
            tk.Label(self, text=parameters[i - rowIdx], font=f).grid(
                row=i, column=0, sticky="W")
            p = tk.Entry(self)
            p.grid(row=i, column=1, sticky="W")
            param_values.append(p)
        rowIdx += 5
        tk.Button(self, text="Submit Parameters", font=f,
                  command=lambda: self.run_bioturb_model([p.get() for p in param_values])).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx += 1
        tk.Button(self, text="Save Graph Data as .csv", font=f, command=self.download_bioturb_data).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx += 1

        self.f = Figure(figsize=(9, 5), dpi=100)
        plot_setup(self, self.f, "ARCHIVE", "Time", "Bioturbated Sensor Data")

    def upload_csv(self):
        # Open the file choosen by the user
        self.txtfilename = fd.askopenfilename(filetypes=(('csv files', 'csv'),))
        self.currentTxtFileLabel.configure(text=basename(self.txtfilename))

    """
     Checks whether a string represents a valid signed/unsigned floating-point number
     """

    def check_float(self, str):
        try:
            float(str)
            return True
        except:
            return False

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
        for i in range(2, 5):
            if not self.check_float(params[i]):
                tk.messagebox.showerror(title="Run Bioturbation Model",
                                        message=str(params[i]) + " is not a proper value")
                return False
        # convert parameters to integers for further validation
        params_copy = copy.deepcopy(params)
        params_copy = [float(p) for p in params_copy]
        if params_copy[0] >= params_copy[1]:
            tk.messagebox.showerror(title="Run Bioturbation Model",
                                    message="Start year cannot be greater than or equal to end year")
            return False
        if self.days[-1] != params_copy[1] - params_copy[0]:
            tk.messagebox.showerror(title="Run Bioturbation Model", message="The time interval " + params[0] + "-" +
                                                                            params[
                                                                                1] + " is not the same length as the time interval within the uploaded data")
            return False
        return True

    def run_bioturb_model(self, params):
        # check whether csv file can be opened
        try:
            pseudoproxy = pd.read_csv(self.txtfilename)["Pseudoproxy"]
        except:
            tk.messagebox.showerror(title="Run Bioturbation Model", message="Error with reading csv file")
        self.days = []
        self.iso = []
        year = []
        for i in range(len(pseudoproxy)):
            year.append(pseudoproxy[i])
            if (i + 1) % 12 == 0:
                self.iso.append(mean(year))
                self.days.append((i + 1) / 12)
                year.clear()
        if not self.validate_params(params):
            print("hello")
            return
        self.age = int(params[1]) - int(params[0])
        self.mxl = np.ones(self.age) * float(params[2])
        self.abu = np.ones(self.age) * float(params[3])
        self.numb = int(params[4])
        # Run the bioturbation model
        self.oriabu, self.bioabu, self.oriiso, self.bioiso = bio.bioturbation(self.abu, self.iso, self.mxl, self.numb)

        # Plot the bioturbation model
        plot_draw(self, self.f, "ARCHIVE", "Time", "Bioturbated Sensor Data", self.days, [self.bioiso, self.oriiso],
                  "normal")

    def download_bioturb_data(self):
        bio1 = self.bioiso[:, 0]
        bio2 = self.bioiso[:, 1]
        ori = self.oriiso[:, 0]
        print(self.oriiso)
        df = pd.DataFrame({"Time": self.days, "Original Pseudoproxy": ori,
                           "Bioturbated Carrier 1": bio1, "Bioturbated Carrier 2": bio2})
        export_file_path = fd.asksaveasfilename(defaultextension='.csv')
        df.to_csv(export_file_path, index=None)

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()