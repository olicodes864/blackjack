import tkinter as tk

window = tk.Tk()

# Test setup
test_frame = tk.Frame(window)
test_frame.pack()

#% Image testing
#% Image Testing
def card_filepath(card):
    suits = ("♠", "S", "♥", "H", "♦", "D", "♣", "C")
    result = card[0]
    for i in range(0, 8, 2):
        if suits[i] == card[1]:
            result += suits[i+1]
    return f"blackjack_ui_assets/cards/{result}.png"

def card_to_image(card):
    return tk.PhotoImage(file=card_filepath(card))

def display_card_image(hand, frame):
    cards = ()
    for card in hand:
        cards += (card_to_image(card), )

    for i, card in enumerate(cards):
        card_label = tk.Label(
            frame, 
            image=card
        )
        card_label.grid(row=0, column=i, padx=10, pady=10)
    return cards

def add_card_image(card, frame, position):
    card_image = card_to_image(card)
    card_label = tk.Label(
        frame, 
        image=card_image
    )
    card_label.grid(row=0, column=position, padx=5, pady=5)
    return card_image
# Starting hand
displayed_cards = display_card_image(
    (("A", "♠"), ("10", "♥")),
    test_frame
)
def clear_hand(frame):
    widgets = frame.winfo_children()
    for widget in widgets:
        widget.destroy()
    
# Test 1
new_image = add_card_image(("Q", "♦"), test_frame, 2)

# Test 2
new_image_2 = add_card_image(("3", "♣"), test_frame, 3)

window.after(3000, lambda: clear_hand(test_frame))
#displayed_cards = display_card_image((("Q", "♥"), ("7", "♠"), ("A", "♦"), ("3", "♣")), window)
# → 2 images


#card_image = card_to_image(("Q", "♥"))

# card_label = tk.Label(
#     window, 
#     image=card_image
# )


#card_label.pack()

window.mainloop()
