# table_utils.py

import tkinter as tk
from tkinter import ttk
from data import PANEL_DATA  # Import PANEL_DATA from data.py


def create_data_table(parent, panel_code, location, image_update_callback, current_month=None):
    """
    Creates a table displaying fouling percentage for each month for a single panel.

    Args:
        parent (tk.Frame): The parent frame to which the table will be added.
        panel_code (str): The code of the panel for which to display data.
        location (str): The location of the panel.
        image_update_callback (callable): Function to call when a row is double-clicked.
        current_month (str): The currently selected month to highlight.
    """
    panel_data_by_month = {}
    location_data = PANEL_DATA.get(location, {})
    if not location_data:
        ttk.Label(parent, text=f"No data available for {location}").pack()
        return

    has_data = False
    available_months = sorted(location_data.keys(), key=lambda m: int(m.split()[1]) if m.startswith("Month ") else m)

    for month_str in available_months:
        if panel_code in location_data[month_str]:
            fouling = location_data[month_str][panel_code].get("fouling")
            if fouling is not None:
                panel_data_by_month[month_str] = fouling
                has_data = True

    if not has_data:
        ttk.Label(parent, text=f"No fouling data available for Panel {panel_code} in {location}").pack()
        return

    months = sorted(panel_data_by_month.keys(), key=lambda m: int(m.split()[1]) if m.startswith("Month ") else m)

    # Create treeview widget with larger font
    style = ttk.Style()
    style.configure("Treeview", font=('Arial', 12), rowheight=25)
    style.configure("Treeview.Heading", font=('Arial', 12, 'bold'))
    style.map("Treeview", background=[('selected', 'lightblue')])

    tree = ttk.Treeview(parent, style="Treeview")
    tree["columns"] = ["Fouling Percentage"]
    tree.column("#0", width=120, stretch=tk.NO)
    tree.column("Fouling Percentage", anchor=tk.CENTER, width=150)
    tree.heading("#0", text="Month")
    tree.heading("Fouling Percentage", text="Fouling (%)")

    # Insert data into the table
    for month in months:
        fouling_value = panel_data_by_month[month]
        if fouling_value is not None:
            formatted_fouling = f"{fouling_value:.2f}%"
            tree.insert("", tk.END, text=month, values=[formatted_fouling])
        else:
            tree.insert("", tk.END, text=month, values=["N/A"])

    # Highlight the current month if provided
    if current_month:
        for i, month in enumerate(months):
            if month == current_month:
                tree.selection_set(tree.get_children()[i])
                break

    # Bind double-click event
    def on_row_double_click(event):
        item = tree.selection()[0]
        selected_month = tree.item(item, "text")
        image_update_callback(selected_month)

    tree.bind("<Double-1>", on_row_double_click)
    tree.pack(fill=tk.BOTH, expand=True)
    return tree

    def on_row_double_click(event, tree_widget):
        item = tree_widget.selection()[0]
        selected_month = tree_widget.item(item, "text")
        image_update_callback(selected_month)

    tree.pack(fill=tk.BOTH, expand=True)
    return tree


def create_comparison_data_table(parent, panel1_code, panel2_codes, location1, location2, month1, month2):
    """
    Creates a comparison table that shows single panel data for both panels
    when data is missing for one panel.
    """
    # Get data for both panels
    panel1_data = PANEL_DATA.get(location1, {}).get(month1, {}).get(panel1_code, {})
    panel2_data = PANEL_DATA.get(location2, {}).get(month2, {}).get(panel2_codes[0], {})

    # If no data for either panel, show message
    if not panel1_data and not panel2_data:
        ttk.Label(parent, text="No data available for either panel").pack()
        return None

    # Create treeview widget
    tree = ttk.Treeview(parent)
    tree["columns"] = ["Panel 1", "Panel 2"]

    # Configure columns
    tree.column("#0", width=120, stretch=tk.NO)
    tree.column("Panel 1", anchor=tk.CENTER, width=150)
    tree.column("Panel 2", anchor=tk.CENTER, width=150)

    # Create headings
    tree.heading("#0", text="Metric")
    tree.heading("Panel 1", text=f"{panel1_code} ({location1})")
    tree.heading("Panel 2", text=f"{panel2_codes[0]} ({location2})")

    # If one panel has no data, use the other panel's data for both columns
    if not panel2_data:
        panel2_data = panel1_data  # Use panel1 data for both
    elif not panel1_data:
        panel1_data = panel2_data  # Use panel2 data for both

    # Add data rows
    metrics = set(panel1_data.keys()).union(set(panel2_data.keys()))
    for metric in sorted(metrics):
        val1 = panel1_data.get(metric, "N/A")
        val2 = panel2_data.get(metric, "N/A")

        # Format values consistently
        if isinstance(val1, (int, float)):
            val1 = f"{val1:.2f}%" if metric == "fouling" else f"{val1:.2f}"
        if isinstance(val2, (int, float)):
            val2 = f"{val2:.2f}%" if metric == "fouling" else f"{val2:.2f}"

        tree.insert("", tk.END, text=metric, values=[val1, val2])

    tree.pack(fill=tk.BOTH, expand=True)
    return tree