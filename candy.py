import pygame
import random
import sys

# Ekran boyutları
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

# Yılanın boyutu
BLOCK_SIZE = 15

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Yönler
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Yılan sınıfı
class Snake:
    def __init__(self):
        self.body = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT

    def move(self):
        head = self.body[0]
        x, y = self.direction
        new_head = (head[0] + x * BLOCK_SIZE, head[1] + y * BLOCK_SIZE)
        self.body.insert(0, new_head)
        self.body.pop()

    def grow(self):
        tail = self.body[-1]
        x, y = self.direction
        new_tail = (tail[0] - x * BLOCK_SIZE, tail[1] - y * BLOCK_SIZE)
        self.body.append(new_tail)

    def draw(self, surface):
        for segment in self.body:
            pygame.draw.rect(surface, WHITE, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))

    def collide_with_wall(self):
        head = self.body[0]
        return head[0] < 0 or head[0] >= SCREEN_WIDTH or head[1] < 0 or head[1] >= SCREEN_HEIGHT

    def collide_with_self(self):
        head = self.body[0]
        return any(segment == head for segment in self.body[1:])

    def change_direction(self, direction):
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction

# Yem sınıfı
class Food:
    def __init__(self):
        self.position = self.randomize_position()

    def draw(self, surface):
        pygame.draw.rect(surface, RED, (self.position[0], self.position[1], BLOCK_SIZE, BLOCK_SIZE))

    def randomize_position(self):
        x = random.randint(0, (SCREEN_WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (SCREEN_HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        return x, y

# Oyun
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Game")

    clock = pygame.time.Clock()

    snake = Snake()
    food = Food()

    score = 0
    font = pygame.font.Font(None, 36)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction(UP)
                elif event.key == pygame.K_DOWN:
                    snake.change_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    snake.change_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction(RIGHT)

        snake.move()

        if snake.body[0] == food.position:
            snake.grow()
            food.position = food.randomize_position()
            score += 10

        if snake.collide_with_wall() or snake.collide_with_self():
            pygame.quit()
            sys.exit()

        screen.fill(BLACK)
        snake.draw(screen)
        food.draw(screen)

        text = font.render("Score: " + str(score), True, WHITE)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(10)  # Zorluk ayarı

if __name__ == "__main__":
    main()
