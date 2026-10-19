# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

"""
QA_score_grader.py is a script that gathers all the games/tests where the QA_score has not been saved yet.
the QA's are not automaticly graded because the questons and answers of the SQUADv2.0 dataset are not perfect or because of a typo you could miss out on a good answer.
That's why human supervision is needed to grade these answers. 

scores will be saved automatically in the main_df. Change the QA_score of that test from main_df to `numpy.nan` to redo the grading. 
"""

import os
import pandas as pd
import numpy as np

dataframe_folder_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(dataframe_folder_path)
df_path_read = os.path.join(dataframe_folder_path, fr'{dataframe_folder_path}\experiment_data\read_df.pkl')
df_path_main = os.path.join(dataframe_folder_path, fr'{dataframe_folder_path}\experiment_data\main_df.pkl')

print(df_path_main)
print(df_path_read)
print()

if not os.path.exists(df_path_read):
    print("not exists: ",df_path_read)
if not os.path.exists(df_path_main):
    print("not exists: ",df_path_main)


if not os.path.exists(df_path_read) or not os.path.exists(df_path_main):
    print("df not correctly installed/couldnt find them. so cant make it work :(")
    quit()

df_read = pd.read_pickle(df_path_read)
df_main = pd.read_pickle(df_path_main)

# add check if the QA_score list is still empty
if "QA_score" not in df_main.columns:
    df_main["QA_score"] =  np.nan

# finding all NaN QA scores and selecting the not validated QA answers rows
df_main_na = df_main["QA_score"].isna()
df_removed_na = df_main[df_main_na]


for index, x in df_removed_na.iterrows():
    name = index[0]
    timestamp = index[1]

    # gathering total score of specific test
    QA_score = 0
    if index in df_read.index:
        data = df_read.loc[index]
        for index, row in data.iterrows():
            print("Question:        ", row.question)
            print("Correct answer:  ", row.correct_answer)
            print("Player's answer: ", row.player_answer)
            print()
            
            response = ""
            while len(response) == 0:
                response = input("Y/N or yes/no if answer is correct or wrong:\n")
            
            if response.lower() == "y" or response.lower() == "yes":
                print("graded correct answer")
                QA_score += 1
            else:
                print("graded wrong answer")

            print("\n\n")

    # saving new scores in df    
    print(f"QA score updated of the test on {timestamp}: ", QA_score)
    df_main.loc[index, "QA_score"] = QA_score
    df_main.to_pickle(df_path_main)
    print("Updated dataframe with latest score")

    print("\n\n\n\n\n\n\n\n\n\n\n\n")

print("\n\n\n\n\n\n\n\n\n\n\n\n")
print("Done with grading the scores, thank you!")