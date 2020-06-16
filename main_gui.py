import tkinter as tk                # python 3
from tkinter import font as tkfont  # python 3
import os
from os.path import basename
import tkinter.filedialog as fd
import pandas as pd
import webbrowser
import sensor_carbonate as carb
import sensor_leafwax as leafwax
import lake_archive_bioturb as bio
from subprocess import Popen, PIPE
import copy

# Imports for Lake Model
import numpy as np
import matplotlib

matplotlib.use('TkAgg')  # Necessary for Mac Mojave
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from math import pi, sqrt, exp

# Imports for plotting
from statistics import mean

"""
if you want the user to upload something from the same directory as the gui
then you can use initialdir=os.getcwd() as the first parameter of askopenfilename
"""
LARGE_FONT = ("Verdana", 26)
f = ("Verdana", 8)

def callback(url):
    webbrowser.open_new(url)

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
        for F in (StartPage, PageOne, PageEnvTimeSeries, PageEnvSeasonalCycle, PageCarbonate, PageLeafwax,
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

        button = tk.Button(self, text="Run Lake Environment Model", font=f, command=lambda: controller.show_frame("PageOne"))
        button.pack(ipadx=35, ipady=3, pady=(40, 5))

        # Leads to PageEnvTimeSeries
        buttonTimeSeries = tk.Button(self, text="Plot Environment Time Series", font=f, command=lambda: controller.show_frame("PageEnvTimeSeries"))
        buttonTimeSeries.pack(ipadx=35, ipady=3, pady=(5, 5))

        # Leads to PageEnvSeasonalCycle
        buttonTimeSeries = tk.Button(self, text="Plot Environment Seasonal Cycle", font=f, command=lambda: controller.show_frame("PageEnvSeasonalCycle"))
        buttonTimeSeries.pack(ipadx=35, ipady=3, pady=(5, 5))

        # Leads to PageCarbonate
        carbButton = tk.Button(self, text="Run Carbonate Model", font=f,
                    command=lambda: controller.show_frame("PageCarbonate"))
        carbButton.pack(ipadx=30, ipady=3, pady=(5, 5))

        # Leads to PageLeafwax
        leafButton = tk.Button(self, text="Run Leafwax Model", font=f,
                            command=lambda: controller.show_frame("PageLeafwax"))
        leafButton.pack(ipadx=30, ipady=3, pady=(5, 5))

        # Leads to PageLeafwax
        bioButton = tk.Button(self, text="Run Bioturbation Model", font=f,
                               command=lambda: controller.show_frame("PageBioturbation"))
        bioButton.pack(ipadx=30, ipady=3, pady=(5, 5))

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        rowIdx = 1
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(
            self, text="Run Lake Environment Model", font=LARGE_FONT)
        label.grid(row=rowIdx, columnspan=3, rowspan=3, pady=5)

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
        graphButton = tk.Button(self, text="Upload .txt File", font=f,
                                command=self.uploadTxt)
        graphButton.grid(row=rowIdx, column=1, pady=10,
                         ipadx=30, ipady=3, sticky="W")
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
                      "neutral drag coefficient 1.8 HAD 1.7GISS 1.2CCSM", "shortwave extinction coefficient (1/m)",
                      "fraction of advected air over lake", "albedo of melting snow", "albedo of non-melting snow",
                      "prescribed depth in meters", "prescribed salinity in ppt", "d18O of air above lake",
                      "dD of air above lake", "number of years for spinup",
                      "true for explict boundry layer computations; presently only for sigma coord climate models",
                      "sigma level for boundary flag", "true for variable lake depth", "true for variable ice cover",
                      "true for variable salinity", "true for variable d18O", "true for variable dD",
                      "height of met inputs"]
        param_values = []
        tk.Label(self, text="Lake-Specific Parameters", font=LARGE_FONT).grid(
            row=rowIdx, column=0, sticky="W")
        tk.Label(self, text="Simulation-Specific Parameters", font=LARGE_FONT).grid(
            row=rowIdx, column=2, sticky="W")
        rowIdx += 1
        for i in range(rowIdx, rowIdx + 16):
            tk.Label(self, text=parameters[i - rowIdx], font=f).grid(
                row=i, column=0, sticky="W")
            p = tk.Entry(self)
            p.grid(row=i, column=1, sticky="W")
            param_values.append(p)

        for i in range(rowIdx + 16, rowIdx + 25):
            tk.Label(self, text=parameters[i - rowIdx], font=f).grid(
                row=i - 16, column=2, sticky="W")
            p = tk.Entry(self)
            p.grid(row=i - 16, column=3, sticky="W")
            param_values.append(p)

        rowIdx += 16

        # Submit entries for .inc file
        submitButton = tk.Button(self, text="Submit Parameters", font=f,
                                 command=lambda: self.editInc([p.get() for p in param_values], parameters))
        submitButton.grid(row=rowIdx, column=1, pady=10, ipadx=30, ipady=3, sticky="W")

        rowIdx += 1

        # Button to run the model (Mac/Linux only)
        runButton = tk.Button(
            self, text="Run Model", font=f, command=lambda: self.compileModel(runButton))
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
    Takes a .txt file
    """

    def uploadTxt(self):
        # Open the file choosen by the user
        self.txtfilename = fd.askopenfilename(
            filetypes=(('text files', 'txt'),))
        base = basename(self.txtfilename)
        nonbase = (self.txtfilename.replace("/","\\")).replace(base,'')[:-1]
        self.currentTxtFileLabel.configure(text=base)
        with open("env_heatflux.f90", "r+") as f:
            new = f.readlines()
            if self.txtfilename != "":
                if nonbase == os.getcwd():
                    new[18] = "      !data_input_filename = '" + base + "'\n"
                    new[732] = "      open(unit=15,file='" + base + "',status='old')\n"
                else:
                    new[18] = "      !data_input_filename = '" + self.txtfilename + "'\n"
                    new[732] = "      open(unit=15,file='" + self.txtfilename + "',status='old')\n"
            f.seek(0)
            f.truncate()
            f.writelines(new)
            f.close()
        with open("heatflux.inc","r+") as f:
            new = f.readlines()
            if self.txtfilename != "":
                if nonbase == os.getcwd():
                    new[61] = "    character(38) :: datafile='" + base + "' ! the data file to open in FILE_OPEN subroutine\n"
                else:
                    new[61] = "    character(38) :: datafile='"+self.txtfilename+"' ! the data file to open in FILE_OPEN subroutine\n"
            f.seek(0)
            f.truncate()
            f.writelines(new)
            f.close()

    """
    Edits the parameters in the .inc file
    """

    def editInc(self, parameters, comments):
        with open("heatflux.inc", "r+") as f:
            new = f.readlines()
            # names of the parameters that need to be modified
            names = ["oblq", "xlat", "xlon", "gmt", "max_dep", "basedep", "b_area", "cdrn", "eta", "f", "alb_slush",
                     "alb_snow", "depth_begin", "salty_begin", "o18air", "deutair", "nspin", "bndry_flag",
                     "sigma", "wb_flag", "iceflag", "s_flag", "o18flag", "deutflag", "z_screen"]
            # line numbers in the .inc file that need to be modified
            rows = [28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 41, 42, 44, 45, 69, 70, 71, 72, 73, 74, 75, 76, 77]
            for i in range(0, len(parameters)):
                if len(parameters[i]) != 0:
                    new[rows[i]] = "    parameter (" + names[i] + " = " + parameters[i] + ")   ! " + comments[i] + "\n"
            f.seek(0)
            f.truncate()
            f.writelines(new)
            f.close()

    def compileModel(self, btn):
        response = tk.messagebox.askyesno(title="Run Model", message="Running the model will take several minutes, and "
                                                                     "GUI functionality will temporarily stop. You will receive a notification "
                                                                     "once the model has finished. Do you wish to proceed?")
        if response == 1:
            cygwin1 = Popen(['bash'], stdin=PIPE, stdout=PIPE)
            result1 = cygwin1.communicate(input=b"gfortran -o 'TEST1' env_heatflux.f90")
            print(result1)
            self.runModel()
            tk.messagebox.showinfo(title="Run Model", message="Model has completed running. You will find "
                                                              "surface_output.dat located in your "
                                                              "current working directory.")
        else:
            pass

    def runModel(self):
        cygwin2 = Popen(['bash'], stdin=PIPE, stdout=PIPE)
        result2 = cygwin2.communicate(input=b"./TEST1.exe")
        print(result2)


"""
Page to plot time series
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
        self.plt = self.f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.plt.set_title(r'Time Series', fontsize=12)
        self.plt.set_xlabel('Time')
        self.plt.set_ylabel('Lake Surface Temperature')

        # Graph button for each variable

        # Lake Surface Temperature
        LSTButton = tk.Button(self, text="Graph Surface Temperature", font=f,
                              command=lambda: self.generate_env_time_series(1,
                                                                            'Lake Surface Temperature (\N{DEGREE SIGN}C)'))  # 2nd column
        LSTButton.grid(row=rowIdx, column=1, pady=1,
                       ipadx=30, ipady=10, sticky="W")
        rowIdx += 1

        # Mixing Depth
        MDButton = tk.Button(self, text="Graph Mixing Depth", font=f,
                             command=lambda: self.generate_env_time_series(2, 'Mixing Depth (m)'))  # 3rd column
        MDButton.grid(row=rowIdx, column=1, pady=1,
                      ipadx=30, ipady=10, sticky="W")
        rowIdx += 1

        # Evaporation Rate
        ERButton = tk.Button(self, text="Graph Evaporation Rate", font=f,
                             command=lambda: self.generate_env_time_series(3,
                                                                           'Evaporation Rate (mm/day)'))  # 4th column
        ERButton.grid(row=rowIdx, column=1, pady=1,
                      ipadx=30, ipady=10, sticky="W")
        rowIdx += 1

        # Latent Heat Flux
        LHFButton = tk.Button(self, text="Graph Latent Heat Flux", font=f,
                              command=lambda: self.generate_env_time_series(3,
                                                                            'Latent Heat Flux (W/$m^2$)'))  # 4th column
        LHFButton.grid(row=rowIdx, column=1, pady=1,
                       ipadx=30, ipady=10, sticky="W")
        rowIdx += 1

        # Sensible Heat Flux
        SHFButton = tk.Button(self, text="Graph Sensible Heat Flux", font=f,
                              command=lambda: self.generate_env_time_series(3,
                                                                            'Sensible Heat Flux (W/$m^2$)'))  # 4th column
        SHFButton.grid(row=rowIdx, column=1, pady=1,
                       ipadx=30, ipady=10, sticky="W")
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
    Returns:
     - Nothing, just generates a graph on the page
    """

    # extracts data from .dat file and plots data based on given column number
    def generate_env_time_series(self, column, varstring):
        self.days = []  # x-axis
        self.yaxis = []  # y-axis
        # determining nspin
        self.nspin = ""
        with open("heatflux.inc", "r") as inc:
            lines = inc.readlines()
            nspin_line = lines[69]
            idx = 0
            while nspin_line[idx] != "=":
                idx += 1
            idx += 1
            while nspin_line[idx] != ")":
                self.nspin += nspin_line[idx]
                idx += 1
            self.nspin = int(self.nspin)
        print(self.nspin)

        # generate data (Using BCC-ERA for now)
        with open("BCC-ERA-Tlake-humid_surf.dat", "r") as data:
            line_num = 0
            for line in data:

                line_vals = line.split()
                if line_num >= self.nspin * 12:
                    self.days.append(line_vals[0])  # ignore nspin
                    self.yaxis.append(line_vals[column])
                line_num += 1

        self.days = [int(float(day)) for day in self.days]  # convert days to int

        self.f.clf()
        self.plt = self.f.add_subplot(111)
        self.plt.set_title(r'' + varstring + ' over Time')
        self.plt.set_xlabel('Time (Day of the Year)')
        self.plt.set_ylabel(varstring)
        self.plt.scatter(self.days, self.yaxis, color="#ff6053")
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(
            row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.canvas.draw()


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
        self.plt = self.f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.plt.set_title(r'Seasonal Cycle', fontsize=12)
        self.plt.set_xlabel('Day of the Year')
        self.plt.set_ylabel('')

        # Graph button for each variable

        # Lake Surface Temperature
        LSTButton = tk.Button(self, text="Graph Surface Temperature", font=f,
                              command=lambda: self.generate_env_seasonal_cycle(1,
                                                                               'Lake Surface Temperature (\N{DEGREE SIGN}C)'))  # 2nd column
        LSTButton.grid(row=rowIdx, column=1, pady=1,
                       ipadx=30, ipady=10, sticky="W")
        rowIdx += 1

        # Mixing Depth
        MDButton = tk.Button(self, text="Graph Mixing Depth", font=f,
                             command=lambda: self.generate_env_seasonal_cycle(2, 'Mixing Depth (m)'))  # 3rd column
        MDButton.grid(row=rowIdx, column=1, pady=1,
                      ipadx=30, ipady=10, sticky="W")
        rowIdx += 1

        # Evaporation Rate
        ERButton = tk.Button(self, text="Graph Evaporation Rate", font=f,
                             command=lambda: self.generate_env_seasonal_cycle(3,
                                                                              'Evaporation Rate (mm/day)'))  # 4th column
        ERButton.grid(row=rowIdx, column=1, pady=1,
                      ipadx=30, ipady=10, sticky="W")
        rowIdx += 1

        # Latent Heat Flux
        LHFButton = tk.Button(self, text="Graph Latent Heat Flux", font=f,
                              command=lambda: self.generate_env_seasonal_cycle(3,
                                                                               'Latent Heat Flux (W/$m^2$)'))  # 4th column
        LHFButton.grid(row=rowIdx, column=1, pady=1,
                       ipadx=30, ipady=10, sticky="W")
        rowIdx += 1

        # Sensible Heat Flux
        SHFButton = tk.Button(self, text="Graph Sensible Heat Flux", font=f,
                              command=lambda: self.generate_env_seasonal_cycle(3,
                                                                               'Sensible Heat Flux (W/$m^2$)'))  # 4th column
        SHFButton.grid(row=rowIdx, column=1, pady=1,
                       ipadx=30, ipady=10, sticky="W")
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
    Returns:
     - Nothing, just generates a graph on the page
    """

    # Treating 375 as part of the year for now
    # Treating everything >375 to be 15, 45, etc.
    def generate_env_seasonal_cycle(self, column, varstring):
        self.xaxis = [15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345, 375]  # x-axis
        self.ydict = {}  # dict to list all y of an x as an array, to be meaned later

        """
        # determining nspin
        self.nspin = ""
        with open("heatflux.inc", "r") as inc:
            lines = inc.readlines()
            nspin_line = lines[69]
            idx = 0
            while nspin_line[idx] != "=":
                idx += 1
            idx += 1
            while nspin_line[idx] != ")":
                self.nspin += nspin_line[idx]
                idx += 1
            self.nspin = int(self.nspin)
        print(self.nspin)
        """

        # Hard code nspin = 10
        self.nspin = 10

        # generate data (Using BCC-ERA for now)
        with open("BCC-ERA-Tlake-humid_surf.dat", "r") as data:
            line_num = 0
            for line in data:
                line_vals = line.split()  # convert each line into a list of floats
                if line_num >= self.nspin * 12:
                    xval = int(float(line_vals[0]) % 405)
                    if xval in self.ydict:  # if xval is already a key in ydict
                        self.ydict[xval].append(float(line_vals[column]))  # update y array with desired value
                    else:  # xval not a key in ydict yet
                        self.ydict[xval] = []
                line_num += 1

        # After yval array is formed for each xval, generate the axtual yaxis data
        self.yaxis = []  # actual plotting data for y
        for xval in range(15, 376, 30):  # count from 15 to 375 by 30's
            self.yaxis.append(mean(self.ydict[xval]))  # mean the yvals for each xval and append it to yaxis

        self.f.clf()
        self.plt = self.f.add_subplot(111)
        self.plt.set_title(r'' + varstring + ' Seasonal Cycle')
        self.plt.set_xlabel('Day of the Year')
        self.plt.set_ylabel('Average ' + varstring)
        self.plt.scatter(self.xaxis, self.yaxis, color="#ff6053")
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(
            row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.canvas.draw()

class PageCarbonate(tk.Frame):

    def __init__(self, parent, controller):
        rowIdx = 1
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(
            self, text="Run Carbonate Sensor Model", font=LARGE_FONT)
        label.grid(row=rowIdx, columnspan=3, rowspan=3, pady=5)

        rowIdx += 3

        self.model = tk.StringVar()
        self.model.set("ONeil")
        model_names = ["ONeil", "Kim-ONeil", "ErezLuz", "Bemis", "Lynch"]
        for name in model_names:
            tk.Radiobutton(self, text=name, value=name, variable=self.model).grid(row=rowIdx, column=0, sticky="W")
            rowIdx += 1
        tk.Button(self, text="Submit Model", command=self.run_carbonate_model).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx += 1

        tk.Button(self, text="Generate Graph of Carbonate Proxy Data", command=self.generate_graph).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx+=1
        tk.Button(self, text="Save Graph Data as .csv", command=self.download_carb_data).grid(
            row=rowIdx, column=0, sticky="W")

        self.f = Figure(figsize=(10, 5), dpi=100)
        self.plt = self.f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.plt.set_title(r'SENSOR', fontsize=12)
        self.plt.set_xlabel('Time')
        self.plt.set_ylabel('Simulated Carbonate Data')

    """
    Create time series data for carbonate sensor
    """

    def run_carbonate_model(self):
        surf_tempr = []
        self.days = []
        """
        self.nspin = ""
        with open("heatflux.inc", "r") as inc:
            lines = inc.readlines()
            nspin_line = lines[69]
            idx = 0
            while nspin_line[idx] != "=":
                idx += 1
            idx += 1
            while nspin_line[idx] != ")":
                self.nspin += nspin_line[idx]
                idx += 1
            self.nspin = int(self.nspin)
        with open("BCC-ERA-Tlake-humid_surf.dat", 'r') as data:
            tempr_yr = []
            for line in data:
                line_vals = line.split()
                tempr_yr.append(line_vals[1])
            surf_tempr.append(tempr_yr[self.nspin*12+2:len(tempr_yr)])
        surf_tempr = np.array(surf_tempr[0], dtype=float)
        """
        with open("BCC-ERA-Tlake-humid_surf.dat") as data:
            tempr_yr = []
            lines = data.readlines()
            cur_row = lines[len(lines)-1].split()
            next_row = lines[len(lines)-2].split()
            i = 2
            while int(float(cur_row[0])) > int(float(next_row[0])):
                tempr_yr.insert(0, cur_row[1])
                self.days.insert(0, int(float(cur_row[0])))
                cur_row = copy.copy(next_row)
                i+=1
                next_row = lines[len(lines)-i].split()
            tempr_yr.insert(0, cur_row[1])
            self.days.insert(0, int(float(cur_row[0])))
            surf_tempr.append(tempr_yr[:])
        surf_tempr = np.array(surf_tempr[0], dtype=float)
        self.LST = surf_tempr
        self.d180w = -2
        self.carb_proxy = carb.carb_sensor(self.LST, self.d180w, model=self.model.get())

    def generate_graph(self):
        """
        with open("BCC-ERA-Tlake-humid_surf.dat", "r") as data:
            line_num = 0
            for line in data:
                line_vals = line.split()
                self.days.append(line_vals[0])
            self.days = self.days[self.nspin * 12 + 2:len(self.days)]
        self.days = [int(float(day)) for day in self.days]
        """
        self.f.clf()
        self.plt = self.f.add_subplot(111)
        self.plt.set_title(r'SENSOR')
        self.plt.set_xlabel('Time')
        self.plt.set_ylabel('Simulated Carbonate Data')
        self.plt.scatter(self.days, self.carb_proxy, color="#ff6053")
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.canvas.draw()

    def download_carb_data(self):
        df = pd.DataFrame({"Time":self.days, "Simulated Carbonate Data":self.carb_proxy})
        export_file_path = fd.asksaveasfilename(defaultextension='.csv')
        df.to_csv(export_file_path, index=None)

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
                                command = lambda: self.uploadLeafwaxTxt("sample"))
        graphButton.grid(row=rowIdx, column=1, pady=10,
                         ipadx=30, ipady=3, sticky="W")
        #Upload own text file
        graphButton = tk.Button(self, text="Upload own .txt File", font=f,
                                command = lambda: self.uploadLeafwaxTxt("user_file"))
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
        self.plt = self.f.add_subplot(111)
        self.plt.set_title(r'SENSOR', fontsize=12)
        self.plt.set_xlabel('Time')
        self.plt.set_ylabel('Simulated Leafwax Data')
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.canvas.draw()

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

        self.nspin = ""
        with open("heatflux.inc", "r") as inc:
            lines = inc.readlines()
            nspin_line = lines[69]
            idx = 0
            while nspin_line[idx] != "=":
                idx += 1
            idx += 1
            while nspin_line[idx] != ")":
                self.nspin += nspin_line[idx]
                idx += 1
            self.nspin = int(self.nspin)

        self.fC_3 = 0.7  # fraction of C3 plants
        self.fC_4 = 0.3  # fraction of C4 plants
        self.eps_c3 = -112.8  # pm 34.7
        self.eps_c4 = -124.5  # pm 28.2

        # define the error range on the epsilon (apparent fractionation) measurement:
        self.eps_c3_err = 34.7
        self.eps_c4_err = 28.2

        self.leafwax_proxy = leafwax.wax_sensor(self.dDp, self.fC_3, self.fC_4, self.eps_c3, self.eps_c4)

        #add uncertainties in apparent fractionation via monte-carlo resampling process:
        self.delta_d_wax_mc, self.Q1, self.Q2 = leafwax.wax_uncertainty(self.dDp, self.fC_3, self.fC_4, self.eps_c3,
                                                                        self.eps_c4, self.eps_c3_err, self.eps_c4_err)
        # where Q1 is the 2.5th percentile, Q2 is the 97.5th percentile of the 1000 MC realizations

    def generate_graph(self):
        self.days = []
        with open("BCC-ERA-Tlake-humid_surf.dat", "r") as data:
            line_num = 0
            for line in data:
                line_vals = line.split()
                if line_num >= 142:
                    self.days.append(line_vals[0])
                line_num += 1
        self.days = [int(float(day)) for day in self.days]
        self.f.clf()
        self.plt = self.f.add_subplot(111)
        self.plt.set_title(r'SENSOR')
        self.plt.set_xlabel('Time')
        self.plt.set_ylabel('Simulated Leaf Wax Data')

        self.plt.fill_between(self.days,self.Q1,self.Q2,facecolor='grey',edgecolor='none',alpha=0.20)
        self.plt.plot(self.days, self.leafwax_proxy, color="#000000", linewidth=3)
        self.plt.scatter(self.days, self.leafwax_proxy, color="#000000")
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.canvas.draw()

    def download_leafwax_data(self):
        df = pd.DataFrame({"Time":self.days, "Simulated Leafwax Data":self.leafwax_proxy, "95% CI Lower Bound":self.Q1,
                           "95% CI Upper Bound":self.Q2})
        path = fd.askdirectory()
        df.to_csv(path+"/leafwax_timeseries.csv", index=False)

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
        tk.Button(self, text="Submit Data", command=self.upload_csv, font=f).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx += 1
        parameters = ["Start Year:","End Year:", "Mixed Layer Thickness Coefficient:", "Abundance:", "Number of Carriers:"]
        param_values = []
        for i in range(rowIdx, rowIdx + 5):
            tk.Label(self, text=parameters[i - rowIdx], font=f).grid(
                row=i, column=0, sticky="W")
            p = tk.Entry(self)
            p.grid(row=i, column=1, sticky="W")
            param_values.append(p)
        rowIdx+=5
        tk.Button(self, text="Submit Parameters", font=f, command=lambda: self.run_bioturb_model([p.get() for p in param_values])).grid(
            row=rowIdx, column=0, sticky="W")

    def upload_csv(self):
        # Open the file choosen by the user
        self.txtfilename = fd.askopenfilename(filetypes=(('csv files', 'csv'),))
        self.currentTxtFileLabel.configure(text=basename(self.txtfilename))

    def run_bioturb_model(self, params):
        for p in params:
            if not p:
                tk.messagebox.showerror(title="Run Bioturbation Model", message="Not all parameters were entered.")
                return
        params = [int(p) for p in params]
        if params[0] > params[1]:
            tk.messagebox.showerror(title="Run Bioturbation Model", message="Start year cannot be greater than end year")
        self.age = params[1] - params[0]
        self.mxl = np.ones(self.age)*params[2]
        print(np.ones(self.age)*params[3])
        self.abu2 = list(np.ones(self.age)*params[3])[(-(self.age)-1):-1]
        print(self.abu2)
        self.numb = params[4]
        self.iso = pd.read_csv(self.txtfilename)["Pseudoproxy"]
        self.oriabu, self.bioabu, self.oriiso, self.bioiso = bio.bioturbation(self.abu2, self.iso, self.mxl, self.numb)
        print(self.oriabu)

        """
        self.f.clf()
        self.plt = self.f.add_subplot(111)
        self.plt.set_title(r'ARCHIVE')
        self.plt.set_xlabel('Time')
        self.plt.set_ylabel('Bioturbated Data')

        self.plt.plot(self.days, self.bioiso, color="#000000", linewidth=3)
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.canvas.draw()
        """

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()