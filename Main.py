
#& Imports
import tkinter as tk
from blackjack import *
from betting import payout
from card_ui import *

#% Game State
deck = create_deck()
player_hand = ()
dealer_hand = ()
dealer_timer = None
message_timer = None
bankroll = 1000
current_bet = 0
selected_bet = 0
betting_active = True

#% GUI operations
def clear_message():
    global message_timer
    game_canvas.itemconfig(message_text, text="")
    message_timer = None

def show_message(text, time):
    global message_timer
    game_canvas.itemconfig(message_text, text=text)
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
    window.destroy()
#% Game functions (Blackjack)
def disable_hit_stand():
    hit_button.config(state="disabled")
    stand_button.config(state="disabled")

def disable_bet():
    deal_button.config(state="disabled")
    clear_bet_button.config(state="disabled")

def end_round(text): #! finishes/freezes current round
    cancel_timer()

    game_canvas.itemconfig(message_text, text=text)

    disable_bet()
    disable_hit_stand()

    update_total(dealer_hand, dealer_total_text, hand_value)

    if bankroll == 0:
        window.after(3000, game_over)
    else:
        window.after(3000, betting_phase)

def game_over():
    disable_hit_stand()
    disable_bet()
    game_canvas.itemconfig(
    message_text,
    text="You ran out of money!"
    )
    game_canvas.itemconfig(reset_window_id, state="normal")
    
def reset_game(): #! Resets the entire game
    global bankroll, player_hand, dealer_hand, selected_bet

    player_hand = ()
    dealer_hand = ()
    reset_display()
    
    bankroll = 1000
    selected_bet = 0

    game_canvas.itemconfig(reset_window_id, state="hidden")
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
    global selected_bet

    if betting_active and selected_bet + amount <= bankroll:
        selected_bet += amount
        update_bet_display()

def clear_selected_bet():
    global selected_bet

    if betting_active:
        selected_bet = 0
        update_bet_display()

def deal_clicked(): #! commits selected bet
    global bankroll, selected_bet, current_bet, betting_active

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
        text=f"Current Bet: ${bet_to_display}"
    )

def betting_phase(): #! prepares next round
    global current_bet, betting_active

    current_bet = 0
    betting_active = True

    update_bet_display()
    disable_hit_stand()
    deal_button.config(state="normal")
    clear_bet_button.config(state="normal")

    game_canvas.itemconfig(
        message_text,
        text="Place a bet to start"
    )
    


#% Main Game Functions
def hit():
    global deck, player_hand

    #! deal card & calculate value & update hand
    player_hand, deck = deal_to_hand(player_hand, deck)
    new_card = player_hand[-1]
    add_card_image(new_card, player_card_ui, len(player_hand)-1)
    value = update_total(player_hand, player_total_text, hand_value)

    show_message("You chose to HIT", 2000)

    if value > 21:
        end_round("BUST!")
    elif value == 21:
        cancel_timer()
        stand()

def stand():
    global deck, dealer_hand, player_hand, dealer_timer
    player_value = hand_value(player_hand)

    reveal_card_image(dealer_hand[1], dealer_card_ui, 1)
    dealer_value = update_total(dealer_hand, dealer_total_text, hand_value)

    def one_step_dealer():
        nonlocal dealer_value
        global deck, dealer_hand, dealer_timer
        

        if dealer_value < 17:
            show_message("Dealer takes another card", 1000)
            dealer_hand, deck = deal_to_hand(dealer_hand, deck)
            dealer_value = update_total(dealer_hand, dealer_total_text, hand_value)
            new_card = dealer_hand[-1]
            add_card_image(new_card, dealer_card_ui, len(dealer_hand)-1)
            
            if dealer_value >= 17:
                outcome, reason = determine_result(player_value, dealer_value)
                display_result(outcome, reason)
                dealer_timer = None
            else:
                dealer_timer = window.after(2000, one_step_dealer)

        else:
            outcome, reason = determine_result(player_value, dealer_value)
            display_result(outcome, reason)
            dealer_timer = None

    dealer_timer = window.after(1000, one_step_dealer)
    disable_hit_stand()

def new_game():
    global deck, player_hand, dealer_hand, bankroll

    cancel_timer()   
    clear_hand(player_card_ui)
    clear_dealer_hand(dealer_card_ui)

    deck = create_deck()
    player_hand = ()
    dealer_hand = ()

    for i in range(4):
        if i%2 == 0:
            player_hand, deck = deal_to_hand(player_hand, deck)
        else:
            dealer_hand, deck = deal_to_hand(dealer_hand, deck)
    


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

        hit_button.config(state="normal")
        stand_button.config(state="normal")
        game_canvas.itemconfig(
            message_text,
            text="Your Turn"
        )


#% Main Window
window = tk.Tk() 
#! creates the main application window and returns it, window stores it
window.protocol("WM_DELETE_WINDOW", close_game)
window.title("Blackjack")#! window title
window.geometry("1200x800")#! window size, 800 pixels wide, 600 pixels tall
#* .geometry expects a geometry string


#% Background
TABLE_IMAGE = tk.PhotoImage(file="blackjack_ui_assets/ui/table_felt_1200x800.png")

#% Chips
CHIP_5_IMAGE = tk.PhotoImage(file="blackjack_ui_assets/ui/chip_5.png").subsample(2, 2)
CHIP_10_IMAGE = tk.PhotoImage(file="blackjack_ui_assets/ui/chip_10.png").subsample(2, 2)
CHIP_25_IMAGE = tk.PhotoImage(file="blackjack_ui_assets/ui/chip_25.png").subsample(2, 2)
CHIP_50_IMAGE = tk.PhotoImage(file="blackjack_ui_assets/ui/chip_50.png").subsample(2, 2)
CHIP_100_IMAGE = tk.PhotoImage(file="blackjack_ui_assets/ui/chip_100.png").subsample(2, 2)
#% Game Canvas
game_canvas = tk.Canvas(window,highlightthickness=0,bd=0)

game_canvas.pack(fill="both",expand=True)
table_image_id = game_canvas.create_image(0,0,image=TABLE_IMAGE,anchor="nw")
title_text = game_canvas.create_text(600,20,text="BLACKJACK",fill="white",font=("Times New Roman", 30))

#% Card UI State: table positions belong here; card spacing belongs in card_ui.py.
dealer_card_ui = create_hand_ui(game_canvas, center_x=600, center_y=240)
player_card_ui = create_hand_ui(game_canvas, center_x=600, center_y=460)

#% Dealer Frame
dealer_text = game_canvas.create_text(600,120,text="DEALER",fill="white",font=("Times New Roman", 18))
dealer_total_text = game_canvas.create_text(600,145,text="Total: ?",fill="white")


#% Player Frame
player_text = game_canvas.create_text(600,345, text="PLAYER",fill="white",font=("Times New Roman", 18))
player_total_text = game_canvas.create_text(600,370,text="Total: ?",fill="white")

#% Betting Frame
bankroll_text = game_canvas.create_text(30,20,text=f"Bankroll: ${bankroll}",fill="white",font=("Times New Roman", 18),anchor="w")
current_bet_text = game_canvas.create_text(1150,20,text=f"Current Bet: ${current_bet}",fill="white",font=("Times New Roman", 18),anchor="e")


#% Canvas controls
hit_button = tk.Button(game_canvas, text="HIT", command=hit, width=14, height=3)
stand_button = tk.Button(game_canvas, text="STAND", command=stand, width=14, height=3)
reset_button = tk.Button(game_canvas, text="RESET", command=reset_game, width=3, height=1)
deal_button = tk.Button(game_canvas, text="DEAL", command=deal_clicked)
clear_bet_button = tk.Button(game_canvas, text="CLEAR", command=clear_selected_bet)

#% Control positions on the Canvas
hit_window_id = game_canvas.create_window(475, 675, window=hit_button, anchor="center")
stand_window_id = game_canvas.create_window(725, 675, window=stand_button, anchor="center")
reset_window_id = game_canvas.create_window(600, 675, window=reset_button, anchor="center", state="hidden")
deal_window_id = game_canvas.create_window(600, 575, window=deal_button, anchor="center")
clear_bet_window_id = game_canvas.create_window(900, 735, window=clear_bet_button, anchor="center")

chip_5_id = game_canvas.create_image(440, 735, image=CHIP_5_IMAGE)
game_canvas.tag_bind(chip_5_id, "<Button-1>", lambda event: add_to_bet(5))
chip_10_id = game_canvas.create_image(520, 735,image=CHIP_10_IMAGE)
game_canvas.tag_bind(chip_10_id, "<Button-1>", lambda event: add_to_bet(10))
chip_25_id = game_canvas.create_image(600, 735,image=CHIP_25_IMAGE)
game_canvas.tag_bind(chip_25_id, "<Button-1>", lambda event: add_to_bet(25))
chip_50_id = game_canvas.create_image(680, 735,image=CHIP_50_IMAGE)
game_canvas.tag_bind(chip_50_id, "<Button-1>", lambda event: add_to_bet(50))
chip_100_id = game_canvas.create_image(760, 735,image=CHIP_100_IMAGE)
game_canvas.tag_bind(chip_100_id, "<Button-1>", lambda event: add_to_bet(100))

#% Message
message_text = game_canvas.create_text(600,625,text="",fill="white",font=("Times New Roman", 20))



betting_phase()

#% Main loop
window.mainloop()#! keeps the program running, whilst waiting for user input etc.
