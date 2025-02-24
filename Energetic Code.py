import tkinter as tk
from tkinter import ttk, filedialog, font, messagebox
import subprocess, os, re, sys
from io import StringIO

# ---------------------------
# EditorTab: One code editor instance with line numbers, syntax highlighting, and autocompletion.
# ---------------------------
class EditorTab:
    def __init__(self, master, file_path=None, content=""):
        self.master = master
        self.file_path = file_path
        self.frame = ttk.Frame(master)
        self.text_font = font.Font(family="Consolas", size=12)
        
        # Left: Line numbers
        self.line_numbers = tk.Canvas(self.frame, width=40)
        self.line_numbers.pack(side="left", fill="y")
        
        # Right: Text widget with scrollbars
        self.v_scroll = ttk.Scrollbar(self.frame, orient="vertical", command=self.on_scroll)
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll = ttk.Scrollbar(self.frame, orient="horizontal", command=self.text_widget_xscroll)
        self.h_scroll.pack(side="bottom", fill="x")
        self.text_widget = tk.Text(
            self.frame, font=self.text_font, undo=True, wrap="none",
            yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set, padx=5, pady=5
        )
        self.text_widget.pack(fill="both", expand=True)
        # Insert initial content
        self.text_widget.insert("1.0", content)
        
        # Bind events for auto‑indent, syntax highlighting, autocompletion, and status updates
        self.text_widget.bind("<KeyRelease>", self.on_key_release)
        self.text_widget.bind("<ButtonRelease>", self.update_cursor_info)
        self.text_widget.bind("<<Modified>>", self.on_modified)
        self.text_widget.bind("<Control-space>", self.trigger_autocomplete)
        self.text_widget.bind("<Control-a>", self.select_all)
        self.text_widget.bind("<Control-A>", self.select_all)
        self.text_widget.bind("<Control-c>", lambda e: self.text_widget.event_generate("<<Copy>>"))
        self.text_widget.bind("<Control-x>", lambda e: self.text_widget.event_generate("<<Cut>>"))
        self.text_widget.bind("<Control-v>", lambda e: self.text_widget.event_generate("<<Paste>>"))
        
        # Autocompletion listbox (popup)
        self.ac_listbox = None

        # Python syntax highlighting patterns
        self.keywords = ["and", "as", "assert", "break", "class", "continue", "def",
                         "del", "elif", "else", "except", "False", "finally", "for", "from",
                         "global", "if", "import", "in", "is", "lambda", "None", "nonlocal",
                         "not", "or", "pass", "raise", "return", "True", "try", "while",
                         "with", "yield"]
        self.text_widget.tag_configure("keyword", foreground="blue")
        self.text_widget.tag_configure("string", foreground="green")
        self.text_widget.tag_configure("comment", foreground="gray")
        
        # Callback for status bar updates (set later)
        self.cursor_info_callback = None

        # Update line numbers immediately
        self.update_line_numbers()
        self.highlight_syntax()

    def text_widget_xscroll(self, *args):
        self.text_widget.xview(*args)
    
    def on_scroll(self, *args):
        self.text_widget.yview(*args)
        self.update_line_numbers()
    
    def select_all(self, event=None):
        self.text_widget.tag_add("sel", "1.0", "end")
        return "break"

    def on_key_release(self, event=None):
        self.highlight_syntax()
        self.update_line_numbers()
        if self.cursor_info_callback:
            self.cursor_info_callback()
        # Dismiss autocompletion if visible
        if self.ac_listbox:
            self.ac_listbox.destroy()
            self.ac_listbox = None

    def on_modified(self, event=None):
        self.text_widget.edit_modified(0)
        self.highlight_syntax()
        self.update_line_numbers()

    def update_line_numbers(self):
        self.line_numbers.delete("all")
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.line_numbers.create_text(2, y, anchor="nw", text=linenum, font=self.text_font)
            i = self.text_widget.index("%s+1line" % i)

    def update_cursor_info(self):
        if self.cursor_info_callback:
            self.cursor_info_callback()

    def highlight_syntax(self):
        content = self.text_widget.get("1.0", "end-1c")
        # Remove previous tags
        for tag in ["keyword", "string", "comment"]:
            self.text_widget.tag_remove(tag, "1.0", "end")
        lines = content.splitlines()
        for i, line in enumerate(lines, start=1):
            # Comments
            comment_index = line.find("#")
            if comment_index != -1:
                start = f"{i}.{comment_index}"
                end = f"{i}.end"
                self.text_widget.tag_add("comment", start, end)
                line = line[:comment_index]
            # Strings
            for match in re.finditer(r"(\'[^\']*\'|\"[^\"]*\")", line):
                start = f"{i}.{match.start()}"
                end = f"{i}.{match.end()}"
                self.text_widget.tag_add("string", start, end)
            # Keywords
            for kw in self.keywords:
                for match in re.finditer(r'\b' + re.escape(kw) + r'\b', line):
                    start = f"{i}.{match.start()}"
                    end = f"{i}.{match.end()}"
                    self.text_widget.tag_add("keyword", start, end)

    def trigger_autocomplete(self, event=None):
        pos = self.text_widget.index("insert")
        line_start = self.text_widget.index(f"{pos} linestart")
        current_line = self.text_widget.get(line_start, pos)
        word = re.split(r'\W+', current_line)[-1]
        if not word:
            return "break"
        suggestions = [kw for kw in self.keywords if kw.startswith(word)]
        if suggestions:
            self.show_autocomplete_list(suggestions, pos)
        return "break"

    def show_autocomplete_list(self, suggestions, pos):
        if self.ac_listbox:
            self.ac_listbox.destroy()
        self.ac_listbox = tk.Listbox(self.text_widget, height=len(suggestions))
        for item in suggestions:
            self.ac_listbox.insert("end", item)
        bbox = self.text_widget.bbox(pos)
        if bbox:
            x, y, width, height = bbox
            self.ac_listbox.place(x=x, y=y+height)
        else:
            self.ac_listbox.place(x=0, y=0)
        self.ac_listbox.bind("<<ListboxSelect>>", self.on_autocomplete_select)
        self.ac_listbox.bind("<Return>", self.on_autocomplete_confirm)
        self.ac_listbox.focus_set()

    def on_autocomplete_select(self, event=None):
        pass

    def on_autocomplete_confirm(self, event=None):
        if self.ac_listbox:
            selection = self.ac_listbox.curselection()
            if selection:
                chosen = self.ac_listbox.get(selection[0])
                pos = self.text_widget.index("insert")
                line_start = self.text_widget.index(f"{pos} linestart")
                current_line = self.text_widget.get(line_start, pos)
                word = re.split(r'\W+', current_line)[-1]
                start_index = f"{pos} - {len(word)}c"
                self.text_widget.delete(start_index, pos)
                self.text_widget.insert(start_index, chosen)
            self.ac_listbox.destroy()
            self.ac_listbox = None
        self.text_widget.focus_set()
        return "break"

    def get_content(self):
        return self.text_widget.get("1.0", "end-1c")

    def set_content(self, content):
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", content)

# ---------------------------
# CodeEditor: The main application window (Energetic Code Pro)
# ---------------------------
class CodeEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Energetic Code Pro")
        self.geometry("1300x900")
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.file_tabs = {}  # Map tab IDs to EditorTab instances
        self.console_output = StringIO()

        # Themes: six themes with complete color definitions.
        self.themes = {
            "Light": {
                "bg": "#f3f3f3",
                "fg": "#464646",
                "editor_bg": "#ffffff",
                "editor_fg": "#464646",
                "line_number_bg": "#e0e0e0",
                "console_bg": "#ffffff",
                "console_fg": "#464646",
                "insert_bg": "#000000"
            },
            "Dark": {
                "bg": "#343434",
                "fg": "#F7F7F7",
                "editor_bg": "#464646",
                "editor_fg": "#F7F7F7",
                "line_number_bg": "#555555",
                "console_bg": "#464646",
                "console_fg": "#F7F7F7",
                "insert_bg": "#FFFFFF"
            },
            "Solarized Light": {
                "bg": "#fdf6e3",
                "fg": "#657b83",
                "editor_bg": "#fdf6e3",
                "editor_fg": "#657b83",
                "line_number_bg": "#eee8d5",
                "console_bg": "#fdf6e3",
                "console_fg": "#657b83",
                "insert_bg": "#586e75"
            },
            "Solarized Dark": {
                "bg": "#002b36",
                "fg": "#839496",
                "editor_bg": "#073642",
                "editor_fg": "#93a1a1",
                "line_number_bg": "#586e75",
                "console_bg": "#073642",
                "console_fg": "#93a1a1",
                "insert_bg": "#839496"
            },
            "Monokai": {
                "bg": "#272822",
                "fg": "#f8f8f2",
                "editor_bg": "#272822",
                "editor_fg": "#f8f8f2",
                "line_number_bg": "#3e3d32",
                "console_bg": "#272822",
                "console_fg": "#f8f8f2",
                "insert_bg": "#f8f8f0"
            },
            "Dracula": {
                "bg": "#282a36",
                "fg": "#f8f8f2",
                "editor_bg": "#282a36",
                "editor_fg": "#f8f8f2",
                "line_number_bg": "#44475a",
                "console_bg": "#282a36",
                "console_fg": "#f8f8f2",
                "insert_bg": "#f8f8f2"
            }
        }
        self.current_theme = "Light"

        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        self.create_menu()
        self.create_toolbar()

        # Main horizontal paned window:
        self.main_pane = ttk.PanedWindow(self, orient="horizontal")
        self.main_pane.pack(fill="both", expand=True)

        # Left pane: Notebook with Explorer and Git tabs.
        self.left_notebook = ttk.Notebook(self.main_pane, width=250)
        self.main_pane.add(self.left_notebook, weight=1)
        self.setup_explorer()
        self.setup_git_panel()

        # Right pane: Editor tabs
        self.editor_notebook = ttk.Notebook(self.main_pane)
        self.main_pane.add(self.editor_notebook, weight=4)
        self.editor_notebook.bind("<Button-1>", self.on_tab_click)
        self.new_file()  # Open initial tab

        # Bottom: Notebook for Console Output and Terminal
        self.bottom_notebook = ttk.Notebook(self)
        self.bottom_notebook.pack(fill="both", expand=False)
        self.setup_console_output()
        self.setup_terminal()

        # Status Bar
        self.status_bar = ttk.Label(self, text="Ln 1, Col 1")
        self.status_bar.pack(side="bottom", fill="x")

    def create_menu(self):
        self.menu_bar = tk.Menu(self)
        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New File", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="New Tab", accelerator="Ctrl+T", command=self.new_file)
        file_menu.add_command(label="Open File", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As", accelerator="Shift+Ctrl+S", command=self.save_as)
        file_menu.add_command(label="Close Tab", accelerator="Ctrl+W", command=self.close_tab)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Edit Menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A",
                              command=lambda: self.current_editor().text_widget.event_generate("<<SelectAll>>"))
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X",
                              command=lambda: self.current_editor().text_widget.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C",
                              command=lambda: self.current_editor().text_widget.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V",
                              command=lambda: self.current_editor().text_widget.event_generate("<<Paste>>"))
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # Run Menu
        run_menu = tk.Menu(self.menu_bar, tearoff=0)
        run_menu.add_command(label="Run", accelerator="F5", command=self.run_code)
        self.menu_bar.add_cascade(label="Run", menu=run_menu)
        
        # View Menu for Themes
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        theme_menu = tk.Menu(view_menu, tearoff=0)
        for theme_name in self.themes.keys():
            theme_menu.add_radiobutton(label=theme_name, command=lambda tn=theme_name: self.change_theme(tn), value=theme_name)
        view_menu.add_cascade(label="Themes", menu=theme_menu)
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Git Menu
        git_menu = tk.Menu(self.menu_bar, tearoff=0)
        git_menu.add_command(label="Refresh Git Status", command=self.refresh_git_status)
        self.menu_bar.add_cascade(label="Git", menu=git_menu)
        
        self.config(menu=self.menu_bar)
        # Global shortcuts
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-t>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Shift-Control-S>", lambda e: self.save_as())
        self.bind("<Control-w>", lambda e: self.close_tab())
        self.bind("<F5>", lambda e: self.run_code())
        self.bind("<Control-a>", lambda e: self.current_editor().select_all())

    def create_toolbar(self):
        self.toolbar = ttk.Frame(self, relief="raised")
        self.toolbar.pack(side="top", fill="x")
        ttk.Button(self.toolbar, text="New", command=self.new_file).pack(side="left", padx=2, pady=2)
        ttk.Button(self.toolbar, text="Open", command=self.open_file).pack(side="left", padx=2, pady=2)
        ttk.Button(self.toolbar, text="Save", command=self.save_file).pack(side="left", padx=2, pady=2)
        ttk.Button(self.toolbar, text="Run", command=self.run_code).pack(side="left", padx=2, pady=2)
        ttk.Button(self.toolbar, text="Git Status", command=self.refresh_git_status).pack(side="left", padx=2, pady=2)

    def setup_explorer(self):
        self.explorer_frame = ttk.Frame(self.left_notebook)
        self.left_notebook.add(self.explorer_frame, text="Explorer")
        ttk.Button(self.explorer_frame, text="Open Folder", command=self.open_folder).pack(fill="x", padx=5, pady=5)
        self.tree = ttk.Treeview(self.explorer_frame)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.on_tree_item_double_click)
        self.populate_tree(os.getcwd())

    def open_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.populate_tree(folder)

    def populate_tree(self, path, parent=""):
        self.tree.delete(*self.tree.get_children(parent))
        try:
            for p in os.listdir(path):
                abspath = os.path.join(path, p)
                isdir = os.path.isdir(abspath)
                oid = self.tree.insert(parent, "end", text=p, values=[abspath])
                if isdir:
                    self.tree.insert(oid, "end")
        except PermissionError:
            pass
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_expand)

    def on_tree_expand(self, event):
        item = self.tree.focus()
        abspath = self.tree.item(item, "values")[0]
        if os.path.isdir(abspath):
            self.tree.delete(*self.tree.get_children(item))
            try:
                for p in os.listdir(abspath):
                    fullpath = os.path.join(abspath, p)
                    isdir = os.path.isdir(fullpath)
                    oid = self.tree.insert(item, "end", text=p, values=[fullpath])
                    if isdir:
                        self.tree.insert(oid, "end")
            except PermissionError:
                pass

    def on_tree_item_double_click(self, event):
        item = self.tree.focus()
        abspath = self.tree.item(item, "values")[0]
        if os.path.isfile(abspath):
            self.open_file(abspath)

    def setup_git_panel(self):
        self.git_frame = ttk.Frame(self.left_notebook)
        self.left_notebook.add(self.git_frame, text="Git")
        self.git_text = tk.Text(self.git_frame, state="disabled")
        self.git_text.pack(fill="both", expand=True, padx=5, pady=5)
        ttk.Button(self.git_frame, text="Refresh", command=self.refresh_git_status).pack(padx=5, pady=5)

    def refresh_git_status(self):
        try:
            result = subprocess.run(["git", "status"], capture_output=True, text=True, cwd=os.getcwd())
            output = result.stdout if result.returncode == 0 else "Not a git repository."
        except Exception as e:
            output = f"Error: {str(e)}"
        self.git_text.config(state="normal")
        self.git_text.delete("1.0", "end")
        self.git_text.insert("1.0", output)
        self.git_text.config(state="disabled")

    def new_file(self, event=None):
        editor_tab = EditorTab(self.editor_notebook)
        # Append an "  X" to the tab text to simulate a close button.
        tab_text = "Untitled  X"
        tab_id = self.editor_notebook.add(editor_tab.frame, text=tab_text)
        editor_tab.cursor_info_callback = self.update_status_bar
        self.file_tabs[tab_id] = editor_tab
        self.editor_notebook.select(editor_tab.frame)

    def open_file(self, path=None, event=None):
        if not path:
            path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            editor_tab = EditorTab(self.editor_notebook, file_path=path, content=content)
            filename = os.path.basename(path)
            tab_text = f"{filename}  X"
            tab_id = self.editor_notebook.add(editor_tab.frame, text=tab_text)
            editor_tab.cursor_info_callback = self.update_status_bar
            self.file_tabs[tab_id] = editor_tab
            self.editor_notebook.select(editor_tab.frame)

    def save_file(self, event=None):
        editor = self.current_editor()
        if editor:
            if editor.file_path:
                with open(editor.file_path, "w", encoding="utf-8") as f:
                    f.write(editor.get_content())
            else:
                self.save_as()

    def save_as(self, event=None):
        editor = self.current_editor()
        if editor:
            path = filedialog.asksaveasfilename(defaultextension=".py",
                                                filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
            if path:
                editor.file_path = path
                with open(path, "w", encoding="utf-8") as f:
                    f.write(editor.get_content())
                filename = os.path.basename(path)
                tab_index = self.editor_notebook.index("current")
                self.editor_notebook.tab(tab_index, text=f"{filename}  X")

    def close_tab(self, event=None):
        current = self.editor_notebook.select()
        if current:
            if len(self.editor_notebook.tabs()) > 1:
                self.editor_notebook.forget(current)
                if current in self.file_tabs:
                    del self.file_tabs[current]
            else:
                self.current_editor().set_content("")

    def on_tab_click(self, event):
        """Detect if the click is on the close (X) area of a tab."""
        try:
            x, y = event.x, event.y
            index = self.editor_notebook.index("@%d,%d" % (x, y))
            bbox = self.editor_notebook.bbox(index)
            if bbox:
                # If click is in the far right of the tab (last 20 pixels), close the tab.
                if x > bbox[0] + bbox[2] - 20:
                    tab_ids = self.editor_notebook.tabs()
                    tab_id = tab_ids[index]
                    self.editor_notebook.forget(index)
                    if tab_id in self.file_tabs:
                        del self.file_tabs[tab_id]
                    return "break"
        except Exception:
            pass

    def run_code(self, event=None):
        editor = self.current_editor()
        if editor:
            code = editor.get_content()
            old_stdout = sys.stdout
            sys.stdout = self.console_output
            self.console_output.truncate(0)
            self.console_output.seek(0)
            try:
                exec(code, {})
            except Exception as e:
                self.console_output.write(f"Error: {str(e)}\n")
            output = self.console_output.getvalue()
            sys.stdout = old_stdout
            self.console_output_text.config(state="normal")
            self.console_output_text.delete("1.0", "end")
            self.console_output_text.insert("end", output)
            self.console_output_text.config(state="disabled")

    def current_editor(self):
        current = self.editor_notebook.select()
        if current in self.file_tabs:
            return self.file_tabs[current]
        else:
            for tab_id, editor in self.file_tabs.items():
                if str(editor.frame) == current:
                    return editor
        return None

    def setup_console_output(self):
        self.console_frame = ttk.Frame(self.bottom_notebook)
        self.bottom_notebook.add(self.console_frame, text="Console Output")
        top_frame = ttk.Frame(self.console_frame)
        top_frame.pack(side="top", fill="x")
        ttk.Button(top_frame, text="Clear", command=lambda: self.console_output_text.delete("1.0", "end")).pack(side="right", padx=5, pady=5)
        self.console_output_text = tk.Text(self.console_frame, height=8, state="disabled")
        self.console_output_text.pack(fill="both", expand=True)

    def setup_terminal(self):
        self.terminal_frame = ttk.Frame(self.bottom_notebook)
        self.bottom_notebook.add(self.terminal_frame, text="Terminal")
        self.terminal_text = tk.Text(self.terminal_frame, height=8)
        self.terminal_text.pack(fill="both", expand=True)
        self.terminal_entry = ttk.Entry(self.terminal_frame)
        self.terminal_entry.pack(fill="x")
        self.terminal_entry.bind("<Return>", self.run_terminal_command)
        self.print_terminal_prompt()
        self.terminal_history = []
        self.terminal_history_index = None
        self.terminal_entry.bind("<Up>", self.on_terminal_up)
        self.terminal_entry.bind("<Down>", self.on_terminal_down)

    def print_terminal_prompt(self):
        self.terminal_text.insert("end", ">> ")
        self.terminal_text.see("end")

    def run_terminal_command(self, event=None):
        command = self.terminal_entry.get().strip()
        if command:
            self.terminal_history.append(command)
            self.terminal_history_index = None
            self.terminal_text.insert("end", command + "\n")
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
            except Exception as e:
                output = f"Error: {str(e)}\n"
            self.terminal_text.insert("end", output)
        self.terminal_entry.delete(0, "end")
        self.print_terminal_prompt()
        return "break"

    def on_terminal_up(self, event):
        if self.terminal_history:
            if self.terminal_history_index is None:
                self.terminal_history_index = len(self.terminal_history) - 1
            else:
                self.terminal_history_index = max(0, self.terminal_history_index - 1)
            self.terminal_entry.delete(0, "end")
            self.terminal_entry.insert(0, self.terminal_history[self.terminal_history_index])
        return "break"

    def on_terminal_down(self, event):
        if self.terminal_history and self.terminal_history_index is not None:
            self.terminal_history_index = min(len(self.terminal_history) - 1, self.terminal_history_index + 1)
            self.terminal_entry.delete(0, "end")
            self.terminal_entry.insert(0, self.terminal_history[self.terminal_history_index])
        return "break"

    def update_status_bar(self):
        editor = self.current_editor()
        if editor:
            pos = editor.text_widget.index("insert")
            line, col = pos.split(".")
            self.status_bar.config(text=f"Ln {line}, Col {int(col)+1}")

    def change_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.apply_theme()

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        # Update root and widget styles
        self.configure(bg=theme["bg"])
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=theme["bg"])
        style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
        style.configure("TButton", background=theme["bg"], foreground=theme["fg"])
        style.configure("TNotebook", background=theme["bg"])
        style.configure("TNotebook.Tab", background=theme["bg"], foreground=theme["fg"])
        # Update all editor tabs
        for editor in self.file_tabs.values():
            editor.text_widget.config(bg=theme["editor_bg"], fg=theme["editor_fg"], insertbackground=theme["insert_bg"])
            editor.line_numbers.config(bg=theme["line_number_bg"])
        # Update console and terminal
        self.console_output_text.config(bg=theme["console_bg"], fg=theme["console_fg"], insertbackground=theme["insert_bg"])
        self.terminal_text.config(bg=theme["console_bg"], fg=theme["console_fg"], insertbackground=theme["insert_bg"])

    def on_exit(self):
        if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            self.destroy()

if __name__ == "__main__":
    app = CodeEditor()
    app.mainloop()
