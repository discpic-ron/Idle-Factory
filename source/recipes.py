class Recipe:
  def __init__(self,name,ingriends):
    self.name = name
    self.ingredients = ingredients
    self.output = output
    self.craft_time = craft_time
    
  def can_afford(self,machine_inventory):
    for item, amount in self.ingredients.items():
            if machine_inventory.get(item, 0) < amount:
                return False
    return True

  def get_progress(self,dt):
    if self.craft_time <= 0: 
      return 1.0
    return dt / self.craft_time
    
  def get_info(self):
    return {
      "name": self.name,
      "ingredients": self.ingredients,
      "output": self.output,
      "time": self.craft_time
    }
