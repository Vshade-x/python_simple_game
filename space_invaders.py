import pygame
import random
import math
from pygame import mixer
import io

# --- FUNCTION TO LOAD TTF FONT BYTES (REMAINS) ---
def get_font_bytes(font_path):
    """Opens the TTF file and reads its binary bytes for Pygame compatibility."""
    with open(font_path, 'rb') as f:
        ttf_bytes = f.read()
    return io.BytesIO(ttf_bytes)

# Initialize Pygame
pygame.init()

# --- GAME CONSTANTS AND SCREEN SETUP ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Title and Icon
pygame.display.set_caption('Space Invaders')
icon = pygame.image.load('forma-alienigena-pixelada-de-un-juego-digital.png')
pygame.display.set_icon(icon)
background = pygame.image.load('fondo.jpg')

# --- SOUND SETUP ---
mixer.music.load('MusicaFondo.mp3')
mixer.music.set_volume(0.3)
mixer.music.play(-1)

# --- SCORE VARIABLES ---
score = 0
font_file = 'Magnolia.ttf' 
score_font_size = 32
score_x = 10
score_y = 10
game_over_font_size = 64

# ==============================================================
# 🌟 CLASS DEFINITIONS (POO) 🌟
# ==============================================================

# 1. CLASS PLAYER: Handles the spaceship.
class Player:
    def __init__(self):
        self.image = pygame.image.load('nave-espacial.png')
        self.x = 370
        self.y = 480
        self.x_change = 0

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self): 
        self.x += self.x_change
        # Boundary checking
        if self.x <= 0:
            self.x = 0
        elif self.x >= 736:
            self.x = 736

# 2. CLASS ENEMY: Handles the enemy aliens.
class Enemy:
    def __init__(self):
        self.image = pygame.image.load('alienigena-aterrador.png')
        self.x = random.randint(0, 736)
        self.y = random.randint(50, 150)
        self.x_change = 0.5 # Velocidad corregida
        self.y_change = 40

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def update_position(self):
        self.x += self.x_change
        # Lógica de rebote
        if self.x <= 0:
            self.x_change = 0.5
            self.y += self.y_change 
        elif self.x >= 736:
            self.x_change = -0.5
            self.y += self.y_change 

# 3. CLASS BULLET: Handles the bullet logic.
class Bullet:
    def __init__(self):
        self.image = pygame.image.load('bala.png')
        self.x = 0
        self.y = 480
        self.y_change = 5 # Velocidad de bala ajustada
        self.state = 'ready' 

    def draw(self, screen):
        if self.state == 'fire':
            screen.blit(self.image, (self.x + 16, self.y + 10))

    def fire(self, x):
        self.state = 'fire'
        self.x = x
        self.y = 480 # Asegura que empiece en la posición inicial del jugador

    def update_position(self):
        if self.state == 'fire':
            self.y -= self.y_change
            if self.y <= 0:
                self.y = 480
                self.state = 'ready'

# 4. CLASS GAME: Handles overall game state, score, and enemy list management.
class Game:
    def __init__(self):
        self.score = 0
        self.enemies = [Enemy() for _ in range(6)]
        self.bullet = Bullet()
        self.player = Player()

    def increase_score(self):
        self.score += 1

# ==============================================================
# --- GAME FUNCTIONS (ADAPTED) ---
# ==============================================================

def display_score(x, y):
    """Displays the current game score."""
    global score # Necesaria para leer el score global
    font = pygame.font.Font(font_file, score_font_size) 
    text = font.render(f'Score: {score}', True, (255,255,255))
    screen.blit(text, (x, y))

def game_over_text():
    """Displays the final 'Game Over' screen message."""
    font = pygame.font.Font(font_file, game_over_font_size) 
    final_text = font.render('Game Over', True, (255,255,255))
    screen.blit(final_text, (232, 240))

def check_collision(x1, y1, x2, y2):
    """Calculates distance between two points to check for collision."""
    distance = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
    if distance < 30: 
        return True
    else:
        return False

# ==============================================================
# 🚀 GAME LOOP EXECUTION 🚀
# ==============================================================

game = Game()
player = game.player
bullet = game.bullet
enemies = game.enemies

is_running = True
while is_running:

    # Background image
    screen.blit(background, (0,0))

    # Event Iteration (Input Handling)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.x_change = -2
            if event.key == pygame.K_RIGHT:
                player.x_change = 2
            if event.key == pygame.K_SPACE:
                if bullet.state == 'ready':
                    bullet.fire(player.x)
                    bullet_sound = mixer.Sound('disparo.mp3')
                    bullet_sound.set_volume(0.3)
                    bullet_sound.play()
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player.x_change = 0

    # --- GAME LOGIC ---
    
    # 1. PLAYER MOVEMENT
    player.move()

    # 2. ENEMY LOGIC & COLLISION CHECK
    for enemy in enemies:
        
        # A. Check for Game Over (Enemy reaches player level)
        if enemy.y > 440: 
            for e in enemies:
                e.y = 2000 
            game_over_text()
            break 

        # B. Move Enemy
        enemy.update_position()

        # C. COLLISION: Bullet vs Enemy
        if bullet.state == 'fire':
            if check_collision(enemy.x, enemy.y, bullet.x, bullet.y):
                
                # Actions on Hit
                collision_sound = mixer.Sound('Golpe.mp3')
                collision_sound.play()
                
                # Reset Bullet
                bullet.state = 'ready'
                bullet.y = player.y
                
                # Increase Score and Respawn Enemy
                game.increase_score()
                enemy.x = random.randint(0, 736)
                enemy.y = random.randint(50, 150)

        # D. Draw Enemy
        enemy.draw(screen)

    # 3. BULLET MOVEMENT AND DRAWING
    bullet.update_position()
    bullet.draw(screen)
    
    # 4. Draw Player (Already drawn in loop, but included here for completeness)
    # player.draw(screen) 
    player.draw(screen)
    
    # 5. UPDATE SCORE DISPLAY (CORRECCIÓN FINAL DE LA SINTAXIS)
    score = game.score 
    display_score(score_x, score_y) 

    pygame.display.update()