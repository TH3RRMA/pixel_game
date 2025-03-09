import pytmx
import pygame
import time  # Import time module for tracking

last_collision_print_time = 0 # Stores the last time we printed collisions


class Map:

    def __init__(self):
        self.tmx_data = None  # Speichert die Map-Daten
        self.tile_size = 0  # Placeholder, will be set after loading map
        self.scale_factor = 3
        self.map_pixel_width = 0
        self.map_pixel_height = 0
        self.is_ui = False

    def load_map(self, filename):
        self.tmx_data = pytmx.load_pygame(filename, pixelalpha=True)

        # Set tile size AFTER loading the TMX file
        self.tile_size = self.tmx_data.tilewidth
        self.map_pixel_width = self.tmx_data.width * self.tile_size * self.scale_factor
        self.map_pixel_height = self.tmx_data.height * self.tile_size * self.scale_factor

        # ✅ Detect if this is a UI map
        self.is_ui = "_ui" in filename.lower()

        print(
            f"🗺️ Map Size: {self.map_pixel_width}x{self.map_pixel_height}, Loaded Map: {filename}, Tile Size: {self.tile_size}, | UI Mode: {self.is_ui}")  # Debug
        return self.tmx_data

    def draw_map(self, screen, camera_x, camera_y, camera):  # self und gespeicherte Map-Daten nutzen
        if self.tmx_data is None:
            return  # Falls keine Map geladen wurde, nichts zeichnen
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)

                    if tile:  # Ensure the tile exists
                        original_tile_size = self.tile_size  # Get original tile size

                        scaled_tile_size = original_tile_size * self.scale_factor

                        # Scale the tile properly
                        scaled_tile = pygame.transform.scale(tile, (scaled_tile_size, scaled_tile_size))

                        # Compute screen position with proper scaling
                        screen_x = x * scaled_tile_size - camera_x
                        screen_y = y * scaled_tile_size - camera_y

                        screen.blit(scaled_tile, (screen_x, screen_y))

            # Debug: Draw Collision Boxes
            for rect in self.get_collision_objects():
                adjusted_rect = pygame.Rect(rect.x - camera_x, rect.y - camera_y, rect.width, rect.height)
                pygame.draw.rect(screen, (255, 0, 0), adjusted_rect, 2)  # Red for collidable objects

            for obj in self.get_interactive_objects():
                adjusted_rect = pygame.Rect(obj["rect"].x - camera_x, obj["rect"].y - camera_y, obj["rect"].width, obj["rect"].height)
                pygame.draw.rect(screen, (0, 255, 0), adjusted_rect, 2)  # Green for interactive objects

            for rect, _ in self.get_exits():
                adjusted_rect = pygame.Rect(rect.x - camera_x, rect.y - camera_y, rect.width, rect.height)
                pygame.draw.rect(screen, (0, 0, 255), adjusted_rect, 2)  # Blue for exits

    def get_collision_objects(self):
        global last_collision_print_time

        collision_objects = []
        current_time = time.time()

        for obj in self.tmx_data.objects:
            if obj.properties.get("collidable"):  # Prüfe die Eigenschaft
                scaled_x = obj.x * self.scale_factor
                scaled_y = (obj.y + self.tile_size / 2) * self.scale_factor
                scaled_width = obj.width * self.scale_factor
                scaled_height = obj.height * self.scale_factor

                rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
                collision_objects.append(rect)

        # ✅ Debugging
        if current_time - last_collision_print_time > 5:
            print("📌 Collision Objects:")
            for rect in collision_objects:
                print(f"   {rect}")
            last_collision_print_time = current_time

        return collision_objects

    def get_interactive_objects(self):
        interactive_objects = []

        for obj in self.tmx_data.objects:
            if obj.properties.get("interact"):  # Check if it's interactive
                scaled_x = obj.x * self.scale_factor
                scaled_y = obj.y * self.scale_factor
                scaled_width = obj.width * self.scale_factor
                scaled_height = obj.height * self.scale_factor

                rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
                interactive_objects.append({"rect": rect, "name": obj.name})

        return interactive_objects

    def get_exits(self):
        """Find all exit objects from the map and return them as pygame.Rects with target maps."""
        exits = []

        for obj in self.tmx_data.objects:
            if "target_map" in obj.properties:  # If the object has a target_map property
                rect = pygame.Rect(obj.x * self.scale_factor, obj.y * self.scale_factor, obj.width * self.scale_factor,
                                   obj.height * self.scale_factor)
                exits.append((rect, obj.properties["target_map"]))  # Store the exit rect + target map name

        return exits

    def draw_ui_layer(self, screen):
        """Draws only UI elements from Tiled on top of the game world"""
        for layer in self.tmx_data.visible_layers:
            if "UI" in layer.name:  # ✅ Only render UI layers
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * self.tile_size * self.scale_factor,
                                           y * self.tile_size * self.scale_factor))



