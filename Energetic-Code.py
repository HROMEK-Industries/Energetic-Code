import os
import subprocess
import re
from tkinter import Tk, Text, Menu, filedialog, Scrollbar, Frame, Button, Label, END, Canvas, IntVar, colorchooser, simpledialog, messagebox, Toplevel
from PIL import Image, ImageTk

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Energetic Code")
        self.root.geometry("800x600")
        self.set_window_icon("Icon.ico")  # Set the application icon

        self.theme_var = IntVar(value=1)  # 1 for light theme, 2 for dark theme, 3 for custom theme

        self.text_editor = Text(self.root, wrap='word', undo=True)
        self.text_editor.pack(side='left', expand=True, fill='both', padx=(5, 0), pady=5)

        self.scroll_bar = Scrollbar(self.root, command=self.text_editor.yview)
        self.scroll_bar.pack(side='right', fill='y')
        self.text_editor.config(yscrollcommand=self.scroll_bar.set)

        self.line_numbers = Canvas(self.root, bg="#FFFFFF", width=30)
        self.line_numbers.pack(side='left', fill='y', padx=(5, 0), pady=5)

        self.text_editor.bind('<KeyRelease>', self.highlight_text)
        self.text_editor.bind("<KeyRelease>", self.enable_auto_completion)
        self.root.bind_all("<Control-f>", lambda event: self.find_and_replace())

        console_frame = Frame(self.root)
        console_frame.pack(expand=True, fill='both', padx=(5, 0), pady=(0, 5))

        console_label = Label(console_frame, text="Console Output")
        console_label.pack(anchor='w')

        self.console = Text(console_frame, wrap='word', state='disabled')
        self.console.pack(expand=True, fill='both')

        self.file_path = None

        buttons_frame = Frame(self.root)
        buttons_frame.pack(pady=(5, 0))

        new_button = Button(buttons_frame, text="New", command=self.new_file)
        new_button.grid(row=0, column=0, padx=5)

        open_button = Button(buttons_frame, text="Open", command=self.open_file)
        open_button.grid(row=0, column=1, padx=5)

        save_button = Button(buttons_frame, text="Save", command=self.save_file)
        save_button.grid(row=0, column=2, padx=5)

        run_button = Button(buttons_frame, text="Run", command=self.run_code)
        run_button.grid(row=0, column=3, padx=5)

        syntax_check_button = Button(buttons_frame, text="Syntax Check", command=self.syntax_check)
        syntax_check_button.grid(row=0, column=4, padx=5)

        self.main_menu = Menu()

        file_menu = Menu(self.main_menu, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        self.main_menu.add_cascade(label="File", menu=file_menu)

        self.root.bind_all("<Control-n>", lambda event: self.new_file())
        self.root.bind_all("<Control-o>", lambda event: self.open_file())
        self.root.bind_all("<Control-s>", lambda event: self.save_file())
        self.root.bind_all("<Control-S>", lambda event: self.save_as_file())

        run_menu = Menu(self.main_menu, tearoff=0)
        run_menu.add_command(label="Run", command=self.run_code, accelerator="F5")
        self.main_menu.add_cascade(label="Run", menu=run_menu)

        settings_menu = Menu(self.main_menu, tearoff=0)
        theme_menu = Menu(settings_menu, tearoff=0)
        theme_menu.add_radiobutton(label="Light", variable=self.theme_var, value=1, command=self.toggle_theme)
        theme_menu.add_radiobutton(label="Dark", variable=self.theme_var, value=2, command=self.toggle_theme)
        theme_menu.add_radiobutton(label="Custom", variable=self.theme_var, value=3, command=self.update_highlight_colors)
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        self.main_menu.add_cascade(label="Settings", menu=settings_menu)

        about_menu = Menu(self.main_menu, tearoff=0)
        about_menu.add_command(label="About", command=self.show_about)
        self.main_menu.add_cascade(label="About", menu=about_menu)

        self.root.config(menu=self.main_menu)

        self.highlight_rules = {
            'keyword': re.compile(r'\b(?:and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|None|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b'),
            'string': re.compile(r'\'[^\']*\'|\"[^\"]*\"'),
            'comment': re.compile(r'#.*'),
            'boolean': re.compile(r'\b(?:True|False)\b'),
        }

        self.light_theme_tags = {
            'keyword': 'orange',
            'string': 'green',
            'comment': 'gray',
            'boolean': 'blue',
        }

        self.dark_theme_tags = {
            'keyword': 'orange',
            'string': 'green',
            'comment': 'gray',
            'boolean': 'blue',
        }

    def highlight_text(self, *args):
        self.text_editor.tag_remove('keyword', '1.0', END)
        self.text_editor.tag_remove('string', '1.0', END)
        self.text_editor.tag_remove('comment', '1.0', END)
        self.text_editor.tag_remove('boolean', '1.0', END)

        theme_tags = self.light_theme_tags if self.theme_var.get() == 1 else self.dark_theme_tags
        for key, pattern in self.highlight_rules.items():
            self.text_editor.tag_remove(key, "1.0", END)
            for match in pattern.finditer(self.text_editor.get("1.0", "end-1c")):
                start_pos = self.text_editor.index(f"1.0 + {match.start()} chars")
                end_pos = self.text_editor.index(f"1.0 + {match.end()} chars")
                self.text_editor.tag_add(key, start_pos, end_pos)
                self.text_editor.tag_configure(key, foreground=theme_tags[key])

    def toggle_theme(self):
        if self.theme_var.get() == 1:  # Light theme
            self.root.config(bg="#FFFFFF")
            self.text_editor.config(bg="#FFFFFF", fg="#000000", insertbackground="#000000")
            self.line_numbers.config(bg="#FFFFFF")
            self.console.config(bg="#FFFFFF", fg="#000000")
        else:  # Dark theme
            self.root.config(bg="#1E1E1E")
            self.text_editor.config(bg="#1E1E1E", fg="#FFFFFF", insertbackground="#FFFFFF")
            self.line_numbers.config(bg="#1E1E1E")
            self.console.config(bg="#1E1E1E", fg="#FFFFFF")

        self.highlight_text()

    def choose_highlight_colors(self):
        colors = {}
        for key in self.highlight_rules.keys():
            color = colorchooser.askcolor(title=f"Choose color for {key}")
            if color[1]:
                colors[key] = color[1]
        return colors

    def update_highlight_colors(self):
        theme_tags = self.light_theme_tags if self.theme_var.get() == 1 else self.dark_theme_tags
        theme_tags.update(self.choose_highlight_colors())
        self.highlight_text()

    def enable_auto_completion(self, event):
        # Get the current line before the cursor
        current_line = self.text_editor.get("insert linestart", "insert")

        # Check if the current line ends with a known Python keyword
        for keyword in ["if", "elif", "else", "for", "while", "def", "class", "try", "except", "with", "import", "from"]:
            if current_line.endswith(keyword):
                self.text_editor.insert("insert", " ")  # Add a space after the keyword
                return "break"  # Prevent default insertion behavior

    def find_and_replace(self):
        # Prompt user for text to find
        search_text = simpledialog.askstring("Find", "Enter text to find:")
        if search_text:
            # Get all occurrences of the search text
            start_index = "1.0"
            while True:
                start_index = self.text_editor.search(search_text, start_index, stopindex=END)
                if not start_index:
                    break
                end_index = self.text_editor.index(f"{start_index}+{len(search_text)}c")
                self.text_editor.tag_add("found", start_index, end_index)
                start_index = end_index

            # Highlight all occurrences
            self.text_editor.tag_config("found", background="yellow", foreground="black")

    def new_file(self):
        # Clear the text editor
        self.text_editor.delete(1.0, END)
        self.file_path = None

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            self.text_editor.delete(1.0, END)
            with open(file_path, "r") as file:
                self.text_editor.insert(1.0, file.read())
            self.file_path = file_path
            self.highlight_text()

    def save_file(self):
        if self.file_path:
            with open(self.file_path, "w") as file:
                file.write(self.text_editor.get(1.0, END))
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_editor.get(1.0, END))
            self.file_path = file_path

    def exit_app(self):
        self.root.quit()

    def run_code(self):
        # Save the code to a temporary file
        with open("temp_code.py", "w") as file:
            file.write(self.text_editor.get(1.0, END))

        # Execute the code using the default Python interpreter
        process = subprocess.Popen(["python", "temp_code.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Display output in console
        self.console.config(state='normal')
        self.console.delete('1.0', END)
        if stdout:
            self.console.insert(END, f"Output:\n{stdout.decode()}\n")
        if stderr:
            self.console.insert(END, f"Error:\n{stderr.decode()}\n")
        self.console.config(state='disabled')

        # Remove temporary file
        os.remove("temp_code.py")

    def syntax_check(self):
        # Save the code to a temporary file
        with open("temp_code.py", "w") as file:
            file.write(self.text_editor.get(1.0, END))

        # Check syntax using Python's built-in syntax checker
        try:
            subprocess.run(["python", "-m", "py_compile", "temp_code.py"], check=True)
            messagebox.showinfo("Syntax Check", "No syntax errors found.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Syntax Check", "Syntax error(s) found. Please check your code.")
        finally:
            os.remove("temp_code.py")

    def show_about(self):
        about_window = Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("600x400")

        about_description = """
        Code Editor by Timur Hromek
        Created at the age of 14

        I developed this code editor out of frustration with existing editors. 
        They weren't lightweight, fast, or good enough for my needs, so I decided 
        to create my own. This editor is designed to provide a seamless coding 
        experience with a focus on speed and functionality.
        """

        about_label = Label(about_window, text=about_description, justify='left', wraplength=500)
        about_label.pack(padx=10, pady=10)

    def set_window_icon(self, icon_path):
        # Load the ICO file
        icon = Image.open(icon_path)

        # Convert the ICO file to a Tkinter-compatible format
        icon_photo = ImageTk.PhotoImage(icon)

        # Set the window icon
        self.root.iconphoto(True, icon_photo)


def main():
    root = Tk()
    code_editor = CodeEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
