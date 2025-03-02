import sys
import pygame
from game_objects import GameObject, Oven, Well, Mill
from player import Player, Camera
from inventory import Inventory
from map import Map
import os

# Initialize Pygame
pygame.init()

# Screen Setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Art Game")
clock = pygame.time.Clock()

# Load Map
tilemap = Map()
tilemap.load_map("../assets/map.tmx")

# Colors and Font
WHITE, BLACK, RED = (255, 255, 255), (0, 0, 0), (255, 0, 0)
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Game States and Player Setup
player = Player(300, 250, 16, 32)
inventory = Inventory()
inventory.add_item("Wheat", 5)
inventory.add_item("Flour", 5)

# Create Objects
oven = Oven(200, 200, 50, 50)
well = Well(400, 200, 50, 50)
mill = Mill(600, 200, 50, 50)
stone = GameObject(0, 0, 50, 50, solid=True)

# Initialize camera
camera = Camera(WIDTH, HEIGHT)
camera.set_map_size(tilemap.map_pixel_width, tilemap.map_pixel_height)
print(camera.fixed_camera)

# Define Game Objects List
game_objects = [oven, well, stone, mill]

# Interaction Handling
interaction_text = None
interaction_timer = 0
key_cooldown = False
interacting_object = None

# Helper Functions

def handle_events():
    """Handles all user input events"""
    global running, game_state, key_cooldown, interacting_object

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and not key_cooldown:
                # Check interaction
                for obj in [well, oven, mill]:
                    if player.rect.colliderect(obj.interaction_zone):
                        obj.interact(player.rect, event)
                        interacting_object = obj
                key_cooldown = True  # Start cooldown after pressing 'E'

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_e:
                key_cooldown = False

        # Handle mouse clicks (inventory or interactions)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            inventory.handle_mouse_click(screen, pygame.mouse.get_pos(), True)

        if event.type == pygame.MOUSEBUTTONUP:
            if oven.interface_open:
                if player.inventory.dragging_item and oven.handle_item_drop(pygame.mouse.get_pos(), player.inventory.dragging_item):
                    player.inventory.dragging_item = None  # Clear dragging item
            else:
                inventory.handle_mouse_release(pygame.mouse.get_pos())

def update_game():
    """Updates game logic including player movement, interactions, and camera"""
    keys = pygame.key.get_pressed()
    dt = min(clock.tick(60) / 1000.0, 1 / 30.0)  # Converts milliseconds to seconds

    collision_rects = tilemap.get_collision_objects()
    interactive_rects = tilemap.get_interactive_objects()
    exits = tilemap.get_exits()

    # Check player interactions
    for rect, target_map in exits:
        if player.rect.colliderect(rect):  # Player touched an exit
            print(f"Transitioning to {target_map}")
            tilemap.load_map(f"../assets/{target_map}")  # Load new map
            # ✅ Update camera size dynamically
            camera.set_map_size(tilemap.map_pixel_width, tilemap.map_pixel_height)
            # ✅ Reset player position to start of new map
            player.pos_x, player.pos_y = 100, 100
            break  # Stop checking other exits

    # Movement Handling
    interface_active = any(obj.interface_open for obj in game_objects)
    if not interface_active:
        player.move(keys, collision_rects, dt)

    # Camera Update
    camera.update(player)

def draw_game():
    """Handles all drawing operations"""
    screen.fill(WHITE)
    camera_x, camera_y = camera.offset_x, camera.offset_y
    tilemap.draw_map(screen, camera_x, camera_y)

    # Draw Player
    player.draw(screen, camera)

    # Draw all game objects
    for obj in game_objects:
        adjusted_rect = camera.apply(obj.rect)
        obj.draw(screen, adjusted_rect)
        obj.show_interaction_hint(screen, player.rect, small_font, adjusted_rect)

    # Draw inventory
    inventory.draw(screen, small_font)

    # Draw interactive areas (Debugging)
    for rect in tilemap.get_interactive_objects():
        adjusted_rect = pygame.Rect(rect.x - camera.offset_x, rect.y - camera.offset_y, rect.width, rect.height)
        pygame.draw.rect(screen, (0, 255, 0), adjusted_rect, 2)

    pygame.display.flip()

# Main Game Loop
running = True
while running:
    handle_events()
    update_game()
    draw_game()

pygame.quit()
sys.exit()
