import pygame
import sys
import random
import pickle
import time

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

SCORE_FILE = 'scores.dat'

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake Game')

def load_scores():
    try:
        with open(SCORE_FILE, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return []

def save_scores(scores):
    with open(SCORE_FILE, 'wb') as f:
        pickle.dump(scores, f)

def main():
    clock = pygame.time.Clock()
    scores = load_scores()
    main_menu(scores, clock)

def main_menu(scores, clock):
    while True:
        screen.fill(BLACK)
        draw_text('Змейка', 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text('1. Начало игры', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text('2. Очки', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        draw_text('3. Два игрока', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
        draw_text('4. Выход', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    select_level(scores, clock)
                if event.key == pygame.K_2:
                    show_high_scores(scores, clock)
                if event.key == pygame.K_3:
                    start_two_players(clock)
                if event.key == pygame.K_4:
                    pygame.quit()
                    sys.exit()

def select_level(scores, clock):
    while True:
        screen.fill(BLACK)
        draw_text('Select Level', 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text('1. Easy', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text('2. Medium', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        draw_text('3. Hard', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
        draw_text('4. Back', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    start_game(scores, 'Easy', clock)
                if event.key == pygame.K_2:
                    start_game(scores, 'Medium', clock)
                if event.key == pygame.K_3:
                    start_game(scores, 'Hard', clock)
                if event.key == pygame.K_4:
                    main_menu(scores, clock)

def start_game(scores, difficulty, clock):
    snake = Snake(GREEN)
    food = Food()
    obstacles = []
    if difficulty in ['Medium', 'Hard']:
        obstacles = [Obstacle() for _ in range(5)]
    score = 0
    lives = 3
    pause = False
    start_time = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_scores(scores)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause = not pause
                else:
                    snake.handle_keys(event)

        if not pause:
            snake.move()
            if snake.head_collides_with_food(food):
                score += 10
                snake.grow()
                food.randomize_position()

            if snake.head_collides_with_wall() or snake.head_collides_with_body() or any(snake.head_collides_with_obstacle(obstacle) for obstacle in obstacles):
                lives -= 1
                if lives == 0:
                    elapsed_time = time.time() - start_time
                    save_scores(scores)
                    scores.append((score, difficulty, elapsed_time))
                    game_over(scores, clock)
                else:
                    snake.reset()

            screen.fill(BLACK)
            snake.draw(screen)
            food.draw(screen)
            for obstacle in obstacles:
                obstacle.draw(screen)
            draw_text(f'Score: {score}', 20, SCREEN_WIDTH // 2, 10)
            draw_text(f'Lives: {lives}', 20, SCREEN_WIDTH // 2, 30)
            elapsed_time = time.time() - start_time
            draw_text(f'Time: {int(elapsed_time)}s', 20, SCREEN_WIDTH // 2, 50)
            pygame.display.flip()
            clock.tick(FPS + difficulty_to_speed(difficulty))
        else:
            screen.fill(BLACK)
            snake.draw(screen)
            food.draw(screen)
            for obstacle in obstacles:
                obstacle.draw(screen)
            draw_text(f'Score: {score}', 20, SCREEN_WIDTH // 2, 10)
            draw_text(f'Lives: {lives}', 20, SCREEN_WIDTH // 2, 30)
            draw_text(f'Time: {int(elapsed_time)}s', 20, SCREEN_WIDTH // 2, 50)
            draw_text('Пауза', 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            pygame.display.flip()

def start_two_players(clock):
    snake1 = Snake(GREEN, [(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)])
    snake2 = Snake(BLUE, [(3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)])
    food = Food()
    obstacles = [Obstacle() for _ in range(5)]
    score1 = 0
    score2 = 0
    pause = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause = not pause
                else:
                    snake1.handle_keys(event, player=1)
                    snake2.handle_keys(event, player=2)

        if not pause:
            snake1.move()
            snake2.move()

            if snake1.head_collides_with_food(food):
                score1 += 10
                snake1.grow()
                food.randomize_position()
            if snake2.head_collides_with_food(food):
                score2 += 10
                snake2.grow()
                food.randomize_position()

            if (snake1.head_collides_with_wall() or snake1.head_collides_with_body() or
                any(snake1.head_collides_with_obstacle(obstacle) for obstacle in obstacles) or
                snake1.positions[0] == snake2.positions[0]):
                game_over_two_players(clock, score1, score2)

            if (snake2.head_collides_with_wall() or snake2.head_collides_with_body() or
                any(snake2.head_collides_with_obstacle(obstacle) for obstacle in obstacles)):
                game_over_two_players(clock, score1, score2)

            screen.fill(BLACK)
            snake1.draw(screen)
            snake2.draw(screen)
            food.draw(screen)
            for obstacle in obstacles:
                obstacle.draw(screen)
            draw_text(f'Player 1 Score: {score1}', 20, SCREEN_WIDTH // 4, 10)
            draw_text(f'Player 2 Score: {score2}', 20, 3 * SCREEN_WIDTH // 4, 10)
            pygame.display.flip()
            clock.tick(FPS + difficulty_to_speed('Medium'))
        else:
            screen.fill(BLACK)
            snake1.draw(screen)
            snake2.draw(screen)
            food.draw(screen)
            for obstacle in obstacles:
                obstacle.draw(screen)
            draw_text(f'Player 1 Score: {score1}', 20, SCREEN_WIDTH // 4, 10)
            draw_text(f'Player 2 Score: {score2}', 20, 3 * SCREEN_WIDTH // 4, 10)
            draw_text('Пауза', 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            pygame.display.flip()

def game_over(scores, clock):
    while True:
        screen.fill(BLACK)
        draw_text('Конец игры', 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text('Press any key to return to menu', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                main_menu(scores, clock)

def game_over_two_players(clock, score1, score2):
    while True:
        screen.fill(BLACK)
        draw_text('Game Over', 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text(f'Player 1 Score: {score1}', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(f'Player 2 Score: {score2}', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        draw_text('Press any key to return to menu', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                main_menu([], clock)

def show_high_scores(scores, clock):
    while True:
        screen.fill(BLACK)
        draw_text('High Scores', 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        for idx, (score, difficulty, elapsed_time) in enumerate(sorted(scores, key=lambda x: x[0], reverse=True)[:10]):
            draw_text(f'{idx + 1}. {score} ({difficulty}) - {int(elapsed_time)}s', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 40 + idx * 30)
        draw_text('Press any key to return to menu', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                main_menu(scores, clock)

def draw_text(text, size, x, y):
    font = pygame.font.Font(None, size)
    surface = font.render(text, True, WHITE)
    rect = surface.get_rect()
    rect.midtop = (x, y)
    screen.blit(surface, rect)

def difficulty_to_speed(difficulty):
    if difficulty == 'Easy':
        return 0
    elif difficulty == 'Medium':
        return 5
    elif difficulty == 'Hard':
        return 10

class Snake:
    def __init__(self, color, initial_positions=None):
        self.positions = initial_positions if initial_positions else [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        self.grow_flag = False
        self.color = color

    def reset(self):
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        self.grow_flag = False

    def handle_keys(self, event, player=1):
        if player == 1:
            if event.key == pygame.K_UP:
                self.direction = (0, -1)
            elif event.key == pygame.K_DOWN:
                self.direction = (0, 1)
            elif event.key == pygame.K_LEFT:
                self.direction = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.direction = (1, 0)
        else:
            if event.key == pygame.K_w:
                self.direction = (0, -1)
            elif event.key == pygame.K_s:
                self.direction = (0, 1)
            elif event.key == pygame.K_a:
                self.direction = (-1, 0)
            elif event.key == pygame.K_d:
                self.direction = (1, 0)

    def move(self):
        cur = self.positions[0]
        x, y = self.direction
        new = (((cur[0] + (x * GRID_SIZE)) % SCREEN_WIDTH), (cur[1] + (y * GRID_SIZE)) % SCREEN_HEIGHT)
        if new in self.positions[2:]:
            self.reset()
        else:
            self.positions.insert(0, new)
            if not self.grow_flag:
                self.positions.pop()
            self.grow_flag = False

    def head_collides_with_food(self, food):
        return self.positions[0] == food.position

    def head_collides_with_wall(self):
        head = self.positions[0]
        return head[0] < 0 or head[0] >= SCREEN_WIDTH or head[1] < 0 or head[1] >= SCREEN_HEIGHT

    def head_collides_with_body(self):
        return len(self.positions) != len(set(self.positions))

    def head_collides_with_obstacle(self, obstacle):
        return self.positions[0] == obstacle.position

    def grow(self):
        self.grow_flag = True

    def draw(self, surface):
        for p in self.positions:
            r = pygame.Rect((p[0], p[1]), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.rect(surface, BLACK, r, 1)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1) * GRID_SIZE, random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

    def draw(self, surface):
        r = pygame.Rect((self.position[0], self.position[1]), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, RED, r)
        pygame.draw.rect(surface, BLACK, r, 1)

class Obstacle:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1) * GRID_SIZE, random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

    def draw(self, surface):
        r = pygame.Rect((self.position[0], self.position[1]), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, GRAY, r)
        pygame.draw.rect(surface, BLACK, r, 1)

if __name__ == '__main__':
    main()
