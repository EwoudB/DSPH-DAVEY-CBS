"""
Module for managing randomized music playback with state tracking.
"""

# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import random
import time
import os
import threading
import json
import platform
from pathlib import Path

# ------------------------------
# Set VLC library path BEFORE importing vlc (Windows only)
# ------------------------------
if platform.system() == "Windows":
    os.environ['PYTHON_VLC_LIB_PATH'] = r"C:\Program Files\VideoLAN\VLC\libvlc.dll"
import vlc

# ------------------------------
# Directories and files
# ------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
BASE_DIR = os.path.join(SCRIPT_DIR, "../music")
STATE_FILE = os.path.join(SCRIPT_DIR, "../music_state.json")

# ---------- Configuration ----------
MUSIC_STATES = ["silent", "WhiteNoise", "FastInstrumental",
                "FastLyrical", "SlowInstrumental", "SlowLyrical"]
STATE_REPEATS = 1  # each state can be selected x amount of times


class MusicAddon:
    """
    Handle music state selection and playback for a user.
    """
    def __init__(self, name):
        self.name = name
        self.ChosenState = None
        self._lock = threading.Lock()

    def load_music_state(self):
        """
        Load played music states from file.
        """
        if not os.path.exists(STATE_FILE):
            return {}
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def save_music_state(self, state):
        """
        Save played music state to file.
        """
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def vlc_path(self, path: Path):
        """
        Convert a file path to a VLC-compatible format.
        """
        path = path.absolute()
        if platform.system() == "Windows":
            return str(path)
        else:
            return path.as_uri()

    def play_song(self, path):
        """
        Play a song using VLC and wait until it finishes.
        """
        vlc_ready_path = self.vlc_path(Path(path))
        player = vlc.MediaPlayer(vlc_ready_path)
        player.play()
        time.sleep(0.5)
        while True:
            state = player.get_state()
            if state in (vlc.State.Ended, vlc.State.Error):
                break
            time.sleep(0.5)

    def choose_non_repeating_song(self, directory, played_list):
        """
        Select a random song not already played for user,
        resetting if all songs in state are played.
        """
        valid_ext = (".mp3", ".wav", ".flac", ".ogg", ".m4a")
        all_songs = [
            str(Path(directory) / f)
            for f in os.listdir(directory)
            if f.lower().endswith(valid_ext)
        ]
        played_filenames = set(os.path.basename(x) for x in played_list)
        fresh_songs = [s for s in all_songs if os.path.basename(
            s) not in played_filenames]
        if not fresh_songs:
            played_list = []
            fresh_songs = all_songs[:]
        chosen = random.choice(fresh_songs)
        return chosen, played_list

    def run_music_loop(self):
        """
        Run music playback with randomized non-repeating states.
        """
        username = self.name
        state_data = self.load_music_state()
        if username not in state_data:
            state_data[username] = {s: 0 for s in MUSIC_STATES}
            state_data[username]["song_history"] = {
                s: [] for s in MUSIC_STATES if s != "silent"}
            self.save_music_state(state_data)
        user_state = state_data[username]

        # Reset counts if all states completed 2 times
        if all(user_state[s] >= STATE_REPEATS for s in MUSIC_STATES):
            for s in MUSIC_STATES:
                user_state[s] = 0
            self.save_music_state(state_data)

        # Choose a state randomly among available
        available_states = [
            s for s in MUSIC_STATES if user_state[s] < STATE_REPEATS]
        chosen_state = random.choice(available_states)
        with self._lock:
            self.ChosenState = chosen_state

        user_state[chosen_state] += 1
        self.save_music_state(state_data)

        if chosen_state == "silent":
            while True:
                time.sleep(1)
        else:
            directory = os.path.join(BASE_DIR, chosen_state)
            if not os.path.exists(directory):
                print(f"Missing directory: {directory}")
                return
            history_list = user_state["song_history"][chosen_state]
            while True:
                song, history_list = self.choose_non_repeating_song(
                    directory, history_list)
                filename = os.path.basename(song)
                history_list.append(filename)
                user_state["song_history"][chosen_state] = history_list
                self.save_music_state(state_data)
                self.play_song(song)

    def get_state(self):
        """
        Return the currently selected music state.
        """
        with self._lock:
            return self.ChosenState
