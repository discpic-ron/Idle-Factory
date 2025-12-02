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

    def get_items(self):
        return list(self.items.values())
