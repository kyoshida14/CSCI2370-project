# CSCI2370 Project

## Setting up
0. **Python version in venv needs to be the same version used your Paraview.** If you have Paraview 5.13.0, then you need Python 3.10.

1. Create `venv` for trame
```sh
python3.10 -m venv .venv            # or change to compatible version
source ./.venv/bin/activate
python -m pip install --upgrade pip
pip install trame
pip install trame-vuetify trame-vtk
pip install vtk
pip install trame-components
pip install --upgrade trame-plotly
pip install pandas plotly
```

3. Create `pvenv` for paraview
```sh
python3.10 -m venv .pvenv            # or change to compatible version
source ./.pvenv/bin/activate
python -m pip install --upgrade pip
pip install trame trame-vtk trame-vuetify
deactivate
```

## Running the app using vtk

0. Make sure you are in `venv`: 

```sh
source ./.venv/bin/activate
```

1. Make sure that all necessary data is there:
    * [`map.vtk`](data/map.vtk) should be placed in the `data` folder directly.
    * e.g., to visualize `Latest_Data_on_Lassa_fever77_HumansOnly` data:
        * make sure that [`Latest_Data_on_Lassa_fever77_HumansOnly` folder](data/Latest_Data_on_Lassa_fever77_HumansOnly) exists in the `data` folder.
        * In the subfolder, there should be [`Latest_Data_on_Lassa_fever77_HumansOnly.csv`](data/Latest_Data_on_Lassa_fever77_HumansOnly/Latest_Data_on_Lassa_fever77_HumansOnly.csv) & [`dayx_vis_vtk` folder](data/Latest_Data_on_Lassa_fever77_HumansOnly/dayx_vis_vtk), which contains vtk for each day.

2. To run the app:

    * To run the Trame app, use the following command in the terminal:
        ```sh
        python3.10 [path_to_app.py]
        ```

        or if you want to specify port:
        ```sh
        python [path_to_app.py] --port 1234
        ```

    * To run the Trame & Paraview app (i.e., Paraview as a backend and Trame as a frontend):
        ```sh
        /Applications/ParaView-5.13.0.app/Contents/bin/pvpython \
        [path_to_your_app.py]  \
        --venv .pvenv/ \
        --data [path_to_your_data.pvsm]
        ```
        * NOTE: make sure to change the python or Paraview app versions as needed



## 3D view using Paraview PVSM

```sh
/Applications/ParaView-5.13.0.app/Contents/bin/pvpython \
code/PVSMLoader.py  \
--venv .pvenv/ \
--data data/pvsm/day0_vis.pvsm
```