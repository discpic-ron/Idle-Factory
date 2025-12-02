from worker import Worker

class companyManager:
  def __init__(self):
    self.machinery = {
      # manual
      "press station": 0,
      "manual sewing machine": 0,
   
      # semi auto
      "electric sewing machine": 0,
      "conveyor belts": 0,
      "packaging tables": 0,
   
      # auto
      "industrial sewing machine": 0,
      "automated cutters": 0
    }
    self.resources = {
      "cloth": 0,
      "thread": 0,
    }
    self.workers = {}
    self.total_employees = 0
    self.production_multiplier = 1
    self.total_lifetime_money = 0
  
  def manage_employee_costs(self,player):
    total_payroll = sum(worker.payroll for worker in self.workers)  # Calculate total payroll
    player.money -= total_payroll                                     # Deduct employee costs
    self.check_morale()                                              # Check and update morale
  
  def manage_machine_costs(self,player):
    # Example for machine maintenance costs
    maintenance_cost = sum(machine.maintenance_cost for machine in self.machines)  # Sum of all machines' upkeep
    player -= maintenance_cost  # Deduct maintenance costs from money

  def check_morale(self):
    # Check each worker's morale and adjust accordingly
    for worker in self.workers:
      if Worker.morale < 50:
        # Action if morale is low, like making adjustments or taking more actions
        Worker.boostMorale()  # Example of boosting morale

  def buyResources(self, player_instance, resource, amount, cost_per_unit):
    """Spend money to buy resources via the Player's wallet."""
    total_cost = amount * cost_per_unit
    if player_instance.money >= total_cost:
        player_instance.money -= total_cost
        self.resources[resource] = self.resources.get(resource, 0) + amount
        print(f"Bought {amount} {resource}. Remaining money: {player_instance.money}")
    else:
        print("Not enough money!")
        
  def prestige(self):
      Player.money = 0
      self.total_lifetime_money = 0
      self.production_multiplier += 0.5
      self.total_employees = 0
      self.machinery = {
        # manual
        "press station": 0,
        "manual sewing machine": 0,
   
          # semi auto
        "electric sewing machine": 0,
        "conveyor belts": 0,
        "packaging tables": 0,
   
          # auto
        "industrial sewing machine": 0,
        "automated cutters": 0
      }
      
      self.resources = {
        "cloth": 0,
        "thread": 0,
      }