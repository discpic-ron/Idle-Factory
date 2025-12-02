import pygame
from player import Player
from worker import Worker
from button import Button
from upgrades import Upgrade
from hardware import Hardware

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_SIZE = 50
MAP_WIDTH = SCREEN_WIDTH // GRID_SIZE   # 16
MAP_HEIGHT = SCREEN_HEIGHT // GRID_SIZE # 12
WHITE = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
state = "main"
tax_rate = 0.15
context_menu_active = False
context_menu_pos = (0, 0)
context_menu_actions = [] # Store the actions list
context_menu_buttons = [] # Store the button instances for event handling
selected_worker = None
placement_mode = None

# Fonts
font_big = pygame.font.Font(None, 74)
font_small = pygame.font.Font(None, 36)

# Sprites
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background.fill((30, 30, 30))
player_sprite = pygame.Surface((GRID_SIZE, GRID_SIZE))
player_sprite.fill((200, 50, 50))

def drawGrid():
    for x in range(0, MAP_WIDTH * GRID_SIZE, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, MAP_HEIGHT * GRID_SIZE))
    for y in range(0, MAP_HEIGHT * GRID_SIZE, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (MAP_WIDTH * GRID_SIZE, y))

def openShop():
    global state
    state = "shop"

# --- Shop Actions ---
def back_action():
  global state
  if state in ["upgrades shop", "worker shop", "hardware shop"]:
    state = "shop"
  else:
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

def buy_action(amount, name=None):
    global state
    close_context_menu() # Close menu after action
    if state == "worker shop":
        if player.money >= amount:
            player.money -= amount
            player.total_employees += 1
            print("Hired a worker!")
        else:
            print("Not enough money to hire a worker!")
    elif state == "machines shop":
        if player.money >= amount and name:
            player.money -= amount
            # Assuming player.machinery is a dict that needs to be initialized/updated
            if name not in player.machinery:
                 player.machinery[name] = 0
            player.machinery[name] += 1
            player.inventory.add_item(name)
            print(f"Bought {name}!")
        else:
            print(f"Not enough money to buy {name}!")
    else:
        return

def buy_upgrade(upgrade):
    close_context_menu() # Close menu after action
    if upgrade.cost <= player.money and not upgrade.purchased: # Fixed logic to check cost first
        player.money -= upgrade.cost
        upgrade.affectsPlayer(player)
        print(f"Purchased {upgrade.name}")
    else:
        print("Not enough money or already purchased!")

# --- UI ---
def draw_ui_bar():
    bar_width = 150   # thickness of the bar
    ui_rect = pygame.Rect(SCREEN_WIDTH - bar_width, 0, bar_width, SCREEN_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), ui_rect)  # dark gray bar
    
def draw_worker_catalog(current_event, start_y=200):
    workers = Worker().registry
    card_width, card_height = 300, 100
    workers_to_render = workers[:5]
    
    for i, w in enumerate(workers_to_render):
        stats = w.showStats()
        row = i // 3
        col = i % 3
        x = 50 + col * (card_width + 20)
        y = start_y + row * (card_height + 20)
    
        # Card background
        card_rect = pygame.Rect(x, y, card_width, card_height)
        pygame.draw.rect(screen, (80, 80, 80), card_rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, card_rect, 2, border_radius=8)
        
         # Portrait placeholder
        portrait_rect = pygame.Rect(x + 10, y + 10, 80, 80)
        pygame.draw.rect(screen, (150, 150, 200), portrait_rect)

        # Text info
        screen.blit(font_small.render(stats["name"], True, WHITE), (x + 100, y + 10))
        screen.blit(font_small.render(stats["gender"], True, WHITE), (x + 100, y + 30))
        screen.blit(font_small.render(f"Morale: {stats['morale']}", True, WHITE), (x + 100, y + 50))
        screen.blit(font_small.render(f"Eff: {stats['efficiency']}", True, WHITE), (x + 100, y + 70))
    
        # Click detection for popup
        if current_event.type == pygame.MOUSEBUTTONDOWN and current_event.button == 1:
            if card_rect.collidepoint(current_event.pos):
                actions = [
                    ("Buy ($50)", lambda payroll=w.payroll: buy_action(payroll)),
                    ("Cancel", close_context_menu)
                ]
                open_context_menu(w, current_event.pos, actions)
                
def draw_upgrades_catalog(current_event, start_y=200):
    upgrades = Upgrade.registry
    card_width, card_height = 300, 100

    for i, upg in enumerate(upgrades):
        stats = upg.showStats()

        row = i // 3
        col = i % 3
        
        x = 50 + col * (card_width + 20)
        y = start_y + row * (card_height + 20)

        # Card background
        card_rect = pygame.Rect(x, y, card_width, card_height)
        pygame.draw.rect(screen, (70, 70, 70), card_rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, card_rect, 2, border_radius=8)

        # Icon placeholder (same vibe as worker portrait)
        icon_rect = pygame.Rect(x + 10, y + 10, 80, 80)
        pygame.draw.rect(screen, (200, 180, 120), icon_rect)

        # Title + cost
        screen.blit(font_small.render(stats["name"], True, WHITE), (x + 100, y + 10))
        screen.blit(font_small.render(f"Cost: ${stats['cost']}", True, WHITE), (x + 100, y + 30))

        # Description (trimmed)
        desc = stats["description"][:28] + ("..." if len(stats["description"]) > 28 else "")
        screen.blit(font_small.render(desc, True, WHITE), (x + 100, y + 55))

        # Click → open upgrade buy popup
        if current_event.type == pygame.MOUSEBUTTONDOWN and current_event.button == 1:
            if card_rect.collidepoint(current_event.pos):
                # FIX: Use defined functions for context menu
                actions = [
                    ("Buy", lambda u=upg: buy_upgrade(u)),
                    ("Cancel", close_context_menu)
                ]
                open_context_menu(upg, current_event.pos, actions)

def draw_hardware_catalog(current_event, start_y=200):
    hardware_items = Hardware.registry
    card_width, card_height = 300, 100

    for i, hrw in enumerate(hardware_items):
        stats = hrw.showStats()

        row = i // 3
        col = i % 3
        
        x = 50 + col * (card_width + 20)
        y = start_y + row * (card_height + 20)

        # Card background
        card_rect = pygame.Rect(x, y, card_width, card_height)
        pygame.draw.rect(screen, (70, 70, 70), card_rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, card_rect, 2, border_radius=8)

        # Icon placeholder (same vibe as worker portrait)
        icon_rect = pygame.Rect(x + 10, y + 10, 80, 80)
        pygame.draw.rect(screen, (200, 180, 120), icon_rect)

        # Title + cost
        screen.blit(font_small.render(stats["name"], True, WHITE), (x + 100, y + 10))
        screen.blit(font_small.render(f"Cost: ${stats['cost']}", True, WHITE), (x + 100, y + 30))

        # Description (trimmed)
        desc = stats["description"][:28] + ("..." if len(stats["description"]) > 28 else "")
        screen.blit(font_small.render(desc, True, WHITE), (x + 100, y + 55))

        # Click → open upgrade buy popup
        if current_event.type == pygame.MOUSEBUTTONDOWN and current_event.button == 1:
          if card_rect.collidepoint(current_event.pos):
            actions = [
                    (f"Buy (${hrw.cost})", lambda amount=hrw.cost, name=hrw.name: buy_action(amount, name)),
                    ("Cancel", close_context_menu)
            ]
            open_context_menu(hrw, current_event.pos, actions)
            
def draw_inventory_bar():
    items = player.inventory.get_items()
    bar_height = 100
    y = SCREEN_HEIGHT - bar_height
    pygame.draw.rect(screen, (40, 40, 40), (0, y, SCREEN_WIDTH, bar_height))

    x = 20
    for item in items:
        rect = pygame.Rect(x, y + 20, 80, 60)
        pygame.draw.rect(screen, (100, 100, 150), rect)
        label = font_small.render(f"{item['name']} x{item['count']}", True, WHITE)
        screen.blit(label, (x + 5, y + 30))
        x += 100
        
def open_context_menu(obj, pos, actions):
    # actions = [("Label", callback), ("Another", callback)...]
    global context_menu_active, context_menu_pos, context_menu_target, context_menu_actions, context_menu_buttons
    context_menu_active = True
    context_menu_pos = pos
    context_menu_target = obj
    context_menu_actions = actions
    # Clear buttons, they will be recreated on draw/event loop
    context_menu_buttons = [] 

def open_upgrade_menu(upg, pos, actions):
    open_context_menu(upg, pos, actions) 
    
def draw_context_menu():
    global context_menu_pos, context_menu_actions, context_menu_buttons

    menu_width = 160
    button_height = 35
    padding = 10

    menu_height = padding * 2 + len(context_menu_actions) * (button_height + 5)

    x, y = context_menu_pos
    menu_rect = pygame.Rect(x, y, menu_width, menu_height)

    pygame.draw.rect(screen, (60, 60, 60), menu_rect, border_radius=6)
    pygame.draw.rect(screen, WHITE, menu_rect, 2, border_radius=6)

    # Recreate buttons only on draw
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
    
def handle_inventory_click(mx, my):
    items = player.inventory.get_items()
    y = SCREEN_HEIGHT - 100
    if my >= y:
        index = (mx - 20) // 100
        if 0 <= index < len(items):
            return items[index]["name"]
    return None
# --- Shop Setup ---
back_btn = Button(20, 20, 100, 40, "Back", back_action)
workers_btn = Button(350, 400, 120, 40, "Workers", workers_tab)
machines_btn = Button(350, 300, 120, 40, "Harware", machines_tab)
upgrades_btn = Button(350, 200, 120, 40, "Upgrades", upgrades_tab)
shop_buttons = [back_btn, workers_btn, machines_btn, upgrades_btn]

buy_wrk_btn = Button(320, 450, 160, 40, "Hire worker", lambda: buy_action(50))
worker_shop_buttons = [back_btn]
shop_open_btn = Button(SCREEN_WIDTH - 120, 100, 100, 50, "Shop", openShop)
machines_shop_buttons = [back_btn]
Hardware("Workbench", "Allows crafting", cost=200)
# --- upgrades ---
upgrade_player_speed = Upgrade("Move faster", "Player moves faster", cost=50, affect_player=True, effect_value=0.2)
if not Upgrade.registry:
    Upgrade.registry = [upgrade_player_speed]
upgrade_buttons = [back_btn]

# --- Demo ---
player = Player(0, 0, player_sprite)
player.money = 500 # Give player some starting money for testing
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break # Exit event loop if quitting

        if state == "main":
            shop_open_btn.handle_event(event)

        elif state == "shop":
            for b in shop_buttons:
                b.handle_event(event)

        elif state == "worker shop":
            for b in worker_shop_buttons:
                b.handle_event(event)
            draw_worker_catalog(event) 

        elif state == "hardware shop":
            for b in machines_shop_buttons:
                b.handle_event(event)
            draw_hardware_catalog(event)

        elif state == "upgrades shop":
            for b in upgrade_buttons:
                b.handle_event(event)
            draw_upgrades_catalog(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not context_menu_active:
            mx, my = event.pos
            gx, gy = mx // GRID_SIZE, my // GRID_SIZE
            
            if player.rect.collidepoint(mx, my):
                player.selected = True
            elif player.selected:
                path = [(player.rect.x // GRID_SIZE, player.rect.y // GRID_SIZE), (gx, gy)]
                player.set_path(path)
                player.selected = False  # optional auto-deselect
        
  
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and context_menu_active:
            mx, my = event.pos
            # Check if click was outside any context menu button
            clicked_on_button = any(b.rect.collidepoint(mx, my) for b in context_menu_buttons)
            if not clicked_on_button:
                # Approximate menu area check
                menu_rect = pygame.Rect(context_menu_pos[0], context_menu_pos[1], 160, 40 * len(context_menu_actions))
                if not menu_rect.collidepoint(mx, my):
                    close_context_menu()
                    
            if placement_mode:
                gx, gy = mx // GRID_SIZE, my // GRID_SIZE
                hardware.place_item(gx, gy, placement_mode)
                player.inventory.remove_item(placement_mode)
                placement_mode = None
            else:
                placement_mode = handle_inventory_click(mx, my)

    player.update()

    screen.blit(background, (0, 0))
    if state == "main":
        drawGrid()
        draw_ui_bar()
        player.draw(screen)

        # Money HUD inside bar
        money_rect = pygame.Rect(SCREEN_WIDTH - 140, 10, 130, 40)
        pygame.draw.rect(screen, (100, 100, 100), money_rect, 0, 10)
        money_text = font_small.render(f"Money: {player.money}", True, (0, 0, 0))
        screen.blit(money_text, (SCREEN_WIDTH - 135, 15))
        shop_open_btn.draw(screen)

    elif state == "shop":
        text = font_big.render("Shop", True, WHITE)
        screen.blit(text, text.get_rect(center=(400, 100)))
        for b in shop_buttons:
            b.draw(screen)

    elif state == "worker shop":
        text = font_big.render("Human Resources", True, WHITE)
        screen.blit(text, text.get_rect(center=(400, 100)))
        draw_worker_catalog(pygame.event.Event(pygame.NOEVENT)) 
        for b in worker_shop_buttons:
            b.draw(screen)

    elif state == "hardware shop":
        text = font_big.render("Hardware Shop", True, WHITE)
        screen.blit(text, text.get_rect(center=(400, 100)))
        for b in machines_shop_buttons:
            b.draw(screen)
        draw_hardware_catalog(pygame.event.Event(pygame.NOEVENT))
        
    elif state == "upgrades shop":
        text = font_big.render("Upgrades", True, WHITE)
        screen.blit(text, text.get_rect(center=(400, 100)))
        for b in upgrade_buttons:
            b.draw(screen)
        draw_upgrades_catalog(pygame.event.Event(pygame.NOEVENT))
    if context_menu_active:
        draw_context_menu() 

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
