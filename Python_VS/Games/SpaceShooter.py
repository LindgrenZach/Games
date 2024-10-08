from typing import Any
import pygame
from os.path import join
from random import randint, uniform

class Player(pygame.sprite.Sprite):
  def __init__(self, groups):
    super().__init__(groups)
    self.image = pygame.image.load(join('Games', 'images', 'player.png')).convert_alpha()
    self.rect = self.image.get_frect(center = (window_width / 2, window_height / 1.5))
    self.direction = pygame.Vector2()
    self.speed = 400

    # cooldown
    self.can_shoot = True
    self.laser_shoot_time = 0
    self.cooldown_duration = 200
    
    

    # mask
    # self.mask = pygame.mask.from_surface(self.image)

 

  def laser_timer(self):
    if not self.can_shoot:
      current_time = pygame.time.get_ticks()
      if current_time - self.laser_shoot_time >= self.cooldown_duration:
        self.can_shoot = True

  def update(self, dt):
    keys = pygame.key.get_pressed()
    self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
    self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
    self.direction = self.direction.normalize() if self.direction else self.direction
    self.rect.center += self.direction * self.speed * dt

    recent_keys = pygame.key.get_just_pressed()
    if recent_keys[pygame.K_SPACE] and self.can_shoot:
      Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
      self.can_shoot = False
      self.laser_shoot_time = pygame.time.get_ticks()
      laser_sound.play()

    self.laser_timer()

class Star(pygame.sprite.Sprite):
  def __init__(self, groups, surf):
    super().__init__(groups)
    self.image = surf
    self.rect = self.image.get_frect(center = (randint(0, window_width),randint(0, window_height)))

class Laser(pygame.sprite.Sprite):
  def __init__(self, surf, pos, groups):
    super().__init__(groups)
    self.image = surf
    self.rect = self.image.get_frect(midbottom = pos)
    self.mask = pygame.mask.from_surface(self.image)

  def update(self, dt):
    self.rect.centery -= 800 * dt
    if self.rect.bottom < 0:
      self.kill()

class Meteor(pygame.sprite.Sprite):
  def __init__(self, surf, pos, groups):
    super().__init__(groups)
    self.original_surf = surf
    self.image = surf
    self.rect = self.image.get_frect(center = pos)
    self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
    self.speed = randint(400, 500)

    # self.mask = pygame.mask.from_surface(self.image)
    self.rotation_speed = randint(40,80)
    self.rotation = 0

  
  def update(self, dt):
    self.rect.center += self.direction * self.speed * dt
    if self.rect.top > window_height:
      self.kill()

    self.rotation += self.rotation_speed * dt
    self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
    self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
  def __init__(self, frames, pos ,groups):
    super().__init__(groups)
    self.frames = frames
    self.frame_index = 0
    self.image = self.frames[self.frame_index]
    self.rect = self.image.get_frect(center = pos)

  def update(self, dt):
    self.frame_index += 20 * dt
    if self.frame_index < len(self.frames):
      self.image = self.frames[int(self.frame_index)]
    else:
      self.kill()

def collisions():
  global running
  collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
  if collision_sprites:
    damage_sound.play()
    running = False
    
  for laser in laser_sprites:
    collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
    if collided_sprites:
      laser.kill()
      AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
      explosion_sound.play()

def display_score():
  current_time = pygame.time.get_ticks() // 100
  text_surf = font.render(str(current_time), True, (240,240,240))
  text_rect = text_surf.get_frect(midbottom = (window_width / 2, window_height - 50))
  display_surface.blit(text_surf, text_rect)
  pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10 )

# general setup
pygame.init()
window_width, window_height = 1280, 720
display_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Invaders')
running = True
clock = pygame.time.Clock()

# Imports
star_surf = pygame.image.load(join('Games', 'images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('Games','images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('Games','images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('Games','images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('Games','images', 'explosion', f'{i}.png')).convert_alpha() for i in range (21)]
laser_sound = pygame.mixer.Sound(join('Games', 'audio', 'laser.wav'))
laser_sound.set_volume(0.6)
explosion_sound = pygame.mixer.Sound(join('Games', 'audio', 'explosion.wav'))
explosion_sound.set_volume(0.8)
damage_sound = pygame.mixer.Sound(join('Games', 'audio', 'damage.ogg'))
damage_sound.set_volume(1)
game_music = pygame.mixer.Sound(join('Games', 'audio', 'game_music.wav'))
game_music.set_volume(0.4)
game_music.play(loops = -1)

# sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
  Star(all_sprites, star_surf)
player = Player(all_sprites)

# custom events ->> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)


#Running the Game
while running:
  #setting framerate
  dt = clock.tick() / 1000
  # event loop
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if event.type == meteor_event:
      x, y = randint(0, window_width), randint(-200, -100)
      Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
  
  #update
  all_sprites.update(dt)
  collisions()

  #draw the game
  display_surface.fill('#21001f')
  display_score()
  all_sprites.draw(display_surface)
  pygame.display.update()
pygame.quit()

