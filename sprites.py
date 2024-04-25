
import pygame as pg
from settings import *
from tilemap import *
from random import uniform, choice
vec = pg.math.Vector2


#COLLISIONS
def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y
def check_collisions(player, obstacles):
    for obstacle in obstacles:
        if player.hit_rect.colliderect(obstacle.rect):
            handle_collision(player, obstacle)
def handle_collision(player, obstacle):
    # Example: Stop the player's movement
    player.vel.x = 0
    player.vel.y = 0
    # Optionally, reposition player slightly away from the obstacle
    if player.hit_rect.centerx < obstacle.rect.centerx:
        player.hit_rect.right = obstacle.rect.left
    else:
        player.hit_rect.left = obstacle.rect.right



class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        original_image = pg.image.load("img/manBlue_gun.png").convert_alpha()
        self.image = pg.transform.scale(original_image,
                                        (int(original_image.get_width() * 0.1), int(original_image.get_height() * 0.1)))
        self.rect = self.image.get_rect()
        self.hit_rect = pg.Rect(0, 0, int(self.rect.width * 1.2), int(self.rect.height * 1.2))
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0  # Rotation is not used for directional movement but keeping it if needed elsewhere
        self.last_shot = 0
        self.health = PLAYER_HEALTH

    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel.y = -PLAYER_SPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel.y = PLAYER_SPEED

        # Normalize the velocity to keep consistent speed in diagonal movement
        if self.vel.length() > 0:
            self.vel = self.vel.normalize() * PLAYER_SPEED

        # Shooting mechanics, similar to previous implementation
        if keys[pg.K_SPACE]:
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                bullet_dir = vec(1, 0)  # Direction might need to be adjusted
                bullet_pos = self.pos + BARREL_OFFSET  # Offset might need to be adjusted
                Bullet(self.game, bullet_pos, bullet_dir)
                self.vel += vec(-KICKBACK, 0)  # Kickback can be adjusted

    def update(self):
        self.get_keys()
        #self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        # Update the hitbox position
        self.hit_rect.center = self.rect.center
        check_collisions(self, self.game.walls)  # assuming obstacles are accessible here


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.original_image = pg.image.load("img/zombie1_hold.png").convert_alpha()
        self.image = pg.transform.scale(self.original_image, (int(self.original_image.get_width() * 0.1), int(self.original_image.get_height() * 0.1)))
        self.rect = self.image.get_rect()
        self.hit_rect = pg.Rect(0, 0, int(self.rect.width * 1.2), int(self.rect.height * 1.2))
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0
        self.health = MOB_HEALTH
        self.acc = vec(0, 0)
        self.speed = choice(MOB_SPEEDS)
        self.vision_radius = 250
        self.IDLE_ROTATION_SPEED = 0
        self.game.debug_mode = False





    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def can_see_player(self):
        if self.pos.distance_to(self.game.player.pos) < self.vision_radius:
            # ... line-of-sight calculation ...
            for wall in self.game.walls:
                if wall.rect.clipline(self.pos, self.game.player.pos):
                    return False  # Vision is blocked by a wall
            return True  # No walls are blocking the view
        return False

    def chase_player(self):
        self.direction = (self.game.player.pos - self.pos).normalize()
        self.pos += self.direction * self.speed * self.game.dt
        self.hit_rect.center = self.pos
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.original_image, self.rot)
        self.rect = self.image.get_rect(center=self.rect.center)

    def idle_behavior(self):
        # Define the idle behavior here.
        # For example, mob stands still:
        self.vel = vec(0, 0)


    def update(self):
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        # self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = vec(1, 0).rotate(-self.rot)
        self.avoid_mobs()
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        self.vision_radius = 250  # For example, 250 pixels
        can_see = self.can_see_player()
        if can_see:
            self.chase_player()
        else:
            self.idle_behavior()  # Stop chasing, wander, or stand still
        if self.health <= 0:
            self.kill()  # Removes the sprite from all groups
        check_collisions(self, self.game.walls)  # assuming obstacles are accessible here
        self.move()
        self.hit_rect.center = self.rect.center




    def move(self):
        self.pos.x += self.vel.x * self.game.dt
        collide_with_walls(self, self.game.walls, 'x')
        self.pos.y += self.vel.y * self.game.dt
        collide_with_walls(self, self.game.walls, 'y')

    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)

class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_img
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = dir.rotate(spread) * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class FinishTrigger(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.all_sprites, game.finish_triggers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((w, h), pg.SRCALPHA)  # SRCALPHA makes it transparent
        self.rect = self.image.get_rect(topleft=(x, y))
        self.game = game
