# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import textwrap
import tkinter as tk
import random
import time
from datetime import datetime
from game_pages.load_df import DF_parser


# ------------------------------
# Directories and files
# ------------------------------
READING_DATASET = DF_parser().squad_qa()

# ---------- Configuration ----------
GAME_TIME_LIMIT = 300  # seconds (short for testing)

FONT = ("Helvetica", 12)
HEADER_FONT = ("Helvetica", 16, "bold")
CANVAS_W = 900
CANVAS_H = 600
CELL_PIX_DEFAULT = 20
BG_COLOR = '#2e2e2e'   # dark grey background (app)
FG_COLOR = '#ffffff'   # foreground (text)
INPUT_BG = '#e5e5e5'   # light input box (Option A)

# skip game button parameters
BUTTON_BG = '#444444'
BUTTON_FG = '#ffffff'
BUTTON_ACTIVE_BG = '#666666'

# ---------- Reading test ----------
class ReadingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        tk.Label(self, text='Reading Test', font=HEADER_FONT,
                 bg=BG_COLOR, fg=FG_COLOR).pack(pady=10)

        # Canvas for centered text
        self.canvas = tk.Canvas(
            self, width=CANVAS_W, height=CANVAS_H-275,
            bg=BG_COLOR, highlightthickness=0
        )
        self.canvas.pack(pady=8)

        # Hidden answer frame
        self.ans_frame = tk.Frame(self, bg=BG_COLOR)

        tk.Label(self.ans_frame, text="Your answer:", font=FONT,
                 bg=BG_COLOR, fg=FG_COLOR)

        self.question_field = tk.Label(self.ans_frame, text='', font=FONT,
                                       bg=BG_COLOR, fg=FG_COLOR)
        self.question_field.pack(pady=6)

        self.answer_var = tk.StringVar()
        self.answer_entry = tk.Entry(
            self.ans_frame, textvariable=self.answer_var,
            width=50, font=FONT, bg=INPUT_BG
        )
        self.answer_entry.pack(pady=6)

        # Buttons
        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(pady=5)

        # Visible at start
        self.show_question_btn = tk.Button(
            btn_frame, text="Show Question",
            bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG,
            command=self.reveal_question
        )
        self.show_question_btn.pack(side="left", padx=6)

        # button for skipping tests, only for dev mode
        tk.Button(btn_frame, text='Skip (end test)', command=self.end_test,
                  bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG).pack(side='left', padx=6)


        self.status_label = tk.Label(
            self, text="", bg=BG_COLOR, fg=FG_COLOR, font=FONT
        )
        self.status_label.pack(pady=4)

        # State
        self.active = False
        self.start_time = time.time() # needs to be time.time()
        self.curr_game_time = datetime.now()
        self.dataset = READING_DATASET
        self.previous_texts = []

        self.context_id = None
        self.context = None
        self.question = None
        self.answer = None

        # "context" or "question"
        self.mode = "context"

        self.bind_all("<Return>", self.on_key)

        # time for when player presses the 'show question' button
        self.time_at_question = datetime.now()

    def start_game(self):
        self.active = True
        self.controller.reading_QA_results = []
        self.controller.QA_done = 0

        self.new_QA()
        self.start_time = time.time() #needs to be time.time()
        self.after(1000, self.check_time)

        # start in context mode
        self.show_question_btn.config(state="normal")
        try:
            self.submit_btn.pack_forget()
        except:
            pass
        try:
            self.ans_frame.pack_forget()
        except:
            pass

    def new_QA(self):
        """gathers new QA combination, checks if text has not already been chosen, otherwise skips and gathers new random sample"""
        self.mode = "context"

        while True:
            sample = self.dataset.iloc[[random.randrange(0,len(self.dataset))]]
            cid = sample.iat[0, 0]
            if cid not in self.previous_texts:
                break

        self.context_id = sample.iat[0, 0]
        self.context = sample.iat[0, 1]
        self.question = sample.iat[0, 2]
        self.answer = sample.iat[0, 3]

        self.previous_texts.append(self.context_id)

        self.answer_var.set("")
        self.draw_context()
        self.curr_game_time = datetime.now()

    def draw_context(self):
        """displays all the text and input fields"""
        self.canvas.delete("all")

        wrapped = textwrap.fill(self.context, width=90)

        # Create text off-screen to measure it
        temp_id = self.canvas.create_text(
            5, 5,
            text=wrapped,
            font=FONT,
            width=CANVAS_W - 20,
            anchor="nw",
            justify="center"
        )

        # Calculate height needed
        bbox = self.canvas.bbox(temp_id)
        text_height = bbox[3] - bbox[1]

        # Desired padding around text
        padding = 40
        needed_height = text_height + padding

        # Set canvas height dynamically
        self.canvas.config(height=max(needed_height, CANVAS_H - 275))

        # Remove temp text
        self.canvas.delete(temp_id)

        # Redraw centered text properly
        self.canvas.create_text(
            CANVAS_W // 2,
            20,
            text=wrapped,
            font=FONT,
            width=CANVAS_W - 20,
            anchor="n",
            justify="center",
            fill=FG_COLOR
        )

        self.status_label.config(text="Read the text, then press 'Show Question'.")

    def reveal_question(self):
        """reveals the question after the show question button has been pressed, enables input to input field"""
        if self.mode != "context":
            return

        self.mode = "question"

        self.question_field.config(text=self.question, width=120)

        # Hidden by default
        self.submit_btn = tk.Button(
            self.ans_frame, text="Submit Answer",
            bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG,
            command=self.submit_answer
        )

        self.ans_frame.pack(pady=6)
        self.submit_btn.pack(side="bottom", pady=6)

        self.answer_entry.config(state="normal")
        self.answer_entry.focus()

        self.show_question_btn.config(state="disabled")
        self.time_at_question = datetime.now()

        self.status_label.config(text="Please enter an answer:")

    def submit_answer(self):
        """checks if response is not empty, then saves answer and calls new_QA to gather new QA"""
        if not self.active or self.mode != "question":
            return

        player_answer = self.answer_var.get().strip()
        if player_answer == "":
            self.status_label.config(text="Don't leave it blank you dingus.")
            return

        #saves time from start till answer of QA. Start is when text is visible, end is when question is send in
        self.controller.add_game_timestamp((self.curr_game_time.strftime('%F %T.%f')[:-3], datetime.now().strftime('%F %T.%f')[:-3]))
        self.controller.reading_QA_results.append({
            "context_id": self.context_id,
            "question": self.question,
            "correct_answer": self.answer,
            "player_answer": player_answer,
            "show_question": self.time_at_question.strftime('%F %T.%f')[:-3],
        })
        self.controller.QA_done += 1

        self.status_label.config(text="")

        # Hide answer UI again
        self.ans_frame.pack_forget()
        self.submit_btn.pack_forget()
        self.show_question_btn.config(state="normal")

        self.new_QA()

    def on_key(self, event):
        if not self.active:
            return

        if self.mode == "question":
            self.submit_answer()

    def check_time(self):
        if time.time() - self.start_time >= GAME_TIME_LIMIT:
            self.active = False
            self.controller.frames['BetweenGamesPage'].set_message(
                'Time is up for the Reading Test. Press Continue to proceed.'
            )
            self.controller.show_frame('BetweenGamesPage')
            return

        self.after(1000, self.check_time)

    def end_test(self):
        if self.active:
            self.active = False
        self.controller.game_finished()