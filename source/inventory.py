import pygame

class Inventory:
    def __init__(self):
        # Each entry: {"name": str, "count": int}
        self.items = {}

    def add_item(self, name, count=1):
        if name in self.items:
            self.items[name]["count"] += count
        else:
            self.items[name] = {"name": name, "count": count}

    def remove_item(self, name, count=1):
        if name in self.items:
            self.items[name]["count"] -= count
            if self.items[name]["count"] <= 0:
                del self.items[name]

    def draw_card(self, x, y, w, h,screen,font,color):
        global font_small
        pygame.draw.rect(screen, (100,100,150), (x, y, w, h))
        screen.blit(font_small.render(f"{self.name} x{self.count}", True, white), (x+5, y+15))

    def get_items(self):
        return list(self.items.values())

