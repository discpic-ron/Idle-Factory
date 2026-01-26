import random
from manager import CompanyManager

class Random_event:
    def __init__(self, manager_instance):
        self.company = manager_instance 
        self.event_names = ["shortage", "surplus", "market crash"]
        self.weights = [15, 40, 5]

    def trigger(self):
        # 1. Roll the dice once to pick the event based on weights
        pick = random.choices(self.event_names, weights=self.weights, k=1)[0]
        
        # 2. Run the function that matches the pick
        if pick == "shortage":
            self.shortage()
        elif pick == "surplus":
            self.surplus()
        elif pick == "market crash":
            self.market_crash()

    def shortage(self):
        print("A shortage occurred!")
        materials = companyManager().unlocked_materials
        chosen_material = random.choice(materials)
        amount = random.randint(1,chosen_material)
        self.company.inventory[chosen_material] -= amount

    def surplus(self):
        print("A surplus! Resources are flooding in.")
        # Logic for 'increase production' goes here

    def market_crash(self):
        print("GLOBAL MARKET CRASH!")
        # Reduce company balance by a percentage
        self.company.balance *= 0.5
