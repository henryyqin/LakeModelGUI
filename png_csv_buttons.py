        # Save as PNG and CSV
        
        tk.Button(self.scrollable_frame, text="Save Graph Data as .csv", font=MED_FONT, command=self.download_csv).grid(
            row=0, column=6, ipadx=10, ipady=3, sticky="NE")
        
        tk.Button(self.scrollable_frame, text="Download graph as .png", font=MED_FONT, command=self.download_png).grid(
            row=0, column=7, ipadx=10, ipady=3, sticky="NE")

        # Return to Start Page
        homeButton = tk.Button(self.scrollable_frame, text="Back to start page", font=f,
            command=lambda: self.parent.show_frame(["PageBioturbation"], "StartPage"))        
        homeButton.grid(row=0, column=8, ipadx=10, ipady=3, sticky="NE")
