from paraview.simple import *
import os

# Input and output directories
coords_folder = "dayx_coords"  
output_folder = "dayx_vis"  
human_stl_file = "standing.stl"  
map_vtk_file = "outputDachNigerialatest.vtk"  

# Create output directory
os.makedirs(output_folder, exist_ok=True)

# Process each CSV in the folder
for csv_file in os.listdir(coords_folder):

    if csv_file.endswith(".csv"):
        # Extract the day name for output naming
        day_name = os.path.splitext(csv_file)[0]

        # Load the CSV as a table
        table = CSVReader(FileName=[os.path.join(coords_folder, csv_file)])

        # Convert to points
        table_to_points = TableToPoints(Input=table)
        table_to_points.XColumn = "x"
        table_to_points.YColumn = "y"
        table_to_points.ZColumn = "z"

        # Add glyph with custom source
        glyph = GlyphWithCustomSource(Input=table_to_points, GlyphSource=STLReader(FileNames=[human_stl_file]))
        glyph.ScaleFactor = 0.05  # Set the scale factor to 0.05
        # glyph.OrientationArray = HOW TO ROTATE 

        # Set coloring by agent type
        glyph_display = Show(glyph)
        ColorBy(glyph_display, ('POINTS', 'agent_types'))  # Replace 'agent_types' with your column name

        agent_types_lut = GetColorTransferFunction('agent_types')
        agent_types_lut.InterpretValuesAsCategories = 1  # Treat values as categories
        agent_types_lut.Annotations = ['0', 'Type A', '1', 'Type B']  # Map values to labels
        agent_types_lut.IndexedColors = [1, 0, 0, 0, 1, 0]  # RGB for 'Type A' and 'Type B'

        glyph_display.LookupTable = agent_types_lut

        glyph_display = Show(glyph)

        # Add map and apply transform
        map_data = LegacyVTKReader(FileNames=[map_vtk_file])
        transform = Transform(Input=map_data)
        transform.Transform.Translate = [-60, 2, 200]
        transform.Transform.Rotate = [270, 0, 0]
        transform.Transform.Scale = [15, 15, 15]

        # Add transformed map to scene 
        map_display = Show(transform)

        # Save visualization as VTK 
        SaveData(os.path.join(output_folder, f"{day_name}.vtk"), proxy=glyph)

        # Clear pipeline for next file
        Delete(table)
        Delete(table_to_points)
        Delete(glyph)
        Delete(map_data)
        Delete(transform)

# Notify user of completion
print(f"Processing complete. Files saved to: {output_folder}")

