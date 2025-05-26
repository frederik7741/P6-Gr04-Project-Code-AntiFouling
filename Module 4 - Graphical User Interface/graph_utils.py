import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data import PANEL_DATA
import numpy as np


def create_timeline_graph(parent_frame, current_location, current_panel, compare_selection,
                          graph_references, update_graph_selection_callback, primary_selected_month,
                          compare_selected_month, set_current_month_callback,
                          set_compare_month_callback, compare_location=None,
                          y_min=0, y_max=100, y_interval=5):
    """Create an interactive graph showing fouling over time for a panel."""
    for ref in graph_references:
        ref.destroy()
    graph_references.clear()

    fig = plt.Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)

    def get_panel_data(location, panel_code):
        months_data = {}
        fouling_data = {}
        for month_str, panels in PANEL_DATA.get(location, {}).items():
            if panel_code in panels:
                try:
                    month_num = int(month_str.split()[1])
                    months_data[month_num] = month_str
                    fouling_data[month_num] = panels[panel_code].get('fouling', 0)
                    if fouling_data[month_num] > 100:
                         fouling_data[month_num] = 100
                    elif fouling_data[month_num] < 0:
                         fouling_data[month_num] = 0
                except (IndexError, ValueError):
                    continue
        return months_data, fouling_data

    primary_months_data, primary_fouling_data = get_panel_data(current_location, current_panel)
    primary_months_sorted = sorted(primary_months_data.keys())
    primary_fouling_sorted = [primary_fouling_data[m] for m in primary_months_sorted]

    if not primary_months_sorted:
        ttk.Label(parent_frame, text=f"No data available for {current_panel}",
                  foreground="red").pack()
        return None, None, None, None, None, None

    (primary_scatter,) = ax.plot(primary_months_sorted, primary_fouling_sorted, 'b-', alpha=0.5, zorder=1,
                                 label=current_panel)

    face_colors = ['black' if month == primary_selected_month else 'none'
                   for month in primary_months_sorted]

    primary_points = ax.scatter(
        primary_months_sorted, primary_fouling_sorted,
        facecolors=face_colors,
        edgecolors='black',
        s=100,
        picker=5,
        zorder=3
    )
    primary_month_map = {month_num: month_str for month_num, month_str in primary_months_data.items()}

    compare_scatter = None
    compare_points = None
    compare_month_map = {}

    if compare_selection and compare_location:
        compare_panel = compare_selection[0]
        compare_months_data, compare_fouling_data = get_panel_data(compare_location, compare_panel)
        compare_months_sorted = sorted(compare_months_data.keys())
        compare_fouling_sorted = [compare_fouling_data[m] for m in compare_months_sorted]

        if compare_months_sorted:
            (compare_scatter,) = ax.plot(compare_months_sorted, compare_fouling_sorted, 'r-', alpha=0.5, zorder=1,
                                         label=compare_panel)
            compare_points = ax.scatter(
                compare_months_sorted, compare_fouling_sorted,
                facecolors=['red' if month == compare_selected_month else 'none'
                            for month in compare_months_sorted],
                edgecolors='red',
                s=100,
                picker=5,
                zorder=3
            )
            compare_month_map = {month_num: month_str for month_num, month_str in compare_months_data.items()}
            ax.legend()

    ax.set_title(f'Fouling Timeline: {current_panel}' +
                 (f' vs {compare_selection[0]}' if compare_selection else ''))
    ax.set_xlabel('Month')
    ax.set_ylabel('Fouling Percentage (%)')
    ax.set_ylim(y_min, y_max)
    ax.yaxis.set_ticks(np.arange(y_min, y_max + 1, y_interval))
    ax.grid(True, zorder=0)

    all_months = sorted(set(primary_months_sorted + (compare_months_sorted if compare_selection else [])))
    ax.set_xticks(all_months)
    ax.set_xticklabels([str(m) for m in all_months])
    ax.xaxis.set_major_locator(plt.FixedLocator(all_months))

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill='both', expand=True)
    graph_references.append(canvas_widget)

    def on_pick(event):
        try:
            if event.artist == primary_points:
                ind = event.ind[0]
                clicked_month_num = primary_months_sorted[ind]
                clicked_month_str = primary_month_map.get(clicked_month_num)
                if clicked_month_str:
                    update_graph_selection_callback(primary_month=clicked_month_num,
                                                    compare_month=compare_selected_month)
                    new_face_colors = ['black' if month == clicked_month_num else 'none'
                                       for month in primary_months_sorted]
                    primary_points.set_facecolor(new_face_colors)
                    canvas.draw()
            elif compare_selection and event.artist == compare_points:
                ind = event.ind[0]
                clicked_month_num = compare_months_sorted[ind]
                clicked_month_str = compare_month_map.get(clicked_month_num)
                if clicked_month_str:
                    update_graph_selection_callback(primary_month=primary_selected_month,
                                                    compare_month=clicked_month_num)
                    new_face_colors = ['red' if month == clicked_month_num else 'none'
                                       for month in compare_months_sorted]
                    compare_points.set_facecolor(new_face_colors)
                    canvas.draw()

        except Exception as e:
            print(f"Error handling pick event: {e}")

    fig.canvas.mpl_connect('pick_event', on_pick)

    return primary_points, primary_month_map, compare_points, compare_month_map, ax, canvas
