import pygame
import math
from player import Player
from worker import Worker
from button import Button
from upgrades import Upgrade
from hardware import Hardware
from manager import companyManager

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Factory Sim")
clock = pygame.time.Clock()

# Constants
running = True
state = "main"
grid_size = 50
map_width = 800 // grid_size
map_height = 600 // grid_size
day = 1
total_game_seconds = 21600.0   # start at 6:00 AM
shift_ended = False
time_scale = 60
current_hour = 6
current_minute = 0
BASE_ARROW = [
   (0, 0),  # Arrow tip
   (-15, 20),
   (-7, 20),
   (-7, 40),
   (7, 40),
   (7, 20),
   (15, 20)
]

# Tutorial Constants
starter_cash_given = False  # prevents duplicate popups
machine_bought = False
machine_placed = False
tutorial = False
inventory_open = False
selected_item_for_placement = None
placement_mode = False

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
gold = (255, 215, 0)
dark_gray = (50, 50, 50)
BOX_BG = (30, 30, 30)
HIGHLIGHT = (200, 200, 50)

# Fonts
font_big = pygame.font.Font(None, 74)
font_small = pygame.font.Font(None, 36)
ui_font = pygame.font.SysFont("Arial", 22, bold=True)

# Sprites
background = pygame.Surface((800, 600))
background.fill((30, 30, 30))
player_sprite = pygame.Surface((grid_size, grid_size))
player_sprite.fill((200, 50, 50))

# Context menu state
context_menu_active = False
context_menu_pos = (0, 0)
context_menu_actions = []
context_menu_buttons = []
context_menu_target = None

# Tutorial dialogue
dialogue_steps = [
   "Welcome to your factory!",
   "You've received starter cash! Use it in the machines section of the shop.",
   "Once you have the machine, place it somewhere.",
   "Go back into the shop and hire your first employee!",
   "Great, You're ready to begin your journey!"
]
popups = []
current_step = 0
full_text = dialogue_steps[current_step]
current_text = ""
char_index = 0
typing_speed = 40  # ms per character
TYPE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TYPE_EVENT, typing_speed)

# UI
def drawGrid():
  for x in range(0, map_width * 50, 50):
    pygame.draw.line(screen, dark_gray, (x, 0), (x, map_height * 50))
  for y in range(0, map_height * 50, 50):
    pygame.draw.line(screen, dark_gray, (0, y), (map_width * 50, y))

def open_context_menu(obj, pos, actions):
   global context_menu_active, context_menu_pos, context_menu_target, context_menu_actions, context_menu_buttons
   context_menu_active = True
   context_menu_pos = pos
   context_menu_target = obj
   context_menu_actions = actions
   context_menu_buttons = []

def draw_context_menu():
  global context_menu_buttons

  if not context_menu_active:
    return

  menu_width = 160
  button_height = 35
  padding = 10
  menu_height = padding * 2 + len(context_menu_actions) * (button_height + 5)

  x, y = context_menu_pos
  menu_rect = pygame.Rect(x, y, menu_width, menu_height)
  pygame.draw.rect(screen, (60, 60, 60), menu_rect, border_radius=6)
  pygame.draw.rect(screen, white, menu_rect, 2, border_radius=6)

  context_menu_buttons = []
  current_y = y + padding
  for label, callback in context_menu_actions:
    btn = Button(x + 10, current_y, menu_width - 20, button_height, label, callback)
    btn.draw(screen)
    context_menu_buttons.append(btn)
    current_y += button_height + 5

def close_context_menu():
  global context_menu_active, context_menu_buttons
  context_menu_active = False
  context_menu_buttons = []

def draw_ui_bar():
  bar_width = 150
  ui_rect = pygame.Rect(800 - bar_width, 0, bar_width, 600)
  pygame.draw.rect(screen, (50, 50, 50), ui_rect)

def drawItems(items, cols, start_x, start_y, font, color, card_w=300, card_h=100, gap=20):
  for i, item in enumerate(items):
    row = i // cols
    col = i % cols
    x = start_x + col * (card_w + gap)
    y = start_y + row * (card_h + gap)
    card_rect = pygame.Rect(x, y, card_w, card_h)
    pygame.draw.rect(screen, (70, 70, 70), card_rect, border_radius=8)
    pygame.draw.rect(screen, white, card_rect, 2, border_radius=8)
    item.draw_card(x, y, card_w, card_h, screen, font, color)
    handle_card_click(item, card_rect)

def suffixNotation(number):
  suffixes = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi']
  magnitude = 0
  while abs(number) >= 1000 and magnitude < len(suffixes) - 1:
    magnitude += 1
    number /= 1000.0
  return f"{number:.1f}{suffixes[magnitude]}"

def create_popup(value, x, y):
  global popups
  popups.append({
    'x': x,
    'y': y,
    'alpha': 255,
    'value': f"+{value}"
  })

def draw_popups(screen, dt):
   for popup in popups[:]:
    popup['y'] -= 40 * dt
    popup['alpha'] -= 200 * dt

    if popup['alpha'] <= 0:
      popups.remove(popup)
      continue

    text_surf = ui_font.render(popup['value'], True, gold)
    temp_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
    temp_surf.blit(text_surf, (0, 0))
    temp_surf.set_alpha(int(popup['alpha']))
    screen.blit(temp_surf, (popup['x'], popup['y']))
   
def wrap_text(text, font, max_width):
  words = text.split(" ")
  lines = []
  current_line = ""

  for word in words:
    test_line = current_line + word + " "
    if font.size(test_line)[0] <= max_width:
      current_line = test_line
    else:
      lines.append(current_line)
      current_line = word + " "
  lines.append(current_line)
  return lines

# Button Functionality
def openShop():
  global state
  state = "shop"

def back_action():
  global state
  if state in ["upgrades shop", "worker shop", "hardware shop"]:
    state = "shop"
  else:
    state = "main"

  if state == "inventory":
    state = "main"
  
def upgrades_tab():
  global state
  state = "upgrades shop"

def workers_tab():
  global state
  state = "worker shop"

def machines_tab():
  global state
  state = "hardware shop"
 
def openInventory():
  global state
  state = "inventory"
 
def buy_action(amount, name=None):
  global state
  close_context_menu()
  if state == "worker shop":
    if player.money >= amount:
      player.money -= amount
      manager.total_employees += 1
      if tutorial == True:
        worker_hired = True
      print("Hired a worker!")
    else:
      print("Not enough money to hire a worker!")

  elif state == "hardware shop":
    if player.money >= amount and name:
      player.money -= amount
      if not hasattr(player, "machinery"):
        companyManager.machinery = {}
      if name not in manager.machinery:
        manager.machinery[name] = 0
      manager.machinery[name] += 1
      player.inventory.add_item(name)
      print(f"Bought {name}!")
      if tutorial == True:
         machine_bought = True
    else:
      print(f"Not enough money to buy {name}!")

def buy_upgrade(upgrade):
  close_context_menu()
  if upgrade.cost <= player.money and not upgrade.purchased:
    player.money -= upgrade.cost
    upgrade.affectsPlayer(player)
    print(f"Purchased {upgrade.name}")
  else:
    print("Not enough money or already purchased!")

# Event Functions
def handle_card_click(item, card_rect):
  global event, state
  if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    if card_rect.collidepoint(event.pos):
      if state == "worker shop" and isinstance(item, Worker):
        actions = [
          (f"Hire (${item.payroll})", lambda w=item: buy_action(w.payroll)),
          ("Cancel", close_context_menu)
        ]
      elif state == "hardware shop" and isinstance(item, Hardware):
        actions = [
          (f"Buy (${item.cost})", lambda h=item: buy_action(h.cost, h.name)),
          ("Cancel", close_context_menu)
        ]
      elif state == "upgrades shop" and isinstance(item, Upgrade):
        actions = [
          (f"Buy (${item.cost})", lambda u=item: buy_upgrade(u)),
          ("Cancel", close_context_menu)
        ]
      else:
        actions = [("Cancel", close_context_menu)]
      open_context_menu(item, event.pos, actions)

# Arrow System
def rotate_point(x, y, angle):
  rad = math.radians(angle)
  cos_a = math.cos(rad)
  sin_a = math.sin(rad)
  return (x * cos_a - y * sin_a, x * sin_a + y * cos_a)

def draw_arrow(surface, pos, angle, color, phase):
  t = pygame.time.get_ticks() * 0.006 + phase

  # direction vector for sliding motion
  rad = math.radians(angle - 90)
  dx = math.cos(rad)
  dy = math.sin(rad)

  # slide along direction
  offset_x = dx * math.sin(t) * 10
  offset_y = dy * math.sin(t) * 10

  rotated = []
  for px, py in BASE_ARROW:
    rx, ry = rotate_point(px, py, angle)
    rotated.append((pos[0] + rx + offset_x, pos[1] + ry + offset_y))

  pygame.draw.polygon(surface, color, rotated)
  pygame.draw.polygon(surface, white, rotated, 2)
 
# Tutorial functions
def open_inventory():
  global inventory_open
  inventory_open = True
 
def close_inventory():
  global inventory_open, placement_mode, selected_item_for_placement
  inventory_open = False
  placement_mode = True
  selected_item_for_placement = None
 
def handle_placement_click(mouse_pos):
  global placement_mode, selected_item_for_placement, machine_placed
  if placement_mode == True:
    return
 
# Clock functions
def startDay(delta_time_seconds):
  global total_game_seconds, current_hour, current_minute
  
  # advance time and return formatted string
  total_game_seconds += delta_time_seconds * time_scale
  seconds_today = total_game_seconds % 86400
  current_hour = int(seconds_today // 3600) % 24
  current_minute = int(seconds_today // 60) % 60
  display_hour = current_hour % 12 or 12
  am_pm = "AM" if current_hour < 12 else "PM"
  return f"{display_hour:02d}:{current_minute:02d} {am_pm}"

def endDay():
  global day, shift_ended_flag, current_hour, current_minute
  if current_hour == 21 and current_minute == 0: # check if shift ended and increment day
    if not shift_ended:
      day += 1
      shift_ended_flag = True
      print(f"--- Shift ended. Starting Day {day}. ---")
  else:
    shift_ended_flag = False
    
def drawClock(start_day,dt):
  # call the endDay function and get the updated display string
  display_time_string = start_day(dt)
  current_time_surface = font_small.render(f"Time: {display_time_string}", True, white)
  day_surface = font_small.render(f"Day: {day}", True, white)
  screen.blit(current_time_surface, (2, 0))
  screen.blit(day_surface, (2, 32))
  
# Buttons
back_btn = Button(20, 20, 100, 40, "Back", back_action)
workers_btn = Button(350, 400, 120, 40, "Workers", workers_tab)
machines_btn = Button(350, 300, 120, 40, "Hardware", machines_tab)
upgrades_btn = Button(350, 200, 120, 40, "Upgrades", upgrades_tab)
shop_open_btn = Button(800 - 120, 100, 100, 50, "Shop", openShop)
inventory_btn = Button(800 - 120, 170, 100, 50, "Inventory", openInventory)

shop_buttons = [back_btn, workers_btn, machines_btn, upgrades_btn]

# Example content
Hardware("Workbench", "Allows crafting", cost=200)
upgrade_player_speed = Upgrade("Move faster", "Player moves faster", cost=50, affect_player=True, effect_value=0.2)
for _ in range(5):
  Worker()
manager = companyManager()
player = Player()
notation = suffixNotation(player.money)
player.money = 0

while running:
  dt = clock.get_time() / 1000
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    if state == "main":
      shop_open_btn.handle_event(event)
      inventory_btn.handle_event(event)
     
    elif state == "shop":
      for b in shop_buttons:
        b.handle_event(event)
    
    elif state in ["worker shop", "hardware shop", "upgrades shop","inventory"]:
      back_btn.handle_event(event)
      
    if event.type == TYPE_EVENT:
      if char_index < len(full_text):
        current_text += full_text[char_index]
        char_index += 1

    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_SPACE and char_index >= len(full_text):
        if current_step < len(dialogue_steps) - 1:  # Advance to next step
          current_step += 1
          full_text = dialogue_steps[current_step]
          current_text = ""
          char_index = 0
          if current_step == 1 and starter_cash_given == False:  # Trigger popup at step 1
            create_popup(500, 400, 300)
            starter_cash_given = True

    # Context menu click handling
    if context_menu_active and event.type == pygame.MOUSEBUTTONDOWN:
      mx, my = event.pos
      clicked = False
      for btn in context_menu_buttons:
        if btn.rect.collidepoint(mx, my):
          btn.handle_event(event)  # Execute the action
          clicked = True
          break
      if not clicked:
        close_context_menu()  # Click outside → close

  screen.blit(background, (0, 0))
  if state == "main":
    drawGrid()
    draw_ui_bar()
    drawClock(startDay,dt)
    box_rect = pygame.Rect(50, 450, 700, 120)
    pygame.draw.rect(screen, BOX_BG, box_rect)
    pygame.draw.rect(screen, white, box_rect, 3)

    lines = wrap_text(current_text, ui_font, 660)
    y = box_rect.y + 15
    for line in lines:
      surf = ui_font.render(line, True, white)
      screen.blit(surf, (box_rect.x + 15, y))
      y += 25

    if char_index >= len(full_text):
      prompt = ui_font.render("[ SPACE ]", True, HIGHLIGHT)
      screen.blit(prompt, (box_rect.right - 120, box_rect.bottom - 35))

    if starter_cash_given == True:
      draw_popups(screen, dt)
      player.money = 500

    money_rect = pygame.Rect(800 - 140, 10, 130, 40)
    pygame.draw.rect(screen, (100, 100, 100), money_rect, 0, 10)
    money_text = font_small.render(f"Money: {player.money}", True, (0, 0, 0))
    screen.blit(money_text, (800 - 135, 15))
    shop_open_btn.draw(screen)
    inventory_btn.draw(screen)

  elif state == "shop":
    text = font_big.render("Shop", True, white)
    screen.blit(text, text.get_rect(center=(400, 100)))
    for b in shop_buttons:
      b.draw(screen)

  elif state == "worker shop":
    text = font_big.render("Human Resources", True, white)
    screen.blit(text, text.get_rect(center=(400, 100)))
    drawItems(Worker.registry, cols=3, start_x=50, start_y=200, font=font_small, color=white)

  elif state == "hardware shop":
    text = font_big.render("Hardware Shop", True, white)
    screen.blit(text, text.get_rect(center=(400, 100)))
    drawItems(Hardware.registry, cols=3, start_x=50, start_y=200, font=font_small, color=white)

  elif state == "upgrades shop":
    text = font_big.render("Upgrades", True, white)
    screen.blit(text, text.get_rect(center=(400, 100)))
    drawItems(Upgrade.registry, cols=3, start_x=50, start_y=200, font=font_small, color=white)
  
  elif state == "inventory":
    text = font_big.render("Inventory", True, white)
    screen.blit(text, text.get_rect(center=(400, 100)))
    
  if state in ["worker shop", "hardware shop", "upgrades shop","inventory"]:
    back_btn.draw(screen)

  if context_menu_active:
    draw_context_menu()
   
  # tutorial steps
  if current_step == 1 and state == "main":
    draw_arrow(screen,(650,130),90,gold,3.7)
     
  elif current_step == 2 and state == "shop":
    draw_arrow(screen, (330, 320), 90, gold, 3.7)
 
  elif current_step == 3:
    draw_arrow(screen, (650, 130), 90, gold, 3.7)
     
  if current_step >= len(dialogue_steps) - 1:
    tutorial = False
     
  pygame.display.flip()
  clock.tick(60)
pygame.quit()
