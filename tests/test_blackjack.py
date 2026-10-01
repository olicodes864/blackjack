from blackjack import * 

def test_is_blackjack():
    ten_value_cards = ("10", "J", "Q", "K")
    for card in ten_value_cards:
        hand = (("A", "Spades"), (card, "Hearts"))
    
        result = is_blackjack(hand)

        assert result == True
def test_blackjack_with_ace():
    hand = (("A", "Spades"), ("9", "Hearts"))
    result = is_blackjack(hand)
    assert result == False
def test_blackjack_with_three_cards():
    hand = (("7", "Spades"), ("7", "Hearts"), ("7", "Clubs"))
    result = is_blackjack(hand)
    assert result == False
def test_hand_value():
    test_hands = (
    ((("10", "Spades"), ("7", "Hearts")), 17),

    ((("A", "Spades"), ("A", "Hearts")), 12),

    ((("A", "Spades"), ("A", "Hearts"), ("9", "Clubs")), 21),

    ((("A", "Spades"), ("A", "Hearts"), ("A", "Clubs"), ("A", "Diamonds")), 14),

    ((("K", "Spades"), ("Q", "Hearts"), ("A", "Clubs")), 21)
)
    for test in test_hands:
        result = hand_value(test[0])
        assert result == test[1]

def test_determine_result():
    test_results = (
    ((18, 22), ("win", "dealer_bust")),
    ((20, 18), ("win", "higher_hand")),
    ((17, 20), ("loss", "lower_hand")),
    ((19, 19), ("draw", "equal_hand"))
)
    for value, expected in test_results:
        player_value, dealer_value = value
        result = determine_result(player_value, dealer_value)
        assert result == expected 

if __name__ == "__main__":
    test_is_blackjack()
    test_blackjack_with_ace()
    test_blackjack_with_three_cards()
    test_hand_value()
    test_determine_result()
    print("All blackjack test passed!")