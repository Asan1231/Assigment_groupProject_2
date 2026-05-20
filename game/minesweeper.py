import pygame
import random
import time

#Difficulty Settings
DIFFICULTIES = {
    "easy": (8, 8, 10),
    "medium": (12, 12, 22),
    "hard": (16, 16, 45)
}

# Cell size in pixels
CELL_SIZE = 28

# Colors of the game
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

# class MinesweeperGame: that implements the Minesweeper game logic and rendering

class MinesweeperGame:

    # constructor that called when the game is selected from the menu

    def __init__(self, screen, fonts, records, draw_text):    

        self.screen = screen
        self.fonts = fonts
        self.records = records
        self.draw_text = draw_text
        
        
        self.done = False  

        self.state = "menu"

        # size and mine count
        self.rows = 0
        self.cols = 0
        self.mines = 0

        #games massives 
        self.board = []
        self.revealed = []
        self.flags = []

        # timer and game state
        self.start_time = 0
        self.game_over = False
        self.win = False

    #start new game with selected difficulty and initialize the board, revealed and flags arrays, place mines and calculate numbers

    def start_game(self, difficulty):

        self.rows, self.cols, self.mines = DIFFICULTIES[difficulty]
    #create the board (create two-dimensional array) and fill it with zeros (empty cells) and -1 (mines)
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
    #Mine placement 
        while mines < self.mines:

        # randomly select a cell and place a mine
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
        # if the cell does not already contain a mine, place a mine and increment the count
            if self.board[r][c] != -1:
                self.board[r][c] = -1
                mines += 1



        for r in range(self.rows):
            for c in range(self.cols):

                if self.board[r][c] == -1:
                    continue

                count = 0
             #Checking the neighbors 
                for i in range(r - 1, r + 2):
                    for j in range(c - 1, c + 2):

                    #Border check(not to go beyond the array.)
                        if 0 <= i < self.rows and 0 <= j < self.cols:

                            #count the number of mine in neighbors
                            if self.board[i][j] == -1:
                                count += 1

                self.board[r][c] = count

        self.state = "game"

        self.game_over = False
        self.win = False

        self.start_time = time.time()

    # recursive function to reveal cells when player clicks on 0 cell

    def reveal(self, row, col):
     #check flags(You cannot open the cage with the flag )
        if self.flags[row][col]:
            return
     #check opening
        if self.revealed[row][col]:
            return
      #oper the cell and mark it as revealed
        self.revealed[row][col] = True
    
        if self.board[row][col] == 0:
         #if the cell is empty (0), recursively reveal all neighboring cells
            for i in range(row - 1, row + 2):
                for j in range(col - 1, col + 2):

                    if 0 <= i < self.rows and 0 <= j < self.cols:
                                     
                        if not self.revealed[i][j]:
                            self.reveal(i, j)

    # check won condition (if all non-mine cells are revealed) and set win and game_over flags accordingly

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

    #Processes: keyboard, mouse

    def handle(self, event):

        if event.type == pygame.KEYDOWN:
         #Exit to menu
            if event.key == pygame.K_ESCAPE:
                self.done = True

        #menu 

        if self.state == "menu":

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:
                    self.start_game("easy")

                elif event.key == pygame.K_2:
                    self.start_game("medium")

                elif event.key == pygame.K_3:
                    self.start_game("hard")

    

        elif self.state == "game":
           #handle mouse clicks for openning cells, flag, and restart game after win or lose
            if event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = pygame.mouse.get_pos()

                board_w = self.cols * CELL_SIZE
                board_h = self.rows * CELL_SIZE
             #center the board on the screen
                start_x = (640 - board_w) // 2
                start_y = (480 - board_h) // 2
             #Converting pixels to a cell
                col = (mx - start_x) // CELL_SIZE
                row = (my - start_y) // CELL_SIZE

                if 0 <= row < self.rows and 0 <= col < self.cols:

                    # left mouse button
                    if event.button == 1:

                        if not self.flags[row][col]:
                           #if cell a mine, open all cells and set game_over flag
                            if self.board[row][col] == -1:

                                self.game_over = True

                                for r in range(self.rows):
                                    for c in range(self.cols):
                                        self.revealed[r][c] = True

                            else:
                                self.reveal(row, col)

                    # right mouse button
                    elif event.button == 3:
                      #taggle flag  
                        if not self.revealed[row][col]:
                            self.flags[row][col] = not self.flags[row][col]

                    self.check_win()

            if event.type == pygame.KEYDOWN:
               #r button (back to menu)
                if event.key == pygame.K_r and self.game_over:
                    self.state = "menu"



    def update(self):
        pass

  # draw the menu with difficulty options and game title
    def draw_menu(self):
       #background and title 
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
      #difficulty buttons   
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

    # draw the game board, cells, timer, and game over/win messages

    def draw_game(self):

        self.screen.fill(BG)

        board_w = self.cols * CELL_SIZE
        board_h = self.rows * CELL_SIZE

        start_x = (640 - board_w) // 2
        start_y = (480 - board_h) // 2

    # panel around the board

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

        # draw cells    

        for r in range(self.rows):
            for c in range(self.cols):

                rect = pygame.Rect(
                    start_x + c * CELL_SIZE,
                    start_y + r * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )

                value = self.board[r][c]

                # opened cell
                if self.revealed[r][c]:

                    pygame.draw.rect(self.screen, OPEN, rect)

                    if value == -1:
                      #draw a red circle for mines
                        pygame.draw.circle(
                            self.screen,
                            RED,
                            rect.center,
                            8
                        )

                    elif value > 0:
                      #draw number for non-empty cells
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

                # closed cell
                else:

                    pygame.draw.rect(self.screen, CLOSED, rect)

                    if self.flags[r][c]:
                    #dwaw flag 
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
             #draw grid lines
                pygame.draw.rect(
                    self.screen,
                    GRID,
                    rect,
                    1
                )

        # timer 

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

        # lose condition

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

        # win condition

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



    def draw(self):

        if self.state == "menu":
            self.draw_menu()

        elif self.state == "game":
            self.draw_game()