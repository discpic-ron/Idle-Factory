import pygame
import math
from player import Player
from worker import Worker
from button import Button
from hardware import Hardware
from inventory import Inventory
from manager import companyManager
from notification import Notification

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
grid = [[None for _ in range(map_width)] for _ in range(map_height)]

# Tutorial Constants
starter_cash_given = False
machine_bought = False
machine_placed = False
tutorial = True
inventory_open = False
selected_item = None
placement_mode = False
worker_hired = False

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
gold = (255, 215, 0)
dark_gray = (50, 50, 50)
BOX_BG = (30, 30, 30)
HIGHLIGHT = (200, 200, 50)
green = (0, 255, 0)
red = (255, 0, 0)

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
   "You've received starter cash! Use it in the hardware shop.",
   "Once you have the machine, place it somewhere.",
   "Go back into the shop and hire your first employee!",
   "Great, You're ready to begin your journey!"
]
popups = []
current_step = 0
full_text = dialogue_steps[current_step]
current_text = ""
char_index = 0
typing_speed = 40
TYPE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TYPE_EVENT, typing_speed)

def unclock(item):
  if player.money == item.cost:
    item.unlocked = True
    return item

# UI
def drawGrid():
  for x in range(0, map_width * 50, 50):
    pygame.draw.line(screen, dark_gray, (x, 0), (x, map_height * 50))
  for y in range(0, map_height * 50, 50):
    pygame.draw.line(screen, dark_gray, (0, y), (map_width * 50, y))

def get_coords(mouse_pos):
    mx, my = mouse_pos
    grid_x = mx // grid_size
    grid_y = my // grid_size
    return grid_x, grid_y
def draw_workers():
    for i in range(manager.total_employees):
      wx = 50 + (i * 40)
      wy = 550
      pygame.draw.circle(screen, (100, 150, 255), (wx, wy), 15)
      pygame.draw.circle(screen, white, (wx, wy), 15, 2)
      
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
    handle_card(item, card_rect)

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
  if state in ["worker shop", "hardware shop"]:
    state = "shop"
  else:
    state = "main"

  if state == "inventory":
    state = "main"

def workers_tab():
  global state
  state = "worker shop"

def machines_tab():
  global state
  state = "hardware shop"

def openInventory():
  global state
  state = "inventory"

def openManager():
  global state
  state = "worker management"
  
def place_item(event, grid_pos):
    global placement_mode, selected_item

    # Check if we are actually in a state to place things
    if state != "main" or not placement_mode or selected_item is None:
        return

    # Use the event type passed from the main loop (MOUSEBUTTONDOWN)
    if event.type == pygame.MOUSEBUTTONDOWN and grid_pos:
        gx, gy = grid_pos
        if grid[gy][gx] is None:
            # We use the hardware object stored in the inventory
            item_name = selected_item.name
            grid[gy][gx] = selected_item
            player_inventory.remove_item(item_name)

            print(f"{item_name} has been placed at {gx}, {gy}!")

            # Reset mode
            selected_item = None
            placement_mode = False
        else:
            print("Space Occupied!")
            
def start_placement(item_obj):
  global state, placement_mode, selected_item,grid_pos
  selected_item = item_obj
  state = "main"
  placement_mode = True
  close_context_menu()

def buy_action(amount, name=None,hardware_obj=None):
  global state,machine_bought
  close_context_menu()
  if state == "worker shop":
    if player.money >= amount:
      player.money -= amount
      manager.total_employees += 1
      notifier.add(f"Bought Worker!",white,font_small)
      print("Hired a worker!")
      if tutorial == True:
        worker_hired = True
    else:
      print("Not enough money to hire a worker!")

  elif state == "hardware shop":
    if player.money >= amount and name:
      player.money -= amount
      if not hasattr(player, "machinery"):
        manager.machinery = {}
      if name not in manager.machinery:
        manager.machinery[name] = 0
      manager.machinery[name] += 1
      notifier.add(f"Bought machine!",white,font_small)
      player_inventory.add_item(name,hardware_obj)
      print(f"Bought {name}!")
      if tutorial == True:
        machine_bought = True
    else:
      print(f"Not enough money to buy {name}!")

# Event Functions
def handle_card(item, card_rect):
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
          (f"Buy (${item.cost})", lambda h=item: buy_action(h.cost, h.name,hardware_obj=h)),
          ("Cancel", close_context_menu)
        ]
      elif state == "inventory":
        actions = [
            ("Place Item",lambda i=item: start_placement(i)),
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

  rad = math.radians(angle - 90)
  dx = math.cos(rad)
  dy = math.sin(rad)

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
  global inventory_open, placement_mode, selected_item
  inventory_open = False
  placement_mode = True
  selected_item = None

def select_item(item_obj):
  global selected_item
  selected_item = item_obj
  if selected_item:
    print(f"Selected: {selected_item.name if hasattr(selected_item, 'name') else 'Unknown'}")
  else:
    print("Selection cleared")

def skip_tutorial():
  global tutorial, current_step, current_text, full_text, char_index,player
  tutorial = False
  starter_cash_given = True
  player.money = 500
  current_step = len(dialogue_steps) - 1
  full_text = ""
  current_text = ""
  char_index = 0

# Clock functions
def startDay(delta_time_seconds):
  global total_game_seconds, current_hour, current_minute

  total_game_seconds += delta_time_seconds * time_scale
  seconds_today = total_game_seconds % 86400
  current_hour = int(seconds_today // 3600) % 24
  current_minute = int(seconds_today // 60) % 60
  display_hour = current_hour % 12 or 12
  am_pm = "AM" if current_hour < 12 else "PM"
  return f"{display_hour:02d}:{current_minute:02d} {am_pm}"

def endDay():
  global day, shift_ended_flag, current_hour, current_minute
  if current_hour == 21 and current_minute == 0:
    if not shift_ended:
      day += 1
      shift_ended_flag = True
      print(f"--- Shift ended. Starting Day {day}. ---")
  else:
    shift_ended_flag = False

def drawClock(start_day,dt):
  display_time_string = start_day(dt)
  current_time_surface = font_small.render(f"Time: {display_time_string}", True, white)
  day_surface = font_small.render(f"Day: {day}", True, white)
  screen.blit(current_time_surface, (2, 0))
  screen.blit(day_surface, (2, 32))

# placement system
def draw_placed_items():
  for y in range(map_height):
    for x in range(map_width):
      tile = grid[y][x]
      if tile:
        rect = pygame.Rect(x * grid_size, y * grid_size, grid_size, grid_size)
        pygame.draw.rect(screen, green, rect.inflate(-4, -4))
        pygame.draw.rect(screen, white, rect.inflate(-4, -4), 1)

def world_to_grid(mx, my):
    gx, gy = mx // grid_size, my // grid_size
    if 0 <= gx < map_width and 0 <= gy < map_height:
        return gx, gy
    return None

def select_item(item_obj):
  global selected_item
  selected_item = item_obj
  if selected_item:
    print(f"Selected: {selected_item.name if hasattr(selected_item, 'name') else 'Unknown'}")
  else:
    print("Selection cleared")

# Buttons
back_btn = Button(20, 20, 100, 40, "Back", back_action)
workers_btn = Button(350, 400, 120, 40, "Workers", workers_tab)
machines_btn = Button(350, 300, 120, 40, "Hardware", machines_tab)
shop_open_btn = Button(800 - 120, 100, 100, 50, "Shop", openShop)
inventory_btn = Button(800 - 120, 170, 100, 50, "Inventory", openInventory)
skip_tutorial_btn = Button(650, 410, 120, 40, "Skip", skip_tutorial)
manage_staff_btn = Button(350, 500, 150, 40, "Manage Staff", lambda: openManager("worker management"))

shop_buttons = [back_btn, workers_btn, machines_btn]

Hardware("Workbench", "Allows crafting", cost=200).unlocked = True
Hardware("Conveyor belt","moves stuff",cost=50).unlocked = True

for _ in range(5):
  Worker()
manager = companyManager()
player = Player()
notifier = Notification()
player_inventory = Inventory()
notation = suffixNotation(player.money)
player.money = 0

while running:
  dt = clock.get_time() / 1000
  mx, my = pygame.mouse.get_pos()
  grid_pos = world_to_grid(mx, my)

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    if state == "main":
      shop_open_btn.handle_event(event)
      inventory_btn.handle_event(event)

    elif state == "shop":
      for b in shop_buttons:
        b.handle_event(event)

    elif state in ["worker shop", "hardware shop","inventory"]:
      back_btn.handle_event(event)

    if tutorial == True:
      skip_tutorial_btn.handle_event(event)

    if event.type == TYPE_EVENT:
      if char_index < len(full_text):
        current_text += full_text[char_index]
        char_index += 1

    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_SPACE and char_index >= len(full_text):
        if current_step < len(dialogue_steps) - 1:
          current_step += 1
          full_text = dialogue_steps[current_step]
          current_text = ""
          char_index = 0
          
    if event.type == pygame.MOUSEBUTTONDOWN:
      mx, my = event.pos
      grid_pos = world_to_grid(mx, my)
  
      if context_menu_active:
          clicked = False
          for btn in context_menu_buttons:
              if btn.rect.collidepoint(mx, my):
                  btn.handle_event(event)
                  clicked = True
                  break
          if not clicked:
              close_context_menu()
      elif state == "main" and placement_mode == True:
            place_item(event, grid_pos)
    notifier.update() 
    
  screen.blit(background, (0, 0)) 
  if state == "main": 
    drawGrid() 
    drawClock(startDay, dt) # Draw placed items
    draw_placed_items()
    draw_workers()
    ui_rect = pygame.Rect(650, 0, 150, 600) 
    pygame.draw.rect(screen, (50, 50, 50), ui_rect) 
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
    
  elif state == "inventory": 
    text = font_big.render("Inventory", True, white) 
    screen.blit(text, text.get_rect(center=(400, 100))) 
    drawItems(player_inventory.get_items(), cols=3, start_x=50, start_y=200, font=font_small, color=white) 
    
  elif state == "worker management":
    text = font_big.render("Staff Management", True, white)
    screen.blit(text, text.get_rect(center=(400, 50)))
    
    # List hied workers
    for i in range(manager.total_employees):
        y_pos = 150 + (i * 60)
        worker_rect = pygame.Rect(50, y_pos, 700, 50)
        pygame.draw.rect(screen, (60, 60, 60), worker_rect, border_radius=5)
        
        name_text = font_small.render(f"Worker #{i+1}", True, white)
        screen.blit(name_text, (70, y_pos + 10))
        
        # Assignment Button logic would go here
        assign_btn = Button(500, y_pos + 5, 180, 40, "Assign Machine", lambda idx=i: open_assignment_menu(idx))
        assign_btn.draw(screen)
        
  if state in ["worker shop", "hardware shop", "inventory"]: 
    back_btn.draw(screen)
    
  if state in ["worker shop", "hardware shop", "inventory", "main"] and tutorial == False: 
    notifier.draw(screen, green)
    
  if context_menu_active: 
    draw_context_menu()
    
  # Tutorial arrows 
  if current_step == 1 and state == "main": 
      draw_arrow(screen, (650, 130), 90, gold, 3.7) 
  elif current_step == 1 and state == "shop": 
    draw_arrow(screen, (330, 320), 90, gold, 3.7) 
  elif current_step == 3 and state == "main": 
    draw_arrow(screen, (650, 130), 90, gold, 3.7) 
  elif current_step == 3 and state == "shop": 
    draw_arrow(screen, (330, 420), 90, gold, 3.7) # Tutorial dialogue box 
    
  if tutorial == True: 
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
      
  if tutorial == True and current_step in [0, 1]: 
    skip_tutorial_btn.draw(screen) 
    
  if placement_mode == True:
    mx, my = pygame.mouse.get_pos()
    grid_pos = world_to_grid(mx, my)
    if grid_pos:
        gx, gy = grid_pos
        # Green ghost
        ghost = pygame.Surface((grid_size, grid_size), pygame.SRCALPHA)
        ghost.fill((*green, 140))  # semi-transparent
        screen.blit(ghost, (gx * grid_size, gy * grid_size))
    
  pygame.display.flip() 
  clock.tick(60) 
pygame.quit()
