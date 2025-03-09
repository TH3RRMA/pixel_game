import sys
import pygame
# from game_objects_old import GameObject, Oven, Well, Mill
from player import Player, Camera
from inventory import Inventory
from storage import Storage, StorageManager
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

# Initialize camera
camera = Camera(WIDTH, HEIGHT)
camera.set_map_size(tilemap.map_pixel_width, tilemap.map_pixel_height)

# Interaction Handling
interaction_text = None
interaction_timer = 0
key_cooldown = False
key_cooldown_timer = 0
interacting_object = None
global ui_open  # ✅ Track if UI is open
ui_open = False  # ✅ Start with UI closed
storage_manager = StorageManager()
# storage_manager.add_storage("storage_1", max_slots=4)

# Load UI Images
ui_storage_original = pygame.image.load("../assets/ui/storage_ui.png").convert_alpha()

# Scale it dynamically using the game's scale factor
UI_SCALE_FACTOR = 3  # Adjust this to match your game scaling
ui_storage = pygame.transform.scale(
    ui_storage_original,
    (ui_storage_original.get_width() * UI_SCALE_FACTOR, ui_storage_original.get_height() * UI_SCALE_FACTOR)
)


# Helper Functions
def handle_events():
    """Handles all user input events"""
    global running, key_cooldown

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and not key_cooldown:
                key_cooldown = True  # ✅ Set cooldown when key is pressed

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_e:
                key_cooldown = False  # ✅ Reset cooldown when key is released

        # ✅ Handle Storage UI
        if ui_open and current_storage_id:
            storage = storage_manager.get_storage(current_storage_id)
            if storage:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    storage.handle_mouse_click(pygame.mouse.get_pos(),
                                               inventory)  # ✅ Handle dragging from storage
                if event.type == pygame.MOUSEBUTTONUP:
                    storage.handle_mouse_release(pygame.mouse.get_pos(), inventory)  # ✅ Drop into inventory

        # ✅ Always allow inventory dragging
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            inventory.handle_mouse_click(screen, pygame.mouse.get_pos(), True)

        if event.type == pygame.MOUSEBUTTONUP:
            inventory.handle_mouse_release(pygame.mouse.get_pos())  # ✅ Drop within inventory


def update_game():
    """Updates game logic including player movement, interactions, and camera"""
    keys = pygame.key.get_pressed()
    dt = min(clock.tick(60) / 1000.0, 1 / 30.0)  # Converts milliseconds to seconds

    collision_rects = tilemap.get_collision_objects()
    interactive_rects = tilemap.get_interactive_objects()
    exits = tilemap.get_exits()

    global key_cooldown_timer, ui_open  # ✅ Track if UI is open

    # ✅ Reduce cooldown timer
    if key_cooldown_timer > 0:
        key_cooldown_timer -= 1  # Decrease every frame

    # ✅ Handle UI toggling
    if handle_ui(keys, interactive_rects):
        return  # Stop execution if UI is active

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

    # ✅ Disable player movement if UI is open
    if not ui_open:
        player.move(keys, collision_rects, dt)
        camera.update(player)


def handle_ui(keys, interactive_rects):
    """Handles UI interactions (opening/closing storage)"""

    global ui_open, key_cooldown_timer, current_storage_id

    # ✅ Close UI when 'E' is pressed
    if ui_open and keys[pygame.K_e] and key_cooldown_timer <= 0:
        print("🔙 Closing UI, returning to game world...")
        ui_open = False
        current_storage_id = None  # ✅ Reset storage tracking
        key_cooldown_timer = 30  # Set cooldown
        return True  # UI action handled, stop execution

    # ✅ Open UI when interacting with storage
    for obj in interactive_rects:
        if player.rect.colliderect(obj["rect"]) and keys[pygame.K_e] and key_cooldown_timer <= 0:
            storage_id = obj["name"]  # ✅ Get storage name from map
            print("📦 Opening storage UI...")
            storage_manager.add_storage(storage_id, 4)  # ✅ Ensure storage exists
            current_storage_id = storage_id  # ✅ Set active storage
            ui_open = True
            key_cooldown_timer = 30  # Set cooldown
            return True  # UI action handled, stop execution

    return False  # No UI actions performed


def draw_game():
    """Handles all drawing operations"""
    screen.fill(WHITE)

    # ✅ Always draw the game world in the background
    camera_x, camera_y = camera.offset_x, camera.offset_y
    tilemap.draw_map(screen, camera_x, camera_y, camera)
    player.draw(screen, camera)

    # ✅ Draw UI on top if active (ignore camera movement)
    if ui_open and current_storage_id:
        # draw_ui_overlay(screen)  # Function to draw UI with PNGs
        storage_manager.get_storage(current_storage_id).draw(screen, small_font)

    # ✅ Always draw inventory (even in UI mode)
    inventory.draw(screen, small_font)
    pygame.display.flip()


def draw_ui_overlay(screen):
    """Draws the UI using images instead of rectangles."""

    # UI Background (Storage Interface)
    # screen.blit(ui_storage, (WIDTH // 2 - ui_storage.get_width() // 2, HEIGHT // 2 - ui_storage.get_height() // 2))  # Position the UI background

    # # Close Button
    # screen.blit(button_close, (600, 120))  # Adjust position as needed
    #
    # # Inventory Slots (Example)
    # for i in range(3):  # Example: 3 slots
    #     slot_x = 150 + (i * 100)  # Space out slots
    #     slot_y = 250
    #     screen.blit(slot_image, (slot_x, slot_y))  # Draw slot image


# Main Game Loop
running = True
while running:
    handle_events()
    update_game()
    draw_game()

pygame.quit()
sys.exit()
