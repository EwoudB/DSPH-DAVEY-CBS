# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk
import random
from datetime import datetime
from game_pages.digit_span_page import DigitSpanPage
from game_pages.intro_page import IntroPage
from game_pages.maze_page import MazePage
from game_pages.reading_page import ReadingPage
from game_pages.between_page import BetweenGamesPage
from game_pages.results_page import ResultsPage


# ---------- Configuration ----------
GAME_LIST = ['digit span forward', 'digit span backward', 'maze', 'reading']

FONT = ("Helvetica", 12)
HEADER_FONT = ("Helvetica", 16, "bold")
BG_COLOR = '#2e2e2e'   # dark grey background (app)
FG_COLOR = '#ffffff'   # foreground (text)


# ---------- Main Application ----------
class App(tk.Tk):
    """Main application of the game, controlls the states of the game, also saves all the scores of the games"""
    def __init__(self):
        """create instanses of all scores and other necessary game variables, creates seed using datetime, loads in IntroPage always"""
        super().__init__()
        self.title('Mental Performance Test')
        self.configure(bg=BG_COLOR)
        self.geometry('1024x768')
        self.fullscreen = False
        self.bind('<F11>', self.toggle_fullscreen)
        self.bind('<Escape>', self.exit_fullscreen)

        # Participant & questionnaire
        self.participant_name = tk.StringVar()
        self.questionnaire_answers = {}

        # Scores
        self.digit_forward_score = 0
        self.digit_backward_score = 0
        self.maze_score = 0
        self.maze_wrong_steps = 0
        self.QA_done = 0
        self.game_timestamps = {}
        self.all_maze_key_presses = []
        self.all_sequence_answers = {}
        self.reading_QA_results = []

        self.date_time = datetime.now().isoformat()
        self.random_seed = self.date_time
        random.seed(self.random_seed)

        # Game order
        self.games = GAME_LIST
        self.current_game_index = -1

        # music state
        self.musicadd = None
        self.music_thread = None
        self.music_state = None

        # Container frame (use tk.Frame so bg applies consistently)
        container = tk.Frame(self, bg=BG_COLOR)
        container.pack(fill='both', expand=True)

        self.frames = {}
        for F in (IntroPage, DigitSpanPage, MazePage, ReadingPage, BetweenGamesPage, ResultsPage):
            page = F(container, self)
            self.frames[F.__name__] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_frame('IntroPage')

    def toggle_fullscreen(self, event=None):
        """toggles fullscreen when pressing f11 on keyboard"""
        self.fullscreen = not self.fullscreen
        self.attributes('-fullscreen', self.fullscreen)

    def exit_fullscreen(self, event=None):
        """exits fullscreen when pressing f11 on keyboard"""
        if self.fullscreen:
            self.fullscreen = False
            self.attributes('-fullscreen', False)

    def show_frame(self, name):
        """shows next frame"""
        frame = self.frames[name]
        frame.tkraise()

    def add_game_timestamp(self, time_value):
        """add timestamps for each significant point in a game, usually called in a game when doind something, usually when seinding in a respons or solving a maze"""
        game_name = self.games[self.current_game_index]
        if game_name not in self.game_timestamps:
            self.game_timestamps[game_name] = []
        self.game_timestamps[game_name].append(time_value)

    def start_next_game(self):
        """Start the next game in order."""
        self.current_game_index += 1
        if self.current_game_index < len(self.games):
            game = self.games[self.current_game_index]
            if game == 'digit span forward' or game == 'digit span backward':
                self.show_frame('DigitSpanPage')
                self.frames['DigitSpanPage'].start_game()
            elif game == 'maze':
                self.show_frame('MazePage')
                self.frames['MazePage'].start_game()
            elif game =='reading':
                self.show_frame('ReadingPage')
                self.frames['ReadingPage'].start_game()
        else:
            self.show_frame('ResultsPage')

    def game_finished(self):
        """Called when a game finishes (time-up or user skipped).
        Show the between-games page (Continue) only after Digit Span finishes or after the full maze sequence finished.
        """
        # Show between-games prompt
        game_name = self.games[self.current_game_index+1] if self.current_game_index+1 < len(self.games) else 'finish'
        self.frames['BetweenGamesPage'].set_message(f'Game finished. Press Continue to start {game_name}.')
        self.show_frame('BetweenGamesPage')
