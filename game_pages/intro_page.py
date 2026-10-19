# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk
from tkinter import messagebox, ttk
import threading
from game_pages.music_addon import MusicAddon

# ---------- Configuration ----------
FONT = ("Helvetica", 12)
HEADER_FONT = ("Helvetica", 16, "bold")
BG_COLOR = '#2e2e2e'   # dark grey background (app)
FG_COLOR = '#ffffff'   # foreground (text)
INPUT_BG = '#e5e5e5'   # light input box (Option A)
BUTTON_BG = '#444444'
BUTTON_FG = '#ffffff'
BUTTON_ACTIVE_BG = '#666666'


# ---------- Intro / Questionnaire Page ----------
class IntroPage(tk.Frame):
    """Introduction page of the main game, IntroPage contains the questionaire and input field for the participants name."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        tk.Label(self, text='\nWelcome — Mental Performance Test', font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR).pack(pady=18)

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(pady=10)

        tk.Label(form, text='Name:', font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(
            row=0, column=0, sticky='w'
        )

        controller.participant_name.set("")

        entry = ttk.Entry(
            form,
            textvariable=controller.participant_name,
            font=FONT
        )
        entry.grid(row=0, column=1, pady=5, sticky="w")

        tk.Label(form, text='I had a good rest and sleep last night?', font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(row=1, column=0, sticky='w')
        self.rest_var = tk.StringVar(value='No')
        rbframe_sleep = tk.Frame(form, bg=BG_COLOR)
        tk.Radiobutton(rbframe_sleep, text='Yes', variable=self.rest_var, value='Yes', bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR).pack(side='left')
        tk.Radiobutton(rbframe_sleep, text='No', variable=self.rest_var, value='No', bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR).pack(side='left')
        rbframe_sleep.grid(row=1, column=1, sticky='w')

        tk.Label(form, text='I have not consumed caffeine or other supplements that can alter my heart rate this morning.', font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(row=2, column=0, sticky='w')
        self.consumed_var = tk.StringVar(value='No')
        rbframe_consumed = tk.Frame(form, bg=BG_COLOR)
        tk.Radiobutton(rbframe_consumed, text='Yes', variable=self.consumed_var, value='Yes', bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR).pack(side='left')
        tk.Radiobutton(rbframe_consumed, text='No', variable=self.consumed_var, value='No', bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR).pack(side='left')
        rbframe_consumed.grid(row=2, column=1, sticky='w')

        tk.Label(form, text='I have not done any exercise before the test.', font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(row=3, column=0, sticky='w')
        self.exercise_var = tk.StringVar(value='No')
        rbframe_exercise = tk.Frame(form, bg=BG_COLOR)
        tk.Radiobutton(rbframe_exercise, text='Yes', variable=self.exercise_var, value='Yes', bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR).pack(side='left')
        tk.Radiobutton(rbframe_exercise, text='No', variable=self.exercise_var, value='No', bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR).pack(side='left')
        rbframe_exercise.grid(row=3, column=1, sticky='w')

        tk.Label(form, text='I am feeling healthy today.', font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(row=4, column=0, sticky='w')
        self.healthy_var = tk.StringVar(value='No')
        rbframe_healthy = tk.Frame(form, bg=BG_COLOR)
        tk.Radiobutton(rbframe_healthy, text='Yes', variable=self.healthy_var, value='Yes', bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR).pack(side='left')
        tk.Radiobutton(rbframe_healthy, text='No', variable=self.healthy_var, value='No', bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR).pack(side='left')
        rbframe_healthy.grid(row=4, column=1, sticky='w')

        tk.Label(form, text='Please describe any issues or symptoms you are experiencing (fill nothing if none):', font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(row=5, column=0, sticky='nw')
        self.comments = tk.Text(form, width=40, height=4, font=FONT, bg='white', fg='black')
        self.comments.grid(row=5, column=1, pady=4)

        tk.Label(form, text='I confirm that the above information is correct and that I am able to participate in the test.', font=FONT, bg=BG_COLOR, fg=FG_COLOR).grid(row=6, column=0, sticky='w')
        self.confirmed_var = tk.StringVar(value='No')
        rbframe_confirmed = tk.Frame(form, bg=BG_COLOR)
        tk.Radiobutton(rbframe_confirmed, text='Yes', variable=self.confirmed_var, value='Yes', bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR).pack(side='left')
        tk.Radiobutton(rbframe_confirmed, text='No', variable=self.confirmed_var, value='No', bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR).pack(side='left')
        rbframe_confirmed.grid(row=6, column=1, sticky='w')

        tk.Button(self, text='Start Tests', command=self.on_start,
                  bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG).pack(pady=14)


    def on_start(self):
        """When start button has been pressed, checks if name is filled and then starts music thread and continues to the next game"""
        name = self.controller.participant_name.get().strip()
        if len(name) == 0:
            messagebox.showwarning('Name required', 'Please enter participant name.')
            return
        self.controller.questionnaire_answers = {
            'rest': self.rest_var.get().strip(),
            'consumed': self.consumed_var.get(),
            'exercise': self.exercise_var.get().strip(),
            'healthy': self.healthy_var.get().strip(),
            'comments': self.comments.get('1.0', 'end').strip(),
            'confirmed': self.confirmed_var.get().strip()
        }

        # Start music in a background thread
        self.controller.musicadd = MusicAddon(name)
        self.controller.music_thread = threading.Thread(target=self.controller.musicadd.run_music_loop,daemon=True)
        self.controller.music_thread.start()

        # Poll until state is set
        self.wait_for_music_state()

        self.controller.game_finished()

    def wait_for_music_state(self):
        """function checks to see if music has started, keeps on waiting until music has started playing"""
        self.controller.music_state = self.controller.musicadd.get_state()
        if self.controller.music_state is None:
            # Check again in 100 ms
            self.after(100, self.wait_for_music_state)
        else:
            self.controller.game_finished()