
#% Creating a deck
def create_deck():
    deck = ()
    ranks = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
    suits = ("♠", "♥", "♦", "♣")
    for suit in suits:
        for rank in ranks:
            card = (rank, suit)
            deck += (card, )
    return deck


#% randomly select card and deal
import random
def deal_card(deck):
    i = random.choice(range(len(deck)))
    card = deck[i]
    deck = deck[:i] + deck[i+1:]
    return card, deck


#% Hands and calculating blackjack values
def hand_value(hand) -> int:
    result = 0
    aces = 0
    face_cards = ("J", "Q", "K")
    for card in hand:
        value = card[0]
        if value in face_cards:
            result += 10
        elif value == "A":
            result += 11
            aces += 1
        else:
            result += int(value)

    while result > 21 and aces > 0:
        result -= 10
        aces -= 1
    
    return result

#% Deal card to hand, remove one card from deck
def deal_to_hand(hand, deck):
    card, deck = deal_card(deck)
    hand += (card, )
    return hand, deck

#% Are the first two cards in hand blackjack?
def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21 

#% Determines Game outcome
def determine_result(player_value, dealer_value):
    if dealer_value > 21:
        return ("win", "dealer_bust")
    elif player_value > dealer_value:
        return ("win", "higher_hand")
    elif player_value < dealer_value:
        return ("loss", "lower_hand")
    else:
        return ("draw", "equal_hand")

