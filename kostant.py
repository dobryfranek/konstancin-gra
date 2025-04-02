import threading
import ctypes
import random
import pygame
import sys
import os

def path(rel) -> str:
    if hasattr(sys, "_MEIPASS"):
        based = sys._MEIPASS
    else:
        based = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(based, rel)

pygame.init()

WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
FONT = pygame.font.SysFont("Consolas", int(WIDTH // 32))
scr = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.FULLSCREEN)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

PLAYER_WIDTH = WIDTH // 18
PLAYER_HEIGHT = PLAYER_WIDTH * 0.9

MATEUSZ = pygame.image.load(path("player.png"))
MATEUSZ = pygame.transform.scale(MATEUSZ, (PLAYER_WIDTH, PLAYER_HEIGHT))

ENEMY_WIDTH = WIDTH // 30
ENEMY_HEIGHT = ENEMY_WIDTH * 0.9
ENEMY = pygame.image.load(path("enemy.png")).convert_alpha()

clock = pygame.time.Clock()

class Player():
    def __init__(self, img: pygame.Surface):
        self.accel = 1
        self.x_vel = 0
        self.img = img
        self.rect = img.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT
    
    def draw(self):
        scr.blit(self.img, self.rect.topleft)
    
    def death(self, title="ALERT", text="MATEUSZ NIE ŻYJE"):
        if hasattr(ctypes, "windll"):
            def m(title, text, icon):
                ctypes.windll.user32.MessageBoxW(0, text, title, icon | 0x1)
            threading.Thread(target=m, args=(title, text, random.choice([0x30, 0x10]))).start()
        else:
            pass

class Enemy():
    def __init__(self, img: pygame.Surface):
        this_size = (ENEMY_WIDTH * random.uniform(0.9, 2), ENEMY_HEIGHT * random.uniform(0.9, 2))
        self.img = pygame.transform.scale(img, this_size)
        self.rect = self.img.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.accel = 9.81 / 32
        self.accel *= ((this_size[0] * this_size[1]) / 8192) ** 0.5
        # self.accel += random.uniform(-1/16, 1/8)
        self.velocity_y = 1
    
    def update(self):
        self.rect.y += self.velocity_y
        self.velocity_y += self.accel
        if self.rect.top > HEIGHT:
            self.rect.y = -self.rect.height
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.velocity_y = 0

    def draw(self):
        scr.blit(self.img, self.rect.topleft)

    def is_collision(self, player):
        if player is None:
            return False
        player_rect: pygame.Rect = player.rect
        enemy_rect: pygame.Rect = self.rect

        if not enemy_rect.colliderect(player_rect):
            return False
        
        for x in range(enemy_rect.left, enemy_rect.right):
            for y in range(enemy_rect.top, enemy_rect.bottom):
                if player_rect.collidepoint(x, y):
                    if self.img.get_at((x - enemy_rect.left, y - enemy_rect.top))[3] > 0:
                        return True
        return False

score = 0

def draw_score():
    surf = FONT.render(str(score), False, BLACK if current_color else WHITE)
    scr.blit(surf, (WIDTH - surf.get_width(), 0))

gierek = Player(MATEUSZ)
enemies = [Enemy(ENEMY) for _ in range(1)]

game_time = 1
friction = 0.97
current_color = 1

running = 1
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = 0
    
    k_pressed = pygame.key.get_pressed()

    if k_pressed[pygame.K_d]:
        gierek.x_vel += gierek.accel
    if k_pressed[pygame.K_a]:
        gierek.x_vel -= gierek.accel
    if k_pressed[pygame.K_s]:
        friction = 0.8
    else:
        friction = 0.97

    gierek.x_vel *= friction # tarcie
    gierek.rect.x += gierek.x_vel
    
    if game_time % 400 == 0:
        for _ in range(2): enemies.append(Enemy(ENEMY))
    
    if game_time % 500 == 0:
        current_color = not current_color

    if gierek.rect.left < 0:
        nowy_gierk = Player(MATEUSZ)
        nowy_gierk.rect.x = gierek.rect.x + WIDTH
    elif gierek.rect.right > WIDTH:
        nowy_gierk = Player(MATEUSZ)
        nowy_gierk.rect.x = gierek.rect.x - WIDTH
    else:
        nowy_gierk = None
    
    if gierek.rect.left < -gierek.rect.w:
        gierek.rect.x += WIDTH
        nowy_gierk = None
    
    elif gierek.rect.right > WIDTH + gierek.rect.w:
        gierek.rect.x -= WIDTH

    if nowy_gierk is not None:
        nowy_gierk.draw()

    gierek.draw()

    for enemy in enemies:
        enemy.update()
        enemy.draw()
        if enemy.is_collision(gierek) or enemy.is_collision(nowy_gierk):
            gierek.death(title="WYNIK: " + str(score))
            running = 0
    

    draw_score()

    pygame.display.update()
    scr.fill(WHITE if current_color else BLACK)
    clock.tick(75)
    game_time += 1
    score = game_time // 50 * 50
        

pygame.quit()