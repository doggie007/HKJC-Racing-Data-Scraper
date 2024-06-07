import os
import pandas as pd

def parse_time(time_str):
    try:
        return '00:{:02d}:{:02d}.{:02d}'.format(
            int(time_str.split(':')[0]),      # Extract minutes
            int(time_str.split(':')[1].split('.')[0]),  # Extract seconds
            int(time_str.split(':')[1].split('.')[1])  # Extract milliseconds
        )
    except:
        return pd.NaT

folder_path = 'Data/Race-Result'

files = sorted(os.listdir(folder_path))

final_pd = pd.DataFrame()

race_id = 0

for file_name in files:
    file_path = os.path.join(folder_path, file_name)
    df = pd.read_csv(file_path)
    df['Race ID'] = race_id

    cols_to_drop = ['Horse', 'Horse URL', 'Jockey', 'Trainer', 'LBW', 'Running Position']
    df = df.drop(columns=cols_to_drop)
    final_pd = pd.concat([final_pd, df], axis=0)

    race_id += 1


final_pd['Finish Time'] = final_pd['Finish Time'].apply(parse_time)
final_pd['Finish Time'] = pd.to_timedelta(final_pd['Finish Time'])

cols_to_numeric = ['Pla.', 'Horse No.', 'Act. Wt.', 'Declar. Horse Wt.', 'Dr.', 'Win Odds']
final_pd[cols_to_numeric] = final_pd[cols_to_numeric].apply(pd.to_numeric, errors='coerce')

final_pd = final_pd.dropna()
cols_to_int = ['Pla.', 'Horse No.', 'Dr.', 'Declar. Horse Wt.']
final_pd[cols_to_int] = final_pd[cols_to_int].astype(int)

# print(final_pd.columns)
# print(final_pd.head())
# print(final_pd.describe())
# print(final_pd.dtypes)

final_pd.to_csv(os.path.join('Data',  f"temp_result.csv"), index = False)

