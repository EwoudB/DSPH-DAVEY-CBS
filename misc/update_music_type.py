# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

"""
update_music_type.py gives an example on how to change the music state 
from a test of a given time. 

this can be used for example to change the music type of a test when 
forgetting to turn on the headphones at the start of the test... 

the parameters are:
- PARTICIPANT NAME = name of the participant of the test (upper case sensitive)
- MUSIC TYPE = music type you want to insert in this test, see game_pages/music_addon.py and then MUSIC_STATES for the states.
- time = datetime of the test you want to change. is the index of the main_df
"""


import os
import pandas as pd

PARTICIPANT_NAME = "placeholder"
MUSIC_TYPE = "silent"
time = pd.to_datetime('2026-01-13 09:16:11.489139')

dataframe_folder_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(dataframe_folder_path)
df_path_main = os.path.join(dataframe_folder_path, f'{dataframe_folder_path}\experiment_data\main_df.pkl')

print(df_path_main)
print()

if not os.path.exists(df_path_main):
    print("df not correctly installed/couldnt find them. try again :(")
    quit()

df_main = pd.read_pickle(df_path_main)
print(df_main.head())
print(df_main["music_state"].unique)


participant_df = df_main.query(f"participant_name == {PARTICIPANT_NAME} and date_time == @time")
df_main.loc[participant_df.index, 'music_state'] = MUSIC_TYPE
print(df_main.head())


print("almost there! Uncomment this line when committing changes")
# df_main.to_pickle(df_path_main)
