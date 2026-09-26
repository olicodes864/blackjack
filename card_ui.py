import tkinter as tk

CARD_GAP = 10 #! leaves 10 pixels between edge of one card and next
MAX_ROW_WIDTH = 1000 #! don't let an entire hand be wider than 1000 pixels

def card_filepath(card):
    suits = ("♠", "S", "♥", "H", "♦", "D", "♣", "C")
    result = card[0]
    for i in range(0, 8, 2):
        if suits[i] == card[1]:
            result += suits[i+1]
    return f"blackjack_ui_assets/cards/{result}.png"

def card_to_image(card):
    return tk.PhotoImage(file=card_filepath(card)).subsample(2, 2)

def card_back_to_image():
    return tk.PhotoImage(file="blackjack_ui_assets/cards/BACK.png").subsample(2, 2)

def create_hand_ui(canvas, center_x, center_y): #! dictionary -> one graphical hand
    return {
        "canvas": canvas,
        "center_x": center_x,
        "center_y": center_y,
        "cards": [],
    }

def layout_hand(hand_ui):#! take however many cards currently exist and centre them around the hand's center_x
    cards = hand_ui["cards"]
    if not cards:
        return

    card_width = max(card["image"].width() for card in cards)
    spacing = card_width + CARD_GAP
    if len(cards) > 1:
        spacing = min(spacing, (MAX_ROW_WIDTH - card_width) / (len(cards) - 1))
        #% don't let the cards run off-screen logic
        #% cards will overlap slightly instead of leaving the screen
    start_x = hand_ui["center_x"] - spacing * (len(cards) - 1) / 2
    #% figures out where the first card must go
    for position, card in enumerate(cards):
        #% move every card to its proper position
        hand_ui["canvas"].coords(
            card["item_id"],
            start_x + position * spacing,
            hand_ui["center_y"],
        )

def display_card_image(hand, hand_ui, hide_second=False):
    clear_hand(hand_ui)#% removes any previous graphical hand
    for position, card in enumerate(hand):
        add_card_image(card, hand_ui, position, face_down=hide_second and position == 1)

def add_card_image(card, hand_ui, position, face_down=False):
    if face_down:
        card_image = card_back_to_image()
    else:
        card_image = card_to_image(card)

    item_id = hand_ui["canvas"].create_image( #%puts the card onto the canvas
        hand_ui["center_x"],
        hand_ui["center_y"],
        image=card_image,
        anchor="center",
    )
    # Keep the PhotoImage alive and the item ID available for movement or deletion.
    hand_ui["cards"].insert(position, {"item_id": item_id, "image": card_image})
    layout_hand(hand_ui)

def reveal_card_image(card, hand_ui, position):
    card_image = card_to_image(card)
    rendered_card = hand_ui["cards"][position]
    hand_ui["canvas"].itemconfig(rendered_card["item_id"], image=card_image)
    rendered_card["image"] = card_image

def clear_hand(hand_ui):
    for card in hand_ui["cards"]:
        hand_ui["canvas"].delete(card["item_id"])
    hand_ui["cards"].clear()

def clear_dealer_hand(hand_ui):
    clear_hand(hand_ui)
