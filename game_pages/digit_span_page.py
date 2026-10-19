# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk
import random
from datetime import datetime

# ---------- Configuration ----------
FONT = ("Helvetica", 12)
HEADER_FONT = ("Helvetica", 16, "bold")
BG_COLOR = '#2e2e2e'   # dark grey background (app)
FG_COLOR = '#ffffff'   # foreground (text)
INPUT_BG = '#e5e5e5'   # light input box (Option A)

# skip game button parameters
BUTTON_BG = '#444444'
BUTTON_FG = '#ffffff'
BUTTON_ACTIVE_BG = '#666666'

DIGIT_DISPLAY_MS = 1000  # ms per digit

# ---------- Digit Span Page ----------
class DigitSpanPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        self.type = ["forward", "backward"]
        self.curr_state = 0  # 0 = forward, 1 = backward

        self.title_label = tk.Label(self, text='', font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR)
        self.title_label.pack(pady=10)

        self.info_text = tk.Label(self, text='', font=FONT, bg=BG_COLOR, fg=FG_COLOR)
        self.info_text.pack(pady=4)

        self.sequence_label = tk.Label(self, text='', font=("Helvetica", 22), bg=BG_COLOR, fg=FG_COLOR)
        self.sequence_label.pack(pady=12)

        entry_frame = tk.Frame(self, bg=BG_COLOR)
        entry_frame.pack(pady=6)
        tk.Label(entry_frame, text='Enter sequence:', font=FONT, bg=BG_COLOR, fg=FG_COLOR).pack(side='left')
        self.answer_var = tk.StringVar()
        self.answer_entry = tk.Entry(entry_frame, textvariable=self.answer_var, font=FONT, width=30, bg=INPUT_BG)
        self.answer_entry.pack(side='left', padx=8)
        self.answer_entry.bind("<Return>", self.on_key)

        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text='Submit', command=self.check_answer,
                  bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG).pack(side='left', padx=6)
        
        # button for skipping tests, only for dev mode
        tk.Button(btn_frame, text='Skip (end test)', command=self.end_test,
                  bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG).pack(side='left', padx=6)

        self.status_label = tk.Label(self, text='', font=FONT, bg=BG_COLOR, fg=FG_COLOR)
        self.status_label.pack(pady=6)

        # State
        self.active = False
        self.seq_len = 1
        self.current_sequence = []
        self.current_sequence_backwards = []
        self.mistakes = 0
        self.controller.digit_forward_score = 0
        self.controller.digit_backward_score = 0
        self.curr_game_time = datetime.now()
        self.sequence = 0
        self.sequence_answers = []


    def start_game(self):
        """starts digit span game, checks the curr_state variable to see what state the digit span needs to be in"""
        self.active = True
        self.seq_len = 1
        self.mistakes = 0
        self.answer_var.set('')

        text = f'Digit Span Test {self.type[self.curr_state]}'
        self.title_label.config(text=text)

        order = "in sequential order" if self.type[self.curr_state] == "forward" else "in backwards order"
        self.info_text.config(text=f'You will see digits one-by-one. Then type the full sequence {order}.')
        self.answer_entry.config(state='disabled')
        self.status_label.config(text='')
        self.after(400, self.generate_new_sequence)
        self.sequence_answers = []

    def generate_new_sequence(self):
        """creates a randomized number sequence based on the current seq_len, calls the show_next_digit function to display the sequence in order"""
        if not self.active:
            return
        # build sequence
        sequence = [str(random.randint(0,9)) for _ in range(self.seq_len)]
        self.current_sequence = sequence.copy()
        self.current_sequence_backwards = sequence.copy()
        self.current_sequence_backwards.reverse()
        self.display_index = 0
        self.sequence_label.config(text='')
        self.after(500, self.show_next_digit)

    def show_next_digit(self):
        """displays the given sequence in order, gives acces for the input field until the full sequence is displayed"""
        if not self.active:
            return

        sequence = self.current_sequence if self.type[self.curr_state] == "forward" else self.current_sequence_backwards
        self.sequence = sequence

        if self.display_index < len(sequence):
            d = sequence[self.display_index]
            self.sequence_label.config(text=d)
            self.display_index += 1
            # Clear after digit display
            self.after(DIGIT_DISPLAY_MS, lambda: self.sequence_label.config(text=''))
            self.after(DIGIT_DISPLAY_MS + 150, self.show_next_digit)
        else:
            # Enable input
            self.answer_var.set('')
            self.answer_entry.config(state='normal')
            self.answer_entry.focus()
            self.status_label.config(text=f'')
            self.curr_game_time = datetime.now()

    def check_answer(self):
        """function checks if the given sequence is correct based on the current game type (forward or backward)"""
        if not self.active:
            return
        ans = self.answer_var.get().strip()
        if len(ans) == 0:
            return
        correct = ''.join(self.current_sequence)

        # save time took to answer each sequence. Start at first possible input, end is when answer is send
        submit_time = datetime.now()
        self.controller.add_game_timestamp((self.curr_game_time.strftime('%F %T.%f')[:-3], submit_time.strftime('%F %T.%f')[:-3]))

        if ans == correct:
            self.sequence_answers.append((submit_time.strftime('%F %T.%f')[:-3], ''.join(self.sequence), ans, True))
            if self.type[self.curr_state] == "forward":
                self.controller.digit_forward_score += 1
            else:
                self.controller.digit_backward_score += 1

            self.status_label.config(text='Correct!')
            self.seq_len += 1
            self.answer_entry.config(state='disabled')
            self.after(400, self.generate_new_sequence)
        else:
            self.sequence_answers.append((submit_time.strftime('%F %T.%f')[:-3], ''.join(self.sequence), int(ans), False))
            self.mistakes += 1
            if self.mistakes >= 3:
                self.end_test()
                return
            else:
                self.status_label.config(text=f'Incorrect. Try again. Mistakes: {self.mistakes}')
                self.answer_entry.config(state='disabled')
                self.after(400, self.generate_new_sequence)
        self.answer_var.set('')

    def end_test(self):
        """ends test, calls controller to tell that the game is finished"""
        self.active = False
        game_type = "forward" if self.type[self.curr_state] == "forward" else "backward"
        self.controller.all_sequence_answers[game_type] = self.sequence_answers

        self.after(DIGIT_DISPLAY_MS*5, lambda: self.status_label.config(text=' '))

        self.seq_len = 1
        self.mistakes = 0

        # transition to backward
        self.curr_state += 1
        self.controller.game_finished()

    def on_key(self, event):
        """on_key event handler, checks if answer is not empty and if 'Return' key has been selected, then calls check_answer function to validate answer"""
        if not self.active or len(self.answer_var.get().strip()) == 0:
            return
        if event.keysym != 'Return':
            return
        self.check_answer()