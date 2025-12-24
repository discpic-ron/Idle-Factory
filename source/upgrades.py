import pygame

class Upgrade:
  registry = []
  def __init__(self, name, description, cost, affect_player=False, effect_value=0):
        self.name = name
        self.description = description
        self.cost = cost
        self.affect_player = affect_player
        self.unlocked = False
        self.purchased = False
        self.effect_value = effect_value
        Upgrade.registry.append(self)

  def affectsPlayer(self, player):
        """Apply upgrade effect to player if not already purchased."""
        if self.affect_player and not self.purchased:
            player.click_power += self.effect_value
            self.purchased = True

  def isUnlocked(self, player):
        """Check if upgrade can be bought."""
        return self.unlocked and player.money >= self.cost

  def draw_card(self, x, y, w, h, screen, font,color):
    stats = self.showStats()
    pygame.draw.rect(screen, (200,180,120), (x+10, y+10, 80, 80))
    screen.blit(font.render(stats["name"], True, color), (x+100, y+10))
    screen.blit(font.render(f"Cost: ${stats['cost']}", True, color), (x+100, y+30))
    desc = stats["description"][:28] + ("..." if len(stats["description"]) > 28 else "")
    screen.blit(font.render(desc, True, color), (x+100, y+55))

  def showStats(self):
        return {
            "name": self.name,
            "description": self.description,
            "cost": self.cost,
            "purchased": self.purchased
        }
