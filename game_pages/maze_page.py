# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import tkinter as tk
import random
import time
from datetime import datetime, timedelta

# ---------- Configuration ----------
GAME_TIME_LIMIT = 300  # seconds (short for testing)
MAZE_SEQUENCE = [3,3,3, 5,5,5, 8,8,8, 13,13,13, 21,21,21, 34,34,34, 55,55,55, 89,89,89, 144, 233]
MAZE_ALGORITHM = 'prims'  # 'backtracker' or 'prims'

FONT = ("Helvetica", 12)
HEADER_FONT = ("Helvetica", 16, "bold")
CANVAS_W = 900
CANVAS_H = 600
CELL_PIX_DEFAULT = 20
BG_COLOR = '#2e2e2e'   # dark grey background (app)
FG_COLOR = '#ffffff'   # foreground (text)

# skip game button parameters
BUTTON_BG = '#444444'
BUTTON_FG = '#ffffff'
BUTTON_ACTIVE_BG = '#666666'

# ---------- Maze Page (partial redraw) ----------
class MazePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        tk.Label(self, text='Maze Test', font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR).pack(pady=10)
        tk.Label(self, text='Use arrow keys or wasd to move to the exit. Solve as many mazes as possible.', font=FONT, bg=BG_COLOR, fg=FG_COLOR).pack(pady=4)

        self.canvas = tk.Canvas(self, width=CANVAS_W, height=CANVAS_H, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(pady=8)

        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(pady=6)

        # button for skipping tests, only for dev mode
        tk.Button(btn_frame, text='Skip (end test)', command=self.end_test,
                  bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG).pack()

        self.active = False
        self.start_time = time.time() # needs to be time.time()
        self.n_index = 0
        self.maze_grid = None
        self.n = None
        self.player = None
        self.goal = None
        self.path = set()
        self.optimal_path = 0
        self.last_dir = (0, 1)
        self.maze_generator = get_maze_generator(MAZE_ALGORITHM)
        self.timeKeySinceNewMaze = 0

        self.cell_items = {}
        self.player_item = None

        self.bind_all('<Key>', self.on_key)
        self.key_presses_this_maze = []
        self.time_at_last_key = datetime.now()
        self.start_game_time = datetime.now()
        self.all_key_presses = []


    def start_game(self):
        self.start_time = time.time() #needs to be time.time()
        self.n_index = 0
        self.controller.maze_score = 0
        self.path = set()
        self.last_dir = (0,1)
        self.cell_items.clear()
        self.player_item = None
        self.new_maze()
        self.after(1000, self.check_time)
        self.canvas.focus_set()
        self.start_game_time = datetime.now()

    def new_maze(self):
        """Creates new maze based on given maze generator algorithm, uses the find_optimal_path function to save the least amount of steps of the most optimal path"""
        if self.n_index >= len(MAZE_SEQUENCE):
            self.active = False
            self.controller.frames['BetweenGamesPage'].set_message('Maze task finished. Press Continue to proceed.')
            self.controller.show_frame('BetweenGamesPage')
            return
        self.n = MAZE_SEQUENCE[self.n_index]
        self.maze_grid = self.maze_generator.generate(self.n)
        w = len(self.maze_grid)
        self.player = (1, 1)
        self.goal = (w - 2, w - 2)

        self.optimal_path = self.find_optimal_maze_path(self.maze_grid)

        self.path = set()
        self.path.add((1,1))
        self.draw_base_maze()
        self.draw_player()

        self.key_presses_this_maze = []
        self.time_at_last_key = datetime.now()
        self.start_game_time = datetime.now()
        self.timeKeySinceNewMaze = time.time()

    def draw_base_maze(self):
        """draws the maze on the screen, green square is start, yellow is finish, grey is already walked path, red traingle is player"""
        self.canvas.delete('all')
        grid = self.maze_grid
        if grid is None:
            return
        w = len(grid)
        cell = max(4, min(CELL_PIX_DEFAULT, CANVAS_W // w, CANVAS_H // w))
        total_w = cell * w
        self.cell = cell
        self.off_x = (CANVAS_W - total_w) // 2
        self.off_y = (CANVAS_H - total_w) // 2

        self.cell_items.clear()
        for y in range(w):
            for x in range(w):
                px = self.off_x + x * cell
                py = self.off_y + y * cell
                if grid[y][x] == 1:
                    item = self.canvas.create_rectangle(px, py, px+cell, py+cell, fill='black', width=0)
                else:
                    item = self.canvas.create_rectangle(px, py, px+cell, py+cell, fill='white', width=0)
                self.cell_items[(x, y)] = item

        # start (green) and goal (yellow)
        s_item = self.cell_items.get((1,1))
        if s_item:
            self.canvas.itemconfig(s_item, fill='green')
        g_item = self.cell_items.get(self.goal)
        if g_item:
            self.canvas.itemconfig(g_item, fill='yellow')

    def draw_player(self):
        """draws a red triangle on where the player is located, orientation of triangle tells where player is heading to"""
        # remove old marker
        if self.player_item:
            self.canvas.delete(self.player_item)
            self.player_item = None
        px, py = self.player
        cx = self.off_x + px*self.cell + self.cell/2
        cy = self.off_y + py*self.cell + self.cell/2
        s = self.cell * 0.4
        dx, dy = self.last_dir
        if (dx, dy) == (1, 0):
            pts = [cx - s, cy - s, cx - s, cy + s, cx + s, cy]
        elif (dx, dy) == (-1, 0):
            pts = [cx + s, cy - s, cx + s, cy + s, cx - s, cy]
        elif (dx, dy) == (0, -1):
            pts = [cx - s, cy + s, cx + s, cy + s, cx, cy - s]
        else:
            pts = [cx - s, cy - s, cx + s, cy - s, cx, cy + s]
        self.player_item = self.canvas.create_polygon(pts, fill='red', outline='')

    def on_key(self, event):
        """event to check what key was pressed in game, uses the arrow or wasd keys to check movement, calculates if move is possible, then updates board"""
        if self.maze_grid is None or self.player is None:
            return

        # check when at new maze, input is not enabled at start for short period
        if not self.active:
            time_diff = time.time() - self.timeKeySinceNewMaze
            if time_diff < 0.5:
                return
        else: # enable input
            self.active = True
            self.time_at_last_key = datetime.now()

        key = event.keysym
        moves = {'Left': (-1, 0), 'Right': (1, 0), 'Up': (0, -1), 'Down': (0, 1), 'a': (-1, 0), 'd': (1, 0), 'w': (0, -1), 's': (0, 1)}
        if key not in moves:
            return
        dx, dy = moves[key]
        px, py = self.player
        nx, ny = px + dx, py + dy
        w = len(self.maze_grid)
        if 0 <= nx < w and 0 <= ny < w and self.maze_grid[ny][nx] == 0: #check if move possible
            prev_item = self.cell_items.get((px, py))
            if prev_item:
                if (px, py) != (1,1) and (px, py) != self.goal:
                    self.canvas.itemconfig(prev_item, fill='lightgrey')

            self.key_presses_this_maze.append((key, datetime.now().strftime('%F %T.%f')[:-3]))

            self.player = (nx, ny)
            self.path.add((nx,ny))
            self.last_dir = (dx, dy)
            self.draw_player()

            if self.player == self.goal:
                # save time took per maze. Start is at first possible input (+0.5s), end is when goal is reached
                finish_time = self.start_game_time + timedelta(seconds=0.5)
                self.controller.add_game_timestamp((finish_time.strftime('%F %T.%f')[:-3], datetime.now().strftime('%F %T.%f')[:-3]))

                self.key_presses_this_maze.insert(0, (self.key_presses_this_maze[0][0], self.key_presses_this_maze[0][1]))
                self.all_key_presses.append(self.key_presses_this_maze)

                # solved — award score and immediately continue to next maze if available
                self.controller.maze_score += 1
                self.controller.maze_wrong_steps += len(self.path) - len(self.optimal_path)
                self.n_index += 1
                # if more mazes remain, generate next immediately
                if self.n_index < len(MAZE_SEQUENCE):
                    self.new_maze()
                else:
                    # finished all configured mazes -> show BetweenGamesPage for Continue
                    self.active = False
                    self.controller.frames['BetweenGamesPage'].set_message(f'Maze task finished. Total maze score: {self.controller.maze_score}. Press Continue.')
                    self.controller.show_frame('BetweenGamesPage')

    def find_optimal_maze_path(self, grid):
        """finds most optimal path using A* algorithm"""
        from heapq import heappush, heappop

        start_pos = (1, 1)
        goal_pos = (len(self.maze_grid) - 2, len(self.maze_grid) - 2)

        # Basic Manhattan distance
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heappush(open_set, (0, start_pos))

        came_from = {}
        g_cost = {start_pos: 0}
        f_cost = {start_pos: heuristic(start_pos, goal_pos)}

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        while open_set:
            _, current = heappop(open_set)

            if current == goal_pos:
                # Reconstruct path
                route = []
                while current in came_from:
                    route.append(current)
                    current = came_from[current]
                route.append(start_pos)
                return route

            cx, cy = current

            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy

                # Skip walls and out-of-bounds
                if nx < 0 or ny < 0 or nx >= len(grid) or ny >= len(grid[0]):
                    continue
                if grid[nx][ny] == 1:
                    continue

                tentative_g = g_cost[current] + 1

                if (nx, ny) not in g_cost or tentative_g < g_cost[(nx, ny)]:
                    came_from[(nx, ny)] = current
                    g_cost[(nx, ny)] = tentative_g
                    f_cost[(nx, ny)] = tentative_g + heuristic((nx, ny), goal_pos)
                    heappush(open_set, (f_cost[(nx, ny)], (nx, ny)))

        # No path found
        return set()

    def check_time(self):
        if time.time() - self.start_time >= GAME_TIME_LIMIT:
            self.active = False
            self.end_test()
            return
        self.after(1000, self.check_time)

    def end_test(self):
        if self.active:
            self.active = False
        self.controller.all_maze_key_presses = self.all_key_presses
        self.controller.game_finished()

# ---------- Maze Generators (Strategy Pattern) ----------
class MazeGenerator:
    def generate(self, n):
        """Generate a maze grid for an n x n logical maze. Returns a grid of size (2*n+1)."""
        raise NotImplementedError

class BacktrackerMaze(MazeGenerator):
    def generate(self, n):
        w = 2 * n + 1
        grid = [[1 for _ in range(w)] for _ in range(w)]
        def carve(cx, cy):
            grid[cy][cx] = 0
            dirs = [(2,0),(-2,0),(0,2),(0,-2)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < w and 0 < ny < w and grid[ny][nx] == 1:
                    grid[cy + dy//2][cx + dx//2] = 0
                    carve(nx, ny)
        carve(1,1)
        return grid

class PrimsMaze(MazeGenerator):
    def generate(self, n):
        w = 2 * n + 1
        grid = [[1 for _ in range(w)] for _ in range(w)]
        start = (1,1)
        grid[start[1]][start[0]] = 0
        walls = []
        def add_walls(x,y):
            for dx, dy in [(2,0),(-2,0),(0,2),(0,-2)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < w and 0 < ny < w and grid[ny][nx] == 1:
                    walls.append((x + dx//2, y + dy//2, x, y))
        add_walls(*start)
        while walls:
            idx = random.randrange(len(walls))
            wx, wy, px, py = walls.pop(idx)
            dx = wx - px; dy = wy - py
            ox, oy = wx + dx, wy + dy
            if 0 < ox < w and 0 < oy < w and grid[oy][ox] == 1:
                grid[wy][wx] = 0
                grid[oy][ox] = 0
                add_walls(ox, oy)
        return grid

def get_maze_generator(name):
    return PrimsMaze() if name == 'prims' else BacktrackerMaze()