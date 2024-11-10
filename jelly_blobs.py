import pygame
import random
import sys
import math
import json
import os

pygame.init()
screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Jelly Blob of Doom")
clock = pygame.time.Clock()
player_size = 5
player_x = screen_width // 2
player_y = screen_height // 2
player_speed = 3
blobs = []
time = 0
blobs_eaten = 0
biggest_blob_eaten = 0
distance_traveled = 0
start_time = 0
save_file = "jelly_save.json"


def generate_blob():
    size = random.randint(5, int(screen_height * 0.224))
    max_speed = (1.0 - 0.8 * (size / (screen_height * 0.224))) * screen_width
    speed = (random.uniform(max_speed / 2, max_speed) / 60) * (2/3) * 0.8
    if random.random() < 0.5:
        x = -size
        direction = 1
    else:
        x = screen_width + size
        direction = -1
    y = random.randint(0, screen_height - size)
    color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    return {'x': x, 'y': y, 'size': size, 'speed': speed * direction, 'offset': 0, 'phase': 0, 'color': color}

def save_game():
    data = {
        "player_size": player_size,
        "player_x": player_x,
        "player_y": player_y,
        "blobs": blobs,
        "time": time,
        "blobs_eaten": blobs_eaten,
        "biggest_blob_eaten": biggest_blob_eaten,
        "distance_traveled": distance_traveled,
        "start_time": start_time
    }
    with open(save_file, "w") as f:
        json.dump(data, f)

def load_game():
    global player_size, player_x, player_y, blobs, time, blobs_eaten, biggest_blob_eaten, distance_traveled, start_time, game_paused
    if os.path.exists(save_file):
        with open(save_file, "r") as f:
            data = json.load(f)
        player_size = data["player_size"]
        player_x = data["player_x"]
        player_y = data["player_y"]
        blobs = data["blobs"]
        for blob in blobs:
            blob['color'] = tuple(blob['color'])
        time = data["time"]
        blobs_eaten = data["blobs_eaten"]
        biggest_blob_eaten = data["biggest_blob_eaten"]
        distance_traveled = data["distance_traveled"]
        start_time = data["start_time"]
        game_paused = True

if os.path.exists(save_file):
    load_question = True
    while load_question:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    load_game()
                    load_question = False
                elif event.key == pygame.K_n:
                    load_question = False

        font = pygame.font.Font(None, 74)
        question_text = font.render("Reload existing savegame? [y/n]", True, (255, 255, 255))
        question_rect = question_text.get_rect(center=(screen_width / 2, screen_height / 2))
        screen.fill((100, 70, 30))
        screen.blit(question_text, question_rect)
        pygame.display.flip()
        clock.tick(30)

running = True
game_over = False
game_paused = False

if start_time == 0:
    start_time = pygame.time.get_ticks()

while running:
    time += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if not game_over:
                    save_game()
                running = False
            elif event.key == pygame.K_SPACE and game_over:
                running = False
            elif event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                game_paused = False

    if not game_over and not game_paused:
        keys = pygame.key.get_pressed()
        prev_x, prev_y = player_x, player_y
        if keys[pygame.K_LEFT]:
            player_x = max(0, player_x - player_speed)
        if keys[pygame.K_RIGHT]:
            player_x = min(screen_width - player_size, player_x + player_speed)
        if keys[pygame.K_UP]:
            player_y = max(0, player_y - player_speed)
        if keys[pygame.K_DOWN]:
            player_y = min(screen_height - player_size, player_y + player_speed)
        distance_traveled += ((player_x - prev_x)**2 + (player_y - prev_y)**2)**0.5

        if random.random() < 0.1 and len(blobs) < 50:
            blobs.append(generate_blob())

    screen.fill((100, 70, 30))

    for blob in blobs[:]:
        if not game_over:
            blob['x'] += blob['speed']
            blob['phase'] = (blob['phase'] + 0.1) % (2 * math.pi)
            blob['offset'] = (2 * math.sin(blob['phase'])) * 0.6 * 0.6 # Reduced oscillation to 60% (multiplied by 0.6)

            width = blob['size'] * (1 + (0.25 * math.sin(2 * blob['phase'])) * 0.6 * 0.6)  # Reduced oscillation
            height = width * 0.85

        blob_rect = pygame.Rect(blob['x'], blob['y'] + blob['offset'], width, height)
        pygame.draw.ellipse(screen, blob['color'], blob_rect)

        if blob['x'] < -blob['size'] or blob['x'] > screen_width + blob['size']:
            blobs.remove(blob)

        if not game_over:
            dist = ((player_x + player_size / 2 - (blob['x'] + width / 2))**2 + (player_y + player_size / 2 - (blob['y'] + height / 2 + blob['offset']))**2)**0.5

            if blob['size'] > player_size and dist < blob['size'] / 2:
                time_survived = (pygame.time.get_ticks() - start_time) / 1000
                efficiency = (blobs_eaten / time_survived) * 60 if time_survived > 0 else 0
                font = pygame.font.Font(None, 74)
                text = font.render(f"Game Over! Score: {int(player_size)}", True, (255, 255, 255))
                text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2 - 100))
                small_font = pygame.font.Font(None, 30)
                stats_text = small_font.render(f"Blobs Eaten: {blobs_eaten}, Biggest: {int(biggest_blob_eaten)}, Time: {int(time_survived)}s, Distance: {int(distance_traveled)}, Efficiency: {efficiency:.1f} blobs/min", True, (180, 180, 180))
                stats_rect = stats_text.get_rect(center=(screen_width / 2, screen_height / 2))
                exit_text = small_font.render("<press SPACE to exit>", True, (150, 150, 150))
                exit_text_rect = exit_text.get_rect(center=(screen_width / 2, screen_height / 2 + 100))
                game_over = True

            elif blob['size'] < player_size and dist < player_size / 2:
                player_size += blob['size'] / 50
                blobs_eaten += 1
                biggest_blob_eaten = max(biggest_blob_eaten, blob['size'])
                blobs.remove(blob)

    if game_over:
            screen.blit(text, text_rect)
            screen.blit(stats_text, stats_rect)
            screen.blit(exit_text, exit_text_rect)

    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    pygame.draw.ellipse(screen, (0, 0, 255), player_rect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()


