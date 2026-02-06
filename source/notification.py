class Notification:
  def __init__(self):
    self.notifications = []

  def add(self, message, color, font):
    surf = font.render(message, True, color)
    self.notifications.append({
      "surf": surf,
      "time": pygame.time.get_ticks()
    })
    if len(self.notifications) > 4:
      self.notifications.pop(0)

  def update(self):
    now = pygame.time.get_ticks()
    self.notifications = [n for n in self.notifications if now - n["time"] < 3000]

  def draw(self, screen, color):
    y = screen.get_height() - 10
    for n in reversed(self.notifications):
      w, h = n["surf"].get_size()
      rect = pygame.Rect(screen.get_width()-w-20, y-h-20, w+20, h+20)
      pygame.draw.rect(screen, color, rect, border_radius=5)
      screen.blit(n["surf"], n["surf"].get_rect(center=rect.center))
      y = rect.top - 10
