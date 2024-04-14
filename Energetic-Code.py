import tkinter as tk
from tkinter import ttk

#window
window = tk.Tk()
window.title("Energetic-Code")
window.geometry("800x600")

def run(event=None):
    print("hey")

def new_file_clicked(event=None):
    print("hey")


#Create the top bar
menu_bar = tk.Menu()

file_menu = tk.Menu(menu_bar, tearoff=False)
file_menu.add_command(label="New",accelerator="Ctrl+N",command=new_file_clicked)
file_menu.add_command(label="Save",accelerator="Ctrl+S",command="save")
file_menu.add_command(label="Save_as",accelerator="Shift+Ctrl+A",command="save_as")
file_menu.add_command(label="open",accelerator="Ctrl+O",command="open")
file_menu.add_separator()
file_menu.add_command(label="Exit",accelerator=None, command=exit)
menu_bar.add_cascade(menu=file_menu, label="File")

run = tk.Menu(menu_bar, tearoff=False)
run.add_command(label="Run",accelerator="F5",command=run)
menu_bar.add_cascade(menu=run, label="Run")


preferences_menu = tk.Menu(menu_bar, tearoff=False)
theme_menu = tk.Menu(menu_bar,tearoff=False)
theme = tk.IntVar()
theme.set(1)
theme_menu.add_radiobutton(label="Light",value=1,variable=theme)
theme_menu.add_radiobutton(label="Dark",value=2,variable=theme)
preferences_menu.add_cascade(menu=theme_menu,label="Themes")
menu_bar.add_cascade(menu=preferences_menu, label="Preferences")


#shortcuts
window.bind_all("<Control-n>", new_file_clicked)
window.bind_all("<Control-N>", new_file_clicked)

#run the program
window.config(menu=menu_bar)
window.mainloop()
