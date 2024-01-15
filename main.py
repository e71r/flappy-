
import pygame as pg 
from config import *
import random
import json

pg.init()
pg.font.init()
font = pg.font.Font("font.ttf", 25)
bigfont = pg.font.Font("font.ttf", 40)

def load_image(path, width = None, height = None) -> pg.Surface:
    img = pg.image.load(path)
    if width and height:
        img = pg.transform.scale(img, (width,height))
    return img

def render_text(text, font,color = (255,0,0)):
    return font.render(text, True, color)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_json(path, text):
    with open(path, "w", encoding="utf-8") as f:
        return json.dump(text, f)


class Pipe(pg.sprite.Sprite):
    def __init__(self, x_left, sizey, sizex, side = "bottom"):
        super().__init__()

        spritesheet = load_image("bin/assets/Tiles/Style 1/PipeStyle1.png")

        self.image = spritesheet.subsurface((0,0, 32, 60)) 
        if side == "up":
            self.image = pg.transform.flip(self.image, False, True)
            
        self.image = pg.transform.scale(self.image, (sizex, sizey))
        self.rect = self.image.get_rect()
        if side == "bottom":
            self.rect.bottom = SCREEN_HEIGHT
        elif side == "up":
            self.rect.y = 0
    
        self.flied = False
        self.rect.left = SCREEN_WIDTH
        self.speed = 2
    


        

    def update(self):
        if self.rect.right <= 0:
            self.kill()
        self.rect.x -= self.speed

        

        



class Player(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.load_animation()

        self.image = self.animation[0]
        self.timer = pg.time.get_ticks()
        self.jump_timer = None

        self.rect = self.image.get_rect(x = x, y = y)

        self.current_frame = 0
        self.interval = 250
        self.jump_interval = 150
        self.is_jumping = False
        self.gravity = 3
        self.jump_force = 5
        self.angle = 180

        self.angle = 90
        self.next_angle = 0
        self.y_vel = 0


    def update(self):
        
        if pg.time.get_ticks() - self.timer >= self.interval:
            self.current_frame += 1
            if self.current_frame == len(self.animation)-1:
                self.current_frame = 0

            self.image = self.animation[self.current_frame]
            self.timer = pg.time.get_ticks()

        if self.jump_timer != None and self.is_jumping:
            if pg.time.get_ticks() - self.jump_timer >= self.jump_interval:
                self.is_jumping = False
                self.y_vel = 0
                self.next_angle = self.angle + 35

        self.rect.y += self.y_vel
    

        

        # mouse = pg.mouse.get_pressed()

        # if mouse[0] and not self.is_jumping:
        #     self.y_vel = -self.jump_force
        #     self.is_jumping = True
        #     self.jump_timer = pg.time.get_ticks()

        if self.y_vel == 0:
            if not self.is_jumping:
                self.y_vel = self.gravity

    

    def load_animation(self):
        sprite_size = 16
        sprite_scale = 3
        spritesheet = load_image("bin/assets/Player/StyleBird1/Bird1-1.png")

        self.animation = []

        for i in range(4):
            x = i * sprite_size
            y = 0
            rect = pg.Rect(x,y, sprite_size, sprite_size)
            img = spritesheet.subsurface(rect)
            img = pg.transform.scale(img, (sprite_size*sprite_scale, sprite_size*sprite_scale))
            self.animation.append(img)

    def jump(self):
        if not self.is_jumping:
            self.y_vel = -self.jump_force
            self.is_jumping = True
            self.jump_timer = pg.time.get_ticks()

        

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("flappy bird")
        self.setup()
        

    def setup(self):
        self.mode = "game"
        self.background = load_image("bin/assets/Background/Background7.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player = Player(SCREEN_WIDTH // 2-16*3, SCREEN_HEIGHT // 2) # 16 * 3 - Это размер игрока ( тоесть sprite_size * sprite_scale )
        self.running = True
        self.all_sprites = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.all_sprites.add(self.player)

        self.clock = pg.time.Clock()
        self.obstacles_spawn_interval = random.randint(1500, 3000)
        self.obstacles_spawn_timer = pg.time.get_ticks()
        self.score = 0
        self.maxspeed = 5
        self.speed = 2
        
        self.speedchanged = {}

        self.run()
    
    def run(self):
        while self.running:
            self.event()
            self.update()
            self.draw()

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.player.jump()
            if self.mode == "game over":
                if event.type == pg.KEYDOWN:
                    self.setup()
                
            
    
    def update(self):
        if self.mode == "game over":
            return

        if self.score >= 1000//2:
            quit()
        self.player.update()
        self.obstacles.update()
        self.clock.tick(FPS)
    
        if self.player.rect.y >= SCREEN_HEIGHT or self.player.rect.y <= 0:
            self.mode = "game over"
        ## obstacles ##
        hits = pg.sprite.spritecollide(self.player, self.obstacles, False)
        for hit in hits:
            self.mode = "game over"
            data = load_json("save.json")

            if self.score//2 >= data["highscore"]:
                data["highscore"] = self.score//2
                save_json("save.json", data)
                continue
    

        if pg.time.get_ticks() - self.obstacles_spawn_timer >= self.obstacles_spawn_interval:
            pipeside1 = "up"
            pipeside2 = "bottom"
            pipesizey1 = random.randint(150, 250)

            gap = random.randint(150, 200)

            pipe1 = Pipe(SCREEN_WIDTH, pipesizey1, 100, pipeside1)

            pipeside2 = "bottom"
            pipe2 = Pipe(SCREEN_WIDTH, SCREEN_HEIGHT - pipesizey1 - gap, 100, pipeside2)

            self.obstacles.add(pipe1, pipe2)
            self.all_sprites.add(pipe1, pipe2)

            self.obstacles_spawn_timer = pg.time.get_ticks()
            self.obstacles_spawn_interval = random.randint(1500, 3000)

        for obst in self.obstacles:
            if not obst.flied:

                if obst.rect.x < self.player.rect.x:
                    obst.flied = True
                    self.score += 1
                    


            obst.speed = self.speed

        if self.speed < self.maxspeed and self.score // 2 % 10 == 0 and self.score != 0:
            if str(self.score//2) not in self.speedchanged:
                self.speed += 1
                self.speedchanged[str(self.score//2)] = True

        

    


                

    def draw(self):
        self.screen.blit(self.background, (0,0))
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect)

        if self.mode == "game over":
            data = load_json("save.json")
            gap = 50
            text = render_text("Game over", font)
            
            text2 = render_text("High score: " + str(data["highscore"]), font)
            self.screen.blit(text, (SCREEN_WIDTH//2-gap*3, SCREEN_HEIGHT//2))
            self.screen.blit(text2, (SCREEN_WIDTH//2-gap*3, SCREEN_HEIGHT//2+gap))

        # score #
        
        sc = render_text(str(self.score//2), bigfont, (255,255,255))
        self.screen.blit(sc, (25,25))
        

        pg.display.flip()

if __name__ == "__main__":
    Game()