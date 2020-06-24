import tkinter as tk                # python 3
from tkinter import font as tkfont  # python 3
import os
from os.path import basename
import tkinter.filedialog as fd
import subprocess
import pandas as pd
import webbrowser
from tkinter import ttk
import multiprocessing
import threading
import copy

# Carbonate sensor
import sensor_carbonate as carb

# GDGT
import sensor_gdgt as gdgt

# Leafwax sensor
import sensor_leafwax as leafwax

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
plt.style.use('seaborn-whitegrid')

"""
if you want the user to upload something from the same directory as the gui
then you can use initialdir=os.getcwd() as the first parameter of askopenfilename
"""
LARGE_FONT = ("Verdana", 26)
MED_FONT = ("Verdana", 18)
f = ("Verdana", 12)

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
        for F in (StartPage, PageEnvModel, PageEnvTimeSeries, PageEnvSeasonalCycle, PageCarbonate, PageLeafwax, PageGDGT):
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


"""
Page to run the environment model
"""
class PageEnvModel(tk.Frame):

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
                 1) Upload a text file to provide input data for the lake model\n
                 2) Enter lake-specific and simulation-specific parameters\n
                 3) If parameters are left empty, default parameters for Lake Tanganyika will be used instead
                 """,  font=f, justify="left"
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

        #Entries for .inc file
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
        rowIdx+=1
        for i in range(rowIdx,rowIdx+16):
            tk.Label(self, text=parameters[i-rowIdx], font=f).grid(
                row=i, column=0, sticky="W")
            p = tk.Entry(self)
            p.grid(row=i, column=1, sticky="W")
            param_values.append(p)

        for i in range(rowIdx+16,rowIdx+25):
            tk.Label(self, text=parameters[i-rowIdx], font=f).grid(
                row=i-16, column=2, sticky="W")
            p = tk.Entry(self)
            p.grid(row=i-16, column=3, sticky="W")
            param_values.append(p)

        rowIdx+=16

        #Submit entries for .inc file
        submitButton = tk.Button(self, text="Submit Parameters", font=f,
                                 command=lambda: self.editInc([p.get() for p in param_values], parameters))
        submitButton.grid(row=rowIdx, column=1, pady=10, ipadx=30, ipady=3, sticky="W")

        rowIdx+=1


        # Button to run the model (Mac/Linux only)
        runButton = tk.Button(
            self, text="Run Model", font=f,command=lambda: self.runModel(runButton))
        runButton.grid(row=rowIdx, column=1, ipadx=30, ipady=3, sticky="W")
        rowIdx+=1

        csvButton = tk.Button(self, text='Download CSV', font=f, command=lambda: self.download_csv())
        csvButton.grid(row=rowIdx, column=2, ipadx=30, ipady=3, sticky="W")

        # Return to Start Page
        homeButton = tk.Button(self, text="Back to start page", font=f,
                               command=lambda: controller.show_frame("StartPage"))
        # previousPageB.pack(anchor = "w", side = "bottom")
        homeButton.grid(row=rowIdx, column=3, ipadx=25,
                        ipady=3, pady=3, sticky="E")
        rowIdx += 1

    """
    Takes a .txt file
    """

    def uploadTxt(self):
        # Open the file choosen by the user
        self.txtfilename = fd.askopenfilename(
            filetypes=(('text files', 'txt'),))
        self.currentTxtFileLabel.configure(text=basename(self.txtfilename))
        with open("env_heatflux.f90", "r+") as f:
            new = f.readlines()
            if self.txtfilename != "":
                new[18] = "      !data_input_filename = '"+self.txtfilename+"'\n"
                new[732] = "      open(unit=15,file='"+self.txtfilename+"',status='old')\n"
            f.seek(0)
            f.truncate()
            f.writelines(new)
            f.close()
        with open("Malawi.inc","r+") as f:
            new = f.readlines()
            if self.txtfilename != "":
                new[56] = "    character(38) :: datafile='"+self.txtfilename+"' ! the data file to open in FILE_OPEN subroutine\n"
            f.seek(0)
            f.truncate()
            f.writelines(new)
            f.close()

    """
    Edits the parameters in the .inc file
    """

    def editInc(self, parameters, comments):
        with open("Malawi.inc", "r+") as f:
            new = f.readlines()
            #names of the parameters that need to be modified
            names = ["oblq","xlat","xlon","gmt","max_dep","basedep","b_area","cdrn","eta","f","alb_slush",
                           "alb_snow", "depth_begin", "salty_begin", "o18air", "deutair", "nspin", "bndry_flag",
                           "sigma","wb_flag","iceflag","s_flag","o18flag","deutflag","z_screen"]
            #line numbers in the .inc file that need to be modified
            rows = [28,29,30,31,32,33,34,35,36,37,38,39,41,42,44,45,69,70,71,72,73,74,75,76,77]
            for i in range(0, len(parameters)):
                if len(parameters[i]) != 0:
                    new[rows[i]] = "    parameter ("+names[i]+" = "+parameters[i]+")   ! "+comments[i]+"\n"
            f.seek(0)
            f.truncate()
            f.writelines(new)
            f.close()

    """
    Takes a .inc file
    def uploadInc(self):
        # Open the file choosen by the user
        self.incfilename = fd.askopenfilename(
            filetypes=(('include files', 'inc'),))
        self.currentIncFileLabel.configure(text=basename(self.incfilename))
        print(self.incfilename)
    Edits the .inc file that was chosen by the user (for Mac)
    def editTextMac(self):
        # Checks if a file was uploaded at all
        if self.incfilename == '':
            return
        subprocess.call(['open', '-a', 'TextEdit', self.incfilename])
    Edits the .inc file that was chosen by the user (for Windows)
    def editTextWindows(self):
        # Checks if a file was uploaded at all
        if self.incfilename == '':
            return
        subprocess.Popen([notepad, self.incfilename])
    """

    """
    Disables run model button and creates separate process for lake model
    """

    def runModel(self, btn):
        btn["state"]="disabled"
        model_process = multiprocessing.Process(target=self.computeModel)
        model_process.start()
        """
        pbar = ttk.Progressbar(self, orient="horizontal", length=100, mode="indeterminate")
        pbar.grid(row=30,column=1, sticky="W")
        pbar.start()
        file_path = os.getcwd() + "/profile_output.dat"
        self.after(30000, lambda: self.check_file(file_path, 0, pbar, btn))
        """


    """
    Compiles a Fortran wrapper and runs the model
    """

    def computeModel(self):
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
        read_file = pd.read_csv("ERA-HIST-Tlake_surf.dat")
        export_file_path = fd.asksaveasfilename(defaultextension='.csv')
        read_file.to_csv(export_file_path, index=None)

"""
Page to plot environment model time series
"""
class PageEnvTimeSeries(tk.Frame):

    def __init__(self, parent, controller):
        rowIdx=1
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(
            self, text="Environment Model Time Series", font=LARGE_FONT)
        label.grid(row=rowIdx, columnspan=3, rowspan=3, pady=5, sticky="we")
        rowIdx+=3

        # Empty graph, default
        self.f = Figure(figsize=(10, 5), dpi=100)
        self.plt = self.f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.plt.set_title(r'Time Series', fontsize=12)
        self.plt.set_xlabel('Days')
        self.plt.set_ylabel('Lake Surface Temperature')
 

        # Lake Surface Temperature
        LSTButton = tk.Button(self, text="Graph Surface Temperature", font=f, 
                        command=lambda : self.generate_env_time_series(1, 'Surface Temperature')) # 2nd column
        LSTButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Mixing Depth
        MDButton = tk.Button(self, text="Graph Mixing Depth", font=f, 
                        command=lambda : self.generate_env_time_series(2, 'Mixing Depth')) # 3rd column
        MDButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Evaporation Rate
        ERButton = tk.Button(self, text="Graph Evaporation", font=f, 
                        command=lambda : self.generate_env_time_series(3, 'Evaporation')) # 4th column
        ERButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Latent Heat Flux
        LHFButton = tk.Button(self, text="Graph Latent Heat (QEW)", font=f, 
                        command=lambda : self.generate_env_time_series(4, 'Latent Heat Flux (QEW)')) # 5th column
        LHFButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Sensible Heat Flux
        SHFButton = tk.Button(self, text="Graph Sensible Heat (QHW)", font=f, 
                        command=lambda : self.generate_env_time_series(5, 'Sensible Heat (QHW)')) # 6th column
        SHFButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Downwelling Shortwave Radiation (SWW)
        SWWButton = tk.Button(self, text="Graph Downwelling Shortwave Radiation (SWW)", font=f, 
                        command=lambda : self.generate_env_time_series(6, 'Downwelling Shortwave Radiation (SWW)')) # 6th column
        SWWButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Upwelling Longwave Raditation (LUW)
        LUWButton = tk.Button(self, text="Graph Upwelling Longwave Raditation (LUW)", font=f, 
                        command=lambda : self.generate_env_time_series(7, 'Upwelling Longwave Raditation (LUW)')) # 6th column
        LUWButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Max Mixing Depth
        MMDButton = tk.Button(self, text="Graph Max Mixing Depth", font=f, 
                        command=lambda : self.generate_env_time_series(8, 'Max Mixing Depth')) # 6th column
        MMDButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Lake Depth
        LDButton = tk.Button(self, text="Graph Lake Depth", font=f, 
                        command=lambda : self.generate_env_time_series(9, 'Lake Depth')) # 6th column
        LDButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=10
        

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
    # only takes data after the lake has reached equilibriam, e.g. when the days stop repeating
    def generate_env_time_series(self, column, varstring):
        self.days = [] # x-axis
        self.yaxis = [] # y-axis

        with open("ERA-HIST-Tlake_surf.dat") as data:
            lines = data.readlines()
            cur_row = lines[len(lines)-1].split()
            next_row = lines[len(lines)-2].split()
            i = 2
            while int(float(cur_row[0])) > int(float(next_row[0])):
                self.yaxis.insert(0, float(cur_row[column]))
                self.days.insert(0, int(float(cur_row[0])))
                cur_row = copy.copy(next_row)
                i+=1
                next_row = lines[len(lines)-i].split()
            self.yaxis.insert(0, float(cur_row[column]))
            self.days.insert(0, int(float(cur_row[0])))




        self.f.clf()
        self.plt = self.f.add_subplot(111)
        self.plt.ticklabel_format(useOffset=False) # this is to disable matplotlib offset
        self.plt.set_title(r'' + varstring + ' over Time')
        self.plt.set_xlabel('Days')
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
        rowIdx=1
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(
            self, text="Environment Model Seasonal Cycle", font=LARGE_FONT)
        label.grid(row=rowIdx, columnspan=3, rowspan=3, pady=5, sticky="we")
        rowIdx+=3

        # Empty graph, default
        self.f = Figure(figsize=(10, 5), dpi=100)
        self.plt = self.f.add_subplot(111)
        self.plt.ticklabel_format(useOffset=False) # this is to disable matplotlib offset
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.plt.set_title(r'Seasonal Cycle', fontsize=12)
        self.plt.set_xlabel('Day of the Year')
        self.plt.set_ylabel('')

        # Graph button for each variable

        # Lake Surface Temperature
        LSTButton = tk.Button(self, text="Graph Surface Temperature", font=f, 
                        command=lambda : self.generate_env_seasonal_cycle(1, 'Surface Temperature')) # 2nd column
        LSTButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Mixing Depth
        MDButton = tk.Button(self, text="Graph Mixing Depth", font=f, 
                        command=lambda : self.generate_env_seasonal_cycle(2, 'Mixing Depth')) # 3rd column
        MDButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Evaporation Rate
        ERButton = tk.Button(self, text="Graph Evaporation", font=f, 
                        command=lambda : self.generate_env_seasonal_cycle(3, 'Evaporation')) # 4th column
        ERButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Latent Heat Flux
        LHFButton = tk.Button(self, text="Graph Latent Heat (QEW)", font=f, 
                        command=lambda : self.generate_env_seasonal_cycle(4, 'Latent Heat Flux (QEW)')) # 5th column
        LHFButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Sensible Heat Flux
        SHFButton = tk.Button(self, text="Graph Sensible Heat (QHW)", font=f, 
                        command=lambda : self.generate_env_seasonal_cycle(5, 'Sensible Heat (QHW)')) # 6th column
        SHFButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Downwelling Shortwave Radiation (SWW)
        SWWButton = tk.Button(self, text="Graph Downwelling Shortwave Radiation (SWW)", font=f, 
                        command=lambda : self.generate_env_seasonal_cycle(6, 'Downwelling Shortwave Radiation (SWW)')) # 6th column
        SWWButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Upwelling Longwave Raditation (LUW)
        LUWButton = tk.Button(self, text="Graph Upwelling Longwave Raditation (LUW)", font=f, 
                        command=lambda : self.generate_env_seasonal_cycle(7, 'Upwelling Longwave Raditation (LUW)')) # 6th column
        LUWButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Max Mixing Depth
        MMDButton = tk.Button(self, text="Graph Max Mixing Depth", font=f, 
                        command=lambda : self.generate_env_seasonal_cycle(8, 'Max Mixing Depth')) # 6th column
        MMDButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=1

        # Lake Depth
        LDButton = tk.Button(self, text="Graph Lake Depth", font=f, 
                        command=lambda : self.generate_env_seasonal_cycle(9, 'Lake Depth')) # 6th column
        LDButton.grid(row=rowIdx, column=1, pady=5,
                         ipadx=25, ipady=5, sticky="W")
        rowIdx+=10

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
        self.days = [] # x-axis
        self.yaxis = [] # y-axis

        with open("ERA-HIST-Tlake_surf.dat") as data:
            lines = data.readlines()
            cur_row = lines[len(lines)-1].split()
            next_row = lines[len(lines)-2].split()
            i = 2
            while int(float(cur_row[0])) > int(float(next_row[0])):
                self.yaxis.insert(0, float(cur_row[column]))
                self.days.insert(0, int(float(cur_row[0])))
                cur_row = copy.copy(next_row)
                i+=1
                next_row = lines[len(lines)-i].split()
            self.yaxis.insert(0, float(cur_row[column]))
            self.days.insert(0, int(float(cur_row[0])))

        # At this point, self.days and self.yaxis are identical to the ones in envtimeseries

        self.ydict = {} # dictionary to store the y values for each day from 15 to 375
        for day in self.days: # 15, 45, ...
            # if the day is not a key, then make an empty list
            if day % 390 not in self.ydict:
                self.ydict[day % 390] = []
            # otherwise append to that list
            else:
                self.ydict[day % 390].append(self.yaxis[int((day - 15)/30)]) # (day - 15)/30 gets the correct index


        # After yval array is formed for each xval, generate the axtual yaxis data
        self.seasonal_yaxis = [] # actual plotting data for y
        self.seasonal_days = range(15, 376, 30) # actual plotting data for x, count from 15 to 375 by 30's
        for day in self.seasonal_days:
            self.seasonal_yaxis.append(mean(self.ydict[day])) # mean the values of each day

        self.f.clf()
        self.plt = self.f.add_subplot(111)
        self.plt.ticklabel_format(useOffset=False) # this is to disable matplotlib offset
        self.plt.set_title(r'' + varstring + ' Seasonal Cycle')
        self.plt.set_xlabel('Day of the Year')
        self.plt.set_ylabel('Average ' + varstring)
        self.plt.scatter(self.seasonal_days, self.seasonal_yaxis, color="#ff6053")
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(
            row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.canvas.draw()

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
            tk.Radiobutton(self, text=name, font=MED_FONT, value=name, variable=self.model).grid(row=rowIdx, column=0, pady=1,
                         ipadx=20, ipady=5, sticky="W")
            rowIdx += 1
        tk.Button(self, text="Submit Model", font=MED_FONT, command=self.run_carbonate_model).grid(
            row=rowIdx, column=0, pady=1,
                         ipadx=20, ipady=5, sticky="W")
        rowIdx += 1

        tk.Button(self, text="Generate Graph of Carbonate Proxy Data", font=MED_FONT, command=self.generate_graph).grid(
            row=rowIdx, column=0, pady=1,
                         ipadx=20, ipady=5, sticky="W")
        rowIdx+=1
        tk.Button(self, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_carb_data).grid(
            row=rowIdx, column=0, pady=1,
                         ipadx=20, ipady=5, sticky="W")
        rowIdx+=1

        # Return to Start Page
        tk.Button(self, text="Back to start", font=f,
                                command=lambda: controller.show_frame("StartPage")).grid(
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
        with open("ERA-HIST-Tlake_surf.dat") as data:
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

        self.model = tk.StringVar()
        self.model.set("TEX86-tierney")
        model_names = ["TEX86-tierney","TEX86-powers","TEX86-loomis","MBT-R","MBT-J"]
        for name in model_names:
            tk.Radiobutton(self, text=name, value=name, variable=self.model).grid(row=rowIdx, column=0, sticky="W")
            rowIdx+=1
        tk.Button(self, text="Submit Model", command=self.run_gdgt_model).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx+=1


        tk.Button(self, text="Generate Graph of GDGT Proxy Data", command=self.generate_graph).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx+=1
        tk.Button(self, text="Save Graph Data as .csv", command=self.download_gdgt_data).grid(
            row=rowIdx, column=0, sticky="W")
        rowIdx+=1

        # Return to Start Page
        tk.Button(self, text="Back to start", 
                                command=lambda: controller.show_frame("StartPage")).grid(
                                row=rowIdx, column=0, sticky="W")

        # # previousPageB.pack(anchor = "w", side = "bottom")
        # homeButton.grid(row=rowIdx, column=3, ipadx=25,
        #                 ipady=3, pady=30, sticky="W")
        # rowIdx += 1

        self.f = Figure(figsize=(9, 5), dpi=100)
        self.plt = self.f.add_subplot(111)
        self.plt.set_title(r'SENSOR', fontsize=12)
        self.plt.set_xlabel('Time')
        self.plt.set_ylabel('Simulated GDGT Data')
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.canvas.draw()
    """
    Create time series data for GDGT sensor
    """

    def run_gdgt_model(self):
        surf_tempr = []
        self.days = []
        with open("ERA-HIST-Tlake_surf.dat") as data:
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

        # unchanged
        climate_input = 'ERA_INTERIM_climatology_Tang_2yr.txt'
        air_tempr = []
        with open(climate_input, 'r') as data:
            airtemp_yr = []
            for line in data:
                line_vals = line.split()
                airtemp_yr.append(line_vals[2])
            air_tempr.append(airtemp_yr)
        air_tempr = np.array(air_tempr[0], dtype = float)

        self.LST = surf_tempr
        self.MAAT = air_tempr
        self.beta = 1./50.
        self.gdgt_proxy = gdgt.gdgt_sensor(self.LST,self.MAAT,self.beta,model=self.model.get())

    def generate_graph(self):
        self.f.clf()
        self.plt = self.f.add_subplot(111)
        self.plt.set_title(r'SENSOR')
        self.plt.set_xlabel('Time')
        self.plt.set_ylabel('Simulated GDGT Data')
        self.plt.scatter(self.days, self.gdgt_proxy, color="#ff6053")
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.canvas.draw()

    def download_gdgt_data(self):
        df = pd.DataFrame({"Time":self.days, "Simulated GDGT Data":self.gdgt_proxy})
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
            self, text="Run Lake Environment Model", font=LARGE_FONT)
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
        with open("Malawi.inc", "r") as inc:
            lines = inc.readlines()
            nspin_line = lines[62]
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

        # add uncertainties in apparent fractionation via monte-carlo resampling process:
        #self.delta_d_wax_mc, self.Q1, self.Q2 = leafwax.wax_uncertainty(self.dDp, self.fC_3, self.fC_4, self.eps_c3,
                                                                        #self.eps_c4, self.eps_c3_err, self.eps_c4_err)

        # where Q1 is the 2.5th percentile, Q2 is the 97.5th percentile of the 1000 MC realizations

    def generate_graph(self):
        self.days = []
        with open("ERA-HIST-Tlake_surf.dat", "r") as data:
            line_num = 0
            for line in data:
                line_vals = line.split()
                if line_num >= self.nspin * 12 and line_num >= 142:
                    self.days.append(line_vals[0])
                line_num += 1
        self.days = [int(float(day)) for day in self.days]
        # TEMPORARY: CUTTING NUMBER OF DAYS SO THAT X AND Y IS SAME SIZE
        self.leafwax_proxy = self.leafwax_proxy[:24]
        self.f.clf()
        self.plt = self.f.add_subplot(111)
        self.plt.set_title(r'SENSOR')
        self.plt.set_xlabel('Time')
        self.plt.set_ylabel('Simulated Leaf Wax Data')
        # error line chart
        # sigma = float(sigmaRaw)
        # self.R3 = sigma 
        # inputs = len(self.X)
        # self.X = self.cell
        # self.X = self.X.reshape(inputs,1)
        # Xn = analytical_error.analytical_error(self.X, sigma, inputs)
        # Xn = Xn[:,0,:].reshape(inputs, inputs) 
        # self.gaussq1=mquantiles(Xn,prob=[0.025,0.975],axis=1)
        # q2=self.time
        # self.plt.fill_between(q2,self.gaussq1[:,0],self.gaussq1[:,1],
        #     label='100 Gaussian Analytical Error Realizations, CI', facecolor='darkgray',alpha=0.5)
        #self.plt.errorbar(self.days, self.leafwax_proxy, yerr=0.8, fmt='o', color='black', ecolor='lightgray', elinewidth=3, capsize=0)

        self.plt.scatter(self.days, self.leafwax_proxy, color="#ff6053")
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=16, columnspan=15, sticky="nw")
        self.canvas.draw()

    def download_leafwax_data(self):
        df = pd.DataFrame({"Time":self.days, "Simulated Leafwax Data":self.leafwax_proxy})
        path = fd.askdirectory()
        df.to_csv(path+"/leafwax_timeseries.csv", index=False)

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()