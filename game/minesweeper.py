import pygame
import random
import time

# ─────────────────────────────────────────
# Настройки сложности
# ─────────────────────────────────────────

DIFFICULTIES = {
    "easy": (8, 8, 10),
    "medium": (12, 12, 22),
    "hard": (16, 16, 45)
}

CELL_SIZE = 28

BG = (22, 22, 30)
PANEL = (35, 35, 48)
GRID = (60, 60, 80)

CLOSED = (70, 70, 95)
OPEN = (180, 180, 190)

WHITE = (255, 255, 255)
RED = (220, 60, 60)
GREEN = (60, 220, 120)
YELLOW = (255, 200, 50)

NUMBER_COLORS = {
    1: (100, 180, 255),
    2: (120, 220, 120),
    3: (255, 120, 120),
    4: (180, 120, 255),
    5: (255, 160, 90),
    6: (80, 220, 220),
    7: (255, 255, 255),
    8: (180, 180, 180),
}


class MinesweeperGame:

    def __init__(self, screen, fonts, records, draw_text):

        self.screen = screen
        self.fonts = fonts
        self.records = records
        self.draw_text = draw_text

        self.done = False

        self.state = "menu"

        self.rows = 0
        self.cols = 0
        self.mines = 0

        self.board = []
        self.revealed = []
        self.flags = []

        self.start_time = 0
        self.game_over = False
        self.win = False

    # ─────────────────────────────────────

    def start_game(self, difficulty):

        self.rows, self.cols, self.mines = DIFFICULTIES[difficulty]

        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        self.revealed = [
            [False for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

        self.flags = [
            [False for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

        mines = 0

        while mines < self.mines:

            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)

            if self.board[r][c] != -1:
                self.board[r][c] = -1
                mines += 1

        # числа

        for r in range(self.rows):
            for c in range(self.cols):

                if self.board[r][c] == -1:
                    continue

                count = 0

                for i in range(r - 1, r + 2):
                    for j in range(c - 1, c + 2):

                        if 0 <= i < self.rows and 0 <= j < self.cols:
                            if self.board[i][j] == -1:
                                count += 1

                self.board[r][c] = count

        self.state = "game"

        self.game_over = False
        self.win = False

        self.start_time = time.time()

    # ─────────────────────────────────────

    def reveal(self, row, col):

        if self.flags[row][col]:
            return

        if self.revealed[row][col]:
            return

        self.revealed[row][col] = True

        if self.board[row][col] == 0:

            for i in range(row - 1, row + 2):
                for j in range(col - 1, col + 2):

                    if 0 <= i < self.rows and 0 <= j < self.cols:

                        if not self.revealed[i][j]:
                            self.reveal(i, j)

    # ─────────────────────────────────────

    def check_win(self):

        total = self.rows * self.cols - self.mines

        opened = 0

        for r in range(self.rows):
            for c in range(self.cols):

                if self.revealed[r][c] and self.board[r][c] != -1:
                    opened += 1

        if opened == total:
            self.win = True
            self.game_over = True

    # ─────────────────────────────────────

    def handle(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                self.done = True

        # ───────── MENU ─────────

        if self.state == "menu":

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:
                    self.start_game("easy")

                elif event.key == pygame.K_2:
                    self.start_game("medium")

                elif event.key == pygame.K_3:
                    self.start_game("hard")

        # ───────── GAME ─────────

        elif self.state == "game":

            if event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = pygame.mouse.get_pos()

                board_w = self.cols * CELL_SIZE
                board_h = self.rows * CELL_SIZE

                start_x = (640 - board_w) // 2
                start_y = (480 - board_h) // 2

                col = (mx - start_x) // CELL_SIZE
                row = (my - start_y) // CELL_SIZE

                if 0 <= row < self.rows and 0 <= col < self.cols:

                    # ЛКМ
                    if event.button == 1:

                        if not self.flags[row][col]:

                            if self.board[row][col] == -1:

                                self.game_over = True

                                for r in range(self.rows):
                                    for c in range(self.cols):
                                        self.revealed[r][c] = True

                            else:
                                self.reveal(row, col)

                    # ПКМ
                    elif event.button == 3:

                        if not self.revealed[row][col]:
                            self.flags[row][col] = not self.flags[row][col]

                    self.check_win()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r and self.game_over:
                    self.state = "menu"

    # ─────────────────────────────────────

    def update(self):
        pass

    # ─────────────────────────────────────

    def draw_menu(self):

        self.screen.fill(BG)

        self.draw_text(
            self.screen,
            self.fonts["big"],
            "MINESWEEPER",
            150,
            70,
            RED
        )

        pygame.draw.rect(
            self.screen,
            PANEL,
            (150, 150, 340, 180),
            border_radius=10
        )

        self.draw_text(
            self.screen,
            self.fonts["med"],
            "[1] EASY 8x8",
            220,
            180,
            GREEN
        )

        self.draw_text(
            self.screen,
            self.fonts["med"],
            "[2] MEDIUM 12x12",
            190,
            230,
            YELLOW
        )

        self.draw_text(
            self.screen,
            self.fonts["med"],
            "[3] HARD 16x16",
            205,
            280,
            RED
        )

    # ─────────────────────────────────────

    def draw_game(self):

        self.screen.fill(BG)

        board_w = self.cols * CELL_SIZE
        board_h = self.rows * CELL_SIZE

        start_x = (640 - board_w) // 2
        start_y = (480 - board_h) // 2

        # панель

        pygame.draw.rect(
            self.screen,
            PANEL,
            (
                start_x - 10,
                start_y - 10,
                board_w + 20,
                board_h + 20
            ),
            border_radius=12
        )

        # клетки

        for r in range(self.rows):
            for c in range(self.cols):

                rect = pygame.Rect(
                    start_x + c * CELL_SIZE,
                    start_y + r * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )

                value = self.board[r][c]

                # открытая
                if self.revealed[r][c]:

                    pygame.draw.rect(self.screen, OPEN, rect)

                    if value == -1:

                        pygame.draw.circle(
                            self.screen,
                            RED,
                            rect.center,
                            8
                        )

                    elif value > 0:

                        text = self.fonts["small"].render(
                            str(value),
                            True,
                            NUMBER_COLORS[value]
                        )

                        self.screen.blit(
                            text,
                            (
                                rect.x + 10,
                                rect.y + 5
                            )
                        )

                # закрытая
                else:

                    pygame.draw.rect(self.screen, CLOSED, rect)

                    if self.flags[r][c]:

                        pygame.draw.polygon(
                            self.screen,
                            YELLOW,
                            [
                                (rect.x + 8, rect.y + 6),
                                (rect.x + 22, rect.y + 12),
                                (rect.x + 8, rect.y + 18)
                            ]
                        )

                        pygame.draw.line(
                            self.screen,
                            WHITE,
                            (rect.x + 8, rect.y + 6),
                            (rect.x + 8, rect.y + 22),
                            2
                        )

                pygame.draw.rect(
                    self.screen,
                    GRID,
                    rect,
                    1
                )

        # таймер

        timer = int(time.time() - self.start_time)

        self.draw_text(
            self.screen,
            self.fonts["small"],
            f"TIME: {timer}",
            20,
            20,
            WHITE
        )

        self.draw_text(
            self.screen,
            self.fonts["small"],
            "LMB - OPEN | RMB - FLAG",
            20,
            50,
            WHITE
        )

        # проигрыш

        if self.game_over and not self.win:

            self.draw_text(
                self.screen,
                self.fonts["big"],
                "GAME OVER",
                170,
                20,
                RED
            )

            self.draw_text(
                self.screen,
                self.fonts["small"],
                "[R] back to menu",
                240,
                60,
                WHITE
            )

        # победа

        if self.win:

            self.draw_text(
                self.screen,
                self.fonts["big"],
                "YOU WIN!",
                200,
                20,
                GREEN
            )

            self.draw_text(
                self.screen,
                self.fonts["small"],
                "[R] back to menu",
                240,
                60,
                WHITE
            )

    # ─────────────────────────────────────

    def draw(self):

        if self.state == "menu":
            self.draw_menu()

        elif self.state == "game":
            self.draw_game()

            