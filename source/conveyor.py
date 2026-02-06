class Conveyor:
  def __init__(self):
    self.inputs = [] 
    self.outputs = []
    
  def addItem(self,item):
    self.inputs.append(item)
    
  def assignOutput(self,output):
    self.outputs.append(output)
    
  def push(self, item):
    for i in self.inputs:
      pass
    
