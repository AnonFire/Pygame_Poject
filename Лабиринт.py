import pygame
import os
from pygame.locals import *
import random
from copy import deepcopy


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
    return image


def generate_level(name):
    global stil
    y = 0
    for line in open(name, 'r').readlines():
        x = 0
        for j in line:
            if j == ' ':
                Doroga(dorogi, x, y, stil)
            elif j == '#':
                Stena(steni, x, y, stil)
            elif j == '1':
                Doroga(dorogi, x, y, stil)
                Bomb(bombs, (x, y), stil)
            x += 1
        y += 1


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.left = 10
        self.top = 100
        self.cell_size = 30

    def get_cell(self, mouse_pos):
            x, y = mouse_pos
            x -= self.left
            y -= self.top
            return x // self.cell_size, y // self.cell_size


pygame.init()
screen = pygame.display.set_mode((1480, 900))
pygame.display.set_caption("Labirint")
pygame.display.set_icon(load_image('Icon.jpg'))
pygame.display.flip()
a = True
screen.fill((70, 130, 180))
pygame.display.update()
steni = pygame.sprite.Group()
obecti = pygame.sprite.Group()
dorogi = pygame.sprite.Group()
bombs = pygame.sprite.Group()
board = Board(25, 25)
coins = pygame.sprite.Group()


class Hero(pygame.sprite.Sprite):
    m = [[load_image("hero1L.png"), load_image("hero1R.png")],
         [load_image("hero2L.png"), load_image("hero2R.png")],
         [load_image("hero3L.png"), load_image("hero3R.png")],
         [load_image("hero4L.png"), load_image("hero4R.png")],
         [load_image("hero5L.png"), load_image("hero5R.png")]]

    def __init__(self, group):
        super().__init__(group)
        self.image = Hero.m[0][0]
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.life = 7
        self.bonus = 0
        self.ignor = 0
        self.money = 0

    def move_x(self, a):
        global x, steni
        x += a
        self.rect.x += a * 30
        if pygame.sprite.spritecollideany(self, steni):
            self.rect.x -= a * 30
            x -= a

    def move_y(self, a):
        global y, steni
        self.rect.y += a * 30
        y += a
        if pygame.sprite.spritecollideany(self, steni):
            self.rect.y -= a * 30
            y -= a

    def move(self, a):
        x, y = a
        self.rect.x = 30 * x + 10
        self.rect.y = 30 * y + 100


class Crist(pygame.sprite.Sprite):
    m = [load_image("crist1.png"), load_image("crist2.png"),
         load_image("crist3.png"), load_image("crist4.png"),
         load_image("crist5.png")]

    def __init__(self, group):
        super().__init__(group)
        self.image = Crist.m[0]
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def move(self, a):
        x, y = a
        self.rect.x = 30 * x + 10
        self.rect.y = 30 * y + 100


class Stena(pygame.sprite.Sprite):
    m = [load_image("stena1.png"), load_image("stena2.png")]

    def __init__(self, group, x, y, st):
        super().__init__(group)
        self.image = Stena.m[st]
        self.rect = self.image.get_rect()
        self.rect.x = x * 30 + 10
        self.rect.y = y * 30 + 100
        self.st = st


class Doroga(pygame.sprite.Sprite):
    m = [load_image("doroga1.png"), load_image("doroga2.png")]

    def __init__(self, group, x, y, st):
        super().__init__(group)
        self.image = Doroga.m[st]
        self.rect = self.image.get_rect()
        self.rect.x = x * 30 + 10
        self.rect.y = y * 30 + 100
        self.st = st


class NotCrist(pygame.sprite.Sprite):
    m = [load_image("not_crist1.png"), load_image("not_crist2.png"),
         load_image("not_crist3.png"), load_image("not_crist4.png"),
         load_image("not_crist5.png")]

    def __init__(self, group):
        super().__init__(group)
        self.image = NotCrist.m[0]
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def move(self, a):
        x, y = a
        self.rect.x = 30 * x + 10
        self.rect.y = 30 * y + 100


class Bomb(pygame.sprite.Sprite):
    im = pygame.transform.scale(load_image("bomb.png"), (30, 30))
    m = [load_image("doroga1.png"), load_image("doroga2.png")]

    def __init__(self, group, a, st):
        super().__init__(group)
        x, y = a
        self.image = Bomb.im
        self.rect = self.image.get_rect()
        self.rect.x = x * 30 + 10
        self.rect.y = y * 30 + 100
        self.st = st
        self.damage = 1

    def boom(self):
        self.image = Bomb.m[self.st]
        self.damage = 0


class Coin(pygame.sprite.Sprite):
    im = pygame.transform.scale(load_image("coin.png"), (30, 30))
    m = [load_image("doroga1.png"), load_image("doroga2.png")]

    def __init__(self, group, st):
        global steni, obecti, bombs
        super().__init__(group)
        x = random.randint(1, 24)
        y = random.randint(1, 24)
        self.image = Coin.im
        self.rect = self.image.get_rect()
        self.rect.x = x * 30 + 10
        self.rect.y = y * 30 + 100
        while (pygame.sprite.spritecollideany(self, steni) or
               pygame.sprite.spritecollideany(self, obecti) or
               pygame.sprite.spritecollideany(self, bombs)):
            x = random.randint(1, 24)
            y = random.randint(1, 24)
            self.rect.x = x * 30 + 10
            self.rect.y = y * 30 + 100
        self.st = st
        self.money = random.randint(3, 7)

    def take(self):
        self.rect.y = 1000


def bonus():
    i = random.randint(0, 1)
    if i:
        hero.bonus = (hero.bonus + 1) % 3
        hero.life = min(hero.life + 1, 10)
    i = random.randint(0, 2)
    if not i:
        hero.ignor = min(hero.ignor + 1, 7)


def GameOver():
    global sound, clock, screen
    sound.play()
    screen.blit(pygame.transform.scale(load_image("gameover.png"),
                                       (1480, 900)), (0, 0))
    pygame.display.flip()
    pygame.display.update()
    clock.tick(0.25)


n = 0
stil = 0
hero = Hero(obecti)
hero.ignor = 0
crist = Crist(obecti)
crist_rand = NotCrist(obecti)
obecti.draw(screen)
steni.draw(screen)
dorogi.draw(screen)
bombs.draw(screen)
coll = []


def records():
    screen.fill((0, 0, 0))
    tabl = open('tabl_records.txt').readlines()
    font = pygame.font.Font(None, 68)
    j = 0
    for i in tabl:
        text = font.render(i, 1, (255, 215, 0))
        screen.blit(text, (x_0 + i * 50, y_0 + i * 50))
        x_0 = 740 - text.get_width() / 2
        y_0 = 450 - (text.get_height() + 10) / 2 * len(tabl)
        pygame.draw.rect(screen, (255, 0, 0), (x_0, y_0 + j * 60, 50, 50))
        j += 1
    pygame.display.flip()
    pygame.display.update()
    exit = load_image('exit.png')
    while True:
        screen.blit(pygame.transform.scale(exit, (500, 125)), (970, 10))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                while True:
                    pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if y >= 10 and y <= 135 and x >= 970 and x <= 1470:
                    return
        pygame.display.flip()
        pygame.display.update()


def menu():
    global n, hero, coll
    screen.fill((0, 0, 0))
    start = load_image('start.png')
    exit = load_image('exit.png')
    cont = load_image('cont.png')
    tabl = load_image('tabl.png')
    while True:
        screen.fill((0, 0, 0))
        screen.blit(pygame.transform.scale(start, (500, 125)), (490, 200))
        screen.blit(pygame.transform.scale(exit, (500, 125)), (490, 615))
        screen.blit(pygame.transform.scale(cont, (500, 125)), (490, 335))
        screen.blit(pygame.transform.scale(tabl, (500, 125)), (490, 480))        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                while True:
                    pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if y >= 200 and y <= 325 and x >= 490 and x <= 990:
                    return
                if y >= 335 and y <= 470 and x >= 490 and x <= 990:
                    try:
                        m = open('save.txt', 'r').read().split()
                        m = [int(i) for i in m]
                        n, hero.bonus, hero.ignor, hero.money = m[:4]
                        hero.lfe = 7 + hero.bonus
                        coll = m[4:].copy()
                        return
                    except Exception:
                        continue
                elif y >= 480 and y <= 605 and x >= 490 and x <= 990:
                    print(1)
                    records()
                    print(2)
                    pygame.display.flip()
                    pygame.display.update()
                    
                    x, y = 0, 0
                elif y >= 615 and y <= 740 and x >= 490 and x <= 990:
                    pygame.quit()
                    while True:
                        pass
        pygame.display.flip()
        pygame.display.update()


def f(n):
    S = 0
    for i in range(n + 1):
        S += 1.5 ** i * 75
    return int(S)


menu()
hero.image = Hero.m[n][0]
crist.image = Crist.m[n]
crist_rand.image = NotCrist.m[n]
clock = pygame.time.Clock()
pygame.mixer.music.load('fon.mp3')
pygame.mixer.music.play(-1)
boom = pygame.mixer.Sound('boom.wav')
sound = pygame.mixer.Sound('GameOver.wav')
take = pygame.mixer.Sound('take.wav')
M_sp = [[(10, 20), (14, 19), (12, 23)], [(9, 15), (15, 15), (12, 23)],
        [(3, 3), (18, 21), (12, 23)], [(10, 16), (14, 16), (12, 12)],
        [(5, 19), (19, 7), (23, 1)]]

Hero_pos = M_sp[n][2]
board.board = generate_level('level' + str(n + 1) + '.txt')
lvl = pygame.transform.scale(load_image("level.jpg"), (100, 105))
c = pygame.transform.scale(load_image('coin.png'), (50, 50))
coins_count = 0
cont = load_image('unpause.png')
pause = load_image('pause.png')
zast = load_image('zast.jpg')
exit = load_image('exit.png')
replay = load_image('replay.png')
new_game = load_image('new_game.png')
for i in range(random.randint(10, 15)):
    Coin(coins, stil)
m = [11, 12, 13, 14, 15, 21, 22, 23, 24, 25, 31, 32, 33, 34, 35]
bon_n = -1
bon = load_image('bonus0.jpg')
while a:
    if hero.money >= 1.5 ** hero.ignor * 75 and hero.ignor != 7:
        hero.money -= 1.5 ** hero.ignor * 75
        hero.ignor = min(hero.ignor + 1, 7)
    if coins_count >= 10:
        bon_n += coins_count // 10
        coins_count %= 10
        bon = load_image('bonus' + str(m[(bon_n) % 15]) + '.jpg')
    screen.fill((70, 130, 180))
    crist.move(M_sp[n][0])
    screen.blit(bon, (800, 350))
    for i in range(hero.life):
        screen.blit(load_image("life.png"), (800 + i * 50, 90))
    for i in range(1, hero.ignor + 1):
        screen.blit(load_image("armor" + str(i) + ".png"), (740 + i * 60, 150))
    j = 0
    for i in coll:
        screen.blit(pygame.transform.scale(
            load_image("crist" + str(i) + ".png"),
            (50, 50)), (800 + j * 50, 220))
        j += 1
    j = None
    screen.blit(lvl, (320, 0))
    font = pygame.font.Font(None, 68)
    text = font.render(str(int(hero.money)), 1, (255, 215, 0))
    screen.blit(c, (800 + text.get_width(), 280))
    text1 = font.render('Осталость ' + str(10 - coins_count % 10), 1,
                        (255, 215, 0))
    screen.blit(text1, (850 + text.get_width(), 280))
    screen.blit(c, (text1.get_width() + 850 + text.get_width(), 280))
    screen.blit(text, (800, 280))
    screen.blit(pause, (1400, 10))
    screen.blit(replay, (1340, 10))
    screen.blit(new_game, (1280, 10))
    crist_rand.move(M_sp[n][1])
    hero.move(Hero_pos)
    x, y = Hero_pos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            a = False
            open('save.txt', 'w').write(str(n) + ' ' + str(hero.bonus) + ' ' +
                                        str(hero.ignor) + ' ' +
                                        str(hero.money) + ' ' +
                                        ' '.join([str(i) for i in coll]))
    if pygame.key.get_pressed()[pygame.K_DOWN]:
        hero.move_y(1)
    elif pygame.key.get_pressed()[pygame.K_UP]:
        hero.move_y(-1)
    elif pygame.key.get_pressed()[pygame.K_LEFT]:
        hero.move_x(-1)
        hero.image = Hero.m[n][0]
    elif pygame.key.get_pressed()[pygame.K_RIGHT]:
        hero.move_x(1)
        hero.image = Hero.m[n][1]
    if pygame.mouse.get_pressed()[0]:
        x1, y1 = pygame.mouse.get_pos()
        if abs(x1 - 1365) <= 25 and abs(y1 - 35) <= 25:
            x, y = M_sp[n][2]
            hero.image = Hero.m[n][0]
            hero.life = 7 + hero.bonus
            steni = pygame.sprite.Group()
            dorogi = pygame.sprite.Group()
            bombs = pygame.sprite.Group()
            coins = pygame.sprite.Group()
            board.board = generate_level('level' + str(n + 1) + '.txt')
            crist.image = Crist.m[n]
            crist_rand.image = NotCrist.m[n]
            for i in range(random.randint(10, 15)):
                Coin(coins, stil)
        elif abs(x1 - 1305) <= 25 and abs(y1 - 35) <= 25:
            screen.fill((70, 130, 180))
            pygame.display.update()
            steni = pygame.sprite.Group()
            obecti = pygame.sprite.Group()
            dorogi = pygame.sprite.Group()
            bombs = pygame.sprite.Group()
            board = Board(25, 25)
            coins = pygame.sprite.Group()
            n = 0
            coins_count = 0
            bon_n = -1
            bon = load_image('bonus0.jpg')
            stil = 0
            hero = Hero(obecti)
            hero.ignor = 0
            crist = Crist(obecti)
            crist_rand = NotCrist(obecti)
            coll = []
            x, y = M_sp[n][2]
            hero.image = Hero.m[n][0]
            hero.life = 7 + hero.bonus
            steni = pygame.sprite.Group()
            dorogi = pygame.sprite.Group()
            bombs = pygame.sprite.Group()
            coins = pygame.sprite.Group()
            board.board = generate_level('level' + str(n + 1) + '.txt')
            crist.image = Crist.m[n]
            crist_rand.image = NotCrist.m[n]
            for i in range(random.randint(10, 15)):
                Coin(coins, stil)
        elif x1 - 1400 <= 50 and x1 >= 1400 and 10 <= y1 and y1 - 10 <= 50:
            pygame.mixer.music.pause()
            screen.blit(zast, (0, 0))
            screen.blit(cont, (10, 10))
            screen.blit(exit, (70, 0))
            pygame.display.flip()
            pygame.display.update()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        open('save.txt', 'w'
                             ).write(str(n) + ' ' +
                                     str(hero.bonus) + ' ' +
                                     str(hero.ignor) + ' ' +
                                     str(hero.money) + ' ' +
                                     ' '.join([str(i) for i in coll]))
                        pygame.quit()
                        y = text.get_height() + 10
                        n = 1480 // y
                        mas = open('tabl_records.txt').readlines()
                        mas.append(str(hero.money + f(hero.inor)))
                        mas = sorted(mas, key=int)
                        open('tabl_records.txt', 'w').write('\n'.join(mas[:n]))                        
                        while True:
                            pass
                if pygame.mouse.get_pressed()[0]:
                    x1, y1 = pygame.mouse.get_pos()
                    if abs(x1 - 35) <= 25 and abs(y1 - 35) <= 25:
                        break
                    if abs(x1 - 204) <= 134 and abs(y1 - 47.5):
                        open('save.txt',
                             'w').write(str(n) + ' ' +
                                        str(hero.bonus) + ' ' +
                                        str(hero.ignor) + ' ' +
                                        str(hero.money) + ' ' +
                                        ' '.join([str(i) for i in coll]))
                        pygame.quit()
                        y = text.get_height() + 10
                        n = 1480 // y
                        mas = open('tabl_records.txt').readlines()
                        mas.append(str(hero.money + f(hero.inor)))
                        mas = sorted(mas, key=int)
                        open('tabl_records.txt', 'w').write('\n'.join(mas[:n]))
                        while True:
                            pass
            pygame.mixer.music.unpause()
    Hero_pos = x, y
    steni.draw(screen)
    dorogi.draw(screen)
    bombs.draw(screen)
    coins.draw(screen)
    obecti.draw(screen)
    if pygame.sprite.spritecollideany(hero, bombs):
        j = random.randint(0, 9)
        if not j < hero.ignor:
            hero.life -= pygame.sprite.spritecollideany(hero, bombs).damage
        if pygame.sprite.spritecollideany(hero, bombs).damage:
            boom.play()
            pygame.sprite.spritecollideany(hero, bombs).boom()
    while pygame.sprite.spritecollideany(hero, coins):
        hero.money += pygame.sprite.spritecollideany(hero, coins).money
        coins_count += 1
        take.play()
        pygame.sprite.spritecollideany(hero, coins).take()
    if hero.life == 0:
        pygame.mixer.music.stop()
        GameOver()
        pygame.mixer.music.play(-1)
        n = 0
        hero.bonus = max(hero.bonus - 1, 0)
        hero.life = 7 + hero.bonus
        hero.ignor = max(hero.ignor - 1, 0)
        hero.money *= 0.75
        if coll != []:
            del coll[-1]
        steni = pygame.sprite.Group()
        dorogi = pygame.sprite.Group()
        bombs = pygame.sprite.Group()
        coins = pygame.sprite.Group()
        Hero_pos = M_sp[n][2]
        hero.image = Hero.m[n][0]
        board.board = generate_level('level' + str(n + 1) + '.txt')
        crist.image = Crist.m[n]
        crist_rand.image = NotCrist.m[n]
        for i in range(random.randint(10, 15)):
            Coin(coins, stil)
    if Hero_pos == M_sp[n][0]:
        coll.append(n + 1)
        coll = sorted(list(set(coll)))
        if len(coll) == 5:
            stil = (stil + 1) % 2
            coll = []
        n = (n + 1) % 5
        Hero_pos = M_sp[n][2]
        hero.image = Hero.m[n][0]
        hero.life = 7 + hero.bonus
        steni = pygame.sprite.Group()
        dorogi = pygame.sprite.Group()
        bombs = pygame.sprite.Group()
        coins = pygame.sprite.Group()
        board.board = generate_level('level' + str(n + 1) + '.txt')
        crist.image = Crist.m[n]
        crist_rand.image = NotCrist.m[n]
        bonus()
        for i in range(random.randint(10, 15)):
            Coin(coins, stil)
    elif Hero_pos == M_sp[n][1]:
        coll.append(n + 1)
        coll = sorted(list(set(coll)))
        if len(coll) == 5:
            stil = (stil + 1) % 2
            coll = []
        n = random.randint(0, 4)
        Hero_pos = M_sp[n][2]
        hero.image = Hero.m[n][0]
        hero.life = 7 + hero.bonus
        steni = pygame.sprite.Group()
        dorogi = pygame.sprite.Group()
        bombs = pygame.sprite.Group()
        coins = pygame.sprite.Group()
        board.board = generate_level('level' + str(n + 1) + '.txt')
        crist.image = Crist.m[n]
        crist_rand.image = NotCrist.m[n]
        bonus()
        for i in range(random.randint(10, 15)):
            Coin(coins, stil)
    pygame.display.flip()
    pygame.display.update()
    clock.tick(15)
pygame.quit()
y = text.get_height() + 10
n = 1480 // y
mas = open('tabl_records.txt').readlines()
mas.append(str(hero.money + f(hero.inor)))
mas = sorted(mas, key=int)
open('tabl_records.txt', 'w').write('\n'.join(mas[:n]))