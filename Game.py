# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

from game_pages.main_app import App

# ---------- Run ----------
if __name__ == '__main__':
    app = App()
    app.toggle_fullscreen()
    app.mainloop()
