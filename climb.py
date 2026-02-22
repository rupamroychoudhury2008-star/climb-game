import pygame
import random
import sys
import math

pygame.init()

# Screen settings
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wall Climber")
clock = pygame.time.Clock()

# --- Core Variables ---
player_w, player_h = 20, 40
left_wall_x = 60
right_wall_x = WIDTH - 60 - player_w

def reset_game():
    global wall_side, player_y, climb_speed, score, true_score, is_jumping
    global jump_progress, jump_speed, obstacles, particles, game_state, camera_y
    
    wall_side = 0 
    player_y = HEIGHT - 150
    climb_speed = 6
    score = 0
    true_score = 0.0
    camera_y = 0 # Used for scrolling textures
    
    is_jumping = False
    jump_progress = 0.0 
    jump_speed = 0.06
    
    obstacles = []
    particles = []
    game_state = "PLAYING"

# --- Obstacles & Particles ---
def spawn_obstacle():
    if game_state == "PLAYING":
        side = random.choice([0, 1])
        x = left_wall_x if side == 0 else right_wall_x
        obstacles.append({"rect": pygame.Rect(x, -50, player_w, 30), "side": side})

def spawn_dust(x, y, is_sliding):
    # Slide kicks dust up, climbing kicks dust down
    vy = random.uniform(-2, -0.5) if is_sliding else random.uniform(0.5, 3)
    vx = random.uniform(-1, 1)
    particles.append({"x": x, "y": y, "vx": vx, "vy": vy, "life": 255, "size": random.randint(3, 6)})

pygame.time.set_timer(pygame.USEREVENT, 1500)
reset_game()

# --- Game Loop ---
while True:
    screen.fill((30, 30, 40)) 
    
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.USEREVENT:
            spawn_obstacle()
        if event.type == pygame.KEYDOWN:
            if game_state == "PLAYING" and event.key == pygame.K_SPACE and not is_jumping:
                is_jumping = True
                jump_progress = 0.0
            if game_state == "GAME_OVER" and event.key == pygame.K_r:
                reset_game()

    keys = pygame.key.get_pressed()
    
    if game_state == "PLAYING":
        # 2. Climbing Logic
        is_climbing = keys[pygame.K_UP] and not is_jumping
        is_sliding = not keys[pygame.K_UP] and not is_jumping

        if is_climbing:
            true_score += 0.1
            score = int(true_score)
            camera_y += climb_speed
            for obs in obstacles:
                obs["rect"].y += climb_speed
                
            # Spawn climbing dust
            dust_x = left_wall_x + player_w if wall_side == 0 else right_wall_x
            spawn_dust(dust_x, player_y + player_h, False)

        elif is_sliding:
            camera_y -= 2 
            for obs in obstacles:
                obs["rect"].y -= 2 
                
            # Spawn sliding dust
            dust_x = left_wall_x + player_w if wall_side == 0 else right_wall_x
            spawn_dust(dust_x, player_y, True)

        # 3. Jumping Logic
        if is_jumping:
            jump_progress += jump_speed
            if jump_progress >= 1.0:
                is_jumping = False
                wall_side = 1 - wall_side 
                
            start_x = left_wall_x if wall_side == 0 else right_wall_x
            end_x = right_wall_x if wall_side == 0 else left_wall_x
            
            current_x = start_x + (end_x - start_x) * jump_progress
            arc_height = math.sin(jump_progress * math.pi) * 50
            current_y = player_y - arc_height
            player_rect = pygame.Rect(current_x, current_y, player_w, player_h)
        else:
            current_x = left_wall_x if wall_side == 0 else right_wall_x
            player_rect = pygame.Rect(current_x, player_y, player_w, player_h)

        # Collision Check
        for obs in obstacles:
            if player_rect.colliderect(obs["rect"]):
                game_state = "GAME_OVER"

        # Cleanup off-screen obstacles
        obstacles = [obs for obs in obstacles if obs["rect"].y < HEIGHT + 100 and obs["rect"].y > -200]

    # 4. Draw the Walls (With Scrolling Textures)
    pygame.draw.rect(screen, (70, 70, 75), (0, 0, left_wall_x, HEIGHT))
    pygame.draw.rect(screen, (70, 70, 75), (right_wall_x + player_w, 0, WIDTH, HEIGHT))
    
    # Draw scrolling lines on the walls to show speed
    for y in range(0, HEIGHT + 50, 50):
        scroll_y = (y + camera_y) % HEIGHT
        pygame.draw.line(screen, (50, 50, 55), (0, scroll_y), (left_wall_x, scroll_y), 3)
        pygame.draw.line(screen, (50, 50, 55), (right_wall_x + player_w, scroll_y), (WIDTH, scroll_y), 3)

    # 5. Draw Particles
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 15
        p["size"] -= 0.2
        if p["life"] <= 0 or p["size"] <= 0:
            particles.remove(p)
        else:
            surf = pygame.Surface((int(p["size"]), int(p["size"])))
            surf.fill((200, 200, 200))
            surf.set_alpha(p["life"])
            screen.blit(surf, (p["x"], p["y"]))

    # 6. Draw Obstacles & Player
    for obs in obstacles:
        pygame.draw.rect(screen, (255, 60, 60), obs["rect"], border_radius=4)

    color = (50, 255, 200) if not is_jumping else (255, 255, 0)
    # Flash red if game over
    if game_state == "GAME_OVER": color = (255, 0, 0)
    pygame.draw.rect(screen, color, player_rect, border_radius=5)
    
    # 7. UI / Score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Height: {score}m", True, (255, 255, 255))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

    if game_state == "GAME_OVER":
        go_font = pygame.font.SysFont(None, 48)
        go_text = go_font.render("CRASHED!", True, (255, 50, 50))
        sub_text = font.render("Press 'R' to Restart", True, (200, 200, 200))
        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 + 20))

    pygame.display.flip()
    clock.tick(60)
