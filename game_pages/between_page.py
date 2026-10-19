# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk

# ---------- Configuration ----------
HEADER_FONT = ("Helvetica", 16, "bold")
BG_COLOR = '#2e2e2e'   # dark grey background (app)
FG_COLOR = '#ffffff'   # foreground (text)
BUTTON_BG = '#444444'
BUTTON_FG = '#ffffff'
BUTTON_ACTIVE_BG = '#666666'


# ---------- Between Games Page (Continue only when needed) ----------
class BetweenGamesPage(tk.Frame):
    """
    BetweenGamesPage class creates a page in between games for the participant to be able to give some breating space for the participant after each test.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.message_var = tk.StringVar()
        tk.Label(self, textvariable=self.message_var, font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR).pack(pady=40)
        tk.Button(self, text='Continue', command=self.on_continue,
                  bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG).pack(pady=30)

    def set_message(self, txt: str):
        """
        Set message after game has been completed, the name of the last completed game is displayed in here
        """
        self.message_var.set(txt)

    def on_continue(self):
        """closes the page and continues to the next page/game in sequence based on the order of the games in the controller application"""
        self.controller.start_next_game()