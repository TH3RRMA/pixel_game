import pygame
from inventory import Inventory


class Player:
    def __init__(self, x, y, width, height, speed=200, sprite_sheet_path="../assets/player.png"):
        self.pos_x = float(x)  # Store precise position
        self.pos_y = float(y)

        self.sprite_width = width  # Width of the sprite
        self.sprite_height = height  # Height of the full sprite

        # Adjusted collision box (smaller and lower)
        self.collision_width = width * 3
        self.collision_height = height
        self.collision_offset_y = height + self.collision_height  # Move it to the legs

        self.rect = pygame.Rect(x, y + self.collision_offset_y, self.collision_width, self.collision_height)
        self.speed = speed
        self.inventory = Inventory()  # Add inventory to the player
        self.old_x, self.old_y = None, None
        self.current_direction = "down"
        self.current_frame = 0
        self.animation_counter = 0

        # Load the sprite sheet
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()

        # Extract individual frames (assuming 4 directions, 3 frames per direction)
        self.frames = {
            "right": {
                "walk": [self.get_sprite(2, i) for i in range(0, 6)],
                "idle": [self.get_sprite(1, i) for i in range(0, 6)]
            },
            "up": {
                "walk": [self.get_sprite(2, i) for i in range(6, 12)],
                "idle": [self.get_sprite(1, i) for i in range(6, 12)]
            },
            "left": {
                "walk": [self.get_sprite(2, i) for i in range(12, 18)],
                "idle": [self.get_sprite(1, i) for i in range(12, 18)]
            },
            "down": {
                "walk": [self.get_sprite(2, i) for i in range(18, 24)],
                "idle": [self.get_sprite(1, i) for i in range(18, 24)]
            }
        }
        self.current_state = "idle"
        self.skill_sheet = pygame.image.load("../assets/skills.png").convert_alpha()
        self.icon_width = 48
        self.icon_height = 16
        self.skill_ui_pos = (200, 300)  # relative to UI
        self.skill_level = [
            {"name": "cooking", "level": 2, "color": 0},
            {"name": "serving", "level": 1, "color": 1},
            {"name": "leading", "level": 2, "color": 2},
            {"name": "dummheit", "level": 4, "color": 3},
            {"name": "leading", "level": 2, "color": 4}
        ]

    def get_sprite(self, row, col, sprite_height=32, sprite_width=16, scale_factor=3):
        """ Extracts a sprite from the sprite sheet. """

        x = col * sprite_width
        y = row * sprite_height

        # Get the original sprite
        sprite = self.sprite_sheet.subsurface(pygame.Rect(x, y, sprite_width, sprite_height))

        # Scale up the sprite
        scaled_size = (sprite_width * scale_factor, sprite_height * scale_factor)
        return pygame.transform.scale(sprite, scaled_size)

    def move(self, keys, collision_rects, dt):
        """
        Moves the player based on key input.
        """
        self.old_x, self.old_y = self.pos_x, self.pos_y
        moving = False  # Track if player is moving

        move_amount = self.speed * dt  # ✅ Normalize movement speed using `dt`

        if keys[pygame.K_w]:
            self.pos_y -= move_amount
            self.current_direction = "up"
            moving = True
        if keys[pygame.K_s]:
            self.pos_y += move_amount
            self.current_direction = "down"
            moving = True
        if keys[pygame.K_a]:
            self.pos_x -= move_amount
            self.current_direction = "left"
            moving = True
        if keys[pygame.K_d]:
            self.pos_x += move_amount
            self.current_direction = "right"
            moving = True

        # Convert float positions back to integers for Pygame Rect
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y) + self.collision_offset_y  # Adjust so it's around the legs

        # Collision check
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                print(f"🚧 COLLISION at {self.rect} with {rect} | Position: ({self.pos_x}, {self.pos_y})")  # Debug print
                # Revert movement if a collision happens
                self.pos_x, self.pos_y = self.old_x, self.old_y
                self.rect.x = int(self.pos_x)
                self.rect.y = int(self.pos_y) + self.collision_offset_y  # Keep offset
                break  # Stop checking further collisions

        # Animate if moving
        if moving:
            self.animation_counter += 1
            if self.animation_counter % 10 == 0:  # Change frame every 10 ticks
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.current_direction]["walk"])
            self.current_state = "walk"
        else:
            self.animation_counter += 1
            if self.animation_counter % 10 == 0:  # slower idle animation
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.current_direction]["idle"])
            self.current_state = "idle"

    def draw(self, screen, camera):
        """ Draws the current sprite on screen. """
        current_sprite = self.frames[self.current_direction][self.current_state][self.current_frame]

        if camera.fixed_camera:
            # ✅ If map is small, draw player at actual position
            screen_x = round(self.pos_x) - camera.offset_x
            screen_y = round(self.pos_y) - camera.offset_y
        else:
            # ✅ If map is large, keep player centered on screen
            screen_x = round(self.pos_x) - camera.offset_x  # screen.get_width() // 2 - current_sprite.get_width() // 2
            screen_y = round(self.pos_y) - camera.offset_y  # screen.get_height() // 2 - current_sprite.get_height() // 2

        screen.blit(current_sprite, (screen_x, screen_y))

        # ✅ Draw collision box from self.rect
        debug_rect = camera.apply(self.rect)  # Adjust collision box based on camera movement

        # Debug: Draw the correctly aligned collision box
        pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)  # Red box (1px border)

    def get_skill_icon(self, col, row):
        rect = pygame.Rect(col * self.icon_width, row * self.icon_height,
                           self.icon_width, self.icon_height)
        return self.skill_sheet.subsurface(rect)

    def draw_skill_bar(self, screen, offset=(0, 0), font=None):
        x_base, y_base = self.skill_ui_pos[0] + offset[0], self.skill_ui_pos[1] + offset[1]
        for i, skill in enumerate(self.skill_level):
            icon = self.get_skill_icon(skill["level"], skill["color"])
            x = x_base
            y = y_base + i * (self.icon_height + 30)
            # 🖼 scale the icon before blitting
            scaled_icon = pygame.transform.scale(
                icon,
                (self.icon_width * 3, self.icon_height * 3)
            )
            screen.blit(scaled_icon, (x, y))

            if font:
                label = font.render(skill["name"], True, (0, 0, 0))  # white text
                screen.blit(label, (x + self.icon_width * 3 + 15, y + 5))


class Camera:
    def __init__(self, width, height):
        self.offset_x = 0
        self.offset_y = 0
        self.width = width
        self.height = height
        self.map_width = 0  # Will be set when the map is loaded
        self.map_height = 0
        self.fixed_camera = False  # Determines if the camera should be fixed

    def set_map_size(self, map_width, map_height):
        """Sets the size of the map dynamically after loading."""
        self.map_width = map_width
        self.map_height = map_height

        # ✅ If the map is smaller than the screen, fix the camera
        if self.map_width <= self.width and self.map_height <= self.height:
            self.fixed_camera = True
            self.offset_x = -(self.width - self.map_width) // 2
            self.offset_y = -(self.height - self.map_height) // 2
        else:
            self.fixed_camera = False

    def update(self, player):
        """
        Updates the camera position based on the player.
        - Keeps the player centered if the map is large.
        - Allows free movement if the map is small.
        """
        print(f"📌 Player: ({player.pos_x}, {player.pos_y}) | Camera Offset: ({self.offset_x}, {self.offset_y})")
        if not self.fixed_camera:
            target_x = player.pos_x - self.width // 2
            target_y = player.pos_y - self.height // 2
            self.offset_x = max(0, min(target_x, self.map_width - self.width))
            self.offset_y = max(0, min(target_y, self.map_height - self.height))

    def apply(self, rect):
        """
        Adjusts the given rect's position by the camera's offset.
        """
        return pygame.Rect(rect.x - self.offset_x, rect.y - self.offset_y, rect.width, rect.height)
