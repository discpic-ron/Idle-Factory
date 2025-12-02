import time
import json

class offlineProgress:
  def __init__(self,save_file="save_data.json"):
    self.save_file = save_file

  def saveTimestamp(self):
    with open(self.save_file, "w") as f:
      json.dump({"last_active": time.time()}, f)

  def loadTimestamp(self):
    try:
      with open(self.save_file, "r") as f:
        data = json.load(f)
        return data.get("last_active", time.time())
    except FileNotFoundError:
      return time.time(self)

  def get_offline_duration(self):
    last_active = self.load_timestamp()
    now = time.time()
    return now - last_active  # in seconds

  def calculate_offline_gains(self,workers, lines):
    duration = self.get_offline_duration()
    ticks = int(duration // 60)  # 1 tick per minute offline
    total_output = 0

    for _ in range(ticks):
      for line in lines:
        if not line.assigned_product:
          continue
          output = line.base_output * line.level
          for w in workers:
            output += w.produce()
          total_output += output

      earnings = round(total_output * 2)  # $2 per unit
      return earnings