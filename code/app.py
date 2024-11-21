'''
To run:
    python code/app_main.py --data [data_path]
For example:
    python code/app_main.py --data data/Latest_Data_on_Lassa_fever77_HumansOnly.csv
'''

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, plotly, vtk

import pandas as pd
import sys
import plotly.graph_objects as go
import os

from vtkmodules.vtkIOLegacy import vtkPolyDataReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

CURRENT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))


# -----------------------------------------------------------------------------
# Modify here
# -----------------------------------------------------------------------------

data_path = os.path.join(CURRENT_DIRECTORY, "../data/Latest_Data_on_Lassa_fever77_HumansOnly.csv")
vtk_dir = os.path.join(CURRENT_DIRECTORY, "../data/vtk")
map_vtk_path = os.path.join(CURRENT_DIRECTORY, "../data/vtk/map.vtk")

# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------

# Read the data
df = pd.read_csv(data_path)
df['Time'] = df['Time'].astype(int)

# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------

# VTK pipeline
renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

# Read the data for all days
day_readers = {}

# reader_day0 = vtkPolyDataReader()
# reader_day0.SetFileName(day0_vtk_path)
# reader_day0.Update()
# reader_day1 = vtkPolyDataReader()
# reader_day1.SetFileName(day1_vtk_path)
# reader_day1.Update()

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
renderer.ResetCamera()
renderWindow.Render()

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server = get_server(client_type = "vue2")
state, ctrl = server.state, server.controller

# Initialize state variables
state.day = 0
state.max_day = len(df) - 1


# -----------------------------------------------------------------------------
# visualization functions
# -----------------------------------------------------------------------------

def get_2d_viz(day):
    day_df = df[df['Time'] == day].drop(columns=['Time'])
    if day_df.empty:
        print(f"No data found for day: {day}")
        return go.Figure()  # Return empty figure if no data found for the day
    
    # Create bar chart
    state_vars = day_df.columns.tolist()
    state_var_labels = {
        "S_H": "Susceptible",
        "E_H": "Exposed",
        "E_TH": "Quarantined",
        "E_NT": "Exposed but not quarantined",
        "I_H": "Infectious",
        "I_QH": "Infectious & Isolated",
        "D_H": "Dead & infectious",  # "Infectious Human Corpse or Dead infectious human"
    }
    labels = [state_var_labels[state_var] for state_var in state_vars]
    state_values = day_df.iloc[0, :].tolist()
    state_var_colors = {
        "S_H": "#F1C40F",
        "E_H": "#EF5F33",
        "E_TH": "#E26A6A",
        "E_NT": "#CF366C",
        "I_H": "#3498DB",
        "I_QH": "#14C7DE",
        "D_H": "#515C5D"
    }
    colors = [state_var_colors[state_var] for state_var in state_vars]

    max_y_value = df.drop(columns=['Time']).max().max()

    fig = go.Figure(
        data=[go.Bar(
            x=labels, y=state_values,
            marker=dict(color=colors),
            )
        ],
    )
    fig.update_layout(
        title=f"Human population in each state on day {day}",
        yaxis_title="Number of People (10<sup>4</sup>)",
        yaxis=dict(range=[0, max_y_value]),
    )
    return fig

def get_3d_viz(day):
    # Create a placeholder 3D bar chart (update with actual 3D data)
    fig = go.Figure(
        data=[go.Bar(x=["day-10", "day", "day+10"], y=[day - 10, day, day + 10])],
    )
    fig.update_layout(
        title="3D Visualization (Placeholder)",
        scene=dict(
            xaxis=dict(title='X'),
            yaxis=dict(title='Y'),
            zaxis=dict(title='Z'),
        ),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------

@state.change("day")
def update_day(day, **kwargs):
    # print(f"Updating visualizations for day: {day}")
    if day is None:
        return

    # Update 2D viz
    ctrl.update_2d_viz(get_2d_viz(day))

    # Update 3D viz
    vtk_path = os.path.join(vtk_dir, f"day{day}_vis.vtk")
    if os.path.exists(vtk_path):
        if day not in day_readers:
            reader = vtkPolyDataReader()
            reader.SetFileName(vtk_path)
            reader.Update()
            day_readers[day] = reader
        mapper.SetInputConnection(day_readers[day].GetOutputPort())
    else:   # VTK file for the day not found
        # TODO: handle this case propoerly
        if day % 2 == 0:
            mapper.SetInputConnection(day_readers[0].GetOutputPort())
        else:
            mapper.SetInputConnection(day_readers[1].GetOutputPort())
    renderWindow.Render()
    ctrl.view_update()

# -----------------------------------------------------------------------------
# Layout 
# -----------------------------------------------------------------------------
    
with SinglePageLayout(server) as layout:
    layout.title.set_text("Lassa Fever Simulation Data")

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            # Row to hold two parts: left and right
            with vuetify.VRow(classes="fill-height"):
                # Left part: 3d viz
                with vuetify.VCol(classes="d-flex flex-column align-center", style="width: 90%;"):
                    with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
                        view = vtk.VtkLocalView(renderWindow)
                        ctrl.view_update = view.update
                        ctrl.view_reset_camera = view.reset_camera
                
                # Right part: Fig 1 (70%) and Fig 2 (30%)
                with vuetify.VCol(classes="fill-height"):
                    # Top right: Fig 1 (takes top 70%)
                    with vuetify.VRow(classes="d-flex flex-column align-center", style="height: 90%;"):
                        ctrl.update_2d_viz = plotly.Figure(
                            display_mode_bar=("false",),
                        ).update

                    # Bottom right: Fig 2 (takes bottom 30%)
                    # TODO: ticks
                    with vuetify.VRow(classes="d-flex flex-column align-center", style="height: 10%;"):
                        vuetify.VSlider(
                            v_model=("day", 0),
                            min=0,
                            max=("max_day", 100),
                            step=1,
                            label="Day",
                            style="height: 100%; width: 90%;",
                            # tick_labels=True,
                            # tick_size=4,
                            # ticks="always",
                        )

    with layout.toolbar:
        vuetify.VSpacer()
        # vuetify.VDivider(vertical=True, classes="mx-2")
        vuetify.VSwitch(
            v_model="$vuetify.theme.dark",
            hide_details=True,
            dense=True,
        )
        with vuetify.VBtn(icon=True, click=ctrl.view_reset_camera):
            vuetify.VIcon("mdi-crop-free")

if __name__ == "__main__":
    server.start()
