import pygame

class NotificationManager:
  def __init__(self):
    self.notifications = []
    self.font = pygame.font.SysFont(None, 24)
    self.duration = 3000
    self.padding = 10
    self.max_notifs = 4

  def add(self, message, color):
    surf = self.font.render(message, True, color)
    self.notifications.append({
      "surf": surf,
      "time": pygame.time.get_ticks()
    })
    if len(self.notifications) > self.max_notifs:
      self.notifications.pop(0)

  def update(self):
    now = pygame.time.get_ticks()
    self.notifications = [n for n in self.notifications if now - n["time"] < self.duration]

  def draw(self, screen, color):
    y = screen.get_height() - self.padding
    for n in reversed(self.notifications):
      w, h = n["surf"].get_size()
      rect = pygame.Rect(screen.get_width()-w-2*self.padding, y-h-2*self.padding, w+2*self.padding, h+2*self.padding)
      pygame.draw.rect(screen, color, rect, border_radius=5)
      screen.blit(n["surf"], n["surf"].get_rect(center=rect.center))
      y = rect.top - self.padding
