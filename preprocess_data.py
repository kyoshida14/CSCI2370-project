import pandas as pd

input_file = 'data/Latest Data on Lassa fever77.csv'
df = pd.read_csv(input_file)

df.rename(columns={'Time (days)': 'Time'}, inplace=True)

# rename the columns to keep only the text inside the parentheses
df.columns = [col.split('(')[-1].strip(')') if '(' in col else col for col in df.columns]

df_melted = df.melt(id_vars=['Time'], 
                    var_name='Category', 
                    value_name='Value')

category_mapping = {category: idx for idx, category in enumerate(df_melted['Category'].unique())}
df_melted['Category_num'] = df_melted['Category'].map(category_mapping)

output_file = 'data/reformatted_LassaFever77.csv'
df_melted.to_csv(output_file, index=False)

print(f"Data has been reformatted and saved to {output_file}")

