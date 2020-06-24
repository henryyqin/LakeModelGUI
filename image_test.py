from tkinter.ttk import Label
from PIL import ImageTk, Image 
import PIL.Image 
import PIL.ImageTk 


img = Image.open("tanganyika.png")
img = img.resize((250, 250), Image.ANTIALIAS) #The (250, 250) is (height, width)
img = ImageTk.PhotoImage(img) # convert to PhotoImage
image = C.create_image(1500,0, anchor = NE, image = img)
# image.pack() # canvas objects do not use pack() or grid()