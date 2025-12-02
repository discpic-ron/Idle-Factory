import pygame
from manager import companyManager
from inventory import Inventory

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, player_sprite):
        super().__init__()
        self.image = player_sprite
        self.rect = self.image.get_rect(topleft=(x*50, y*50))
        self.path = []
        self.speed = 2.0
        self.selected = False
        self.money = 0
        self.unlocked_upgrades = {}
        self.inventory = Inventory()
        self.prestige = False
      
    def getStats(self):
      ## Return player statistics, managing prestige accordingly
      if self.prestige:
          # Resetting stats for prestige while keeping a record of total earnings
          current_stats = {
              "Money": 0,                                      # Reset current money
              "Lifetime Money": self.total_lifetime_money,    # Keep lifetime money intact
              "Unlocked Upgrades": self.unlocked_upgrades,    # Retain unlocked upgrades
          }
          self.prestige = False  # Reset prestige status after returning stats
          return current_stats
      else:
          # If not prestiging, simply return the current stats
          return {
              "Money": self.money,
              "Lifetime Money": self.total_lifetime_money,
              "Unlocked Upgrades": self.unlocked_upgrades,
          }
          
    def addMoney(self, amount):
      ## Method to add money and track lifetime earnings
      self.money += amount
      self.total_lifetime_money += amount
      
    def activatePrestige(self):
      self.prestige = True
      return self.prestige
      
    def gain_resource_from_action(self, manager_instance, resource, amount):
      """Action: Player finds/gains a resource through a non-purchase action (e.g., harvesting)."""
      manager_instance.resources[resource] = manager_instance.resources.get(resource, 0) + amount
      print(f"Player gained {amount} of {resource}. Total: {manager_instance.resources[resource]}")
      
    def set_path(self, path):
        self.path = path

    def update(self):
      if self.path:
        tx, ty = self.path[0]
        target_px, target_py = tx*50, ty*50

        if self.rect.x < target_px: self.rect.x += self.speed
        elif self.rect.x > target_px: self.rect.x -= self.speed
        if self.rect.y < target_py: self.rect.y += self.speed
        elif self.rect.y > target_py: self.rect.y -= self.speed

        if self.rect.x == target_px and self.rect.y == target_py:
          self.path.pop(0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # Draw selection outline if selected
        if self.selected:
            pygame.draw.rect(surface, (0,255,0), self.rect, 3)