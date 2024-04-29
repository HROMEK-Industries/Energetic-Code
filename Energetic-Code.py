from tkinter import ttk,filedialog,font
from io import StringIO
import tkinter as tk
import sys
import re

#window
window = tk.Tk()
window.title("Energetic Code")
window.geometry("800x600")

#variables
file_path = None
console_position = tk.IntVar()
console_position.set(4)
console_output = StringIO()

theme = tk.IntVar()
theme.set(1)
light_theme = {"window_bg": "#f3f3f3",
               "menu_bar_bg":"#f3f3f3",
               "menu_bar_fg":"#464646",
               "editor_frame": "#f3f3f3",
               "editor_number_bg": "#ffffff",
               "editor_number_fg": "#76c3df",
               "editor_number_border": "#F5F5F5",
               "editor_text_bg": "#ffffff",
               "editor_text_fg": "#464646",
               "console_frame":"#f3f3f3",
               "console_label": "#3F3F3F",
               "console_bg":"#ffffff", 
               "console_fg": "#464646",
               "mark": "#1b1b1b",
               "keyword": "#3d5aff",
               "bool": "#873dff",
               "string": "#dd4141",
               "comment": "#3cc827"}

dark_theme = {"window_bg": "#343434",
               "menu_bar_bg":"#343434",
               "menu_bar_fg":"#F7F7F7",
               "editor_frame": "#1e1e1e",
               "editor_number_bg": "#464646",
               "editor_number_fg": "#76c3df",
               "editor_number_border": "#3E3E3E",
               "editor_text_bg": "#464646",
               "editor_text_fg": "#F7F7F7",
               "console_frame":"#343434",
               "console_label": "#d8d8d8",
               "console_bg":"#464646", 
               "console_fg": "#F7F7F7",
               "mark": "#FFFFFF",
               "keyword": "#F99216",
               "bool": "#F95E16",
               "string": "#72D532",
               "comment": "#797979"}

selected_theme = None

police_default = ("Helvetica", 12)

# keywords =  re.compile(r'\b(?:and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|None|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b'),
keywords = ["and","as","async","assert","break","class","continue","def","del","elif","else","except","False","finally","for","from","global","if","import","in","is","lambda","None","nonlocal","not","or","pass","raise","return","True","try","while","with","yield"]



#functions
def KeyRelease_function(event=None):
    highlight_function()
    add_numbers_line()

#file functions
def run(event=None):
    sys.stdout = console_output
    console_text = console_output.getvalue()
    terminal_text.config(state="normal")
    code_data = editor_text.get(1.0, tk.END)

    try:
        exec(code_data)
        terminal_text.delete(1.0, tk.END)  # Efface la console avant l'exécution du code
        terminal_text.insert("end", str(console_text))
        terminal_text.config(state="disable")
    except Exception as e:
        terminal_text.delete(1.0, tk.END)
        terminal_text.insert("end", f"Error: {str(e)}\n")
        terminal_text.config(state="disable")

def new_file(event=None):
    global file_path
    editor_text.delete(1.0, tk.END)
    editor_text.insert(1.0, "#write your code here")
    file_path = None
    print("new file :" +str(file_path))

def save_file(event=None):
    if file_path != None or "":
        with open(str(file_path), "w") as f:
            f.write(editor_text.get(1.0, tk.END))
    else :
        save_as()
    print("save :" +str(file_path))

def save_as(event=None):
    global file_path
    file_path = tk.filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
    print("save as :" + file_path)
    with open(str(file_path), "w") as f:
        f.write(editor_text.get(1.0, tk.END))

def open_file(event=None):
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    with open(file_path, "r") as f:
        content = f.read()
        editor_text.delete(1.0, tk.END)
        editor_text.insert(tk.END, content)
    print("save as :" +str(file_path))

#editor functions
def select_all(event=None):
    editor_text.tag_add("sel", "1.0", "end")

def add_indetations():

    print("hey")

# hard code part
def add_numbers_line(event=None):
    police = editor_text.cget("font")
    if police:
    # Extracts the height of the font
        line_height = tk.font.Font(font=police).metrics("linespace")
    else:
        #choose a default height in wrong issue
        line_height = 20  # Vous pouvez ajuster cette valeur selon votre besoin

    lines_number_canva.delete("numero_ligne")
    
    y0 = int(editor_text.yview()[0] * editor_text.winfo_height())
    y1 = int(editor_text.yview()[1] * editor_text.winfo_height())

    first_visible_line = editor_text.index("@0,%d" % y0).split('.')[0]
    last_visible_line = editor_text.index("@0,%d" % y1).split('.')[0]

    for i in range(int(first_visible_line), int(last_visible_line) + 1):
        y = (i - int(first_visible_line)) * line_height
        lines_number_canva.create_text(5, y, anchor="nw", text=str(i),fill=selected_theme["editor_number_fg"], tags="line_number")

#theme
def themes_function():
    global selected_theme
    if theme.get() == 1:
        selected_theme = light_theme
    elif theme.get() ==2:
        selected_theme = dark_theme

    #for window
    window.config(bg=selected_theme["window_bg"])
    #menu bar
    menu_bar.config(bg=selected_theme["menu_bar_bg"],fg=selected_theme["menu_bar_fg"],)
    #for text editor
    editor_Frame.config(bg=selected_theme["editor_frame"])
    lines_number_canva.config(bg=selected_theme["editor_number_bg"],highlightbackground=selected_theme["editor_number_border"])
    lines_number_canva.itemconfigure("line_number", fill=selected_theme["editor_number_fg"])
    editor_text.config(bg=selected_theme["editor_text_bg"], fg=selected_theme["editor_text_fg"],insertbackground=selected_theme["mark"])
    #for terminal
    terminal_frame.config(bg=selected_theme["console_frame"])
    terminal_label.config(bg=selected_theme["console_frame"],fg=selected_theme["console_label"])
    terminal_text.config(bg=selected_theme["console_bg"], fg=selected_theme["console_fg"])

#still in progress
def highlight_function(event=None):
    #deletes the existant tags
    editor_text.tag_remove("keyword", 1.0, tk.END)
    editor_text.tag_remove("string", 1.0, tk.END)
    editor_text.tag_remove("comment", 1.0, tk.END)
    editor_text.tag_remove("bool", 1.0, tk.END)

    code_data = editor_text.get(1.0, tk.END)

    #divides the code in lines
    lines = code_data.split("\n")

    for i, line in enumerate(lines, 1):
        #for keywords
        for keyword in keywords:
        # searches word in the text belonging to keywords list
            for match in re.finditer(r'\b{}\b'.format(keyword), line):
               
                start_index = "{}.{}".format(i, match.start())
                end_index = "{}.{}".format(i, match.end())
                
                if match.group(0) != "True" and match.group(0) != "False":
                    editor_text.tag_add("keyword", start_index, end_index)
                else:
                    editor_text.tag_add("bool", start_index, end_index)

        #for strings
        for string in re.finditer(r'(\'[^\']*\'|\"[^\"]*\")', line):
            first_str = f"{i}.{string.start()}" 
            last_str = f"{i}.{string.end()}"
            editor_text.tag_add("string", first_str, last_str)
        # for comment
        for comment in re.finditer(r'(#.*)', line):
            begin_comment = f"{i}.{comment.start()}"
            end_comment = f"{i}.end"
            editor_text.tag_add("comment", begin_comment, end_comment)
    #apply the color
    editor_text.tag_configure("bool", foreground=selected_theme["bool"])
    editor_text.tag_configure("keyword", foreground=selected_theme["keyword"])
    editor_text.tag_configure("string", foreground=selected_theme["string"])
    editor_text.tag_configure("comment", foreground=selected_theme["comment"])

#Create the top bar
menu_bar = tk.Menu(borderwidth=0)
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
preferences_menu.add_cascade(menu=console_position_menu,label="Console position(in progress)")

#block text
editor_Frame = tk.Frame(window,bg="red")
editor_Frame.pack(fill="both",expand=True)

lines_number_canva = tk.Canvas(editor_Frame,width=30)
# lines_number_canva = tk.Canvas(editor_Frame,width=30,highlightbackground="#F5F5F5")

lines_number_canva.pack(side="left",fill="y")

editor_text = tk.Text(editor_Frame, font=police_default,borderwidth=0, highlightthickness=0)
editor_text.pack(side="left",fill="both",expand=True)


# #terminal block
terminal_frame = tk.Frame(window)
terminal_frame.pack(expand=True,fill="both",padx=(5, 0),pady=(0,5))
terminal_label = tk.Label(terminal_frame, text="console output:")
terminal_label.pack(anchor="w")
terminal_text = tk.Text(terminal_frame,bg="gainsboro",state="disabled",borderwidth=0, highlightthickness=0)
terminal_text.pack(fill="both")


#shortcuts
window.bind_all("<F5>", run)
window.bind_all("<Control-Key-5>", run)
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
editor_text.bind("<KeyRelease>", KeyRelease_function)
# window.bind_all("<Control-slash>", comment_line)
# window.bind_all("<Control-slash>", comment_line)


window.config(menu=menu_bar)
themes_function()
new_file()
window.mainloop()
