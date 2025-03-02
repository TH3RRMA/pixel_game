import pygame
from inventory import Inventory


class Player:
    def __init__(self, x, y, width, height, speed=5, sprite_sheet_path="../assets/player.png"):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.inventory = Inventory()  # Add inventory to the player
        self.old_x = None
        self.old_y = None

        # Load the sprite sheet
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()

        # Extract individual frames (assuming 4 directions, 3 frames per direction)
        self.frames = {
            "right": [self.get_sprite(2, i) for i in range(0, 6)],
            "up": [self.get_sprite(2, i) for i in range(6, 12)],
            "left": [self.get_sprite(2, i) for i in range(12, 18)],
            "down": [self.get_sprite(2, i) for i in range(18, 24)]
        }

        self.current_direction = "down"
        self.current_frame = 0
        self.animation_counter = 0

    def get_sprite(self, row, col, sprite_height=32, sprite_width=16, scale_factor=3):
        """ Extracts a sprite from the sprite sheet. """

        x = col * sprite_width
        y = row * sprite_height

        # Debug: Draw a red rectangle around the selected sprite
        debug_sprite = self.sprite_sheet.copy()
        pygame.draw.rect(debug_sprite, (255, 0, 0), (x, y, sprite_width, sprite_height), 1)

        # Show the full sheet with the selection
        pygame.image.save(debug_sprite, "debug_spritesheet.png")  # Saves a debug image

        # Get the original sprite
        sprite = self.sprite_sheet.subsurface(pygame.Rect(x, y, sprite_width, sprite_height))

        # Scale up the sprite
        scaled_size = (sprite_width * scale_factor, sprite_height * scale_factor)
        return pygame.transform.scale(sprite, scaled_size)

    def move(self, keys, collision_rects):
        """
        Moves the player based on key input.
        """
        self.old_x, self.old_y = self.rect.x, self.rect.y
        moving = False  # Track if player is moving

        if keys[pygame.K_w]:
            self.rect.y -= self.speed
            self.current_direction = "up"
            moving = True
        if keys[pygame.K_s]:
            self.rect.y += self.speed
            self.current_direction = "down"
            moving = True
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.current_direction = "left"
            moving = True
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.current_direction = "right"
            moving = True

        # Collision check
        if any(self.rect.colliderect(rect) for rect in collision_rects):
            self.rect.x, self.rect.y = self.old_x, self.old_y  # Revert if collision

        # Animate if moving
        if moving:
            self.animation_counter += 1
            if self.animation_counter % 10 == 0:  # Change frame every 10 ticks
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.current_direction])

    def stop_movement(self):
        """ Stops player movement immediately. """
        self.current_frame = 0  # Reset to idle frame when key is released

    def draw(self, screen):
        """ Draws the current sprite on screen. """
        current_sprite = self.frames[self.current_direction][self.current_frame]
        screen.blit(current_sprite, self.rect.topleft)

    # def add_item(self, name, count):
    #     """
    #     Adds an item to the player's inventory or updates the count if it already exists.
    #     """
    #     for item in self.inventory.items:
    #         if item["name"] == name:
    #             item["count"] += count
    #             return
    #     self.inventory.items.append({"name": name, "count": count})


class Camera:
    def __init__(self, width, height):
        self.offset_x = 0
        self.offset_y = 0
        self.width = width
        self.height = height

    def update(self, player, world_width, world_height):
        """
        Updates the camera position based on the player.
        Includes smooth movement and boundary constraints.
        """
        # Target position to center the player
        target_x = player.rect.centerx - self.width // 2
        target_y = player.rect.centery - self.height // 2

        # Smooth transition (lerp effect)
        self.offset_x += (target_x - self.offset_x) * 0.1  # Adjust the smoothing factor here (0.1 is smooth)
        self.offset_y += (target_y - self.offset_y) * 0.1

        # Clamp the camera within world boundaries
        self.offset_x = max(0, min(self.offset_x, world_width - self.width))
        self.offset_y = max(0, min(self.offset_y, world_height - self.height))

    def apply(self, rect):
        """
        Adjusts the given rect's position by the camera's offset.
        """
        return rect.move(-self.offset_x, -self.offset_y)
