class Hardware:
    registry = []
    def __init__(self, name, description, cost):
      self.name = name
      self.description = description
      self.cost = cost
      self.unlocked = False
      self.purchased = False
      self.placed_items = {}
      Hardware.registry.append(self)
    
    def place_item(self, gx, gy, name):
        if (gx, gy) not in self.placed_items:
            self.placed_items[(gx, gy)] = name
            print(f"Placed {name} at {gx},{gy}")
        else:
            print("Cell already occupied!")
            
    def draw(self, surface):
        for (gx, gy), name in self.placed_items.items():
            rect = pygame.Rect(gx * GRID_SIZE, gy * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, (100, 200, 100), rect)
            label = font_small.render(name[:3], True, WHITE)  # short label
            surface.blit(label, (rect.x + 5, rect.y + 5))
    
    def isUnlocked(self, player):
      """Check if upgrade can be bought."""
      return self.unlocked and player.money >= self.cost

    def showStats(self):
      return {
        "name": self.name,
        "description": self.description,
        "cost": self.cost,
        "purchased": self.purchased
      }