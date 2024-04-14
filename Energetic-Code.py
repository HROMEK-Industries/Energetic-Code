import os
import subprocess
import re
from tkinter import Tk, Text, Menu, filedialog, Scrollbar, Frame, Button, Label, END, Canvas, IntVar, Radiobutton, colorchooser

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Energetic Code")
        self.root.geometry("800x600")

        self.theme_var = IntVar(value=1)  # 1 for light theme, 2 for dark theme, 3 for custom theme

        self.text_editor = Text(self.root, wrap='word', undo=True)
        self.text_editor.pack(side='left', expand=True, fill='both', padx=(5, 0), pady=5)

        self.scroll_bar = Scrollbar(self.root, command=self.text_editor.yview)
        self.scroll_bar.pack(side='right', fill='y')
        self.text_editor.config(yscrollcommand=self.scroll_bar.set)

        self.line_numbers = Canvas(self.root, bg="#FFFFFF", width=30)
        self.line_numbers.pack(side='left', fill='y', padx=(5, 0), pady=5)

        self.text_editor.bind('<KeyRelease>', self.highlight_text)

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
        theme_menu.add_radiobutton(label="Custom", variable=self.theme_var, value=3, command=self.choose_custom_theme)
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        self.main_menu.add_cascade(label="Settings", menu=settings_menu)

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

    def choose_custom_theme(self):
        color = colorchooser.askcolor(title="Choose Color")
        if color[1]:
            self.root.config(bg=color[1])
            self.text_editor.config(bg=color[1])
            self.line_numbers.config(bg=color[1])
            self.console.config(bg=color[1])

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

        try:
            # Execute the code using the default Python interpreter
            process = subprocess.Popen(["python", "temp_code.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()

            # Display output and errors in the console
            self.console.config(state='normal')
            self.console.delete(1.0, END)
            self.console.insert(END, stdout)
            if stderr:
                self.console.insert(END, stderr, 'error')
            self.console.config(state='disabled')

        except Exception as e:
            # Display error if execution fails
            self.console.config(state='normal')
            self.console.delete(1.0, END)
            self.console.insert(END, f"Error occurred: {str(e)}")
            self.console.config(state='disabled')

        finally:
            # Remove temporary file
            os.remove("temp_code.py")

def main():
    root = Tk()
    code_editor = CodeEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
