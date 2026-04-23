import pygame
import random

# Импортируем константы из основного файла (или определяем их здесь)
# Для простоты определим размеры, которые нужны змейке
SCREEN_W, SCREEN_H = 640, 480
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (220, 50, 50)
GREEN = (50, 205, 50)
TEAL  = (32, 178, 170)
AMBER = (255, 176, 0)

class SnakeGame:
    def __init__(self, screen, fonts, records, draw_pixel_text):
        self.screen = screen
        self.fonts = fonts
        self.records = records
        self.draw_pixel_text = draw_pixel_text # Передаем функцию отрисовки текста
        self.done = False
        
        self.block_size = 20
        self.snake = [(320, 240), (300, 240), (280, 240)]
        self.direction = pygame.K_RIGHT
        self.next_direction = pygame.K_RIGHT
        
        self.food = self._spawn_food()
        self.score = 0
        self.game_over = False
        
        self.move_delay = 100 
        self.last_move_time = pygame.time.get_ticks()

    def _spawn_food(self):
        while True:
            x = random.randrange(40, SCREEN_W - 60, self.block_size)
            y = random.randrange(40, SCREEN_H - 60, self.block_size)
            if (x, y) not in self.snake:
                return (x, y)

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_over:
                self.done = True
            
            if event.key == pygame.K_UP and self.direction != pygame.K_DOWN:
                self.next_direction = event.key
            elif event.key == pygame.K_DOWN and self.direction != pygame.K_UP:
                self.next_direction = event.key
            elif event.key == pygame.K_LEFT and self.direction != pygame.K_RIGHT:
                self.next_direction = event.key
            elif event.key == pygame.K_RIGHT and self.direction != pygame.K_LEFT:
                self.next_direction = event.key
            elif event.key == pygame.K_ESCAPE:
                self.done = True

    def update(self):
        if self.game_over:
            return

        now = pygame.time.get_ticks()
        if now - self.last_move_time > self.move_delay:
            self.last_move_time = now
            self.direction = self.next_direction
            
            head_x, head_y = self.snake[0]
            if self.direction == pygame.K_UP: head_y -= self.block_size
            if self.direction == pygame.K_DOWN: head_y += self.block_size
            if self.direction == pygame.K_LEFT: head_x -= self.block_size
            if self.direction == pygame.K_RIGHT: head_x += self.block_size
            
            new_head = (head_x, head_y)

            if (head_x < 40 or head_x >= SCREEN_W - 40 or 
                head_y < 40 or head_y >= SCREEN_H - 40 or 
                new_head in self.snake):
                self.game_over = True
                if self.score > self.records.get("snake", 0):
                    self.records["snake"] = self.score
                return

            self.snake.insert(0, new_head)

            if new_head == self.food:
                self.score += 10
                self.food = self._spawn_food()
                if self.move_delay > 50: self.move_delay -= 1
            else:
                self.snake.pop()

    def draw(self):
        s = self.screen
        s.fill(BLACK)
        pygame.draw.rect(s, TEAL, (40, 40, SCREEN_W - 80, SCREEN_H - 80), 2)
        pygame.draw.rect(s, RED, (*self.food, self.block_size-2, self.block_size-2))
        
        for i, (x, y) in enumerate(self.snake):
            color = GREEN if i == 0 else TEAL
            pygame.draw.rect(s, color, (x, y, self.block_size - 2, self.block_size - 2))

        self.draw_pixel_text(s, self.fonts["small"], f"SCORE: {self.score}", 50, 15, AMBER)
        
        if self.game_over:
            self.draw_pixel_text(s, self.fonts["big"], "GAME OVER", 200, 180, RED)
            self.draw_pixel_text(s, self.fonts["small"], "Press any key to menu", 220, 240, WHITE)