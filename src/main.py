import sys
import pygame
from game_objects import GameObject, Oven, Well, Mill
from player import Player, Camera
from inventory import Inventory
from map import Map
import os
print("Current Working Directory:", os.getcwd())


# Initialize Pygame
pygame.init()

# Screen Setup
WORLD_WIDTH, WORLD_HEIGHT = 6400, 6400
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Art Game")
clock = pygame.time.Clock()

# Maps laden
tilemap = Map()  # Erstellt eine Instanz der Map-Klasse
tilemap.load_map("../assets/map.tmx")  # Map-Datei laden

# Colors and Font
WHITE, BLACK, RED = (255, 255, 255), (0, 0, 0), (255, 0, 0)
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Game States and Player Setup
game_state = "start"
player = Player(400, 300, 16, 32)
inventory = Inventory()
inventory.add_item("Wheat", 5)
inventory.add_item("Flour", 5)


# Create Objects
oven = Oven(200, 200, 50, 50)
well = Well(400, 200, 50, 50)
mill = Mill(600, 200, 50, 50)
stone = GameObject(0, 0, 50, 50, solid=True)

# Define Interaction Zone (in front of the oven)

interaction_text = None  # For interaction message
interaction_timer = 0  # Timer for displaying the message

# Initialize camera
camera = Camera(WIDTH, HEIGHT)

# Main Loop
running = True
key_cooldown = False  # To prevent rapid toggling of the interface
interacting_object = None  # To track which object is being interacted with


while running:
    # print("running")
    screen.fill(WHITE)
    camera_x, camera_y = camera.offset_x, camera.offset_y
    tilemap.draw_map(screen, camera_x, camera_y)
    keys = pygame.key.get_pressed()
    dt = clock.tick(60)  # / 1000  # Delta time for frame-independent movement
    print(f"FPS: {clock.get_fps():.2f}")  # Debug FPS

    mouse_pressed = pygame.mouse.get_pressed()[0]

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Debugging mouse pos
        # if event.type == pygame.MOUSEBUTTONUP:  # Trigger on mouse release
        #     mouse_pos = pygame.mouse.get_pos()
        #     x, y = (200 + 50, 50 + 100)  # Coordinates for slot
        #     slot_rect = pygame.Rect(x, y, 80, 80)  # Create a slot rectangle
        #     if slot_rect.collidepoint(mouse_pos):  # Check if mouse is within the slot
        #         print(f"Mouse released in slot at {mouse_pos} within {slot_rect}.")
        #     else:
        #         print(f"Mouse released outside the slot at {mouse_pos}.")

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed = pygame.mouse.get_pressed()[0]
                inventory.handle_mouse_click(screen, mouse_pos, mouse_pressed)

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            if oven.interface_open:
                print(f"{player.inventory.dragging_item}")
                # Try dropping into oven
                if player.inventory.dragging_item and oven.handle_item_drop(mouse_pos, player.inventory.dragging_item):
                    print(f"{player.inventory.dragging_item} dropped into oven.")
                    player.inventory.dragging_item = None  # Clear dragging item
            else:
                # Handle general inventory release
                inventory.handle_mouse_release(mouse_pos)

        if game_state == "play":
            # Handle interactions with the well
            well.handle_mouse_events(event, player.inventory)

        # start screen
        if game_state == "start" and event.type == pygame.KEYDOWN:
            game_state = "play"  # starts the game

        # Interaction Check (only for when game is in play state)
        if game_state == "play" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and not key_cooldown:
                # Check interaction for each object if player is near
                for obj in [well, oven, mill]:
                    if player.rect.colliderect(obj.interaction_zone):
                        # If not interacting yet, start interaction
                        obj.interact(player.rect, event)
                        interacting_object = obj  # Track which object is being interacted with

                key_cooldown = True  # Start cooldown after pressing 'E'

    # Reset key cooldown after the key is released
    if keys[pygame.K_e] == 0:  # When 'E' is released
        key_cooldown = False

    if game_state == "start":
        # create start screen
        text = font.render("Press any key to start", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    elif game_state == "play":

        # List of all game objects
        game_objects = [oven, well, stone, mill]
        collision_rects = tilemap.get_collision_objects()
        interactive_rects = tilemap.get_interactive_objects()
        exits = tilemap.get_exits()

        for rect in interactive_rects:
            adjusted_rect = pygame.Rect(rect.x - camera.offset_x, rect.y - camera.offset_y, rect.width, rect.height)
            pygame.draw.rect(screen, (0, 255, 0), adjusted_rect, 2)

        for rect, target_map in exits:
            if player.rect.colliderect(rect):  # Player touched an exit
                print(f"Transitioning to {target_map}")
                tilemap.load_map(f"../assets/{target_map}")  # Load the new map
                player.rect.topleft = (100, 100)  # Reset player position
                break

        # Player interaction check
        for rect in interactive_rects:
            if player.rect.colliderect(rect) and keys[pygame.K_e]:  # Press "E" to interact
                print("Interacted with object!")

        # Check if interface is open for any object
        interface_active = any(obj.interface_open for obj in game_objects)
        if not interface_active:  # Allow movement only if no interface is active
            keys = pygame.key.get_pressed()  # Check keys every frame
            player.move(keys, collision_rects)

        # Collision detection for all objects
        # for obj in game_objects:
        #     if obj.handle_collision(player):
        #         player.rect.x, player.rect.y = player.old_x, player.old_y  # Revert to old position
        #         break  # Stop checking further once a collision is detected

        # Boundaries
        if player.rect.x < 0: player.rect.x = 0
        if player.rect.y < 0: player.rect.y = 0
        if player.rect.x > WIDTH - player.rect.width: player.rect.x = WIDTH - player.rect.width
        if player.rect.y > HEIGHT - player.rect.height: player.rect.y = HEIGHT - player.rect.height

        # Update camera
        camera.update(player, WORLD_WIDTH, WORLD_HEIGHT)

        # Draw Player
        adjusted_player_rect = camera.apply(player.rect)
        player.draw(screen)  # , adjusted_player_rect)
        inventory.draw(screen, small_font)

        # Draw all game objects
        for obj in game_objects:
            adjusted_rect = camera.apply(obj.rect)
            obj.draw(screen, adjusted_rect)
            obj.show_interaction_hint(screen, player.rect, small_font, adjusted_rect)

        # Draw the interfaces (make sure to draw interfaces after objects)
        for obj in game_objects:
            obj.update_interface()
            obj.draw_interface(screen, small_font)

    pygame.display.flip()
    # print("Flipping screen...")
    clock.tick(60)

pygame.quit()
sys.exit()
