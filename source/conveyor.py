class Conveyor:
    DIRS = [
        (0, -1),   # up
        (1, 0),    # right
        (0, 1),    # down
        (-1, 0),   # left
    ]

    def __init__(self, direction=1):
        self.direction = direction      # 0=up,1=right,2=down,3=left
        self.items = []                 # items moving on the belt
        self.output_target = None       # next machine/conveyor

    def addItem(self, item):
        # Only accept item if belt is empty or last item has moved enough
        if not self.items:
            self.items.append({"item": item, "progress": 0.0})
            return True

        if self.items[-1]["progress"] > 0.2:
            self.items.append({"item": item, "progress": 0.0})
            return True

        return False

    def update_connections(self, x, y, grid, map_width, map_height):
        dx, dy = Conveyor.DIRS[self.direction]
        tx, ty = x + dx, y + dy

        if 0 <= tx < map_width and 0 <= ty < map_height:
            self.output_target = grid[ty][tx]
        else:
            self.output_target = None

    def push(self):
        if not self.items or not self.output_target:
            return

        first = self.items[0]

        # Try to push into next machine/conveyor
        if hasattr(self.output_target, "addItem"):
            if self.output_target.addItem(first["item"]):
                self.items.pop(0)
