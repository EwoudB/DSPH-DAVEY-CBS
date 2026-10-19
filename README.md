# DSPH-DAVEY-CBS
extract from code from DSPH class of 2025-2026, team DAVEY with the cognitive behavior game framework. 

## installation process:
### Requirements + config
First pip install the requirements from the `requirements.txt` file:

```
pip install -r requirements.txt
```

You need to create your own 'config.yaml' file inside the root directory folder
Example structure of the `config.yaml` file:

```
digit_span : 'path/to/pickle'
maze : 'path/to/pickle'
reading_comprehension : 'path/to/pickle' 
main : 'path/to/pickle'
game_times: 'path/to/pickle'
heart_rate: 'path/to/pickle'

squad_df: 'path/to/pickle'
data_folder_path: 'path/to/folder/for/saving/experiment/data'
```

### install + prep squad dataset
install the squad v2 training dataset from this site: `https://rajpurkar.github.io/SQuAD-explorer/`, scroll down to `Training Set V2.0` and download this.
after this format the json data to a pickled pandas dataframe. this can be done using the script `/misc/save_squad_to_pkl.py`.

### music types
The music that we used for this experiment is not shared on github since this is too large, if you think you might need this data you can get this on request.
The used states of music can be found in `game_pages/music_addon.py` file. use this 

## Start game
After setting everything up, you then can run the game by calling: `Game.py` and try to play the game yourself.

## misc files

use `QA_score_grader.py` to grade the QA answers given after a test.

combine muse or polar data using the `get_csv_files.py`. currently only support for combining the muse athena data is implemented.  