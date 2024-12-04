

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, plotly, vtk

import pandas as pd
import sys
import plotly.graph_objects as go
import os
import numpy as np
import time

from vtkmodules.vtkIOLegacy import vtkPolyDataReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkCommonCore import vtkUnsignedCharArray
from vtkmodules.vtkWebGLExporter import vtkPVWebGLExporter

CURRENT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))


# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
# Modify here
data_filename = "Latest_Data_on_Lassa_fever77_HumansOnly"

# No need to modify below
data_dir = os.path.join(CURRENT_DIRECTORY, f"../data/{data_filename}")
data_path = os.path.join(data_dir, f"{data_filename}.csv")
vtk_dir = os.path.join(data_dir, "dayx_vis_vtk")
map_vtk_path = os.path.join(CURRENT_DIRECTORY, "../data/map.vtk")
output_base_dir = os.path.join(data_dir, "webGL_output")

# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------

# Read the data
df = pd.read_csv(data_path)
df['Time'] = df['Time'].astype(int)
max_day = df['Time'].max()

# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------

# VTK pipeline
renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
# renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
style = vtkInteractorStyleTrackballCamera()
renderWindowInteractor.SetInteractorStyle(style)

# Read the day VTK file as user selects the day
day_readers = {}

# Create mapper and actor for the Glyphs
mapper = vtkPolyDataMapper()
## NOTE: if you want to statistically visualize the data for day 0, uncomment the line below
# mapper.SetInputConnection(reader_day0.GetOutputPort())

actor = vtkActor()
actor.SetMapper(mapper)

# Read the map data
reader_map = vtkPolyDataReader()
reader_map.SetFileName(map_vtk_path)
reader_map.Update()
# Create mapper and actor for the Glyphs
mapper_map = vtkPolyDataMapper()
mapper_map.SetInputConnection(reader_map.GetOutputPort())
actor_map = vtkActor()
actor_map.SetMapper(mapper_map)

# Add the actors to the renderer
renderer.AddActor(actor)
renderer.AddActor(actor_map)


def hex_to_rgb(hex_color):
    """Convert hex color (e.g., '#FF5733') to normalized RGB (0-1)."""
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]

def add_3d_colors(day_reader):
    # Add colors to the 3D visualization
    polydata = day_reader.GetOutput() # THIS LOADS THE POLYDATA INTO A VARIABLE (THIS IS HOW YOU ACCESS AND UPDATE DATA)

    point_data = polydata.GetPointData()

    # Access arrays as vtkAbstractArray
    polydata_agent_type_array = point_data.GetAbstractArray("agent_type")
    polydata_color_array = point_data.GetAbstractArray("color")

    agent_type_list = []
    for i in range(1, polydata_agent_type_array.GetNumberOfTuples()):
        agent_type_list.append(polydata_agent_type_array.GetValue(i)) 

    colors_list = []
    for i in range(1, polydata_color_array.GetNumberOfTuples()):
        colors_list.append(polydata_color_array.GetValue(i)) 

    # Convert to RGB and repeat as necessary
    rgb_colors = np.array([hex_to_rgb(color) for color in colors_list])
    num_points = polydata.GetNumberOfPoints()
    if len(rgb_colors) < num_points:
        rgb_colors = np.tile(rgb_colors, (num_points // len(rgb_colors) + 1, 1))[:num_points]

    # Create a vtkUnsignedCharArray for colors
    color_array = vtkUnsignedCharArray()
    color_array.SetName("Colors")
    color_array.SetNumberOfComponents(3)  # RGB has 3 components
    color_array.SetNumberOfTuples(num_points)

    # Populate the color array
    for i in range(num_points):
        color_array.SetTuple3(i, *(rgb_colors[i] * 255))  # Convert back to 0-255 range

    # Assign the color array to the polydata
    polydata.GetPointData().SetScalars(color_array)

    return polydata


def export_scene_to_webGL(renderWindow, output_name):
    """Export the current VTK render window to an interactive HTML file."""
    output_name = os.path.abspath(output_name)
    # Ensure the output directory exists
    directory = os.path.dirname(output_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    else:
        print(f"Directory already exists: {directory}")
    
    print(f"Exporting to: {output_name}")

    # Export the WebGL scene
    exporter = vtkPVWebGLExporter()
    exporter.SetRenderWindow(renderWindow)
    exporter.SetFileName(output_name)  # Use correct path
    try:
        print("Starting WebGL export...")
        exporter.Write()
        print(f"Successfully exported WebGL scene to {output_name}")
    except Exception as e:
        print(f"Export failed: {e}")


for day in range(max_day + 1):
    # Prepare the VTK file path
    day_vtk_path = os.path.join(vtk_dir, f"{day}_data_coords.vtk")
    reader = vtkPolyDataReader()
    reader.SetFileName(day_vtk_path)
    reader.Update()

    # Set up mapper and actor for the scene
    polydata = add_3d_colors(reader)
    mapper.SetInputConnection(reader.GetOutputPort())
    mapper.SetInputData(polydata)
    renderWindow.Render()

    # Export to WebGL
    output_name = os.path.join(output_base_dir, f"webGL_day{day}", f"webGL_day{day}")
    export_scene_to_webGL(renderWindow, output_name)

