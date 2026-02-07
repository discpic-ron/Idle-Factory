from recipes import Recipe

class machine:
  def __init__(self,recipe):
    self.progress = 0
    self.recipe = recipe # this uses a dict
    self.is_working = False
    
  def update(self,dt):
    if not self.is_working:
      if self.can_start():
        self.is_working = True
        self.progress = 0
        
    if self.is_working:
      self.progress += dt / self.recipe["time"]
      
    if self.progress >= 1.0:
      self.complete_craft()
      
  def can_start(self):
    if Recipe.can_afford() == True:
      return True
    else:
      return False
      
  def complete_craft(self):
    self.progress = 0
    self.is_working = False
