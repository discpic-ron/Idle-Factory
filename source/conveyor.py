class Conveyor:
  def __init__(self,direction):
    self.direction = direction
    self.inputs = [] 
    self.output = None
    
  def addItem(self,item):
    if not self.items:
      self.inputs.append({"item":item,"progress":0.0})
    if self.items[-1]["progress"] > 0.2:
        self.items.append({"type": item, "progress": 0.0})
      
  def update_connections(self,x, y, grid):
    dx, dy = DIRS[self.direction_index]
    tx, ty = x + dx, y + dy

    if 0 <= tx < map_width and 0 <= ty < map_height:
      self.output_target = grid[ty][tx]
    else:
        self.output_target = None
    
  def push(self, item):
    if not self.items or not self.output_target:
      return
    item = self.items[0]
    if hasattr(self.output_target, "addItem"):
      if self.output_target.addItem(item):
         self.items.pop(0)
