import pandas as pd

def format_csv(file_path):
    df = pd.read_csv(file_path)
    columns_to_keep = ['Time', 'S_H', 'E_H', 'E_TH', 'E_NT', 'I_H', 'I_QH', 'D_H']
    df = df[columns_to_keep]
    return df

def save_csv(df, output_file):
    df.to_csv(output_file, index=False)

def main():
    # files = ['data/SimData1.csv', 'data/SimData2.csv', 'data/SimData3.csv']
    files = ['data/Latest Data on Lassa fever77.csv']
    for file in files:
        df = format_csv(file)
        save_csv(df, file.replace('.csv', '_HumansOnly.csv'))
    print("Data has been reformatted and saved to the respective files.")

if __name__ == '__main__':
    main()    