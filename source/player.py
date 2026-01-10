import pygame
from manager import companyManager
from inventory import Inventory

class Player:
    def __init__(self):
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
      
