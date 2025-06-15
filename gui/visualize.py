import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import os # Added to check for file existence
import math # Added for trigonometry
import plotly.graph_objects as go
import plotly.io as pio

def visualize_cnc_operations(filepath, ax=None):
    """
    Visualizes the CNC cutting operations on a metal sheet by reading an Excel file.
    Includes features to handle many data points and avoid label overlap.

    Args:
        filepath (str): The path to the Excel file containing the CNC instructions.
        ax (matplotlib.axes.Axes, optional): The Axes object to draw on. If None, a new plot is created and shown.
    """
    # --- Check if file exists ---
    if not os.path.exists(filepath):
        print(f"Error: The file '{filepath}' was not found.")
        if ax:
            ax.clear()
            ax.text(0.5, 0.5, "File not found", ha='center', va='center', transform=ax.transAxes)
            if hasattr(ax, 'total_data_extent_x_calculated'): delattr(ax, 'total_data_extent_x_calculated')
            if hasattr(ax, 'total_data_extent_y_calculated'): delattr(ax, 'total_data_extent_y_calculated')
            fig = ax.get_figure()
            if fig: fig.canvas.draw_idle()
        return

    # --- Read data from Excel ---
    try:
        df = pd.read_excel(filepath)
        data = df.to_dict('records')
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
        if ax:
            ax.clear()
            ax.text(0.5, 0.5, "Error reading file", ha='center', va='center', transform=ax.transAxes)
            if hasattr(ax, 'total_data_extent_x_calculated'): delattr(ax, 'total_data_extent_x_calculated')
            if hasattr(ax, 'total_data_extent_y_calculated'): delattr(ax, 'total_data_extent_y_calculated')
            fig = ax.get_figure()
            if fig: fig.canvas.draw_idle()
        return

    # --- Constants ---
    SHEET_WIDTH = 200  # Visual width of the sheet in the plot
    HOLE_DIAMETER = 15 # Diameter of the punched hole
    INITIAL_VIEW_WIDTH = 2000 # The initial visible width of the sheet in mm (reduced for more obvious panning)
    
    # Tool positions from the machine description
    POS_V_NOTCH = 0
    POS_HOLE_PUNCH = 1250
    POS_SHEAR = 4334.5

    if not data:
        print("Warning: No data records found in the Excel file after reading.")
        if ax:
            ax.clear()
            ax.text(0.5, 0.5, "No data to visualize", ha='center', va='center', transform=ax.transAxes)
            if hasattr(ax, 'total_data_extent_x_calculated'): delattr(ax, 'total_data_extent_x_calculated')
            if hasattr(ax, 'total_data_extent_y_calculated'): delattr(ax, 'total_data_extent_y_calculated')
            fig_ref = ax.get_figure() # Use a different variable name to avoid conflict
            if fig_ref: fig_ref.canvas.draw_idle()
        return

    # Robust total_feed calculation
    valid_feed_distances = []
    for i_row, row_data_item in enumerate(data):
        try:
            feed_dist_val = row_data_item.get('Feed Dist')
            if feed_dist_val is not None:
                valid_feed_distances.append(float(feed_dist_val))
            else:
                # print(f"Warning (visualize_cnc_operations): 'Feed Dist' missing in data index {i_row}. Assuming 0.")
                valid_feed_distances.append(0.0)
        except (ValueError, TypeError):
            # print(f"Warning (visualize_cnc_operations): Invalid 'Feed Dist' value ('{row_data_item.get('Feed Dist')}') in data index {i_row}. Assuming 0.")
            valid_feed_distances.append(0.0)
    total_feed = sum(valid_feed_distances)

    # --- Setup the plot ---
    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(20, 10))
    else:
        fig = ax.get_figure()
        ax.clear()

    if total_feed <= 1e-6: # Using a small epsilon for float comparison
        print("Warning: Total feed distance is zero or negligible. No meaningful plot to generate.")
        ax.text(0.5, 0.5, "No operations or zero feed", ha='center', va='center', transform=ax.transAxes)
        if hasattr(ax, 'total_data_extent_x_calculated'): delattr(ax, 'total_data_extent_x_calculated')
        if hasattr(ax, 'total_data_extent_y_calculated'): delattr(ax, 'total_data_extent_y_calculated')
        if fig: fig.canvas.draw_idle()
        return

    # Draw the initial rectangular metal sheet for the entire length
    sheet = patches.Rectangle((0, 0), total_feed + 100, SHEET_WIDTH, 
                              edgecolor='black', facecolor='lightgray', 
                              label='Sheet Metal', linewidth=2)
    ax.add_patch(sheet)

    # --- Process each operation ---
    current_feed_position = 0
    shear_cuts = []

    for i, row in enumerate(data):
        # The sheet is fed first
        feed_distance = row['Feed Dist']
        current_feed_position += feed_distance
        tool = row['Tool']
        
        # --- Logic to prevent label overlap ---
        # Alternate the vertical position of the labels for each step.
        text_y_pos = SHEET_WIDTH + 10 + (i % 2) * 20 
        
        if tool == 'v':
            # ** V-NOTCH LOGIC WITH LATERAL MOVEMENT **
            cut_position_x = current_feed_position - POS_V_NOTCH
            
            # Read the lateral travel distance for the V-notch from the data.
            vnotch_travel = row['Vnotch Trav Dist']
            
            sheet_center_y = SHEET_WIDTH / 2
            top_edge_y = SHEET_WIDTH
            
            # Calculate the vertical position of the V-notch tip.
            # It starts at the centerline and is shifted by the travel distance.
            # Positive travel moves it down, negative moves it up.
            tip_y = sheet_center_y - vnotch_travel
            
            # The vertical height of the V-notch (from its tip to the top edge).
            v_height = top_edge_y - tip_y
            
            # For a 90-degree total angle, each arm is at 45 degrees to the vertical.
            # tan(45 degrees) = 1. The horizontal half-width equals the height.
            horizontal_half_width = v_height * math.tan(math.radians(45))
            
            # Define the three points of the triangular cut
            p1_tip = (cut_position_x, tip_y) # The tip of the V at its shifted position
            p2_top_left = (cut_position_x - horizontal_half_width, top_edge_y)
            p3_top_right = (cut_position_x + horizontal_half_width, top_edge_y)
            
            v_notch_shape = patches.Polygon([p1_tip, p2_top_left, p3_top_right], closed=True, color='red')
            ax.add_patch(v_notch_shape)
            ax.text(cut_position_x, text_y_pos, f'V({i+1})\n@{cut_position_x:.1f}mm', color='red', ha='center', va='bottom', fontsize=7)

        elif tool == 'h':
            cut_position_x = current_feed_position - POS_HOLE_PUNCH
            center_y = SHEET_WIDTH / 2
            
            hole = patches.Circle((cut_position_x, center_y), HOLE_DIAMETER / 2, color='blue')
            ax.add_patch(hole)
            ax.text(cut_position_x, text_y_pos, f'H({i+1})\n@{cut_position_x:.1f}mm', color='blue', ha='center', va='bottom', fontsize=7)
 
        elif 'f' in str(tool):
            cut_position_x = current_feed_position - POS_SHEAR
            
            if tool == 'fp45':
                start_point = (cut_position_x - SHEET_WIDTH / 2, 0)
                end_point = (cut_position_x + SHEET_WIDTH / 2, SHEET_WIDTH)
            elif tool == 'fm45':
                start_point = (cut_position_x + SHEET_WIDTH / 2, 0)
                end_point = (cut_position_x - SHEET_WIDTH / 2, SHEET_WIDTH)
            else: # f0
                start_point = (cut_position_x, 0)
                end_point = (cut_position_x, SHEET_WIDTH)

            shear_cuts.append({'start': start_point, 'end': end_point, 'step': i+1, 'x_pos': cut_position_x})

    # Draw shear cuts last so they appear on top
    for shear in shear_cuts:
        ax.plot([shear['start'][0], shear['end'][0]], 
                 [shear['start'][1], shear['end'][1]], 
                 color='green', linewidth=3, linestyle='--')
        # Alternate y-position for shear labels to prevent overlap
        shear_text_y_pos = SHEET_WIDTH + 35 + ((shear['step'] - 1) % 2) * 20 
        ax.text(shear['x_pos'], shear_text_y_pos, f"S({shear['step']})\n@{shear['x_pos']:.1f}mm", color='green', ha='center', va='bottom', fontsize=7)

    # --- Final plot adjustments ---
    # Set the initial x-axis limit to a smaller window.
    ax.set_xlim(0, INITIAL_VIEW_WIDTH)
    
    ax.set_ylim(-40, SHEET_WIDTH + 100) # Increased Y-limit to make space for labels
    ax.set_xlabel('Sheet Length (mm)')
    ax.set_ylabel('Sheet Width (mm)')
    
    # Updated title to reflect the initial view and panning action.
    ax.set_title(f'CNC Emulation: Showing First {INITIAL_VIEW_WIDTH}mm (Use Pan Tool to Scroll Right)')
    
    # Setting aspect 'auto' allows the x-axis to be "zoomed" independent of the y-axis.
    ax.set_aspect('auto', adjustable='box')
    plt.grid(True, linestyle=':', alpha=0.6)
    
    legend_handles = [
        patches.Patch(color='red', label='V-Notch Cut'),
        patches.Patch(color='blue', label='Hole Punch'),
        patches.Patch(color='green', label='Shear Cut', fill=False, linestyle='--'),
        patches.Patch(facecolor='lightgray', edgecolor='black', label='Sheet Metal')
    ]
    ax.legend(handles=legend_handles, loc='upper right')

    # Store total calculated data extents on the axes for scrollbar setup
    ax.total_data_extent_x_calculated = (0, total_feed + 100)
    ax.total_data_extent_y_calculated = ax.get_ylim() # Use the actual ylim that was set
    
    if fig: 
        fig.subplots_adjust(left=0.05, right=0.99, top=0.95, bottom=0.1)

    if ax is None and fig is not None: # Only call plt.show() if we created the figure for standalone use
        plt.show()

if __name__ == '__main__':
    # --- IMPORTANT ---
    # Replace 'your_cnc_data.xlsx' with the actual name of your Excel file.
    excel_file_path = 'temp_1.xlsx'
    
    visualize_cnc_operations(excel_file_path)

def visualize_cnc_operations_plotly(filepath):
    """
    Visualizes CNC cutting operations using Plotly for an interactive experience.

    Args:
        filepath (str): The path to the Excel file.

    Returns:
        plotly.graph_objects.Figure: The Plotly figure object, or None if an error occurs.
    """
    if not os.path.exists(filepath):
        print(f"Error: The file '{filepath}' was not found.")
        return None

    try:
        df = pd.read_excel(filepath)
        data = df.to_dict('records')
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
        return None

    SHEET_WIDTH = 200
    HOLE_DIAMETER = 15
    INITIAL_VIEW_WIDTH = 2000 # Initial x-axis view

    POS_V_NOTCH = 0
    POS_HOLE_PUNCH = 1250
    POS_SHEAR = 4334.5

    fig = go.Figure()

    # Calculate total_feed robustly
    valid_feed_distances = []
    for i_row, row_data in enumerate(data):
        try:
            feed_dist_val = row_data.get('Feed Dist')
            if feed_dist_val is not None:
                valid_feed_distances.append(float(feed_dist_val))
            else:
                print(f"Warning: 'Feed Dist' missing in Excel row {i_row + 2} (data index {i_row}). Assuming 0 for total_feed calculation.")
        except (ValueError, TypeError):
            print(f"Warning: Invalid 'Feed Dist' value ('{row_data.get('Feed Dist')}') in Excel row {i_row + 2} (data index {i_row}). Assuming 0 for total_feed calculation.")
    total_feed = sum(valid_feed_distances)

    if not data:
        print("Warning: No data found in the Excel file to visualize.")
        fig.update_layout(title="No data to display")
        return fig

    # --- Draw the sheet ---
    fig.add_shape(type="rect",
                  x0=0, y0=0, x1=max(100, total_feed + 100), y1=SHEET_WIDTH, # Ensure x1 is at least 100
                  line=dict(color="Black"),
                  fillcolor="LightSkyBlue", opacity=0.5,
                  layer="below")

    current_feed_position = 0
    annotations = []
    shear_legend_added = {'fp45': False, 'fm45': False, 'f0': False} # Track legend entries for shear types

    for i, row in enumerate(data):
        try:
            feed_distance = float(row.get('Feed Dist', 0))
            current_feed_position += feed_distance
            tool = str(row.get('Tool', '')).strip().lower()
            text_y_pos = SHEET_WIDTH + 10 + (i % 2) * 30

            if not tool:
                print(f"Warning: Empty tool type in Excel row {i + 2} (data index {i}). Skipping operation.")
                continue

            if tool == 'v':
                cut_position_x = current_feed_position - POS_V_NOTCH
                vnotch_travel = float(row.get('Vnotch Trav Dist', 0))
                sheet_center_y = SHEET_WIDTH / 2
                top_edge_y = SHEET_WIDTH
                tip_y = sheet_center_y - vnotch_travel
                v_height = top_edge_y - tip_y

                if v_height < 0:
                    print(f"Warning: V-notch travel in Excel row {i + 2} (data index {i}) results in tip above sheet edge. Skipping V-notch.")
                    continue
                
                horizontal_half_width = v_height * math.tan(math.radians(45)) # tan(45) is 1
                
                p1_tip = (cut_position_x, tip_y)
                p2_top_left = (cut_position_x - horizontal_half_width, top_edge_y)
                p3_top_right = (cut_position_x + horizontal_half_width, top_edge_y)
                
                path = f'M {p1_tip[0]},{p1_tip[1]} L {p2_top_left[0]},{p2_top_left[1]} L {p3_top_right[0]},{p3_top_right[1]} Z'
                fig.add_shape(type="path", path=path, fillcolor="Red", line_color="Red", layer="above")
                annotations.append(dict(x=cut_position_x, y=text_y_pos, text=f'V({i+1})<br>@{cut_position_x:.1f}mm', showarrow=False, font=dict(color="Red", size=9)))

            elif tool == 'h':
                cut_position_x = current_feed_position - POS_HOLE_PUNCH
                center_y = SHEET_WIDTH / 2
                fig.add_shape(type="circle",
                              xref="x", yref="y",
                              x0=cut_position_x - HOLE_DIAMETER / 2, y0=center_y - HOLE_DIAMETER / 2,
                              x1=cut_position_x + HOLE_DIAMETER / 2, y1=center_y + HOLE_DIAMETER / 2,
                              line_color="Blue", fillcolor="Blue", opacity=0.7, layer="above")
                annotations.append(dict(x=cut_position_x, y=text_y_pos, text=f'H({i+1})<br>@{cut_position_x:.1f}mm', showarrow=False, font=dict(color="Blue", size=9)))

            elif 'f' in tool:
                cut_position_x = current_feed_position - POS_SHEAR
                start_point, end_point = None, None
                current_shear_type = None

                if tool == 'fp45':
                    start_point, end_point = (cut_position_x - SHEET_WIDTH / 2, 0), (cut_position_x + SHEET_WIDTH / 2, SHEET_WIDTH)
                    current_shear_type = 'fp45'
                elif tool == 'fm45':
                    start_point, end_point = (cut_position_x + SHEET_WIDTH / 2, 0), (cut_position_x - SHEET_WIDTH / 2, SHEET_WIDTH)
                    current_shear_type = 'fm45'
                elif tool == 'f0':
                    start_point, end_point = (cut_position_x, 0), (cut_position_x, SHEET_WIDTH)
                    current_shear_type = 'f0'
                else:
                    print(f"Warning: Unknown shear tool type '{tool}' in Excel row {i + 2} (data index {i}). Skipping shear.")
                    continue
                
                show_this_shear_in_legend = False
                if current_shear_type and not shear_legend_added[current_shear_type]:
                    show_this_shear_in_legend = True
                    shear_legend_added[current_shear_type] = True
                
                fig.add_trace(go.Scatter(x=[start_point[0], end_point[0]], y=[start_point[1], end_point[1]],
                                         mode='lines', 
                                         line=dict(color='Green', width=3, dash='dash'), 
                                         name=f'Shear ({tool.upper()})' if show_this_shear_in_legend else None,
                                         legendgroup='shear',
                                         showlegend=show_this_shear_in_legend ))
                annotations.append(dict(x=cut_position_x, y=SHEET_WIDTH + 45 + (i%2)*10, text=f'S({tool.upper()},{i+1})<br>@{cut_position_x:.1f}mm', showarrow=False, font=dict(color="Green", size=9)))
            else:
                print(f"Warning: Unknown tool type '{tool}' in Excel row {i + 2} (data index {i}). Skipping operation.")

        except (ValueError, TypeError) as e_calc:
            print(f"Error processing Excel row {i + 2} (data: {row}): Calculation or type error - {e_calc}. Skipping operation.")
        except KeyError as e_key:
            print(f"Error processing Excel row {i + 2} (data: {row}): Missing expected data key - {e_key}. Skipping operation.")
        except Exception as e_gen:
            print(f"An unexpected error occurred processing Excel row {i + 2} (data: {row}): {e_gen}. Skipping operation.")

    fig.update_layout(
        annotations=annotations,
        title=f'CNC Emulation (Plotly): First {INITIAL_VIEW_WIDTH}mm (Pan/Zoom enabled)',
        xaxis_title='Sheet Length (mm)',
        yaxis_title='Sheet Width (mm)',
        xaxis_range=[0, INITIAL_VIEW_WIDTH],
        yaxis_range=[-50, SHEET_WIDTH + 100],
        legend_title_text='Operations',
        plot_bgcolor='white'
    )
    fig.update_xaxes(gridcolor='lightgrey')
    fig.update_yaxes(gridcolor='lightgrey', scaleanchor="x", scaleratio=0.1) # Adjust scaleratio for visual preference

    # Add legend items for shapes (Plotly handles trace legends automatically if showlegend=True and name is provided)
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(color='LightSkyBlue', size=10, line=dict(color='Black', width=1)), name='Sheet Metal'))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(color='Red', symbol='square', size=10), name='V-Notch Cut'))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(color='Blue', symbol='circle', size=10), name='Hole Punch'))
    # Shear legend entries are now created dynamically for each type if they appear in the data.

    return fig
