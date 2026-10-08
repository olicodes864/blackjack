
#& Imports
import tkinter as tk
from time import monotonic
from blackjack import *
from betting import payout
from card_ui import *

#% Game State
deck = create_deck()
player_hand = ()
dealer_hand = ()
dealer_timer = None
message_timer = None
chip_animation_timer = None
bankroll = 1000
current_bet = 0
selected_bet = 0
last_bet_chip = None  # The most recently accepted chip determines the pot's colour.
betting_active = True

#% GUI operations
def clear_message():
    global message_timer
    game_canvas.itemconfig(message_text, text="")
    message_timer = None

def show_message(text, time):
    global message_timer
    game_canvas.itemconfig(message_text, text=text.upper())
    message_timer = window.after(time, clear_message)

def reset_display():
    game_canvas.itemconfig(dealer_total_text, text="Total: ?")
    game_canvas.itemconfig(player_total_text, text="Total: ?")

def display_result(outcome, reason):
    global bankroll

    bankroll = payout(bankroll, current_bet, outcome)
    game_canvas.itemconfig(
        bankroll_text,
        text=f"Bankroll: ${bankroll}"
    )
        
    if reason == "dealer_bust":
        end_round("Dealer has gone BUST! You Win!")
    elif reason == "higher_hand":
        end_round("You Win!")
    elif reason == "lower_hand":
        end_round("You Lose!")
    else:
        end_round("Draw!")

def cancel_timer():
    global dealer_timer, message_timer
    if dealer_timer != None:
        window.after_cancel(dealer_timer)
        dealer_timer = None
    if message_timer != None:
        window.after_cancel(message_timer)
        message_timer = None

def close_game():
    cancel_timer()
    cancel_chip_animation()
    cancel_hand_animation(player_card_ui)
    cancel_hand_animation(dealer_card_ui)
    close_card_audio()
    window.destroy()

#% Game functions (Blackjack)
def disable_hit_stand():
    set_button_state(hit_button, "disabled")
    set_button_state(stand_button, "disabled")

def disable_bet():
    set_button_state(deal_button, "disabled")
    set_button_state(clear_bet_button, "disabled")

def end_round(text): #! finishes/freezes current round
    cancel_timer()

    game_canvas.itemconfig(message_text, text=text.upper())

    disable_bet()
    disable_hit_stand()

    update_total(dealer_hand, dealer_total_text, hand_value)
    reveal_card_image(dealer_hand[1], dealer_card_ui, 1)

    if bankroll == 0:
        window.after(3000, game_over)
    else:
        window.after(3000, betting_phase)

def game_over():
    disable_hit_stand()
    disable_bet()
    game_canvas.itemconfig(
    message_text,
    text="YOU RAN OUT OF MONEY!"
    )
    game_canvas.itemconfig(reset_button["tag"], state="normal")
    
def reset_game(): #! Resets the entire game
    global bankroll, player_hand, dealer_hand, selected_bet

    player_hand = ()
    dealer_hand = ()
    reset_display()
    
    bankroll = 1000
    selected_bet = 0

    game_canvas.itemconfig(reset_button["tag"], state="hidden")
    betting_phase()

def update_total(hand, total_text, value_fn):
    value = value_fn(hand)
    game_canvas.itemconfig(
        total_text,
        text=f"Total: {value}"
    )
    return value

#% Game functions (Betting)
def add_to_bet(amount):
    global selected_bet, last_bet_chip

    if betting_active and chip_animation_timer is None and selected_bet + amount <= bankroll:
        selected_bet += amount
        last_bet_chip = amount
        animate_bet_chip(amount)

def animate_bet_chip(amount, duration_ms=450):
    global chip_animation_timer
    source_id, image = chip_graphics[amount]
    start_x, start_y = game_canvas.coords(source_id)
    distance = ((860 - start_x) ** 2 + (220 - start_y) ** 2) ** 0.5
    # First contact: pot radius (76) plus half the travelling chip's width.
    rim_progress = max(0, 1 - (76 + image.width() / 2) / distance)
    moving_chip = game_canvas.create_image(
        start_x, start_y, image=image, tags=("moving_bet_chip",)
    )
    disable_bet()
    started = monotonic()

    def next_frame():
        global chip_animation_timer
        chip_animation_timer = None
        progress = min((monotonic() - started) * 1000 / duration_ms, 1)
        eased = progress ** 2  # Accelerate toward the pot instead of slowing down.
        travel = min(eased, rim_progress)
        game_canvas.coords(
            moving_chip,
            start_x + (860 - start_x) * travel,
            start_y + (220 - start_y) * travel,
        )
        if eased < rim_progress:
            chip_animation_timer = game_canvas.after(16, next_frame)
        else:
            game_canvas.delete("moving_bet_chip")
            update_bet_display()
            play_chip_clink()  # One contact sound when the chip reaches the pot's rim.
            if betting_active:
                set_button_state(deal_button, "normal")
                set_button_state(clear_bet_button, "normal")

    next_frame()

def cancel_chip_animation():
    global chip_animation_timer
    if chip_animation_timer is not None:
        game_canvas.after_cancel(chip_animation_timer)
        chip_animation_timer = None
    game_canvas.delete("moving_bet_chip")

def clear_selected_bet():
    global selected_bet, last_bet_chip

    if betting_active:
        cancel_chip_animation()
        selected_bet = 0
        last_bet_chip = None
        update_bet_display()
        set_button_state(deal_button, "normal")
        set_button_state(clear_bet_button, "normal")

def deal_clicked(): #! commits selected bet
    global bankroll, selected_bet, current_bet, betting_active

    if chip_animation_timer is not None:
        return

    if selected_bet == 0:
        show_message("Please select a bet", 2000)
        return

    bankroll -= selected_bet
    current_bet = selected_bet
    selected_bet = 0
    betting_active = False

    update_bet_display()
    new_game()

def update_bet_display():
    game_canvas.itemconfig(
        bankroll_text,
        text=f"Bankroll: ${bankroll}"
    )

    if current_bet > 0:
        bet_to_display = current_bet
    else:
        bet_to_display = selected_bet

    game_canvas.itemconfig(
        current_bet_text,
        text=f"${bet_to_display}"
    )
    display_bet_pot()

def display_bet_pot():
    game_canvas.delete("bet_pot_chips")
    text_color = "white"
    if last_bet_chip is not None:
        game_canvas.create_image(
            860, 220, image=pot_chip_images[last_bet_chip],
            tags=("bet_pot_chips",)
        )
        # Cover the chip's printed denomination with the running wager total.
        game_canvas.create_oval(
            814, 174, 906, 266, fill=pot_chip_colors[last_bet_chip], outline="",
            tags=("bet_pot_chips",)
        )
        text_color = "#171717" if last_bet_chip == 5 else "white"
    game_canvas.itemconfig(current_bet_text, fill=text_color)
    game_canvas.tag_raise("bet_pot_total")

def betting_phase(): #! prepares next round
    global current_bet, betting_active, last_bet_chip

    cancel_chip_animation()
    current_bet = 0
    last_bet_chip = None
    betting_active = True

    update_bet_display()
    disable_hit_stand()
    set_button_state(deal_button, "normal")
    set_button_state(clear_bet_button, "normal")

    game_canvas.itemconfig(
        message_text,
        text="PLACE A BET TO START"
    )
    
#% Main Game Functions
def hit():
    global deck, player_hand, dealer_hand

    disable_hit_stand()
    #! deal card & calculate value & update hand
    player_hand, deck = deal_to_hand(player_hand, deck)
    new_card = player_hand[-1]
    add_card_image(new_card, player_card_ui, len(player_hand)-1, arrange=False)

    def finish_hit():
        value = update_total(player_hand, player_total_text, hand_value)
        show_message("You chose to HIT", 2000)

        if value > 21:
            end_round("BUST!")
        elif value == 21:
            cancel_timer()
            stand()
        else:
            set_button_state(hit_button, "normal")
            set_button_state(stand_button, "normal")

    animate_card(
        player_card_ui, len(player_hand) - 1,
        660, player_card_ui["center_y"] - 40, finish_hit
    )

def stand():
    global deck, dealer_hand, player_hand, dealer_timer
    player_value = hand_value(player_hand)

    reveal_card_image(dealer_hand[1], dealer_card_ui, 1)
    dealer_value = update_total(dealer_hand, dealer_total_text, hand_value)

    def one_step_dealer():
        nonlocal dealer_value
        global deck, dealer_hand, dealer_timer
        dealer_timer = None

        if dealer_value < 17:
            show_message("Dealer takes another card", 1000)
            dealer_hand, deck = deal_to_hand(dealer_hand, deck)
            new_card = dealer_hand[-1]
            add_card_image(new_card, dealer_card_ui, len(dealer_hand)-1, arrange=False)

            def finish_dealer_draw():
                nonlocal dealer_value
                global dealer_timer
                dealer_value = update_total(dealer_hand, dealer_total_text, hand_value)
                if dealer_value >= 17:
                    outcome, reason = determine_result(player_value, dealer_value)
                    display_result(outcome, reason)
                else:
                    # Keep the existing two-second interval between dealer draws.
                    dealer_timer = window.after(1550, one_step_dealer)

            animate_card(
                dealer_card_ui, len(dealer_hand) - 1,
                660, dealer_card_ui["center_y"] - 40, finish_dealer_draw
            )

        else:
            outcome, reason = determine_result(player_value, dealer_value)
            display_result(outcome, reason)
            dealer_timer = None

    dealer_timer = window.after(1000, one_step_dealer)
    disable_hit_stand()

def new_game(test_hands=None):
    global deck, player_hand, dealer_hand, bankroll

    cancel_timer()   
    clear_hand(player_card_ui)
    clear_dealer_hand(dealer_card_ui)

    if test_hands is None:
        deck = create_deck()
        player_hand = ()
        dealer_hand = ()

        for i in range(4):
            if i%2 == 0:
                player_hand, deck = deal_to_hand(player_hand, deck)
            else:
                dealer_hand, deck = deal_to_hand(dealer_hand, deck)
    else:
        player_hand, dealer_hand = test_hands


    player_bj = is_blackjack(player_hand)
    dealer_bj = is_blackjack(dealer_hand)

    result = None 
    if player_bj and dealer_bj:
        result = "You both have BLACKJACK! Draw!" 
        outcome = "draw"  
    elif player_bj:
        result = "You have BLACKJACK! You Win!"
        outcome = "blackjack"
    elif dealer_bj:
        result = "Dealer has BLACKJACK! You Lose!"
        outcome = "loss"

    display_card_image(player_hand, player_card_ui)
    update_total(player_hand, player_total_text, hand_value)

    if result is not None:
        display_card_image(dealer_hand, dealer_card_ui)
       
        bankroll = payout(bankroll, current_bet, outcome)
        update_bet_display()
        end_round(result)
        
    else:
        display_card_image(dealer_hand, dealer_card_ui, hide_second=True)
        
        game_canvas.itemconfig(
            dealer_total_text,
            text="Total: ???"
        )

        set_button_state(hit_button, "normal")
        set_button_state(stand_button, "normal")
        game_canvas.itemconfig(
            message_text,
            text="YOUR TURN"
        )

#% Main Window
window = tk.Tk() 
initialize_card_audio()
initialize_chip_audio()
start_background_music()
#! creates the main application window and returns it, window stores it
window.protocol("WM_DELETE_WINDOW", close_game)
window.title("Blackjack")#! window title
window.geometry("1200x770")  # Trim spare space below the panels without clipping them.
window.configure(bg="#15181C")
#* .geometry expects a geometry string

#% Chips
CHIP_5_IMAGE = tk.PhotoImage(file="blackjack_ui_assets/ui/chip_5.png").subsample(2, 2)
CHIP_10_IMAGE = tk.PhotoImage(file="blackjack_ui_assets/ui/chip_10.png").subsample(2, 2)
CHIP_25_IMAGE = tk.PhotoImage(file="blackjack_ui_assets/ui/chip_25.png").subsample(2, 2)
CHIP_50_IMAGE = tk.PhotoImage(file="blackjack_ui_assets/ui/chip_50.png").subsample(2, 2)
CHIP_100_IMAGE = tk.PhotoImage(file="blackjack_ui_assets/ui/chip_100.png").subsample(2, 2)
pot_chip_images = {
    amount: tk.PhotoImage(file=f"blackjack_ui_assets/ui/chip_{amount}.png")
    for amount in (5, 10, 25, 50, 100)
}
pot_chip_colors = {5: "#ECE5D6", 10: "#013EA8", 25: "#017037", 50: "#A70913", 100: "#222222"}

#% Game Canvas
game_canvas = tk.Canvas(window,highlightthickness=0,bd=0,bg="#15181C")

game_canvas.pack(fill="both",expand=True)


def rounded_panel(x1, y1, x2, y2, radius, fill, outline="", width=1):
    # Repeated points keep the sides straight while smoothing each corner.
    points = (
        x1 + radius, y1, x2 - radius, y1, x2 - radius, y1,
        x2, y1, x2, y1 + radius, x2, y1 + radius,
        x2, y2 - radius, x2, y2 - radius, x2, y2,
        x2 - radius, y2, x2 - radius, y2,
        x1 + radius, y2, x1 + radius, y2, x1, y2,
        x1, y2 - radius, x1, y2 - radius,
        x1, y1 + radius, x1, y1 + radius, x1, y1,
        x1 + radius, y1
    )
    return game_canvas.create_polygon(
        points, smooth=True, splinesteps=24, fill=fill, outline=outline, width=width
    )

# Background surfaces are drawn first, beneath the cards and controls.
rounded_panel(24, 86, 744, 746, 28, "#080B0E")
rounded_panel(20, 80, 740, 740, 28, "#41463C")
rounded_panel(23, 84, 737, 737, 25, "#182D25")
rounded_panel(30, 90, 730, 730, 22, "#0D3D29", outline="#B79D62")
table_image_id = rounded_panel(34, 94, 726, 726, 18, "#145C3E")

rounded_panel(764, 86, 1184, 746, 22, "#080B0E")
rounded_panel(760, 80, 1180, 740, 22, "#444B53")
control_panel_id = rounded_panel(762, 82, 1178, 738, 20, "#252A30")
title_font = ("Times New Roman", 30, "bold")
from tkinter.font import Font
title_metrics = Font(root=window, font=title_font)
title_black_width = title_metrics.measure("BLACK")
title_jack_width = title_metrics.measure("JACK")
title_shadow = game_canvas.create_text(602, 43, text="BLACKJACK", fill="#080B0E", font=title_font)
title_black = game_canvas.create_text(600, 40, text="BLACK", anchor="w", fill="#C94747", font=title_font)
title_text = game_canvas.create_text(600, 40, text="JACK", anchor="w", fill="#E4C779", font=title_font)
title_left_suit = game_canvas.create_text(600, 40, text="♠", fill="#E4C779", font=("Times New Roman", 22))
title_left_diamond = game_canvas.create_text(600, 40, text="♦", fill="#C94747", font=("Times New Roman", 22))
title_right_suits = [
    game_canvas.create_text(600, 40, text=suit, fill=color, font=("Times New Roman", 22))
    for suit, color in (("♥", "#C94747"), ("♣", "#E4C779"))
]


def center_title(event):
    center_x = event.width / 2
    header_y = 40  # Halfway between the window top and the panels at y=80.
    left = center_x - (title_black_width + title_jack_width) / 2
    right = center_x + (title_black_width + title_jack_width) / 2
    game_canvas.coords(title_black, left, header_y)
    game_canvas.coords(title_text, left + title_black_width, header_y)
    game_canvas.coords(title_shadow, center_x + 2, header_y + 3)
    game_canvas.coords(title_left_suit, left - 24, header_y)
    game_canvas.coords(title_left_diamond, left - 54, header_y)
    for index, suit_id in enumerate(title_right_suits):
        game_canvas.coords(suit_id, right + 24 + index * 30, header_y)


game_canvas.bind("<Configure>", center_title)

#% Card UI State: table positions belong here; card spacing belongs in card_ui.py.
dealer_card_ui = create_hand_ui(game_canvas, center_x=400, center_y=240)
player_card_ui = create_hand_ui(game_canvas, center_x=400, center_y=480)

#& Dealer, Player & Betting 
#% Dealer Frame
dealer_text = game_canvas.create_text(400,120,text="DEALER",fill="white",font=("Times New Roman", 18))
dealer_total_text = game_canvas.create_text(400,145,text="Total: ?",fill="white")


#% Player Frame
player_text = game_canvas.create_text(400,365, text="PLAYER",fill="white",font=("Times New Roman", 18))
player_total_text = game_canvas.create_text(400,390,text="Total: ?",fill="white")

#% Betting Frame
bankroll_text = game_canvas.create_text(
    860, 700, text=f"Bankroll: ${bankroll}", fill="white",
    font=("Times New Roman", 16), width=190, justify="center"
)
# Static betting pot: one chip shows the last denomination, with the total on top.
game_canvas.create_oval(788, 148, 940, 300, fill="#0C0F12", outline="")
game_canvas.create_oval(784, 144, 936, 296, fill="#1B2026", outline="#B79D62", width=2)
game_canvas.create_text(860, 130, text="BET", fill="#D4C297", font=("Helvetica", 10, "bold"))
current_bet_text = game_canvas.create_text(
    860, 220, text=f"${current_bet}", fill="white",
    font=("Helvetica", 18, "bold"), width=70, justify="center",
    tags=("bet_pot_total",)
)

#% Canvas controls
# Draw controls on the Canvas so there is no native rectangular button behind them.
def rounded_button_image(width, height, color, radius, raised=False):
    image = tk.PhotoImage(width=width, height=height)
    if raised:
        red, green, blue = (value // 257 for value in window.winfo_rgb(color))
    # Unpainted corner pixels stay transparent, showing the actual table beneath.
    for y in range(height):
        distance = max(radius - y - 0.5, y + 0.5 - (height - radius), 0)
        inset = round(radius - (radius ** 2 - distance ** 2) ** 0.5)
        row_color = color
        if raised:
            highlight = max(0, 1 - y / 8) * 0.22
            shade = max(0, 1 - (height - 1 - y) / 5) * 0.25
            channels = [round((value + (255 - value) * highlight) * (1 - shade))
                        for value in (red, green, blue)]
            row_color = "#{:02x}{:02x}{:02x}".format(*channels)
        image.put(row_color, to=(inset, y, width - inset, y + 1))
    return image


def create_canvas_button(x, y, text, image, text_color, command, font):
    tag = f"button_{text.lower()}"
    radius = 12 if image.height() > 30 else 8
    shadow_image = rounded_button_image(image.width(), image.height(), "#0C0F12", radius)
    game_canvas.create_image(x + 4, y + 4, image=shadow_image, tags=(tag,))
    game_canvas.create_image(x, y, image=image, tags=(tag,))
    text_id = game_canvas.create_text(
        x, y, text=text, fill=text_color, font=font, tags=(tag,)
    )
    button = {
        "state": "normal", "tag": tag, "text_id": text_id, "text_color": text_color,
        "shadow_image": shadow_image  # Keep the shadow image alive.
    }

    def clicked(event):
        if button["state"] == "normal":
            command()

    game_canvas.tag_bind(tag, "<Button-1>", clicked)
    return button


def set_button_state(button, state):
    button["state"] = state
    color = button["text_color"] if state == "normal" else "#A0A0A0"
    game_canvas.itemconfig(button["text_id"], fill=color)

#% Buttons
HIT_BUTTON_IMAGE = rounded_button_image(156, 58, "#32CD32", 12, raised=True)
STAND_BUTTON_IMAGE = rounded_button_image(156, 58, "#EF4444", 12, raised=True)
BET_BUTTON_IMAGE = rounded_button_image(90, 30, "black", 8, raised=True)

#% Control positions on the Canvas
stand_button_y = 650 + (BET_BUTTON_IMAGE.height() - STAND_BUTTON_IMAGE.height()) / 2
hit_button = create_canvas_button(
    860, stand_button_y - 100, "HIT", HIT_BUTTON_IMAGE, "white", hit,
    ("Helvetica", 12, "bold")
)
stand_button = create_canvas_button(
    860, stand_button_y, "STAND", STAND_BUTTON_IMAGE, "black", stand,
    ("Helvetica", 12, "bold")
)
deal_button = create_canvas_button(
    1080, 650, "DEAL", BET_BUTTON_IMAGE, "white", deal_clicked, "TkDefaultFont"
)
clear_bet_button = create_canvas_button(
    1080, 600, "CLEAR", BET_BUTTON_IMAGE, "white", clear_selected_bet, "TkDefaultFont"
)
reset_button = create_canvas_button(
    1080, 700, "RESET", BET_BUTTON_IMAGE, "white", reset_game, "TkDefaultFont"
)
game_canvas.itemconfig(reset_button["tag"], state="hidden")

chip_5_id = game_canvas.create_image(1080, 180, image=CHIP_5_IMAGE)
game_canvas.tag_bind(chip_5_id, "<Button-1>", lambda event: add_to_bet(5))
chip_10_id = game_canvas.create_image(1080, 265,image=CHIP_10_IMAGE)
game_canvas.tag_bind(chip_10_id, "<Button-1>", lambda event: add_to_bet(10))
chip_25_id = game_canvas.create_image(1080, 350,image=CHIP_25_IMAGE)
game_canvas.tag_bind(chip_25_id, "<Button-1>", lambda event: add_to_bet(25))
chip_50_id = game_canvas.create_image(1080, 435,image=CHIP_50_IMAGE)
game_canvas.tag_bind(chip_50_id, "<Button-1>", lambda event: add_to_bet(50))
chip_100_id = game_canvas.create_image(1080, 520,image=CHIP_100_IMAGE)
game_canvas.tag_bind(chip_100_id, "<Button-1>", lambda event: add_to_bet(100))
chip_graphics = {
    5: (chip_5_id, CHIP_5_IMAGE),
    10: (chip_10_id, CHIP_10_IMAGE),
    25: (chip_25_id, CHIP_25_IMAGE),
    50: (chip_50_id, CHIP_50_IMAGE),
    100: (chip_100_id, CHIP_100_IMAGE),
}

#% Message
message_text = game_canvas.create_text(
    400, 650, text="", fill="white", font=("Times New Roman", 28, "bold"),
    width=600, justify="center"
)

#% Temporary GUI test helpers
# Run these manually while testing the GUI flow.
def test_player_blackjack():
    global bankroll, current_bet

    bankroll = 900
    current_bet = 100

    test_hands = (
        (("A", "♠"), ("K", "♥")),
        (("10", "♣"), ("7", "♦"))
    )

    new_game(test_hands)


def test_dealer_blackjack():
    global bankroll, current_bet

    bankroll = 900
    current_bet = 100

    test_hands = (
        (("9", "♠"), ("8", "♥")),
        (("A", "♣"), ("K", "♦"))
    )

    new_game(test_hands)


def test_both_blackjack():
    global bankroll, current_bet

    bankroll = 900
    current_bet = 100

    test_hands = (
        (("A", "♠"), ("K", "♥")),
        (("A", "♣"), ("K", "♦"))
    )

    new_game(test_hands)


def test_player_bust():
    global bankroll, current_bet

    bankroll = 900
    current_bet = 100

    test_hands = (
        (("10", "♠"), ("9", "♥"), ("6", "♣")),
        (("10", "♦"), ("7", "♣"))
    )

    new_game(test_hands)
    end_round("BUST!")


def test_dealer_bust():
    global bankroll, current_bet, deck

    bankroll = 900
    current_bet = 100

    test_hands = (
        (("10", "♠"), ("8", "♥")),
        (("10", "♦"), ("6", "♣"))
    )

    new_game(test_hands)
    deck = (("K", "♠"),)  # Dealer's only possible draw: 16 + 10 = 26.


def test_player_normal_win():
    global bankroll, current_bet

    bankroll = 900
    current_bet = 100

    test_hands = (
        (("10", "♠"), ("Q", "♥")),
        (("10", "♦"), ("7", "♣"))
    )

    new_game(test_hands)


def test_dealer_normal_win():
    global bankroll, current_bet

    bankroll = 900
    current_bet = 100

    test_hands = (
        (("10", "♠"), ("7", "♥")),
        (("10", "♦"), ("Q", "♣"))
    )

    new_game(test_hands)


def test_normal_draw():
    global bankroll, current_bet

    bankroll = 900
    current_bet = 100

    test_hands = (
        (("10", "♠"), ("9", "♥")),
        (("10", "♦"), ("9", "♣"))
    )

    new_game(test_hands)


def test_final_bankroll_loss():
    global bankroll, current_bet, selected_bet, betting_active

    # The player's last $100 has already been committed to this round.
    bankroll = 0
    current_bet = 100
    selected_bet = 0
    betting_active = False
    update_bet_display()
    disable_bet()

    test_hands = (
        (("10", "♠"), ("7", "♥")),
        (("10", "♦"), ("Q", "♣"))
    )

    new_game(test_hands)


def test_dealer_multiple_draws():
    global bankroll, current_bet, selected_bet, betting_active, deck

    bankroll = 900
    current_bet = 100
    selected_bet = 0
    betting_active = False
    update_bet_display()
    disable_bet()

    test_hands = (
        (("10", "♠"), ("8", "♥")),
        (("10", "♦"), ("2", "♣"))
    )

    new_game(test_hands)
    # Either draw order keeps the dealer below 17 after the first card.
    deck = (("2", "♠"), ("3", "♥"))


# Uncomment one of these while manually testing the GUI:
# test_player_blackjack()
# test_dealer_blackjack()
# test_both_blackjack()
#test_player_bust()
#test_dealer_bust()
# test_player_normal_win()
# test_dealer_normal_win()
# test_normal_draw()
# test_final_bankroll_loss()
#test_dealer_multiple_draws()
betting_phase()

#% Main loop
window.mainloop()#! keeps the program running, whilst waiting for user input etc.
