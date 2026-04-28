import pygame
import sys
import json
import os

from snake import SnakeGame
from tetris import TetrisGame    

SCREEN_W, SCREEN_H = 640, 480
FPS = 60
TITLE = "Pixel Arcade"

BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (100, 100, 100)
DGRAY  = ( 30,  30,  30)
PURPLE = (138,  43, 226)
TEAL   = ( 32, 178, 170)
AMBER  = (255, 176,   0)
GREEN  = ( 50, 205,  50)
RED    = (220,  50,  50)

SAVES_FILE = "saves/records.json"


# ── Утилиты ────────────────────────────────────────────────

def load_records() -> dict:
    os.makedirs("saves", exist_ok=True)
    if os.path.exists(SAVES_FILE):
        with open(SAVES_FILE) as f:
            return json.load(f)
    return {"snake": 0, "tetris": 0, "minesweeper": 0, "sudoku": 0}


def save_records(records: dict) -> None:
    os.makedirs("saves", exist_ok=True)
    with open(SAVES_FILE, "w") as f:
        json.dump(records, f, indent=2)


def draw_pixel_text(surface, font, text, x, y, color=WHITE, shadow=True):
    if shadow:
        s = font.render(text, False, BLACK)
        surface.blit(s, (x + 2, y + 2))
    rendered = font.render(text, False, color)
    surface.blit(rendered, (x, y))


def draw_pixel_rect(surface, color, rect, border=2):
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, WHITE, rect, border)


# ── Меню ───────────────────────────────────────────────────

class MenuItem:
    def __init__(self, label: str, key: str, color):
        self.label   = label
        self.key     = key
        self.color   = color
        self.hovered = False

    def draw(self, surface, font, x, y, w=260, h=44):
        bg   = self.color if self.hovered else DGRAY
        rect = pygame.Rect(x, y, w, h)
        draw_pixel_rect(surface, bg, rect, border=2)
        lbl  = f"> {self.label}" if self.hovered else f"  {self.label}"
        draw_pixel_text(surface, font, lbl, x + 12, y + 10, WHITE)

    def hit(self, mx, my, x, y, w=260, h=44) -> bool:
        return pygame.Rect(x, y, w, h).collidepoint(mx, my)


class MenuScreen:
    ITEMS = [
        MenuItem("[Snake]",       "snake",       TEAL),
        MenuItem("[Tetris]",      "tetris",      PURPLE),
        MenuItem("[Minesweeper]", "minesweeper", RED),
        MenuItem("[Sudoku]",      "sudoku",      AMBER),
    ]

    def __init__(self, screen, fonts, records):
        self.screen   = screen
        self.fonts    = fonts
        self.records  = records
        self.selected = None

    def handle(self, event):
        mx, my = pygame.mouse.get_pos()
        ox, oy = 190, 180
        for i, item in enumerate(self.ITEMS):
            item.hovered = item.hit(mx, my, ox, oy + i * 60)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if item.hovered:
                    self.selected = item.key
            if event.type == pygame.KEYDOWN:
                keys = {"1": 0, "2": 1, "3": 2, "4": 3}
                idx  = keys.get(pygame.key.name(event.key))
                if idx is not None:
                    self.selected = self.ITEMS[idx].key

    def draw(self):
        s = self.screen
        s.fill(GRAY)

        draw_pixel_text(s, self.fonts["big"],   "PIXEL ARCADE", 152, 40, AMBER)
        draw_pixel_text(s, self.fonts["small"], "choose a game:", 210, 110, WHITE)

        ox, oy = 190, 180
        for i, item in enumerate(self.ITEMS):
            item.draw(s, self.fonts["med"], ox, oy + i * 60)
            rec = self.records.get(item.key, 0)
            if rec:
                draw_pixel_text(s, self.fonts["small"],
                                f"best: {rec}", ox + 270, oy + i * 60 + 14, GRAY)

        draw_pixel_text(s, self.fonts["small"], "[Q] exit", 10, SCREEN_H - 24, GRAY)


# ── Заглушка для игр ещё не реализованных ──────────────────

class PlaceholderGame:
    COLORS = {"minesweeper": RED, "sudoku": AMBER}
    NAMES  = {"minesweeper": "MINESWEEPER", "sudoku": "SUDOKU"}

    def __init__(self, screen, fonts, key):
        self.screen = screen
        self.fonts  = fonts
        self.key    = key
        self.done   = False
        self.color  = self.COLORS.get(key, WHITE)
        self.name   = self.NAMES.get(key, key.upper())
        self._t     = 0

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.done = True

    def update(self):
        self._t += 1

    def draw(self):
        s = self.screen
        s.fill(BLACK)
        if (self._t // 20) % 2 == 0:
            draw_pixel_text(s, self.fonts["big"], self.name, 180, 140, self.color)
        draw_pixel_text(s, self.fonts["med"],
                        "Game in development...", 130, 220, GRAY)
        draw_pixel_text(s, self.fonts["small"],
                        "[ESC] or click — back to menu", 150, 300, GRAY)
        pygame.draw.rect(s, self.color, (40, 40, SCREEN_W - 80, SCREEN_H - 80), 3)


# ── Главный цикл ────────────────────────────────────────────

def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    fonts = {
        "big":   pygame.font.SysFont("couriernew", 42, bold=True),
        "med":   pygame.font.SysFont("couriernew", 22, bold=True),
        "small": pygame.font.SysFont("couriernew", 16),
    }

    records = load_records()
    current = MenuScreen(screen, fonts, records)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_records(records)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                if isinstance(current, MenuScreen):
                    save_records(records)
                    pygame.quit()
                    sys.exit()
            current.handle(event)

        # ── Переходы между экранами ──────────────────────────
        if isinstance(current, MenuScreen) and current.selected:
            key = current.selected
            current.selected = None

            if key == "snake":
                current = SnakeGame(screen, fonts, records, draw_pixel_text)
            elif key == "tetris":
                current = TetrisGame(screen, fonts, records, draw_pixel_text)  # ← НОВОЕ
            else:
                current = PlaceholderGame(screen, fonts, key)

        elif hasattr(current, "done") and current.done:
            save_records(records)
            current = MenuScreen(screen, fonts, records)

        # ── Обновление и отрисовка ───────────────────────────
        if not isinstance(current, MenuScreen):
            current.update()

        current.draw()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()