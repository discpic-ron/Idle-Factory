import random

class Worker:
  registry = []
  def __init__(self):
    self.gender, self.name = self.generateName()
    self.morale = 100
    self.base_efficiency = 1
    self.payroll = random.randint(1,999)
    self.uniform_purchased = False
    Worker.registry.append(self)

  def generateName(self):
    male_first = ["John", "Michael", "David", "Daniel", "James", "Robert", "Matthew", "Anthony"]
    female_first = ["Sarah", "Emily", "Jessica", "Laura", "Sophia", "Olivia", "Emma", "Isabella"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
      "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez",
        "Lopez", "Gonzalez", "Wilson", "Anderson"]
    if random.choice([True, False]):  # flip a coin
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
      "efficiency": self.base_efficiency
    }
