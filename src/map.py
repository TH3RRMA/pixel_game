import pytmx
import pygame


class Map:

    def __init__(self):
        self.tmx_data = None  # Speichert die Map-Daten
        self.tile_size = 0  # Placeholder, will be set after loading map
        self.scale_factor = 3

    def load_map(self, filename):
        self.tmx_data = pytmx.load_pygame(filename, pixelalpha=True)

        # Set tile size AFTER loading the TMX file
        self.tile_size = self.tmx_data.tilewidth
        print(f"Loaded Map: {filename}, Tile Size: {self.tile_size}, Scale Factor: {self.scale_factor}")  # Debug

        return self.tmx_data

    def draw_map(self, screen, camera_x, camera_y):  # self und gespeicherte Map-Daten nutzen
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

    def get_collision_objects(self):
        collision_objects = []

        for obj in self.tmx_data.objects:
            if obj.properties.get("collidable"):  # Prüfe die Eigenschaft
                scaled_x = obj.x * self.scale_factor
                scaled_y = obj.y * self.scale_factor
                scaled_width = obj.width * self.scale_factor
                scaled_height = obj.height * self.scale_factor

                rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
                collision_objects.append(rect)

        return collision_objects

    def get_interactive_objects(self):
        interactive_objects = []

        for obj in self.tmx_data.objects:
            if obj.properties.get("interact"):  # Prüfe die Eigenschaft
                scaled_x = obj.x * self.scale_factor
                scaled_y = obj.y * self.scale_factor
                scaled_width = obj.width * self.scale_factor
                scaled_height = obj.height * self.scale_factor

                rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
                interactive_objects.append(rect)

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


