import tkinter as tk
import sys
from tkinter import ttk
from io import StringIO

#window
window = tk.Tk()
window.title("Energetic-Code")
window.geometry("800x600")

#variables
theme = tk.IntVar()
theme.set(1)
console_position = tk.IntVar()
console_position.set(4)
console_output = StringIO()

#functions
def run():
    terminal_block.config(state="normal")
    terminal_block.delete(1.0,tk.END)
    code_data = block_txt.get(1.0, tk.END)

    try:
        sys.stdout = console_output
        exec(code_data)
        console_text = console_output.getvalue()
        terminal_block.insert("end", str(console_text))
        terminal_block.config(state="disable")
    except Exception as e:
        terminal_block.insert("end", f"Error: {str(e)}\n")
        terminal_block.config(state="disable")



def new_file_clicked(event=None):
    print("hey")

def save():
    print("save")

def save_as():
    print("save_as")


def open():
    print("open")

#Create the top bar
menu_bar = tk.Menu()
#file
file_menu = tk.Menu(menu_bar, tearoff=False)
file_menu.add_command(label="New",accelerator="Ctrl+N",command=new_file_clicked)
file_menu.add_command(label="Save",accelerator="Ctrl+S",command=save)
file_menu.add_command(label="Save_as",accelerator="Shift+Ctrl+A",command=save_as)
file_menu.add_command(label="open",accelerator="Ctrl+O",command="open")
file_menu.add_separator()
file_menu.add_command(label="Exit",accelerator=None, command=exit)
menu_bar.add_cascade(menu=file_menu, label="File")
#run
run_menu = tk.Menu(menu_bar, tearoff=False)
run_menu.add_command(label="Run",accelerator="F5",command=run)
menu_bar.add_cascade(menu=run_menu, label="Run")
#preferences
preferences_menu = tk.Menu(menu_bar, tearoff=False)
theme_menu = tk.Menu(menu_bar,tearoff=False)
console_position_menu = tk.Menu(menu_bar,tearoff=False)
theme_menu.add_radiobutton(label="Light",value=1,variable=theme)
theme_menu.add_radiobutton(label="Dark",value=2,variable=theme)
console_position_menu.add_radiobutton(label="Right",value=1,variable=console_position)
console_position_menu.add_radiobutton(label="Left",value=2,variable=console_position)
console_position_menu.add_radiobutton(label="Top",value=3,variable=console_position)
console_position_menu.add_radiobutton(label="Bottom",value=4,variable=console_position)
menu_bar.add_cascade(menu=preferences_menu, label="Preferences")
preferences_menu.add_cascade(menu=theme_menu,label="Themes")
preferences_menu.add_cascade(menu=console_position_menu,label="Console position")

#block text
block_txt = tk.Text(window,bg="snow")
block_txt.pack(fill="both")

#terminal block
terminal_block = tk.Text(window,bg="gainsboro",state="disabled")
terminal_block.pack(fill="both")

#shortcuts
window.bind_all("<Control-n>", new_file_clicked)
window.bind_all("<Control-N>", new_file_clicked)

#run the program
window.config(menu=menu_bar)
window.mainloop()