import pygame
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SHIP_SPEED = 5
SPEED_DROP = 2
COLLECTIBLE_VALUE = 1
MULTIPLIER_THRESHOLD = 5
OBSTACLE_COUNT = 10
SHADOW_DROP_SPEED = 1
SHADOW_DURATION = 5000
POWERUP_TYPES = ["speed", "shield"]
LEVEL_DURATION = 30000

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("deep space")

background = pygame.image.load('background.jpeg')
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
background2 = pygame.image.load('background2.jpeg')
background2 = pygame.transform.scale(background2, (SCREEN_WIDTH, SCREEN_HEIGHT))
background3 = pygame.image.load('background3.jpeg')
background3 = pygame.transform.scale(background3, (SCREEN_WIDTH, SCREEN_HEIGHT))
powerup_image = pygame.image.load('powerup.png')
powerup_image = pygame.transform.scale(powerup_image, (30, 30))
player_image = pygame.image.load('player.png')
player_image = pygame.transform.scale(player_image, (50, 30))
obstacle_image = pygame.image.load('pillars.png')
obstacle_image = pygame.transform.scale(obstacle_image, (50, 50))

RED = (255, 0, 0)
BLACK = (0, 0, 0)

class Particle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 5, 5)
        self.lifetime = random.randint(50, 150)
        self.alpha = 255
        self.speed = random.uniform(1, 3)
        self.direction = random.uniform(-0.1, 0.1)

    def update(self):
        self.rect.x -= self.speed
        self.rect.y += self.direction
        self.lifetime -= 1
        self.alpha = max(0, self.alpha - (255 // 50))

    def draw(self, surface):
        if self.alpha > 0:
            particle_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            particle_surface.fill((255, 165, 0, self.alpha))
            surface.blit(particle_surface, self.rect.topleft)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, SCREEN_HEIGHT // 2, 50, 30)
        self.speed = SHIP_SPEED
        self.score = 0
        self.multiplier = 1
        self.collectibles = 0
        self.alive = True
        self.in_shadow = False
        self.shadow_timer = 0
        self.has_shield = False
        self.particles = []

    def update(self):
        if self.in_shadow:
            self.shadow_timer += pygame.time.Clock().get_time()
            if self.shadow_timer >= SHADOW_DURATION:
                self.alive = False
        else:
            self.shadow_timer = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))
        self.update_particles()
        if self.speed > 0:
            self.particles.append(Particle(self.rect.x - 5, self.rect.y + 15))

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def draw_particles(self, surface):
        for particle in self.particles:
            particle.draw(surface)

    def collect(self, collectible):
        self.collectibles += COLLECTIBLE_VALUE
        if collectible.type == "speed":
            self.speed += 2
        elif collectible.type == "shield":
            self.has_shield = True
        if self.collectibles >= MULTIPLIER_THRESHOLD:
            self.multiplier += 1
            self.collectibles = 0

    def collide(self):
        if self.has_shield:
            self.has_shield = False
        else:
            self.alive = False

    def enter_shadow(self):
        self.in_shadow = True
        self.speed = max(0, self.speed - SHADOW_DROP_SPEED)

    def exit_shadow(self):
        self.in_shadow = False
        self.speed = SHIP_SPEED

class Collectible:
    def __init__(self, collectible_type):
        self.rect = pygame.Rect(random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 100), random.randint(0, SCREEN_HEIGHT - 30), 30, 30)
        self.type = collectible_type
        self.speed = random.randint(2, 4)
        self.angle = 0

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < -50:
            self.rect.x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 100)
            self.rect.y = random.randint(0, SCREEN_HEIGHT - 30)
            self.type = random.choice(POWERUP_TYPES)
        self.angle += 5

    def draw(self, surface):
        rotated_image = pygame.transform.rotate(powerup_image, self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, new_rect.topleft)

class Obstacle:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 100), random.randint(0, SCREEN_HEIGHT - 50), 50, 50)
        self.speed = random.randint(3, 7)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < -50:
            self.rect.x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 100)
            self.rect.y = random.randint(0, SCREEN_HEIGHT - 50)
            self.speed = random.randint(3, 7)

def game_over_screen(score):
    font = pygame.font.Font(None, 74)
    text = font.render('Game Over', True, RED)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
    score_text = font.render(f'Score: {int(score)}', True, BLACK)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
    screen.blit(background, (0, 0))
    screen.blit(text, text_rect)
    screen.blit(score_text, score_rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                if event.key == pygame.K_r:
                    main()

def main():
    clock = pygame.time.Clock()
    player = Player()
    collectibles = [Collectible(random.choice(POWERUP_TYPES)) for _ in range(10)]
    obstacles = [Obstacle() for _ in range(OBSTACLE_COUNT)]
    start_time = pygame.time.get_ticks()
    current_background = background
    while player.alive:
        elapsed_time = pygame.time.get_ticks() - start_time
        if elapsed_time >= LEVEL_DURATION and elapsed_time < 2 * LEVEL_DURATION:
            current_background = background2
        elif elapsed_time >= 2 * LEVEL_DURATION:
            current_background = background3
        screen.blit(current_background, (0, 0))
        player.update()
        screen.blit(player_image, player.rect.topleft)
        player.draw_particles(screen)
        for collectible in collectibles:
            collectible.update()
            collectible.draw(screen)
            if player.rect.colliderect(collectible.rect):
                player.collect(collectible)
                collectibles.remove(collectible)
                collectibles.append(Collectible(random.choice(POWERUP_TYPES)))
        for obstacle in obstacles:
            obstacle.update()
            screen.blit(obstacle_image, obstacle.rect.topleft)
            if player.rect.colliderect(obstacle.rect):
                player.collide()
        player.score += player.speed * player.multiplier
        font = pygame.font.Font(None, 36)
        text = font.render(f'Score: {int(player.score)}', True, RED)
        screen.blit(text, (10, 10))
        if player.in_shadow:
            player.enter_shadow()
        else:
            player.exit_shadow()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                player.alive = False
        pygame.display.flip()
        clock.tick(60)
    game_over_screen(player.score)
    pygame.quit()

if __name__ == "__main__":
    main()
