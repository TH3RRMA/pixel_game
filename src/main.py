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
WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Art Game")
clock = pygame.time.Clock()

# Load Map
tilemap = Map()
tilemap.load_map("../assets/maps/map.tmx")
player_ui_maps = [
    Map(), Map(), Map(), Map()
]

# Load different UI pages
player_ui_maps[0].load_map("../assets/player_ui.tmx")
player_ui_maps[1].load_map("../assets/player_ui_2.tmx")
player_ui_maps[2].load_map("../assets/player_ui_3.tmx")
player_ui_maps[3].load_map("../assets/player_ui_4.tmx")

current_ui_page = 0  # Index of current visible UI page


# Colors and Font
WHITE, BLACK, RED = (255, 255, 255), (0, 0, 0), (255, 0, 0)
font = pygame.font.Font("../assets/ui/pixelfont.ttf", 74)
small_font = pygame.font.Font("../assets/ui/pixelfont.ttf", 36)

# Game States and Player Setup
player = Player(300, 250, 16, 32)
player_menu_open = False
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
skills_image = pygame.image.load("../assets/skills.png").convert_alpha()

# ui_storage_original = pygame.image.load("../assets/ui/storage_ui.png").convert_alpha()

# Scale it dynamically using the game's scale factor
# UI_SCALE_FACTOR = 3  # Adjust this to match your game scaling
# ui_storage = pygame.transform.scale(
#     ui_storage_original,
#     (ui_storage_original.get_width() * UI_SCALE_FACTOR, ui_storage_original.get_height() * UI_SCALE_FACTOR)
# )


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
            tilemap.load_map(f"../assets/maps/{target_map}")  # Load new map
            # ✅ Update camera size dynamically
            camera.set_map_size(tilemap.map_pixel_width, tilemap.map_pixel_height)
            # ✅ Reset player position to start of new map
            player.pos_x, player.pos_y = 100, 100
            break  # Stop checking other exits

    # ✅ Disable player movement if UI is open
    if not ui_open and not player_menu_open:
        player.move(keys, collision_rects, dt)
        camera.update(player)


def handle_ui(keys, interactive_rects):
    """Handles UI interactions (opening/closing storage)"""

    global ui_open, key_cooldown_timer, current_storage_id, player_menu_open, current_ui_page

    # Open Player's menu by pressing Tab
    if keys[pygame.K_TAB] and key_cooldown_timer <= 0:
        if player_menu_open:
            player_menu_open = False
            print("Close player menu")
        else:
            player_menu_open = True
            print("Opening player menu")
            current_ui_page = 0  # ✅ Always start on the first page
        key_cooldown_timer = 30

    # Switching menu tabs by pressing q and e
    if player_menu_open and key_cooldown_timer <= 0:
        if keys[pygame.K_q]:
            current_ui_page = (current_ui_page - 1) % len(player_ui_maps)
            print(f"⬅️ Switched to UI page {current_ui_page + 1}")
            key_cooldown_timer = 15  # prevent rapid switching

        elif keys[pygame.K_e]:
            current_ui_page = (current_ui_page + 1) % len(player_ui_maps)
            print(f"➡️ Switched to UI page {current_ui_page + 1}")
            key_cooldown_timer = 15

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
            storage_slots = obj["slots"]
            print("📦 Opening storage UI...")
            storage_manager.add_storage(storage_id, storage_slots)  # ✅ Ensure storage exists
            current_storage_id = storage_id  # ✅ Set active storage
            ui_open = True
            key_cooldown_timer = 30  # Set cooldown
            return True  # UI action handled, stop execution

    return False  # No UI actions performed


def draw_game():
    """Handles all drawing operations"""
    screen.fill(WHITE)
    screen.set_alpha(180)

    # ✅ Always draw the game world in the background
    camera_x, camera_y = camera.offset_x, camera.offset_y
    tilemap.draw_map(screen, camera_x, camera_y, camera)
    player.draw(screen, camera)

    # ✅ Draw UI on top if active (ignore camera movement)
    if ui_open and current_storage_id:
        # draw_ui_overlay(screen)  # Function to draw UI with PNGs
        storage_manager.get_storage(current_storage_id).draw(screen, small_font)

    if player_menu_open:
        # Dim background
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Calculate centered position
        ui_x = (WIDTH - player_ui_maps[current_ui_page].map_pixel_width) // 2 * (-1)
        ui_y = (HEIGHT - player_ui_maps[current_ui_page].map_pixel_height) // 2 * (-1)

        # Draw the UI map centered on screen
        player_ui_maps[current_ui_page].draw_map(screen, ui_x, ui_y, None)
        if current_ui_page == 0:
            player.draw_skill_bar(screen, offset=(ui_x, ui_y), font=small_font)

        pygame.display.flip()
        return  # 🛑 Stop here — no inventory or HUD drawn underneath

    # ✅ Always draw inventory (even in UI mode)
    inventory.draw(screen, small_font)
    pygame.display.flip()


# Main Game Loop
running = True
while running:
    handle_events()
    update_game()
    draw_game()

pygame.quit()
sys.exit()
