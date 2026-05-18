import pygame
import random

SCREEN_W, SCREEN_H = 640, 480

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
DGRAY = (30, 30, 30)

AMBER = (255, 176, 0)
GREEN = (50, 205, 50)
RED = (220, 50, 50)

GRID_SIZE = 9
CELL_SIZE = 40

GRID_X = 140
GRID_Y = 60


PUZZLES = [
    {
        "board": [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
    },

    {
        "board": [
            [0, 2, 0, 6, 0, 8, 0, 0, 0],
            [5, 8, 0, 0, 0, 9, 7, 0, 0],
            [0, 0, 0, 0, 4, 0, 0, 0, 0],
            [3, 7, 0, 0, 0, 0, 5, 0, 0],
            [6, 0, 0, 0, 0, 0, 0, 0, 4],
            [0, 0, 8, 0, 0, 0, 0, 1, 3],
            [0, 0, 0, 0, 2, 0, 0, 0, 0],
            [0, 0, 9, 8, 0, 0, 0, 3, 6],
            [0, 0, 0, 3, 0, 6, 0, 9, 0],
        ]
    },

    {
        "board": [
            [0, 0, 0, 2, 6, 0, 7, 0, 1],
            [6, 8, 0, 0, 7, 0, 0, 9, 0],
            [1, 9, 0, 0, 0, 4, 5, 0, 0],
            [8, 2, 0, 1, 0, 0, 0, 4, 0],
            [0, 0, 4, 6, 0, 2, 9, 0, 0],
            [0, 5, 0, 0, 0, 3, 0, 2, 8],
            [0, 0, 9, 3, 0, 0, 0, 7, 4],
            [0, 4, 0, 0, 5, 0, 0, 3, 6],
            [7, 0, 3, 0, 1, 8, 0, 0, 0],
        ]
    }
]


class SudokuGame:
    def __init__(self, screen, fonts, records, draw_pixel_text):
        self.screen = screen
        self.fonts = fonts
        self.records = records
        self.draw_pixel_text = draw_pixel_text

        self.done = False
        self.game_over = False
        self.win = False

        self.selected = None

        puzzle = random.choice(PUZZLES)

        self.board = [row[:] for row in puzzle["board"]]

        self.fixed = []

        for row in range(9):
            for col in range(9):
                if self.board[row][col] != 0:
                    self.fixed.append((row, col))

    def handle(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                self.done = True

            if self.game_over:
                return

            if self.selected:
                row, col = self.selected

                if (row, col) not in self.fixed:

                    if event.unicode in "123456789":
                        value = int(event.unicode)
                        self.board[row][col] = value

                        if self.check_win():
                            self.win = True
                            self.game_over = True

                            self.records["sudoku"] = (
                                self.records.get("sudoku", 0) + 1
                            )

                    elif event.key in (
                        pygame.K_BACKSPACE,
                        pygame.K_DELETE
                    ):
                        self.board[row][col] = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if (
                GRID_X <= mx < GRID_X + GRID_SIZE * CELL_SIZE
                and
                GRID_Y <= my < GRID_Y + GRID_SIZE * CELL_SIZE
            ):

                col = (mx - GRID_X) // CELL_SIZE
                row = (my - GRID_Y) // CELL_SIZE

                self.selected = (row, col)

    def update(self):
        pass

    def is_valid_move(self, row, col, value):

        if value == 0:
            return True

        for c in range(9):
            if c != col and self.board[row][c] == value:
                return False

        for r in range(9):
            if r != row and self.board[r][col] == value:
                return False

        box_row = (row // 3) * 3
        box_col = (col // 3) * 3

        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):

                if (
                    (r, c) != (row, col)
                    and
                    self.board[r][c] == value
                ):
                    return False

        return True

    def check_win(self):

        for row in range(9):
            for col in range(9):

                value = self.board[row][col]

                if value == 0:
                    return False

                if not self.is_valid_move(row, col, value):
                    return False

        return True

    def draw_grid(self):

        for row in range(9):
            for col in range(9):

                x = GRID_X + col * CELL_SIZE
                y = GRID_Y + row * CELL_SIZE

                rect = pygame.Rect(
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                )

                pygame.draw.rect(
                    self.screen,
                    DGRAY,
                    rect
                )

                pygame.draw.rect(
                    self.screen,
                    WHITE,
                    rect,
                    1
                )

                if self.selected == (row, col):
                    pygame.draw.rect(
                        self.screen,
                        AMBER,
                        rect,
                        3
                    )

                value = self.board[row][col]

                if value != 0:

                    color = WHITE

                    if (row, col) in self.fixed:
                        color = GREEN

                    if not self.is_valid_move(row, col, value):
                        color = RED

                    self.draw_pixel_text(
                        self.screen,
                        self.fonts["med"],
                        str(value),
                        x + 12,
                        y + 8,
                        color
                    )

        for i in range(10):

            width = 3 if i % 3 == 0 else 1

            pygame.draw.line(
                self.screen,
                WHITE,
                (GRID_X + i * CELL_SIZE, GRID_Y),
                (GRID_X + i * CELL_SIZE,
                 GRID_Y + GRID_SIZE * CELL_SIZE),
                width
            )

            pygame.draw.line(
                self.screen,
                WHITE,
                (GRID_X, GRID_Y + i * CELL_SIZE),
                (GRID_X + GRID_SIZE * CELL_SIZE,
                 GRID_Y + i * CELL_SIZE),
                width
            )

    def draw_ui(self):

        self.draw_pixel_text(
            self.screen,
            self.fonts["big"],
            "SUDOKU",
            200,
            10,
            AMBER
        )

        self.draw_pixel_text(
            self.screen,
            self.fonts["small"],
            "Click cell and press number keys",
            170,
            440,
            GRAY
        )

        self.draw_pixel_text(
            self.screen,
            self.fonts["small"],
            "ESC - back to menu",
            10,
            10,
            GRAY
        )

    def draw_overlay(self, title, color):

        overlay = pygame.Surface(
            (SCREEN_W, SCREEN_H),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 180))

        self.screen.blit(overlay, (0, 0))

        self.draw_pixel_text(
            self.screen,
            self.fonts["big"],
            title,
            180,
            200,
            color
        )

        self.draw_pixel_text(
            self.screen,
            self.fonts["small"],
            "Press ESC to return",
            220,
            260,
            WHITE
        )

    def draw(self):

        self.screen.fill(BLACK)

        self.draw_grid()
        self.draw_ui()

        if self.win:
            self.draw_overlay(
                "YOU WIN!",
                GREEN
            )