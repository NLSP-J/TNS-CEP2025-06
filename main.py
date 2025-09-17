import pygame as pg
import random, time
import asyncio

pg.init()
clock = pg.time.Clock()

black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)

win_width = 800
win_height = 600
screen = pg.display.set_mode((win_width, win_height))
pg.display.set_caption('Falling Debris')

font = pg.font.Font(None, 30)
alert_font = pg.font.Font(None, 60)
speed = 5 
score = 0
wave_number = 1
lives = 3 
shield_active = False 
shield_last_used = 0
shield_cooldown = 3
running = True

player_size = 40
player_pos = [win_width / 2, win_height - player_size]
player_image = pg.image.load('./assets/images/mario.png')
player_image = pg.transform.scale(player_image, (player_size, player_size)) 

obj_size = 60
obj_data = []
obj = pg.image.load('./assets/images/e1.png')
obj = pg.transform.scale(obj, (obj_size, obj_size))

life_saver_size = 30
life_saver_data = []
life_saver = pg.Surface((life_saver_size, life_saver_size))
life_saver.fill((255, 0, 0))

bg_image = pg.image.load('./assets/images/background.png')
bg_image = pg.transform.scale(bg_image, (win_width, win_height))

def create_object(obj_data):
    if len(obj_data) < 10 and random.random() < 0.1:    
        x = random.randint(0, win_width - obj_size)
        y = 0 
        obj_data.append([x, y, obj])

def create_life_saver(life_saver_data):
    if len(life_saver_data) < 1 and random.random() < 0.02:
        x = random.randint(0, win_width - life_saver_size)
        y = 0 
        life_saver_data.append([x, y, life_saver])

def update_objects(obj_data):
    global score

    for object in obj_data:
        x, y, image_data = object
        if y < win_height:
            y += speed
            object[1] = y
            screen.blit(image_data, (x, y))
        else:
            obj_data.remove(object)
            score += 1

def update_life_saver(life_saver_data):
    global lives, wave_number, speed

    for saver in life_saver_data:
        x, y, image_data = saver
        if y < win_height:
            y += speed
            saver[1] = y
            screen.blit(image_data, (x, y))
        else:
            life_saver_data.remove(saver)

def collision_check(obj_data, player_pos):
    global running, lives, shield_active
    if shield_active:
        return 
    for object in obj_data:
        x, y, image_data = object
        player_x, player_y = player_pos[0], player_pos[1]
        obj_rect = pg.Rect(x, y, obj_size, obj_size)
        player_rect = pg.Rect(player_x, player_y, player_size, player_size)
        if player_rect.colliderect(obj_rect):
            lives -= 1  
            obj_data.remove(object)
            if lives <= 0:
                running = False
                game_over_text = alert_font.render(f'Game Over! Score: {score}', 10, red)
                screen.blit(bg_image, (0, 0))
                screen.blit(game_over_text, (win_width // 2 - 200, win_height // 2 - 50))
                pg.display.flip()
                time.sleep(2)
            break

def collision_check_life_saver(life_saver_data, player_pos):
    global lives, wave_number, speed, shield_active
    if shield_active:
        return
    for saver in life_saver_data:
        x, y, image_data = saver
        player_x, player_y = player_pos[0], player_pos[1]
        saver_rect = pg.Rect(x, y, life_saver_size, life_saver_size)
        player_rect = pg.Rect(player_x, player_y, player_size, player_size)
        if player_rect.colliderect(saver_rect):
            lives += 3 
            wave_number = max(1, wave_number - 10)  
            speed = max(5, speed - 50)
            life_saver_data.remove(saver)  
            break

def check_wave_transition(obj_data):
    global wave_number, speed, score
    if score >= wave_number * 10: 
        wave_number += 1
        speed += 1
        text_alert = f"Wave {wave_number} starts!"
        text_alert = alert_font.render(text_alert, 10, blue)
        screen.blit(text_alert, (win_width // 2 - 150, win_height // 2 - 200))
        pg.display.flip()
        time.sleep(0.5)

def draw_shield(player_pos):
       pg.draw.circle(screen, (0, 0, 255), (player_pos[0] + player_size // 2, player_pos[1] + player_size // 2), player_size + 10, 5)

async def main():

    global running, player_pos, shield_active, shield_last_used

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.KEYDOWN:
                x, y = player_pos[0], player_pos[1]
                if event.key == pg.K_LEFT:
                    x -= 20
                elif event.key == pg.K_RIGHT:
                    x += 20
                elif event.key == pg.K_SPACE:  
                    current_time = time.time()
                    if current_time - shield_last_used > shield_cooldown:  
                        shield_active = True
                        shield_last_used = current_time  
                player_pos = [x, y]

            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:  
                    shield_active = False

    
        screen.blit(bg_image, (0, 0))
        screen.blit(player_image, (player_pos[0], player_pos[1]))

        
        text_score = f'Score: {score}'
        text_score = font.render(text_score, 10, black)
        screen.blit(text_score, (win_width - 200, win_height - 40))

    
        text_wave = f'Wave: {wave_number}'
        text_wave = font.render(text_wave, 10, black)
        screen.blit(text_wave, (10, 10))  
    
        text_speed = f'Speed: {speed}'
        text_speed = font.render(text_speed, 10, black)
        screen.blit(text_speed, (10, 40)) 

    
        text_lives = f'Lives left: {lives}'
        text_lives = font.render(text_lives, 10, black)
        screen.blit(text_lives, (10, 70))


        create_object(obj_data)
        update_objects(obj_data)


        create_life_saver(life_saver_data)
        update_life_saver(life_saver_data)


        collision_check(obj_data, player_pos)
        collision_check_life_saver(life_saver_data, player_pos)

        check_wave_transition(obj_data)

    
        if shield_active:
            draw_shield(player_pos)


        clock.tick(60)
        pg.display.flip()

        await asyncio.sleep(0)

asyncio.run(main())