from tkinter import ttk,filedialog
from io import StringIO
import tkinter as tk
import sys

#window
window = tk.Tk()
window.title("Energetic-Code")
window.geometry("800x600")

#variables
file_path = None
console_position = tk.IntVar()
console_position.set(4)
console_output = StringIO()

theme = tk.IntVar()
theme.set(1)
light_theme = {"editor_bg": "#f6f6f6","editor_fg": "#000000","console_bg": "#d0d0d0","console_fg": "#000000","mark": "#000000"}
dark_theme = {"editor_bg": "#393e46","editor_fg": "#f7f7f7","console_bg": "#393e46","console_fg": "#f7f7f7", "mark": "#f7f7f7"}
#functions

#file functions
def run(event=None):
    terminal_block.config(state="normal")
    code_data = editor_block.get(1.0, tk.END)
    terminal_block.delete(1.0,tk.END)
    try:
        sys.stdout = console_output
        exec(code_data)
        console_text = console_output.getvalue()
        terminal_block.insert("end", str(console_text))
        terminal_block.config(state="disable")
    except Exception as e:
        terminal_block.insert("end", f"Error: {str(e)}\n")
        terminal_block.config(state="disable")

def new_file(event=None):
    global file_path
    editor_block.delete(1.0, tk.END)
    file_path = None
    print("new file :" +str(file_path))

def save_file(event=None):
    if file_path != None or "":
        with open(str(file_path), "w") as f:
            f.write(editor_block.get(1.0, tk.END))
    else :
        save_as()
    print("save :" +str(file_path))

def save_as(event=None):
    global file_path
    file_path = tk.filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
    print("save as :" + file_path)
    with open(str(file_path), "w") as f:
        f.write(editor_block.get(1.0, tk.END))

def open_file(event=None):
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    with open(file_path, "r") as f:
        content = f.read()
        editor_block.delete(1.0, tk.END)
        editor_block.insert(tk.END, content)
    print("save as :" +str(file_path))

#editor functions
def select_all(event=None):
    editor_block.tag_add("sel", "1.0", "end")

#theme
def themes_function():
    print(theme)
    if theme.get() == 1:
        editor_block.config(bg=light_theme["editor_bg"], fg=light_theme["editor_fg"],insertbackground=light_theme["mark"])
        terminal_block.config(bg=light_theme["console_bg"], fg=light_theme["console_fg"])
    elif theme.get() ==2:
        editor_block.config(bg=dark_theme["editor_bg"], fg=dark_theme["editor_fg"],insertbackground=dark_theme["mark"])
        terminal_block.config(bg=dark_theme["console_bg"], fg=dark_theme["console_fg"])


#Create the top bar
menu_bar = tk.Menu()
#file
file_menu = tk.Menu(menu_bar, tearoff=False)
file_menu.add_command(label="New",accelerator="Ctrl+N",command=new_file)
file_menu.add_command(label="Save",accelerator="Ctrl+S",command=save_file)
file_menu.add_command(label="Save_as",accelerator="Shift+Ctrl+A",command=save_as)
file_menu.add_command(label="open",accelerator="Ctrl+O",command=open_file)
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
theme_menu.add_radiobutton(label="Light",value=1,variable=theme,command=themes_function)
theme_menu.add_radiobutton(label="Dark",value=2,variable=theme,command=themes_function)
console_position_menu.add_radiobutton(label="Right",value=1,variable=console_position)
console_position_menu.add_radiobutton(label="Left",value=2,variable=console_position)
console_position_menu.add_radiobutton(label="Top",value=3,variable=console_position)
console_position_menu.add_radiobutton(label="Bottom",value=4,variable=console_position)
menu_bar.add_cascade(menu=preferences_menu, label="Preferences")
preferences_menu.add_cascade(menu=theme_menu,label="Themes")
preferences_menu.add_cascade(menu=console_position_menu,label="Console position")

#block text
editor_block = tk.Text(window)
editor_block.pack(fill="both")

#terminal block
terminal_block = tk.Text(window,bg="gainsboro",state="disabled")
terminal_block.pack(fill="both")

#shortcuts
window.bind_all("<F5>", run)
window.bind_all("<Control-5>", run)
window.bind_all("<Control-n>", new_file)
window.bind_all("<Control-N>", new_file)
window.bind_all("<Control-s>", save_file)
window.bind_all("<Control-S>", save_file)
window.bind_all("<Shift-Control-s>", save_as)
window.bind_all("<Shift-Control-S>", save_as)
window.bind_all("<Control-o>", open_file)
window.bind_all("<Control-O>", open_file)
window.bind_all("<Control-a>", select_all)
window.bind_all("<Control-A>", select_all)
# window.bind_all("<Control-slash>", comment_line)
# window.bind_all("<Control-slash>", comment_line)



#run the program
# editor_block.config(bg=light_theme["editor_bg"], fg=light_theme["editor_fg"],insertbackground=light_theme["mark"])
# terminal_block.config(bg=light_theme["console_bg"])
window.config(menu=menu_bar)
themes_function()
window.mainloop()