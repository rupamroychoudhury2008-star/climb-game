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

# --- Player Variables ---
# wall_side: 0 = Left Wall, 1 = Right Wall
wall_side = 0 
player_w, player_h = 20, 40
player_y = HEIGHT - 150
climb_speed = 6
score = 0

# Walls
left_wall_x = 60
right_wall_x = WIDTH - 60 - player_w

# --- Jumping Mechanics ---
is_jumping = False
jump_progress = 0.0 # Goes from 0.0 to 1.0
jump_speed = 0.06

# --- Obstacles ---
obstacles = []
def spawn_obstacle():
    side = random.choice([0, 1])
    x = left_wall_x if side == 0 else right_wall_x
    # Spawn above the screen
    obstacles.append({"rect": pygame.Rect(x, -50, player_w, 30), "side": side})

# Timer to spawn obstacles every 1.5 seconds
pygame.time.set_timer(pygame.USEREVENT, 1500)

while True:
    screen.fill((30, 30, 40)) # Dark night sky
    
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.USEREVENT:
            spawn_obstacle()
        if event.type == pygame.KEYDOWN:
            # Press SPACE to leap to the other wall
            if event.key == pygame.K_SPACE and not is_jumping:
                is_jumping = True
                jump_progress = 0.0

    keys = pygame.key.get_pressed()
    
    # 2. Climbing Logic (The Camera Trick)
    # Instead of moving the player up, we push the obstacles down!
    if keys[pygame.K_UP] and not is_jumping:
        score += 1
        for obs in obstacles:
            obs["rect"].y += climb_speed
    elif not is_jumping:
        # If you stop climbing, you slowly slide down the wall
        for obs in obstacles:
            obs["rect"].y -= 2 

    # 3. Jumping (Wall to Wall) Logic
    if is_jumping:
        jump_progress += jump_speed
        if jump_progress >= 1.0:
            is_jumping = False
            wall_side = 1 - wall_side # Swap sides (0 becomes 1, 1 becomes 0)
            
        # Figure out where we are in the air
        start_x = left_wall_x if wall_side == 0 else right_wall_x
        end_x = right_wall_x if wall_side == 0 else left_wall_x
        
        # Move smoothly across the screen
        current_x = start_x + (end_x - start_x) * jump_progress
        
        # Add a little "arc" to the jump so it looks cool
        arc_height = math.sin(jump_progress * math.pi) * 50
        current_y = player_y - arc_height
        
        player_rect = pygame.Rect(current_x, current_y, player_w, player_h)
    else:
        # Stick to the wall
        current_x = left_wall_x if wall_side == 0 else right_wall_x
        player_rect = pygame.Rect(current_x, player_y, player_w, player_h)

    # 4. Draw the Walls
    pygame.draw.rect(screen, (80, 80, 80), (0, 0, left_wall_x, HEIGHT)) # Left Wall
    pygame.draw.rect(screen, (80, 80, 80), (right_wall_x + player_w, 0, WIDTH, HEIGHT)) # Right Wall

    # 5. Draw Obstacles & Check Collisions
    for obs in obstacles[:]:
        pygame.draw.rect(screen, (255, 50, 50), obs["rect"], border_radius=4)
        
        # CRASH!
        if player_rect.colliderect(obs["rect"]):
            print(f"CRASH! Final Height: {score}m")
            pygame.quit()
            sys.exit()
            
        # Remove obstacles once they go way off the bottom
        if obs["rect"].y > HEIGHT + 100:
            obstacles.remove(obs)

    # 6. Draw the Player
    color = (50, 255, 200) if not is_jumping else (255, 255, 0)
    pygame.draw.rect(screen, color, player_rect, border_radius=5)
    
    # 7. UI / Score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Height: {score}m", True, (255, 255, 255))
    screen.blit(score_text, (WIDTH // 2 - 60, 20))

    pygame.display.flip()
    clock.tick(60)