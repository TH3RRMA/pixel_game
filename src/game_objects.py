import pygame


class GameObject:
    def __init__(self, x, y, width, height, solid=True, interaction_text=None, color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.solid = solid
        self.interaction_text = interaction_text
        self.interface_open = False  # Whether the interface is open
        self.loading_progress = 0  # Only needed for objects that have a loading process
        # Slots für Input und Output (je 3 Plätze)
        self.input_slots = [{"item": None, "amount": 0} for _ in range(3)]
        self.output_slots = [{"item": None, "amount": 0} for _ in range(3)]
        self.mysterious_counter = 0
        self.color = color

    def handle_collision(self, player):
        """
        Handles collision with the player if the object is solid.
        Reverts player's position if there is a collision.
        """
        if self.solid and self.rect.colliderect(player):
            return True  # Signal that a collision occurred
        return False

    def draw(self, screen, rect=None):
        """
        Draws the object on the screen with the specified color.
        """
        rect_to_draw = rect if rect else self.rect
        pygame.draw.rect(screen, self.color, rect_to_draw)

    def show_interaction_hint(self, screen, player, font, rect=None):
        rect_to_draw = rect if rect else self.rect
        if self.interaction_text and player.colliderect(self.interaction_zone) and not self.interface_open:
            text = font.render(self.interaction_text, True, (0, 0, 0))
            screen.blit(text, (rect_to_draw.x, rect_to_draw.y - 30))

    def can_interact(self, player):
        """
        Returns True if the player can interact with this object.
        Subclasses can override this for more specific behavior.
        """
        return player.rect.colliderect(self.rect)

    def draw_interface(self, screen, font):
        if self.interface_open:
            # Background for interface
            pygame.draw.rect(screen, (200, 200, 200), (200, 100, 400, 200))
            pygame.draw.rect(screen, (0, 0, 0), (200, 100, 400, 200), 2)

            # Title
            text = font.render(f"{self.__class__.__name__} Interface", True, (0, 0, 0))
            screen.blit(text, (220, 120))

            # Input Slots
            for i, slot in enumerate(self.input_slots):
                item_text = f"{slot['item']} x{slot['amount']}" if slot["item"] else "Leer"
                slot_text = font.render(f"Input {i + 1}: {item_text}", True, (0, 0, 0))
                screen.blit(slot_text, (220, 150 + i * 30))

            # Output Slots
            for i, slot in enumerate(self.output_slots):
                item_text = f"{slot['item']} x{slot['amount']}" if slot["item"] else "Leer"
                slot_text = font.render(f"Output {i + 1}: {item_text}", True, (0, 0, 0))
                screen.blit(slot_text, (220, 240 + i * 30))

    def update_interface(self):
        """
        Updates the loading bar when the interface is open.
        """
        if self.interface_open:
            self.loading_progress += 1  # Increase progress
            if self.loading_progress >= 100:
                self.loading_progress = 0  # Reset progress
                self.mysterious_counter += 1  # Increment counter


class Oven(GameObject):
    def __init__(self, x, y, width, height, solid=True):
        super().__init__(x, y, width, height, solid, interaction_text="Press E to interact", color=(255, 0, 0))  # Call parent constructor
        self.interaction_zone = pygame.Rect(
            self.rect.x, self.rect.y + self.rect.height, self.rect.width, 20
        )
        # Input slots
        self.slots = [
            {"item": None, "count": 0, "type": "Water"},  # First slot: Water only
            {"item": None, "count": 0, "type": "flour"},  # Second slot: Flour only
        ]
        self.slot_width = 80
        self.slot_height = 80
        self.interface_rect = pygame.Rect(200, 50, 400, 300)

    def interact(self, player, event):
        """
        Handles interaction when the player presses E near the well.
        """
        if player.colliderect(self.interaction_zone) and event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            self.interface_open = not self.interface_open
            print(f"Oven interface {'opened' if self.interface_open else 'closed'}.")

    def draw_interface(self, screen, font):
        """
        Draws the well interface (loading bar and counter).
        """
        if self.interface_open:
            # Background
            pygame.draw.rect(screen, (200, 200, 200), self.interface_rect)
            pygame.draw.rect(screen, (0, 0, 0), self.interface_rect, 2)

            # Loading bar
            pygame.draw.rect(screen, (0, 255, 0), (self.interface_rect.x + 20, self.interface_rect.y + 200,
                                                   360 * (self.loading_progress / 100), 30))
            pygame.draw.rect(screen, (0, 0, 0), (self.interface_rect.x + 20, self.interface_rect.y + 200, 360, 30), 2)

            # Draw slots
            for i, slot in enumerate(self.slots):
                x, y = (self.interface_rect.x + 50 + i * (self.slot_width + 20), self.interface_rect.y + 100)
                slot_rect = pygame.Rect(x, y, self.slot_width, self.slot_height)
                pygame.draw.rect(screen, (180, 180, 180), slot_rect)
                pygame.draw.rect(screen, (0, 0, 0), slot_rect, 2)

                # Display item if present
                if slot["item"]:
                    item_text = font.render(f"{slot['item']} x{slot['count']}", True, (0, 0, 0))
                    screen.blit(item_text, (slot_rect.x + 5, slot_rect.y + 5))

            # Close hint
            close_hint = font.render("Press E to close", True, (0, 0, 0))
            screen.blit(close_hint, (self.interface_rect.x + 50, self.interface_rect.y + 250))

    def add_item(self, item_name, count, slot_index):
        """
        Adds an item to the specified slot if it matches the slot type.
        """
        slot = self.slots[slot_index]
        if item_name == slot["type"]:  # Ensure item matches slot type
            if slot["item"] is None:
                slot["item"] = item_name
                slot["count"] = count
            else:
                slot["count"] += count
            return True
        return False  # Item not compatible with the slot

    def remove_item(self, slot_index):
        """
        Removes the item from the specified slot.
        """
        slot = self.slots[slot_index]
        if slot["item"]:
            removed_item = {"name": slot["item"], "count": slot["count"]}
            slot["item"] = None
            slot["count"] = 0
            return removed_item
        return None

    def handle_item_drop(self, mouse_pos, item):
        """
        Handles dropping an item into the oven slots.
        """
        for i in range(len(self.slots)):
            print(f"in position{i}")
            x, y = (self.interface_rect.x + 50 + i * (self.slot_width + 20), self.interface_rect.y + 100)
            slot_rect = pygame.Rect(x, y, self.slot_width, self.slot_height)
            if slot_rect.collidepoint(mouse_pos):  # Check if dropped in slot
                if item["name"] == self.slots[i]["type"]:  # Ensure compatibility
                    if self.slots[i]["item"] is None:  # Slot empty
                        self.slots[i]["item"] = item["name"]
                        self.slots[i]["count"] = item["count"]
                    else:  # Slot contains same item
                        self.slots[i]["count"] += item["count"]
                    print(f"Item {item['name']} x{item['count']} added to oven slot {i}.")
                    return True
        return False  # Drop failed

class Well(GameObject):
    def __init__(self, x, y, width, height, solid=True):
        super().__init__(x, y, width, height, solid, interaction_text="Press E to interact")  # Call parent constructor
        self.interaction_zone = pygame.Rect(self.rect.x, self.rect.y + self.rect.height, self.rect.width, 20)
        self.interface_open = False  # Whether the interface is open
        self.loading_progress = 0  # Loading progress (0-100)
        self.water_counter = 0  # Counter for filled buckets
        self.items = [{"name": "Water", "count": self.water_counter}]
        self.dragging_item = None  # Currently dragged item
        self.drag_offset = (0, 0)  # Offset of the drag from the mouse position

    def interact(self, player, event):
        """
        Handles interaction when the player presses E near the well.
        """
        if player.colliderect(self.interaction_zone) and event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            self.interface_open = not self.interface_open
            print(f"Interface open: {self.interface_open}")

    def update_interface(self):
        """
        Updates the loading bar when the interface is open.
        """
        if self.interface_open:
            self.loading_progress += 1  # Increase progress
            if self.loading_progress >= 100:
                self.loading_progress = 0  # Reset progress
                self.water_counter += 1  # Increment counter
                self.add_item("Water", 1)  # Ensure item count is updated

    def add_item(self, name, count):
        """
        Adds an item to the inventory or updates the count if it already exists.
        """
        for item in self.items:
            if item["name"] == name:
                item["count"] += count
                return
        # If the item does not exist, add a new entry
        self.items.append({"name": name, "count": count})

    def draw_interface(self, screen, font):
        """
        Draws the well interface (loading bar and counter).
        """
        if self.interface_open:
            # Background for interface
            interface_rect = pygame.Rect(200, 100, 400, 300)
            pygame.draw.rect(screen, (200, 200, 200), interface_rect)
            pygame.draw.rect(screen, (0, 0, 0), interface_rect, 2)

            # Loading bar
            loading_bar_rect = pygame.Rect(220, 150, 360 * (self.loading_progress / 100), 30)
            pygame.draw.rect(screen, (0, 255, 0), loading_bar_rect)  # Green bar
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(220, 150, 360, 30), 2)  # Border

            # Display items with count
            for i, item in enumerate(self.items):
                item_text = font.render(f"{item['name']} (x{item['count']})", True, (0, 0, 0))
                item_rect = pygame.Rect(250, 200 + i * 50, 200, 40)  # Adjust box for item
                pygame.draw.rect(screen, (180, 180, 180), item_rect)  # Draw item box
                pygame.draw.rect(screen, (0, 0, 0), item_rect, 2)  # Border
                screen.blit(item_text, (item_rect.x + 10, item_rect.y + 10))  # Position text correctly

                # If dragging this item, draw near the cursor
                if self.dragging_item == item:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    pygame.draw.rect(screen, (255, 255, 0), item_rect)  # Highlight drag item
                    screen.blit(item_text, (mouse_x + self.drag_offset[0], mouse_y + self.drag_offset[1]))

            # Close hint
            close_hint = font.render("Press E to close", True, (0, 0, 0))
            screen.blit(close_hint, (250, interface_rect.bottom - 40))

    def handle_mouse_events(self, event, player_inventory):
        """
        Handles dragging items from the well to the player's inventory.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                for i, item in enumerate(self.items):
                    item_rect = pygame.Rect(250, 200 + i * 50, 100, 40)
                    if item_rect.collidepoint(mouse_x, mouse_y):
                        self.dragging_item = item
                        self.drag_offset = (item_rect.x - mouse_x, item_rect.y - mouse_y)
                        break

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_item:
                # Draw the dragged item near the cursor (handled in `draw_interface`)
                pass

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_item:
                # Check if dropped over inventory
                if player_inventory.handle_item_drop((mouse_x, mouse_y), self.dragging_item):
                    self.dragging_item["count"] -= self.dragging_item["count"]
                    if self.dragging_item["count"] <= 0:
                        self.items.remove(self.dragging_item)  # Remove item if count is zero
                # Reset dragging state
                self.dragging_item = None
                self.drag_offset = (0, 0)

    def close_interface(self, event):
        """
        Closes the interface when E is pressed again.
        """
        if self.interface_open and event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            self.interface_open = False

    def draw(self, screen, rect=None):
        rect_to_draw = rect if rect else self.rect
        pygame.draw.rect(screen, (255, 0, 0), rect_to_draw)  # Draw the oven
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(rect_to_draw.x, rect_to_draw.y + rect_to_draw.height,
                                                          rect_to_draw.width, 20), 1)  # Draw interaction zone (debug)

    def show_interaction_hint(self, screen, player, font, rect=None, color=(0, 0, 0)):
        rect_to_draw = rect if rect else self.rect
        if self.interaction_text and player.colliderect(self.interaction_zone) and not self.interface_open:
            text = font.render(self.interaction_text, True, color)
            screen.blit(text, (rect_to_draw.x, rect_to_draw.y - 30))


class Mill(GameObject):
    def __init__(self, x, y, width, height, solid=True):
        super().__init__(x, y, width, height, solid, interaction_text="Press E to interact")  # Call parent constructor
        self.interaction_zone = pygame.Rect(
            self.rect.x, self.rect.y + self.rect.height, self.rect.width, 20
        )
        self.interface_open = False  # Whether the interface is open
        self.loading_progress = 0  # Loading progress (0-100)
        # Input slots
        self.slots = [
            {"item": None, "count": 0, "type": "Wheat"},  # First slot: Wheat only
        ]
        self.slot_width = 80
        self.slot_height = 80
        self.interface_rect = pygame.Rect(200, 50, 400, 300)
        self.water_counter = 0

    def interact(self, player, event):
        """
        Handles interaction when the player presses E near the well.
        """
        if player.colliderect(self.interaction_zone) and event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            self.interface_open = not self.interface_open
            print(f"Oven interface {'opened' if self.interface_open else 'closed'}.")

    def add_item(self, item_name, count, slot_index):
        """
        Adds an item to the specified slot if it matches the slot type.
        """
        slot = self.slots[slot_index]
        if item_name == slot["type"]:  # Ensure item matches slot type
            if slot["item"] is None:
                slot["item"] = item_name
                slot["count"] = count
            else:
                slot["count"] += count
            return True
        return False  # Item not compatible with the slot

    def remove_item(self, slot_index):
        """
        Removes the item from the specified slot.
        """
        slot = self.slots[slot_index]
        if slot["item"]:
            removed_item = {"name": slot["item"], "count": slot["count"]}
            slot["item"] = None
            slot["count"] = 0
            return removed_item
        return None

    def handle_item_drop(self, mouse_pos, item):
        """
        Handles dropping an item into the oven slots.
        """
        for i in range(len(self.slots)):
            print(f"in position{i}")
            x, y = (self.interface_rect.x + 50 + i * (self.slot_width + 20), self.interface_rect.y + 100)
            slot_rect = pygame.Rect(x, y, self.slot_width, self.slot_height)
            if slot_rect.collidepoint(mouse_pos):  # Check if dropped in slot
                if item["name"] == self.slots[i]["type"]:  # Ensure compatibility
                    if self.slots[i]["item"] is None:  # Slot empty
                        self.slots[i]["item"] = item["name"]
                        self.slots[i]["count"] = item["count"]
                    else:  # Slot contains same item
                        self.slots[i]["count"] += item["count"]
                    print(f"Item {item['name']} x{item['count']} added to oven slot {i}.")
                    return True
        return False  # Drop failed

    def draw_interface(self, screen, font):
        """
        Draws the well interface (loading bar and counter).
        """
        if self.interface_open:
            # Background
            pygame.draw.rect(screen, (200, 200, 200), self.interface_rect)
            pygame.draw.rect(screen, (0, 0, 0), self.interface_rect, 2)

            # Loading bar
            pygame.draw.rect(screen, (0, 255, 0), (self.interface_rect.x + 20, self.interface_rect.y + 200,
                                                   360 * (self.loading_progress / 100), 30))
            pygame.draw.rect(screen, (0, 0, 0), (self.interface_rect.x + 20, self.interface_rect.y + 200, 360, 30), 2)

            # Draw slots
            for i, slot in enumerate(self.slots):
                x, y = (self.interface_rect.x + 50 + i * (self.slot_width + 20), self.interface_rect.y + 100)
                slot_rect = pygame.Rect(x, y, self.slot_width, self.slot_height)
                pygame.draw.rect(screen, (180, 180, 180), slot_rect)
                pygame.draw.rect(screen, (0, 0, 0), slot_rect, 2)

                # Display item if present
                if slot["item"]:
                    item_text = font.render(f"{slot['item']} x{slot['count']}", True, (0, 0, 0))
                    screen.blit(item_text, (slot_rect.x + 5, slot_rect.y + 5))

            # Close hint
            close_hint = font.render("Press E to close", True, (0, 0, 0))
            screen.blit(close_hint, (self.interface_rect.x + 50, self.interface_rect.y + 250))

    def update_interface(self):
        """
        Updates the loading bar when the interface is open.
        """
        if self.interface_open:
            self.loading_progress += 1  # Increase progress
            if self.loading_progress >= 100:
                self.loading_progress = 0  # Reset progress
                self.water_counter += 1  # Increment counter

    def close_interface(self, event):
        """
        Closes the interface when E is pressed again.
        """
        if self.interface_open and event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            self.interface_open = False

    def draw(self, screen, rect=None):
        rect_to_draw = rect if rect else self.rect
        pygame.draw.rect(screen, (255, 0, 0), rect_to_draw)  # Draw the mill
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(rect_to_draw.x, rect_to_draw.y + rect_to_draw.height,
                                                          rect_to_draw.width, 20), 1)  # Draw interaction zone (debug)

    def show_interaction_hint(self, screen, player, font, rect=None, color=(0, 0, 0)):
        rect_to_draw = rect if rect else self.rect
        if self.interaction_text and player.colliderect(self.interaction_zone) and not self.interface_open:
            text = font.render(self.interaction_text, True, color)
            screen.blit(text, (rect_to_draw.x, rect_to_draw.y - 30))
