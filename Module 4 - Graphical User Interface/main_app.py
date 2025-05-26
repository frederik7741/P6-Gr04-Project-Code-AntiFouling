import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle
from data import PANEL_DATA
from image_utils import find_panel_image, load_and_display_image, resize_image
from graph_utils import create_timeline_graph
from table_utils import create_data_table, create_comparison_data_table

class PanelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graphical Interface")
        self.root.state('zoomed') 
        
        self.current_location = "Baltic Asko"  
        self.current_month_p1 = "Month 1"  
        self.current_month_p2 = "Month 1" 
        self.current_view = "panel_list"
        self.current_panel = None
        self.compare_selection = []
        self.image_references = []
        self.graph_references = []
        self.location_buttons = {}
        self.month_buttons = {} 
        self.previous_view = None
        self.last_single_view = None
        self.primary_selected_month_graph = 1
        self.compare_selected_month_graph = 1
        self.show_graph_table = "graph" 
        self.confirm_btn = None  
        self.compare_location_var = tk.StringVar()

        self.create_ui()

    def create_ui(self):
        # Create main frames
        self.banner_frame = tk.Frame(self.root, bg="lightgrey", height=50)
        self.banner_frame.pack(fill='x')

        self.month_frame = tk.Frame(self.root, bg="lightblue", height=40)
        self.month_frame.pack(fill='x')

        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill='both', expand=True)

        # Initialize UI components
        self.render_location_banner()
        self.render_month_selector()
        self.show_panels()

    def render_location_banner(self):
        for widget in self.banner_frame.winfo_children():
            widget.destroy()

        self.location_buttons = {}
        for loc in PANEL_DATA:
            btn = tk.Label(self.banner_frame, text=loc, bg="lightgrey",
                           padx=10, pady=5, font=("Arial", 12))
            btn.bind("<Button-1>", lambda e, l=loc: self.switch_location(l))
            btn.pack(side='left', expand=True)
            self.location_buttons[loc] = btn

        self.highlight_selected_location()

    def highlight_selected_location(self):
        for loc, btn in self.location_buttons.items():
            if loc == self.current_location:
                btn.config(bg="darkgrey", font=("Arial", 12, "bold"))
            else:
                btn.config(bg="lightgrey", font=("Arial", 12))

    def render_month_selector(self):
        for widget in self.month_frame.winfo_children():
            widget.destroy()

        self.month_buttons = {}  
        available_months = sorted(PANEL_DATA.get(self.current_location, {}).keys())

        for month in available_months:
            btn = tk.Label(self.month_frame, text=month, bg="lightblue",
                           padx=10, pady=5, font=("Arial", 10))
            btn.bind("<Button-1>", lambda e, m=month: self.switch_month(m))
            btn.pack(side='left')
            self.month_buttons[month] = btn  

        self.highlight_selected_month()

    def highlight_selected_month(self):
        for month, btn in self.month_buttons.items():
            if month == self.current_month_p1:
                btn.config(bg="steelblue", font=("Arial", 10, "bold"))
            else:
                btn.config(bg="lightblue", font=("Arial", 10))

    def switch_location(self, new_location):
        self.current_location = new_location
        self.current_month_p1 = sorted(PANEL_DATA.get(new_location, {}).keys())[0] if PANEL_DATA.get(
            new_location) else "Month 1"  
        self.current_month_p2 = sorted(PANEL_DATA.get(new_location, {}).keys())[0] if PANEL_DATA.get(
            new_location) else "Month 1"
        self.render_location_banner()
        self.render_month_selector()
        self.show_panels()
        self.current_view = "panel_list"  
        self.current_panel = None
        self.compare_selection = []

    def switch_month(self, new_month):
        """Updates the displayed panels for the new month."""
        self.current_month_p1 = new_month
        self.render_month_selector()  
        self.show_panels()  

    def find_panel_image(self, panel_code, location, is_compare=False):
        """Find panel image path based on location."""
        month_to_use = self.current_month_p2 if is_compare else self.current_month_p1
        return find_panel_image(location, month_to_use, panel_code)

    def show_panels(self):
        self.current_view = "panel_list"
        self.clear_content_frame()

        
        self.banner_frame.pack(fill='x', before=self.content_frame)
        self.month_frame.pack(fill='x', before=self.content_frame)

        self.render_location_banner()
        self.render_month_selector()

        canvas = tk.Canvas(self.content_frame)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        panels = PANEL_DATA.get(self.current_location, {}).get(self.current_month_p1, [])

        panel_groups = {}
        for panel in panels:
            prefix = panel[:2]
            if prefix not in panel_groups:
                panel_groups[prefix] = []
            panel_groups[prefix].append(panel)

        for prefix, group_panels in panel_groups.items():
            group_frame = ttk.LabelFrame(scrollable_frame, text=f"Panel {prefix}")
            group_frame.pack(fill='x', padx=10, pady=5)

            for panel in sorted(group_panels):
                panel_frame = ttk.Frame(group_frame)
                panel_frame.pack(fill='x', pady=2)
                ttk.Label(panel_frame, text=panel).pack(side='left')
                btn_frame = ttk.Frame(panel_frame)
                btn_frame.pack(side='right')
                ttk.Button(btn_frame, text="Graph", command=lambda p=panel: self.show_panel_graph(p)).pack(side='left',
                                                                                                           padx=2)
                ttk.Button(btn_frame, text="Table", command=lambda p=panel: self.show_panel_table(p)).pack(side='left',
                                                                                                           padx=2)

    def show_panel_detail(self, panel_code):
        self.current_panel = panel_code
        self.current_view = "detail"
        self.render_panel_view()

    def show_panel_graph(self, panel_code):
        self.current_panel = panel_code
        self.current_view = "graph"
        self.show_graph_table = "graph"  # Force the table to be shown
        self.render_panel_view()

    def show_panel_table(self, panel):
        self.current_panel = panel
        self.current_view = "table"  
        self.show_graph_table = "table"  # Force the table to be shown
        self.render_panel_view()

    def render_panel_view(self):
        self.clear_content_frame()

        if self.current_view == "panel_list":
            self.banner_frame.pack(fill='x', before=self.content_frame)
            self.month_frame.pack(fill='x', before=self.content_frame)
        else:
            self.banner_frame.pack_forget()
            self.month_frame.pack_forget()

        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill='both', expand=True)

        # Configure grid layout for main_frame
        main_frame.grid_columnconfigure(0, weight=2)
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(0, weight=0)
        main_frame.grid_rowconfigure(1, weight=1)

        panel1_label = ttk.Label(main_frame, font=("Arial", 12, "bold"))
        panel1_label.grid(row=0, column=0, sticky='ew', padx=5, pady=(100, 5))

        panel2_label = ttk.Label(main_frame, font=("Arial", 12, "bold"))
        panel2_label.grid(row=0, column=1, sticky='ew', padx=5, pady=(100, 5))

        img1_label = ttk.Label(main_frame)
        img1_label.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        img2_label = ttk.Label(main_frame)
        img2_label.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')

        data_frame = ttk.Frame(main_frame)
        data_frame.grid(row=0, column=2, padx=10, pady=10, sticky='nsew', rowspan=2)
        data_frame.config(borderwidth=2, relief="solid")

        # Load and display image(s)
        if self.current_view == "compare_view" and self.compare_selection:
            panel1_code = self.current_panel
            panel2_code = self.compare_selection[0]

            img1_path = self.find_panel_image(panel1_code, self.current_location)
            img2_path = self.find_panel_image(panel2_code, self.compare_location_var.get(), is_compare=True)
            if img1_path:
                try:
                    load_and_display_image(self.root, img1_path, img1_label, self.image_references,
                                           max_height_ratio=0.7)
                except (FileNotFoundError, AttributeError) as e:
                    print(f"Error loading image: {e}")
                    img1_label.config(text="")
                    img1_label.image = None
            else:
                img1_label.config(text="")
                img1_label.image = None
            if img2_path:
                try:
                    load_and_display_image(self.root, img2_path, img2_label, self.image_references,
                                           max_height_ratio=0.7)
                except (FileNotFoundError, AttributeError) as e:
                    print(f"Error loading image: {e}")
                    img2_label.config(text="")
                    img2_label.image = None
            else:
                img2_label.config(text="")
                img2_label.image = None

            img2_label.config(text="")
            panel1_label.config(text=f"{panel1_code} ({self.current_month_p1})", anchor='center')
            panel2_label.config(text=f"{panel2_code} ({self.current_month_p2})", anchor='center')
        else:
            panel1_code = self.current_panel
            img_path = self.find_panel_image(panel1_code, self.current_location)
            if img_path:
                try:
                    load_and_display_image(self.root, img_path, img1_label, self.image_references, max_height_ratio=0.7)
                except (FileNotFoundError, AttributeError) as e:
                    print(f"Error loading image: {e}")
                    img1_label.config(text="Image not found")
                    img1_label.image = None
            else:
                img1_label.config(text="")
                img1_label.image = None
            img2_label.config(image=None, text="")
            panel1_label.config(text=f"{panel1_code} ({self.current_month_p1})", anchor='center')
            panel2_label.config(text="")

            self.compare_selection = []

        info_label = ttk.Label(data_frame,
                               text=f"{self.current_panel} ({self.current_month_p1}) vs. {self.compare_selection[0]} ({self.current_month_p2})"
                               if self.current_view == "compare_view" and self.compare_selection
                               else f"{self.current_panel} - {self.current_month_p1}",
                               font=("Arial", 12, "bold"))
        info_label.pack(pady=10)

        switch_frame = ttk.Frame(data_frame)
        switch_frame.pack(pady=10)

        graph_button = ttk.Button(switch_frame, text="Graph", style='Toggle.TButton',
                                  command=lambda: self.switch_graph_table("graph"))
        graph_button.pack(side='left')
        self.graph_button = graph_button

        table_button = ttk.Button(switch_frame, text="Table", style='Toggle.TButton',
                                  command=lambda: self.switch_graph_table("table"))
        table_button.pack(side='left')
        self.table_button = table_button

        self.update_graph_table_button_style()

        self.content_display_frame = ttk.Frame(data_frame)
        self.content_display_frame.pack(fill='both', expand=True)

        table_style = ttk.Style()
        table_style.configure("Treeview.Heading", font=('Helvetica', 14))
        table_style.configure("Treeview", font=('Helvetica', 14), rowheight=25)

        if self.show_graph_table == "graph":
            try:
                for widget in self.content_display_frame.winfo_children():
                    widget.destroy()
                self.graph_references = []

                graph_title = f"Fouling Timeline for {self.current_panel}"
                compare_panels_for_graph = self.compare_selection if self.current_view == "compare_view" else []

                if self.current_view == "compare_view" and self.compare_selection:
                    graph_title = f"Fouling Timeline: {self.current_panel} vs {self.compare_selection[0]}"

                (self.primary_points_graph,
                 self.primary_month_map_graph,
                 self.compare_points_graph,
                 self.compare_month_map_graph,
                 self.ax_graph,
                 self.canvas_graph) = create_timeline_graph(
                    self.content_display_frame,
                    self.current_location,
                    self.current_panel,
                    compare_panels_for_graph,
                    self.graph_references,
                    self.update_graph_selection,
                    int(self.current_month_p1.split()[1]),  
                    int(self.current_month_p2.split()[1]) if self.current_month_p2 else 1,
                    self.switch_month,  
                    self.switch_compare_month,  
                    compare_location=self.compare_location_var.get() if self.current_view == "compare_view" and self.compare_selection else None
                )

                if self.ax_graph:
                    self.ax_graph.set_title(graph_title)
                if self.canvas_graph:
                    self.canvas_graph.get_tk_widget().pack(fill='both', expand=True)
            except Exception as e:
                print(f"Error creating graph: {e}")
                tk.messagebox.showerror("Graph Error", f"An error occurred while creating the graph: {e}")

        elif self.show_graph_table == "table":
            
            for widget in self.content_display_frame.winfo_children():
                widget.destroy()
            if self.current_view == "compare_view":
                
                primary_months = sorted(PANEL_DATA.get(self.current_location, {}).keys(),
                                        key=lambda m: int(m.split()[1]) if m.startswith("Month ") else m)
                
                tree = ttk.Treeview(self.content_display_frame)
                tree["columns"] = [f"{self.current_panel}", f"{self.compare_selection[0]}"]
                tree.column("#0", width=120, stretch=tk.NO)
                tree.column(f"{self.current_panel}", anchor=tk.CENTER, width=150)
                tree.column(f"{self.compare_selection[0]}", anchor=tk.CENTER, width=150)
                tree.heading("#0", text="Month")
                tree.heading(f"{self.current_panel}", text=f"{self.current_panel} ({self.current_location})")
                tree.heading(f"{self.compare_selection[0]}",
                             text=f"{self.compare_selection[0]} ({self.compare_location_var.get()})")
                
                for month in primary_months:
                    panel1_data = PANEL_DATA.get(self.current_location, {}).get(month, {}).get(self.current_panel, {})
                    fouling1 = panel1_data.get("fouling", "N/A")
                    if isinstance(fouling1, (int, float)):
                        fouling1 = f"{fouling1:.2f}%"
                    panel2_data = PANEL_DATA.get(self.compare_location_var.get(), {}).get(
                        month, {}).get(self.compare_selection[0], {})
                    fouling2 = panel2_data.get("fouling", "N/A")
                    if isinstance(fouling2, (int, float)):
                        fouling2 = f"{fouling2:.2f}%"
                    tree.insert("", tk.END, text=month, values=[fouling1, fouling2], tags=(month,))
                comparison_months = sorted(PANEL_DATA.get(self.compare_location_var.get(), {}).keys(),
                                           key=lambda m: int(m.split()[1]) if m.startswith("Month ") else m)
                for month in comparison_months:
                    if month not in primary_months:
                        panel1_data = PANEL_DATA.get(self.current_location, {}).get(month, {}).get(self.current_panel,
                                                                                                   {})
                        fouling1 = panel1_data.get("fouling", "N/A")

                        if isinstance(fouling1, (int, float)):
                            fouling1 = f"{fouling1:.2f}%"
                        panel2_data = PANEL_DATA.get(self.compare_location_var.get(), {}).get(
                            month, {}).get(self.compare_selection[0], {})
                        fouling2 = panel2_data.get("fouling", "N/A")
                        if isinstance(fouling2, (int, float)):
                            fouling2 = f"{fouling2:.2f}%"
                        tree.insert("", tk.END, text=month, values=[fouling1, fouling2], tags=(month,))

                # Bind double-click event to switch months
                def on_row_double_click(event):
                    item = tree.selection()[0]
                    selected_month = tree.item(item, "text")
                    self.current_month_p1 = selected_month
                    self.current_month_p2 = selected_month
                    self.render_panel_view()

                tree.bind("<Double-1>", on_row_double_click)
                tree.pack(fill='both', expand=True)
            else:
                single_panel_table = create_data_table(self.content_display_frame, self.current_panel,
                                                       self.current_location,
                                                       self.update_panel_image_from_table)
                if single_panel_table:
                    single_panel_table.config(style="Treeview")

        if self.current_view != "compare_view" and self.current_view != "compare":
            compare_btn = ttk.Button(main_frame, text="Compare Panels",
                                     command=self.start_compare_mode)
            compare_btn.grid(row=2, column=0, sticky='ew', padx=5, pady=5, columnspan=2)
        elif self.current_view == "compare_view":
            ttk.Label(main_frame).grid(row=2, column=0, columnspan=2)

        back_btn = ttk.Button(self.content_frame,
                              text="Back to Panel List" if self.current_view != "compare_view" else "Back to Single Panel",
                              command=self.show_panels if self.current_view != "compare_view" else lambda: self.switch_view(
                                  self.current_panel, self.last_single_view)).pack(pady=10)

    def update_panel_image_from_table(self, selected_month):
        """
        Updates the displayed panel image based on the month selected in the table.
        Also updates the graph's closed circle position.
        """
        if self.current_panel and self.current_location:
            self.current_month_p1 = selected_month
            self.primary_selected_month_graph = int(selected_month.split()[1])
            self.render_panel_view()

    def update_graph_selection(self, primary_month=None, compare_month=None):
        if primary_month is not None:
            month_str = f"Month {primary_month}"
            if month_str in PANEL_DATA.get(self.current_location, {}):
                self.current_month_p1 = month_str
        self.primary_selected_month_graph = primary_month
        if compare_month is not None:
            month_str_compare = f"Month {compare_month}"
            if self.compare_location_var.get() in PANEL_DATA and month_str_compare in PANEL_DATA.get(self.compare_location_var.get(), {}):
                self.current_month_p2 = month_str_compare
        self.compare_selected_month_graph = compare_month
        self.render_panel_view()

    def switch_graph_table(self, mode):
        self.show_graph_table = mode
        self.render_panel_view()

    def update_graph_table_button_style(self):
        if self.show_graph_table == "graph":
            self.graph_button.config(style='Active.Toggle.TButton')
            self.table_button.config(style='Toggle.TButton')
        else:
            self.graph_button.config(style='Toggle.TButton')
            self.table_button.config(style='Active.Toggle.TButton')

    def start_compare_mode(self):
        self.previous_view = self.current_view
        self.current_view = "compare"
        self.compare_selection = [self.current_panel]
        self.clear_content_frame()

        self.compare_frame = ttk.Frame(self.content_frame)
        self.compare_frame.pack(fill='both', expand=True)

        label = ttk.Label(self.compare_frame, text="Select another Panel to Compare",
                          font=("Arial", 16))
        label.pack(pady=10)

        canvas = tk.Canvas(self.compare_frame)
        scrollbar = ttk.Scrollbar(self.compare_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        location_frame = ttk.Frame(scrollable_frame)
        location_frame.pack(fill='x', pady=5)

        ttk.Label(location_frame, text="Location:", font=("Arial", 12)).pack(side='left')
        self.compare_location_var = tk.StringVar(value=self.current_location)
        location_combo = ttk.Combobox(location_frame, textvariable=self.compare_location_var,
                                      values=list(PANEL_DATA.keys()), state='readonly', font=("Arial", 12))
        location_combo.pack(side='left')
        location_combo.bind("<<ComboboxSelected>>", self.update_compare_options)

        month_frame = ttk.Frame(scrollable_frame)
        month_frame.pack(fill='x', pady=5)
        ttk.Label(month_frame, text="Month:", font=("Arial", 12)).pack(side='left')
        self.compare_month_var = tk.StringVar()
        self.compare_month_combo = ttk.Combobox(month_frame, textvariable=self.compare_month_var, state='readonly', font=("Arial", 12))
        self.compare_month_combo.pack(side='left')

        self.panel_selection_frame = ttk.Frame(scrollable_frame)
        self.panel_selection_frame.pack(fill='x', pady=5)

        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(pady=10)

        self.confirm_btn_style = ttk.Style()
        self.confirm_btn_style.configure("CompareButton.TButton", font=("Arial", 12), padding=(10, 5))
        self.confirm_btn = ttk.Button(button_frame, text="Compare Selected Panel",
                                      command=self.show_compare_view, state='disabled',
                                      style="CompareButton.TButton")
        self.confirm_btn.pack(side='left', anchor='w', padx=5)

        back_btn = ttk.Button(button_frame, text="Cancel",
                              command=lambda: self.switch_view(self.current_panel, self.previous_view),
                              style="CompareButton.TButton")
        back_btn.pack(side='left', padx=5)

        self.update_compare_options()

    def update_compare_options(self, event=None):
        """Updates the available months and panel checkboxes based on the selected location for comparison."""
        selected_location = self.compare_location_var.get()
        available_months = sorted(PANEL_DATA.get(selected_location, {}).keys())
        self.compare_month_combo['values'] = available_months
        if available_months:
            self.compare_month_var.set(available_months[0])
        else:
            self.compare_month_var.set('')

        for widget in self.panel_selection_frame.winfo_children():
            widget.destroy()
        self.panel_vars = {}

        first_month = available_months[0] if available_months else None
        if first_month and selected_location in PANEL_DATA:
            all_panels = sorted(PANEL_DATA[selected_location].get(first_month, []))
            checkbox_size = 16
            style_name = "TCheckbutton"
            style = ttk.Style()
            style.configure(style_name, font=("Arial", checkbox_size),
                            indicatorsize=25,
                            padding=(10, 5))
            for panel in all_panels:
                if panel == self.current_panel:
                    var = tk.BooleanVar(value=True)
                    chk = ttk.Checkbutton(self.panel_selection_frame, text=panel, variable=var,
                                          state='disabled',
                                          style=style_name)
                    chk.pack(anchor='w', padx=10, pady=2)
                    self.panel_vars[panel] = var
                    self.panel_vars[panel].set(True)
                else:
                    var = tk.BooleanVar()
                    chk = ttk.Checkbutton(self.panel_selection_frame, text=panel, variable=var,
                                          command=lambda v=var, p=panel: self.update_compare_selection(v, p),
                                          style=style_name)
                    chk.pack(anchor='w', padx=10, pady=2)
                    self.panel_vars[panel] = var
        elif selected_location in PANEL_DATA and not available_months:
            ttk.Label(self.panel_selection_frame, text="No months available for this location.").pack()
        elif selected_location not in PANEL_DATA:
            ttk.Label(self.panel_selection_frame, text="Location not found.").pack()

        if hasattr(self, 'confirm_btn') and self.confirm_btn:
            self.confirm_btn.config(state='disabled')

    def update_compare_selection(self, var, panel_name):
        for panel, v in self.panel_vars.items():
            if panel != panel_name:
                v.set(False)
        selected = [p for p, v in self.panel_vars.items() if v.get()]
        if self.confirm_btn: 
            self.confirm_btn.config(state='normal' if len(selected) == 1 else 'disabled')

    def show_compare_view(self):
        selected_panels = [p for p, v in self.panel_vars.items() if v.get()]
        if not selected_panels:
            return
        self.compare_selection = selected_panels
        self.last_single_view = self.previous_view
        self.current_view = "compare_view"
        self.current_month_p2 = self.compare_month_var.get()  
        self.render_panel_view()

    def switch_view(self, panel_name, view):
        self.previous_view = self.current_view
        self.current_view = view
        self.current_panel = panel_name
        self.render_panel_view()

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.image_references = []
        for ref in self.graph_references:
            ref.destroy()
        self.graph_references = []

    def switch_compare_month(self, new_month):
        self.current_month_p2 = new_month
        self.render_panel_view()


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure('Toggle.TButton',  borderwidth=1, relief="raised")
    style.map('Toggle.TButton',
              foreground=[('active', 'blue')],
              background=[('active', 'lightblue'), ('!active', 'lightgrey')],
              font=[('active', 'Arial 10 bold')])
    style.configure('Active.Toggle.TButton',  borderwidth=1, relief="raised", background='lightblue', font='Arial 10 bold')

    app = PanelApp(root)
    root.mainloop()
