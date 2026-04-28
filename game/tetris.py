import pygame
import random

# ── Константы тетриса ───────────────────────────────────────────────────────

COLS      = 10      # ширина поля в блоках
ROWS      = 20      # высота поля в блоках
BLOCK     = 22      # размер одного блока в пикселях
FIELD_X   = 120     # x-позиция поля на экране
FIELD_Y   = 20      # y-позиция поля на экране

# Скорость падения: количество кадров между шагами (меньше = быстрее)
SPEEDS = [48, 40, 32, 24, 18, 14, 10, 8, 6, 4]  # уровни 0-9

BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = ( 60,  60,  60)
DGRAY  = ( 30,  30,  30)
LGRAY  = (120, 120, 120)

# ── Фигуры (тетромино) ──────────────────────────────────────────────────────
# Каждая фигура — список поворотов, каждый поворот — список (row, col) клеток

SHAPES = {
    "I": {
        "color": ( 32, 178, 170),   # teal
        "rotations": [
            [(0,0),(0,1),(0,2),(0,3)],
            [(0,0),(1,0),(2,0),(3,0)],
            [(0,0),(0,1),(0,2),(0,3)],
            [(0,0),(1,0),(2,0),(3,0)],
        ]
    },
    "O": {
        "color": (255, 176,   0),   # amber
        "rotations": [
            [(0,0),(0,1),(1,0),(1,1)],
            [(0,0),(0,1),(1,0),(1,1)],
            [(0,0),(0,1),(1,0),(1,1)],
            [(0,0),(0,1),(1,0),(1,1)],
        ]
    },
    "T": {
        "color": (138,  43, 226),   # purple
        "rotations": [
            [(0,0),(0,1),(0,2),(1,1)],
            [(0,0),(1,0),(2,0),(1,1)],
            [(1,0),(1,1),(1,2),(0,1)],
            [(0,1),(1,1),(2,1),(1,0)],
        ]
    },
    "S": {
        "color": ( 50, 205,  50),   # green
        "rotations": [
            [(0,1),(0,2),(1,0),(1,1)],
            [(0,0),(1,0),(1,1),(2,1)],
            [(0,1),(0,2),(1,0),(1,1)],
            [(0,0),(1,0),(1,1),(2,1)],
        ]
    },
    "Z": {
        "color": (220,  50,  50),   # red
        "rotations": [
            [(0,0),(0,1),(1,1),(1,2)],
            [(0,1),(1,0),(1,1),(2,0)],
            [(0,0),(0,1),(1,1),(1,2)],
            [(0,1),(1,0),(1,1),(2,0)],
        ]
    },
    "J": {
        "color": ( 30, 144, 255),   # blue
        "rotations": [
            [(0,0),(1,0),(1,1),(1,2)],
            [(0,0),(0,1),(1,0),(2,0)],
            [(0,0),(0,1),(0,2),(1,2)],
            [(0,1),(1,1),(2,0),(2,1)],
        ]
    },
    "L": {
        "color": (255, 140,   0),   # orange
        "rotations": [
            [(0,2),(1,0),(1,1),(1,2)],
            [(0,0),(1,0),(2,0),(2,1)],
            [(0,0),(0,1),(0,2),(1,0)],
            [(0,0),(0,1),(1,1),(2,1)],
        ]
    },
}

SHAPE_KEYS = list(SHAPES.keys())


# ── Класс падающей фигуры ───────────────────────────────────────────────────

class Piece:
    def __init__(self, key: str):
        self.key      = key
        self.color    = SHAPES[key]["color"]
        self.rotation = 0
        self.row      = 0
        self.col      = COLS // 2 - 2   # по центру поля

    def cells(self, row=None, col=None, rotation=None) -> list[tuple]:
        """Возвращает абсолютные координаты (row, col) для всех клеток фигуры."""
        r = self.row      if row      is None else row
        c = self.col      if col      is None else col
        rot = self.rotation if rotation is None else rotation
        return [(r + dr, c + dc)
                for dr, dc in SHAPES[self.key]["rotations"][rot % 4]]

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4


class TetrisGame:
    """
    Вписывается в систему экранов main.py.
    Интерфейс: handle(event), update(), draw(), done (bool)
    """

    def __init__(self, screen, fonts, records: dict, draw_pixel_text_fn):
        self.screen    = screen
        self.fonts     = fonts
        self.records   = records
        self._dpt      = draw_pixel_text_fn   # утилита из main.py
        self.done      = False

        self._init_game()

    # ── Инициализация / сброс ───────────────────────────────────────────────

    def _init_game(self):
        # Поле: ROWS строк × COLS столбцов; 0 = пусто, иначе цвет (r,g,b)
        self.field: list[list] = [[0] * COLS for _ in range(ROWS)]

        self.score    = 0
        self.lines    = 0        # всего убрано линий
        self.level    = 0
        self.paused   = False
        self.game_over= False

        self._fall_timer = 0     # счётчик кадров для падения
        self._lock_timer = 0     # задержка перед фиксацией (wall kick ощущение)
        self._das_timer  = 0     # delayed auto-shift (зажатая клавиша)
        self._das_dir    = 0     # -1 влево, 1 вправо

        self._piece      = self._new_piece()
        self._next_piece = self._new_piece()

        # ghost (тень куда упадёт)
        self._ghost_row  = 0
        self._update_ghost()

        # анимация убранных линий
        self._flash_lines  = []   # какие строки мигают
        self._flash_timer  = 0

    def _new_piece(self) -> Piece:
        return Piece(random.choice(SHAPE_KEYS))

    # ── Вспомогательные методы поля ────────────────────────────────────────

    def _valid(self, piece: Piece, row=None, col=None, rotation=None) -> bool:
        """Проверяет, что позиция допустима (не выходит за пределы и не перекрывает)."""
        for r, c in piece.cells(row, col, rotation):
            if c < 0 or c >= COLS:
                return False
            if r >= ROWS:
                return False
            if r >= 0 and self.field[r][c]:
                return False
        return True

    def _lock_piece(self):
        """Фиксирует текущую фигуру на поле."""
        for r, c in self._piece.cells():
            if r >= 0:
                self.field[r][c] = self._piece.color
        self._clear_lines()
        self._piece      = self._next_piece
        self._next_piece = self._new_piece()
        self._update_ghost()
        self._fall_timer = 0
        self._lock_timer = 0

        # проверка game over: новая фигура уже перекрывает что-то
        if not self._valid(self._piece):
            self.game_over = True

    def _clear_lines(self):
        """Убирает заполненные строки, начисляет очки."""
        full = [r for r in range(ROWS) if all(self.field[r])]
        if not full:
            return

        self._flash_lines = full
        self._flash_timer = 12   # кадров мигания

        # Убираем строки и добавляем пустые сверху
        for r in full:
            del self.field[r]
            self.field.insert(0, [0] * COLS)

        n = len(full)
        self.lines += n

        # Стандартная таблица очков Tetris (Guideline)
        pts = [0, 100, 300, 500, 800][n] * (self.level + 1)
        self.score += pts

        # Обновляем рекорд
        if self.score > self.records.get("tetris", 0):
            self.records["tetris"] = self.score

        # Повышение уровня каждые 10 линий
        self.level = min(self.lines // 10, 9)

    def _update_ghost(self):
        """Находит строку куда упадёт фигура."""
        r = self._piece.row
        while self._valid(self._piece, row=r + 1):
            r += 1
        self._ghost_row = r

    # ── Управление ─────────────────────────────────────────────────────────

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
                return

            if self.game_over:
                if event.key == pygame.K_r:
                    self._init_game()
                return

            if event.key == pygame.K_p:
                self.paused = not self.paused
                return

            if self.paused:
                return

            if event.key == pygame.K_LEFT:
                self._move(-1)
                self._das_dir   = -1
                self._das_timer = 0
            elif event.key == pygame.K_RIGHT:
                self._move(1)
                self._das_dir   = 1
                self._das_timer = 0
            elif event.key == pygame.K_UP or event.key == pygame.K_x:
                self._try_rotate()
            elif event.key == pygame.K_DOWN:
                self._soft_drop()
            elif event.key == pygame.K_SPACE:
                self._hard_drop()
            elif event.key == pygame.K_z:
                self._try_rotate(ccw=True)

        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self._das_dir = 0

    def _move(self, dx: int):
        new_col = self._piece.col + dx
        if self._valid(self._piece, col=new_col):
            self._piece.col = new_col
            self._update_ghost()

    def _try_rotate(self, ccw=False):
        rot = (self._piece.rotation + (3 if ccw else 1)) % 4
        # Wall kick: пробуем сдвиги 0, ±1, ±2
        for kick in [0, -1, 1, -2, 2]:
            if self._valid(self._piece,
                           col=self._piece.col + kick,
                           rotation=rot):
                self._piece.col      += kick
                self._piece.rotation  = rot
                self._update_ghost()
                return

    def _soft_drop(self):
        if self._valid(self._piece, row=self._piece.row + 1):
            self._piece.row += 1
            self._update_ghost()
            self.score += 1
            self._fall_timer = 0

    def _hard_drop(self):
        dropped = self._ghost_row - self._piece.row
        self._piece.row = self._ghost_row
        self.score += dropped * 2
        self._lock_piece()

    # ── Обновление (вызывается каждый кадр) ────────────────────────────────

    def update(self):
        if self.paused or self.game_over:
            return

        # Автоповтор при зажатой клавише (DAS)
        if self._das_dir != 0:
            self._das_timer += 1
            if self._das_timer > 12:   # 12 кадров задержка, потом каждые 3
                if (self._das_timer - 12) % 3 == 0:
                    self._move(self._das_dir)

        # Мигание убранных линий
        if self._flash_timer > 0:
            self._flash_timer -= 1
            return   # во время мигания фигура не падает

        # Гравитация
        speed = SPEEDS[self.level]
        self._fall_timer += 1
        if self._fall_timer >= speed:
            self._fall_timer = 0
            if self._valid(self._piece, row=self._piece.row + 1):
                self._piece.row += 1
                self._update_ghost()
            else:
                self._lock_timer += 1
                if self._lock_timer >= 30:   # 0.5 сек при 60fps
                    self._lock_piece()

    # ── Отрисовка ───────────────────────────────────────────────────────────

    def draw(self):
        s = self.screen
        s.fill(BLACK)

        self._draw_field()
        self._draw_ghost()
        self._draw_piece()
        self._draw_flash()
        self._draw_border()
        self._draw_ui()

        if self.paused:
            self._draw_overlay("PAUSED", "[P] continue  [ESC] menu")
        if self.game_over:
            self._draw_overlay("GAME OVER", f"score: {self.score}  [R] restart  [ESC] menu")

    def _draw_block(self, surf, row, col, color, alpha=255, offset_x=0, offset_y=0):
        """Рисует один блок (пиксельный стиль: блок + рамка + блик)."""
        x = FIELD_X + col * BLOCK + offset_x
        y = FIELD_Y + row * BLOCK + offset_y
        r, g, b = color

        # Основной прямоугольник
        pygame.draw.rect(surf, color, (x, y, BLOCK - 1, BLOCK - 1))
        # Тёмная тень (низ и право)
        dark = (max(r - 60, 0), max(g - 60, 0), max(b - 60, 0))
        pygame.draw.rect(surf, dark, (x, y + BLOCK - 3, BLOCK - 1, 2))
        pygame.draw.rect(surf, dark, (x + BLOCK - 3, y, 2, BLOCK - 1))
        # Светлый блик (верх и лево)
        light = (min(r + 60, 255), min(g + 60, 255), min(b + 60, 255))
        pygame.draw.rect(surf, light, (x, y, BLOCK - 1, 2))
        pygame.draw.rect(surf, light, (x, y, 2, BLOCK - 1))

    def _draw_field(self):
        """Рисует зафиксированные блоки и сетку."""
        # сетка
        for r in range(ROWS):
            for c in range(COLS):
                rx = FIELD_X + c * BLOCK
                ry = FIELD_Y + r * BLOCK
                pygame.draw.rect(self.screen, DGRAY,
                                 (rx, ry, BLOCK - 1, BLOCK - 1))
        # блоки
        for r in range(ROWS):
            if r in self._flash_lines:
                continue  # мигающие строки рисуются отдельно
            for c in range(COLS):
                if self.field[r][c]:
                    self._draw_block(self.screen, r, c, self.field[r][c])

    def _draw_ghost(self):
        """Прозрачная тень куда упадёт фигура."""
        for dr, dc in SHAPES[self._piece.key]["rotations"][self._piece.rotation % 4]:
            r = self._ghost_row + dr
            c = self._piece.col + dc
            if 0 <= r < ROWS and 0 <= c < COLS:
                x = FIELD_X + c * BLOCK
                y = FIELD_Y + r * BLOCK
                color = self._piece.color
                ghost_color = tuple(max(v - 140, 0) for v in color)
                pygame.draw.rect(self.screen, ghost_color,
                                 (x + 2, y + 2, BLOCK - 5, BLOCK - 5))
                pygame.draw.rect(self.screen, color,
                                 (x + 2, y + 2, BLOCK - 5, BLOCK - 5), 1)

    def _draw_piece(self):
        """Рисует падающую фигуру."""
        for r, c in self._piece.cells():
            if r >= 0:
                self._draw_block(self.screen, r, c, self._piece.color)

    def _draw_flash(self):
        """Мигание убранных строк."""
        if self._flash_timer > 0:
            bright = (self._flash_timer % 4 < 2)
            color = WHITE if bright else (200, 200, 200)
            for row in self._flash_lines:
                for c in range(COLS):
                    x = FIELD_X + c * BLOCK
                    y = FIELD_Y + row * BLOCK
                    pygame.draw.rect(self.screen, color,
                                     (x, y, BLOCK - 1, BLOCK - 1))

    def _draw_border(self):
        """Рамка поля."""
        bx = FIELD_X - 3
        by = FIELD_Y - 3
        bw = COLS * BLOCK + 6
        bh = ROWS * BLOCK + 6
        pygame.draw.rect(self.screen, WHITE, (bx, by, bw, bh), 2)

    def _draw_ui(self):
        """Боковая панель: счёт, уровень, следующая фигура."""
        s   = self.screen
        fn  = self.fonts
        px  = FIELD_X + COLS * BLOCK + 20   # x правой панели
        rec = self.records.get("tetris", 0)

        labels = [
            ("SCORE",  str(self.score)),
            ("BEST",   str(rec)),
            ("LEVEL",  str(self.level + 1)),
            ("LINES",  str(self.lines)),
        ]
        for i, (lbl, val) in enumerate(labels):
            y = 30 + i * 60
            self._dpt(s, fn["small"], lbl,  px, y,      (150, 150, 150))
            self._dpt(s, fn["med"],   val,  px, y + 18, WHITE)

        # Следующая фигура
        self._dpt(s, fn["small"], "NEXT", px, 270, (150, 150, 150))
        preview_x = px
        preview_y = 290
        rotations = SHAPES[self._next_piece.key]["rotations"][0]
        min_r = min(dr for dr, dc in rotations)
        min_c = min(dc for dr, dc in rotations)
        for dr, dc in rotations:
            x = preview_x + (dc - min_c) * BLOCK
            y = preview_y + (dr - min_r) * BLOCK
            r, g, b = self._next_piece.color
            pygame.draw.rect(s, self._next_piece.color,
                             (x, y, BLOCK - 1, BLOCK - 1))
            light = (min(r+60,255), min(g+60,255), min(b+60,255))
            pygame.draw.rect(s, light, (x, y, BLOCK-1, 2))
            pygame.draw.rect(s, light, (x, y, 2, BLOCK-1))

        # Управление
        ctrl_y = 390
        for line in ["↑/X rotate", "↓  soft drop", "SPC hard drop",
                     "Z  rotate ↺", "P  pause", "ESC menu"]:
            self._dpt(s, fn["small"], line, px, ctrl_y, (80, 80, 80))
            ctrl_y += 14

    def _draw_overlay(self, title: str, subtitle: str):
        """Полупрозрачный оверлей для PAUSE / GAME OVER."""
        overlay = pygame.Surface(
            (COLS * BLOCK + 6, ROWS * BLOCK + 6), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (FIELD_X - 3, FIELD_Y - 3))

        cx = FIELD_X + (COLS * BLOCK) // 2
        tw = self.fonts["big"].size(title)[0]
        self._dpt(self.screen, self.fonts["big"],
                  title, cx - tw // 2, FIELD_Y + 140, WHITE)
        sw2 = self.fonts["small"].size(subtitle)[0]
        self._dpt(self.screen, self.fonts["small"],
                  subtitle, cx - sw2 // 2, FIELD_Y + 195, LGRAY)