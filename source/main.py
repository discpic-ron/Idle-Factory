import pygame
from player import Player
from worker import Worker
from button import Button
from upgrades import Upgrade
from hardware import Hardware

# Screen constants
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Factory Sim")
clock = pygame.time.Clock()
running = True

# State
state = "main"
grid_size = 50
map_width = 800 // grid_size
map_height = 600 // grid_size

# Colors
black = (0, 0, 0)
white = (255, 255, 255)

# Fonts
font_big = pygame.font.Font(None, 74)
font_small = pygame.font.Font(None, 36)

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

def drawGrid():
    for x in range(0, map_width * grid_size, grid_size):
        pygame.draw.line(screen, white, (x, 0), (x, map_height * grid_size))
    for y in range(0, map_height * grid_size, grid_size):
        pygame.draw.line(screen, white, (0, y), (map_width * grid_size, y))

def openShop():
    global state
    state = "shop"

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

def open_context_menu(obj, pos, actions):
    global context_menu_active, context_menu_pos, context_menu_target
    global context_menu_actions, context_menu_buttons
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

def drawItems(items, cols, start_x, start_y, font,color,card_w=300, card_h=100, gap=20):
    for i, item in enumerate(items):
        row = i // cols
        col = i % cols
        x = start_x + col * (card_w + gap)
        y = start_y + row * (card_h + gap)
        card_rect = pygame.Rect(x, y, card_w, card_h)
        pygame.draw.rect(screen, (70, 70, 70), card_rect, border_radius=8)
        pygame.draw.rect(screen, white, card_rect, 2, border_radius=8)
        item.draw_card(x, y, card_w, card_h, screen, font,color)
        handle_card_click(item, card_rect)

def buy_action(amount, name=None):
    global state
    close_context_menu()
    if state == "worker shop":
        if player.money >= amount:
            player.money -= amount
            player.total_employees += 1
            print("Hired a worker!")
        else:
            print("Not enough money to hire a worker!")
    elif state == "hardware shop":
        if player.money >= amount and name:
            player.money -= amount
            if not hasattr(player, "machinery"):
                player.machinery = {}
            if name not in player.machinery:
                player.machinery[name] = 0
            player.machinery[name] += 1
            player.inventory.add_item(name)
            print(f"Bought {name}!")
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

def handle_card_click(item, card_rect,):
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

back_btn = Button(20, 20, 100, 40, "Back", back_action)
workers_btn = Button(350, 400, 120, 40, "Workers", workers_tab)
machines_btn = Button(350, 300, 120, 40, "Hardware", machines_tab)
upgrades_btn = Button(350, 200, 120, 40, "Upgrades", upgrades_tab)
shop_buttons = [back_btn, workers_btn, machines_btn, upgrades_btn]

worker_shop_buttons = [back_btn]
machines_shop_buttons = [back_btn]
upgrade_buttons = [back_btn]
shop_open_btn = Button(800 - 120, 100, 100, 50, "Shop", openShop)

# Example content
Hardware("Workbench", "Allows crafting", cost=200)
upgrade_player_speed = Upgrade("Move faster", "Player moves faster", cost=50, affect_player=True, effect_value=0.2)
for _ in range(5):
    Worker()
player = Player(0, 0, player_sprite)
player.money = 500

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "main":
            shop_open_btn.handle_event(event)

        elif state == "shop":
            for b in shop_buttons:
                b.handle_event(event)

        elif state == "worker shop":
            for b in worker_shop_buttons:
                b.handle_event(event)

        elif state == "hardware shop":
            for b in machines_shop_buttons:
                b.handle_event(event)

        elif state == "upgrades shop":
            for b in upgrade_buttons:
                b.handle_event(event)

        # Context menu click handling
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and context_menu_active:
            mx, my = event.pos
            clicked_on_button = any(b.rect.collidepoint(mx, my) for b in context_menu_buttons)
            if not clicked_on_button:
                close_context_menu()

    # UPDATE
    player.update()

    # DRAW
    screen.blit(background, (0, 0))

    if state == "main":
        drawGrid()
        draw_ui_bar()
        player.draw(screen)

        money_rect = pygame.Rect(800 - 140, 10, 130, 40)
        pygame.draw.rect(screen, (100, 100, 100), money_rect, 0, 10)
        money_text = font_small.render(f"Money: {player.money}", True, (0, 0, 0))
        screen.blit(money_text, (800 - 135, 15))
        shop_open_btn.draw(screen)

    elif state == "shop":
        text = font_big.render("Shop", True, white)
        screen.blit(text, text.get_rect(center=(400, 100)))
        for b in shop_buttons:
            b.draw(screen)

    elif state == "worker shop":
        text = font_big.render("Human Resources", True, white)
        screen.blit(text, text.get_rect(center=(400, 100)))
        drawItems(Worker.registry, cols=3, start_x=50, start_y=200,font=font_small,color=white)
        for b in worker_shop_buttons:
            b.draw(screen)

    elif state == "hardware shop":
        text = font_big.render("Hardware Shop", True, white)
        screen.blit(text, text.get_rect(center=(400, 100)))
        drawItems(Hardware.registry, cols=3, start_x=50, start_y=200,font=font_small,color=white)
        for b in machines_shop_buttons:
            b.draw(screen)

    elif state == "upgrades shop":
        text = font_big.render("Upgrades", True, white)
        screen.blit(text, text.get_rect(center=(400, 100)))
        drawItems(Upgrade.registry, cols=3, start_x=50, start_y=200,font=font_small,color=white)
        for b in upgrade_buttons:
            b.draw(screen)

    if context_menu_active:
        draw_context_menu()

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
