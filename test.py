import pygame
import sys
import random
from pygame.math import Vector2
from pygame.locals import *

screenWidth = 800
screenHeight = 600
DRAGON_IMG = pygame.Surface((40, 70))
ORC_IMG = pygame.Surface((40, 40))
BULLET_IMG = pygame.Surface((10, 10))
BULLET_IMG.fill(pygame.Color('red'))

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption("Hero Monster game")
clock = pygame.time.Clock()

#colors
black=(0,0,0)
blue=(0,0, 255)
green=(0,128,0)
red=(255,0,0)
white=(255,255,255)
yellow=(255,255,0)

def app_quit():
    pygame.quit()
    sys.exit("System exit.")

"""Hero - Monster game that has hero with certain power level and two monsters
   Orc and Dragon each with certain power levels. 
   Hero- Green, Orc- Red, Dragon- Orange"""

class Player(pygame.sprite.Sprite):
    def __init__(self, all_sprites, bulletshero, health, damage):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([45, 45])
        self.image.fill(pygame.Color('green'))
        self.rect = self.image.get_rect()
        self.rect.centerx = screenWidth / 2
        self.rect.bottom = screenHeight - 10
        self. health  = health
        self.damage = damage    
        self.allSprites = all_sprites
        self.bulletshero = bulletshero


    def update(self):
        self.speedx = 0
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                app_quit()
            #moves only in x-direction
            if event.type == KEYDOWN and event.key == K_LEFT:   #movement in left for hero
                self.speedx = -10
            if event.type == KEYDOWN and event.key == K_RIGHT:   #movement in right for hero
                self.speedx = 10
            if event.type == KEYDOWN and event.key == K_SPACE:
                self.shootPlayer()

        self.rect.x += self.speedx
        if self.rect.right > screenWidth:
            self.rect.right = screenWidth
        if self.rect.left < 0:
            self.rect.left = 0
            
        if self.health <= 0:
            self.kill()

    def shootPlayer(self):
        # bulllets for player shooting
        bulletPlayer = BulletPlayer(self.rect.centerx, self.rect.top, self.damage)
        self.allSprites.add(bulletPlayer)    #add to group
        self.bulletshero.add(bulletPlayer)
    
class Monster(pygame.sprite.Sprite):

    def __init__(self, projectiles, pos, health, damage, color, monster_type, attack_time, pace =7, turn_after=100, speed=150):
        super().__init__()
        self.monster_type= monster_type
        self.image = self.monster_type
        self.image.fill(pygame.Color(color))
        self.rect = self.image.get_rect(center=pos)
        self.health = health
        self.damage = damage
        self.attack_time = attack_time      #specify milliseconds for each monster
        self.pace_size   = pace             # How big each step is
        self.pace_count  = 0                # distance moved
        self.direction   = -1               # Start moving left (-x)
        self.previous_time = pygame.time.get_ticks()
        self.turn_after  = turn_after       # distance limit            
        self.speed = speed                  # Milliseconds per pace
        self.pace_time   = 0                # time of last step
        self.attack_speed  = 10             # attacking speed of monster
        self.projectiles = projectiles

    def update(self):
        time_now = pygame.time.get_ticks() 
        if time_now - self.previous_time > self.attack_time:
            self.previous_time = time_now
            vel = Vector2(0, 1)
            # Add the projectile to the group.
            self.projectiles.add(Projectile(self.rect.centerx, self.rect.bottom, vel, self.damage, self.health))
        if ( time_now > self.pace_time + self.speed ):   # is it time to move again
            #from IPython import embed;embed()
            self.pace_time = time_now

            # Walk pace in the current direction
            self.pace_count += 1
            self.rect.x     += self.direction * self.pace_size

            # We need to turn around if walked enough paces in the same direction
            if ( self.pace_count >= self.turn_after ):
                # Turn around!
                self.direction *= -1           # reverses the pixel distance
                self.pace_count = 0            # reset the pace count

            # We also should change direction if we hit the screen edge
            if ( self.rect.x <= 0 ):
                self.direction  = 1             # turn right
                self.pace_count = 0
            elif ( self.rect.x >= screenWidth - self.rect.width ):
                self.direction  = -1
                self.pace_count = 0
        
        if self.health <= 0:
            self.kill()


class BulletPlayer(pygame.sprite.Sprite):
    """Shooting bullet for player- user """
    def __init__(self, x, y, damage):
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.Surface([10, 10])
        self.image.fill(pygame.Color('green'))
        self.rect = self.image.get_rect()
        self.damage = damage
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -1

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Projectile(pygame.sprite.Sprite):
    """"bullets for Monsters spawning automatically with definitive ms 
        with class Monster"""
    def __init__(self, x, y, vel, damage, monster_health):
        super().__init__()
        self.image = BULLET_IMG
        self.damage = damage
        self.monster_health = monster_health
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel = Vector2(vel)

    def update(self):
        self.rect.move_ip(self.vel)
        if self.monster_health <=0:
            self.kill()


class Game(object):
    """Game  class using sprite instances for multiple objects continuous simulation"""
    def __init__(self):
        self.allSprites = pygame.sprite.Group()
        self.bulletshero = pygame.sprite.Group()
        self.hero = pygame.sprite.Group()
        self.hero = Player(self.allSprites, self.bulletshero, health=40, damage = 4)
        #self.monster = pygame.sprite.Group()
        self.orc = pygame.sprite.Group()
        self.dragon = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.allSprites.add(self.hero, self.orc, self.dragon, self.bulletshero, self.projectiles)

        #randomly positioning the monsters
        pos1 = (random.randrange(30, 750), random.randrange(500))
        pos2 = (random.randrange(30, 60), random.randrange(400))
        self.orc = Monster(self.projectiles, pos1, health=7, damage = 1, attack_time=1500, color = 'red', monster_type=ORC_IMG)
        self.dragon = Monster(self.projectiles, pos2, health=20, damage = 3, attack_time=2000, color = 'orange', monster_type= DRAGON_IMG)
        self.allSprites.add(self.orc)
        self.allSprites.add(self.dragon)

        running = True
        while running:
            hitplayer = pygame.sprite.spritecollide(self.hero, self.projectiles, True)
            if hitplayer and self.hero.health> 0:
                for bullet in hitplayer:
                    self.hero.health -= bullet.damage
                    print("Monster hits hero, Hero's health is {}".format(self.hero.health))
                    if self.hero.health <= 0:
                        print("hero died. Gameover")
                        app_quit()

            hitorc = pygame.sprite.spritecollide(self.orc, self.bulletshero, True)
            if hitorc and self.orc.health > 0:
                for bullet in hitorc:
                    self.orc.health -= bullet.damage
                    print("Hero hits orc, Orc's health is {}".format(self.orc.health))
            
            hitdragon = pygame.sprite.spritecollide(self.dragon, self.bulletshero, True)
            if hitdragon and self.dragon.health > 0:
                for bullet in hitdragon:
                    self.dragon.health -= bullet.damage
                    print("Hero hits dragon, Dragon's health is {}".format(self.dragon.health))
            
            if (self.orc.health <=0 and self.dragon.health<=0):
                print("Hero wins. GAME OVER")
                app_quit()
            
            self.allSprites.update()
            self.hero.update()
            self.projectiles.update()
            self.orc.update()
            self.dragon.update()
            self.bulletshero.update()
                    
            screen.fill(black)
            self.allSprites.draw(screen)
            self.projectiles.draw(screen)
            pygame.display.flip()

if __name__ == '__main__':
    Game()

