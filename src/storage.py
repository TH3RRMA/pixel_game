import pygame


class Storage:
    def __init__(self, max_slots=4):
        self.items = [None] * max_slots
        self.max_slots = max_slots
        self.slot_width = 32 * 4
        self.slot_height = 32 * 4
        self.padding = 1

        # ✅ Load images
        self.slot_image = pygame.image.load("../assets/ui/inventory_slot.png").convert_alpha()
        self.slot_image = pygame.transform.scale(self.slot_image, (self.slot_width, self.slot_height))

        self.item_images = {
            "Wheat": pygame.image.load("../assets/items/wheat.png").convert_alpha(),
            "Flour": pygame.image.load("../assets/items/flour.png").convert_alpha(),
        }
        self.item_images = {name: pygame.transform.scale(img, (48, 48)) for name, img in self.item_images.items()}

    def draw(self, screen, font):
        """Draws the storage UI."""
        total_width = (self.slot_width * self.max_slots) + (self.padding * (self.max_slots - 1))
        start_x = (screen.get_width() - total_width) // 2
        y = screen.get_height() // 2 - self.slot_height

        for i in range(self.max_slots):
            x = start_x + i * (self.slot_width * (2 / 3) + self.padding)
            screen.blit(self.slot_image, (x, y))

            if self.items[i]:
                item_x = x + (self.slot_width - 48) // 2
                item_y = y + (self.slot_height - 48) // 2
                screen.blit(self.item_images[self.items[i]["name"]], (item_x, item_y))

                if self.items[i]["name"] in self.item_images:
                    screen.blit(self.item_images[self.items[i]["name"]], (item_x, item_y))
                else:
                    print(f"⚠️ WARNING: Image for {self.items[i]['name']} not found!")  # ✅ Debugging

                # Draw item count
                item_count = font.render(f"x{self.items[i]['count']}", True, (0, 0, 0))
                screen.blit(item_count, (x + 40, y + 45))

    def get_slot_index(self, mouse_pos):
        """Returns the index of the storage slot under the mouse."""
        start_x = (pygame.display.get_surface().get_width() - (self.slot_width + self.padding) * self.max_slots) // 2
        y = pygame.display.get_surface().get_height() // 2 - self.slot_height

        for i in range(self.max_slots):
            x = start_x + i * (self.slot_width * (2 / 3) + self.padding)
            slot_rect = pygame.Rect(x, y, self.slot_width, self.slot_height)

            if slot_rect.collidepoint(mouse_pos):
                return i
        return None

    def handle_mouse_click(self, mouse_pos, player_inventory):
        """Handles mouse click to start dragging an item from storage."""
        slot_index = self.get_slot_index(mouse_pos)

        if slot_index is not None and self.items[slot_index]:  # ✅ Item exists in slot
            print(f"🖱️ Picking up {self.items[slot_index]['name']} from storage!")

            # ✅ Assign dragged item to inventory dragging system
            player_inventory.dragging_item = self.items[slot_index]
            player_inventory.dragging_offset = (mouse_pos[0] - slot_index * (self.slot_width + self.padding),
                                                mouse_pos[1] - (
                                                        pygame.display.get_surface().get_height() // 2 - self.slot_height))

            self.items[slot_index] = None  # ✅ Remove item from storage

    def handle_mouse_release(self, mouse_pos, player_inventory):
        """
        Handles dropping an item from storage into inventory, into another storage slot,
        or back to its original storage slot.
        """
        if player_inventory.dragging_item:  # ✅ If dragging FROM storage
            inventory_slot_index = player_inventory.get_slot_index(mouse_pos)
            storage_slot_index = self.get_slot_index(mouse_pos)  # ✅ Check for storage drop

            if inventory_slot_index is not None:  # ✅ Dropping into inventory
                if player_inventory.items[inventory_slot_index] is None:
                    player_inventory.items[inventory_slot_index] = player_inventory.dragging_item
                else:
                    if player_inventory.items[inventory_slot_index]["name"] == player_inventory.dragging_item["name"]:
                        player_inventory.items[inventory_slot_index]["count"] += player_inventory.dragging_item["count"]
                    else:
                        # ✅ Swap items if different
                        player_inventory.items[inventory_slot_index], player_inventory.dragging_item = \
                            player_inventory.dragging_item, player_inventory.items[inventory_slot_index]

                print(f"✅ Moved {player_inventory.dragging_item['name']} to inventory slot {inventory_slot_index}!")
                player_inventory.dragging_item = None  # ✅ Reset dragging item

            elif storage_slot_index is not None:  # ✅ Dropping into another storage slot
                if self.items[storage_slot_index] is None:
                    self.items[storage_slot_index] = player_inventory.dragging_item  # ✅ Move item
                else:
                    if self.items[storage_slot_index]["name"] == player_inventory.dragging_item["name"]:
                        self.items[storage_slot_index]["count"] += player_inventory.dragging_item["count"]  # ✅ Stack
                    else:
                        # ✅ Swap items if different
                        self.items[storage_slot_index], player_inventory.dragging_item = \
                            player_inventory.dragging_item, self.items[storage_slot_index]

                print(f"✅ Moved {player_inventory.dragging_item['name']} to storage slot {storage_slot_index}!")
                player_inventory.dragging_item = None  # ✅ Reset dragging item

            else:
                # ✅ If dropped outside storage & inventory, return to storage slot
                print(f"🔄 Returning {player_inventory.dragging_item['name']} back to storage!")
                for i in range(self.max_slots):
                    if self.items[i] is None:  # Find an empty slot
                        self.items[i] = player_inventory.dragging_item
                        break

                player_inventory.dragging_item = None  # ✅ Reset dragging item


class StorageManager:
    def __init__(self):
        self.storages = {}  # Dictionary to hold multiple storages

    def add_storage(self, storage_id, slots):
        """Creates a new storage if it doesn't exist."""
        if storage_id not in self.storages:
            self.storages[storage_id] = Storage(slots)

    def get_storage(self, storage_id):
        """Retrieves the storage with the given ID."""
        return self.storages.get(storage_id, None)
