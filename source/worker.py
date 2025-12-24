import random
import pygame

class Worker:
    registry = []

    def __init__(self):
        self.gender, self.name = self.generateName()
        self.morale = 100
        self.base_efficiency = 1
        self.payroll = random.randint(50, 300)  # hiring cost
        self.uniform_purchased = False
        self.icon = pygame.Surface((60, 60))
        self.icon.fill((180, 180, 220))
        Worker.registry.append(self)

    def generateName(self):
        male_first = ["John", "Michael", "David", "Daniel", "James", "Robert", "Matthew", "Anthony"]
        female_first = ["Sarah", "Emily", "Jessica", "Laura", "Sophia", "Olivia", "Emma", "Isabella"]
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez",
            "Lopez", "Gonzalez", "Wilson", "Anderson"
        ]
        if random.choice([True, False]):
            first = random.choice(male_first)
            gender = "Male"
        else:
            first = random.choice(female_first)
            gender = "Female"

        last = random.choice(last_names)
        return gender, f"{first} {last}"

    def boostMorale(self):
        if self.morale < 50:
            self.morale += 10
        return self.morale

    def upgradeEfficiency(self, amount):
        self.base_efficiency += amount
        return self.base_efficiency

    def showStats(self):
        return {
            "name": self.name,
            "gender": self.gender,
            "morale": self.morale,
            "efficiency": self.base_efficiency,
            "payroll": self.payroll
        }

    def draw_card(self, x, y, w, h, screen, font, color):
        # Icon
        screen.blit(self.icon, (x + 10, y + 10))

        # Name
        name_text = font.render(self.name, True, color)
        screen.blit(name_text, (x + 80, y + 10))

        # Payroll cost
        cost_text = font.render(f"Payroll: ${self.payroll}", True, color)
        screen.blit(cost_text, (x + 80, y + 45))

        # Description
        desc = font.render("Worker", True, (200, 200, 200))
        screen.blit(desc, (x + 80, y + 75))
