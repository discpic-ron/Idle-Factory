import pygame

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

    def draw_card(self, x, y, w, h, screen, font,color):
      stats = self.showStats()
      pygame.draw.rect(screen, (200,180,120), (x+10, y+10, 80, 80))
      screen.blit(font.render(stats["name"], True, color), (x+100, y+10))
      screen.blit(font.render(f"Cost: ${stats['cost']}", True, color), (x+100, y+30))
      desc = stats["description"][:28] + ("..." if len(stats["description"]) > 28 else "")
      screen.blit(font.render(desc, True, color), (x+100, y+55))


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
