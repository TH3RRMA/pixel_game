import pygame


class Inventory:
    def __init__(self, max_items=8):
        self.items = [None] * max_items  # List to hold items
        self.max_items = max_items  # Maximum items allowed
        self.slot_size = 50  # Size of each inventory slot
        self.selected_index = None  # Index of the currently selected item
        self.dragging_item = None  # Currently dragged item
        self.dragging_offset = (0, 0)  # Offset of mouse relative to the dragged item
        self.slots = []  # Positions of inventory slots
        self.slot_width = 60
        self.slot_height = 60
        self.padding = 10

    def draw(self, screen, font):
        """
        Draws the inventory slots and items on the screen.
        """
        start_x = (screen.get_width() - (self.slot_width + self.padding) * self.max_items) // 2
        y = screen.get_height() - self.slot_height - 20  # Bottom of the screen

        for i in range(self.max_items):
            # Slot background
            x = start_x + i * (self.slot_width + self.padding)
            color = (200, 200, 200) if i != self.selected_index else (255, 255, 0)
            pygame.draw.rect(screen, color, (x, y, self.slot_width, self.slot_height))

            # Draw item if it exists
            if i < len(self.items):
                if self.items[i] is None:
                    continue
                # Render item name and count
                item_name = font.render(self.items[i]["name"], True, (0, 0, 0))
                item_count = font.render(f"x{self.items[i]['count']}", True, (0, 0, 0))
                screen.blit(item_name, (x + 5, y + 5))
                screen.blit(item_count, (x + 5, y + 25))

        # Draw dragged item
        if self.dragging_item:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dragged_text = font.render(f"{self.dragging_item['name']} x{self.dragging_item['count']}", True,
                                       (255, 0, 0))
            screen.blit(dragged_text, (mouse_x - self.dragging_offset[0], mouse_y - self.dragging_offset[1]))

    def add_item(self, name, count):
        """
        Adds an item to the inventory or updates the count if it already exists.
        """
        for i in range(self.max_items):
            if self.items[i] is None:
                self.items[i] = {"name": name, "count": count}
                return
            elif self.items[i]["name"] == name:
                self.items[i]["count"] += count
                return

    def remove_item(self, name, count):
        """
        Removes a specified count of an item from the inventory.
        """
        for item in self.items:
            if item["name"] == name:
                item["count"] -= count
                if item["count"] <= 0:
                    self.items.remove(item)
                return

    def get_slot_index(self, mouse_pos):
        """
        Returns the inventory slot index where the mouse is released, or None if outside slots.
        """
        start_x = (pygame.display.get_surface().get_width() - (self.slot_width + self.padding) * self.max_items) // 2
        y = pygame.display.get_surface().get_height() - self.slot_height - 20

        for i in range(self.max_items):
            x = start_x + i * (self.slot_width + self.padding)
            slot_rect = pygame.Rect(x, y, self.slot_width, self.slot_height)

            if slot_rect.collidepoint(mouse_pos):
                return i  # Mouse is over this slot
        return None  # No valid slot found

    def handle_mouse_click(self, screen, mouse_pos, mouse_pressed):
        """
        Handles mouse clicks to select an inventory slot.
        """
        start_x = (screen.get_width() - (self.slot_width + self.padding) * self.max_items) // 2
        y = screen.get_height() - self.slot_height - 20  # Bottom of the screen

        for i, item in enumerate(self.items):  # Iterate over items with index
            if item is None:
                continue

            x = start_x + i * (self.slot_width + self.padding)
            slot_rect = pygame.Rect(x, y, self.slot_width, self.slot_height)

            if slot_rect.collidepoint(mouse_pos) and mouse_pressed:  # Click and hold
                self.selected_index = i
                if not self.dragging_item:  # Prevent reassigning while dragging
                    self.dragging_item = {"name": item["name"], "count": item["count"]}
                    self.dragging_offset = (mouse_pos[0] - slot_rect.x, mouse_pos[1] - slot_rect.y)
                    item["count"] -= item["count"]
                    self.items[i] = None
                    print(f"Dragging {self.dragging_item}")
                return

    def handle_mouse_release(self, mouse_pos, target=None):
        """
        Handles mouse release to drop an item into a slot or elsewhere.
        If a target (e.g., oven) is provided, attempts to drop the item into it.
        """
        if self.dragging_item:
            print(f"Releasing item: {self.dragging_item}")

            # 1. Check if item is dropped into another inventory slot
            slot_index = self.get_slot_index(mouse_pos)
            if slot_index is not None:
                if self.items[slot_index] is None:  # Slot is empty, place item here
                    self.items[slot_index] = self.dragging_item
                else:
                    # Merge items if they are the same type
                    if self.items[slot_index]["name"] == self.dragging_item["name"]:
                        self.items[slot_index]["count"] += self.dragging_item["count"]
                    else:
                        # Swap items if different
                        self.items[self.selected_index], self.items[slot_index] = self.items[slot_index], self.dragging_item
            else:
                # 2. Try dropping into target (e.g., oven)
                if target and target.handle_item_drop(mouse_pos, self.dragging_item):
                    print("Item successfully dropped into target.")
                else:
                    # 3. If drop fails, return the item to ts original slot
                    if self.items[self.selected_index] is None:
                        self.items[self.selected_index] = self.dragging_item
                    else:
                        self.add_item(self.dragging_item["name"], self.dragging_item["count"])
                        print("Returned item to inventory.")
            self.dragging_item = None  # Reset dragging item
            self.selected_index = None  # Reset index

    def handle_item_drop(self, mouse_pos, item):
        """
        Handles dropping an item into an inventory slot.
        """
        slot_width = 60
        slot_height = 60
        padding = 10
        start_x = (pygame.display.get_surface().get_width() - (slot_width + padding) * self.max_items) // 2
        y = pygame.display.get_surface().get_height() - slot_height - 20

        for i in range(self.max_items):
            x = start_x + i * (slot_width + padding)
            slot_rect = pygame.Rect(x, y, slot_width, slot_height)

            if slot_rect.collidepoint(mouse_pos):  # Check if mouse is over this slot
                print(f"Item dropped into slot {i}: {item['name']} x{item['count']}")
                self.add_item(item["name"], item["count"])  # Add the item to the inventory
                return True
        return False  # Return False if the drop is outside any slot

