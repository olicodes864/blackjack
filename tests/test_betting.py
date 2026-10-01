from betting import *

def test_payout():
    test_payouts = (
    ("win", 1100),
    ("loss", 900),
    ("draw", 1000),
    ("blackjack", 1150)
)
   
    for outcome, expected in test_payouts:
        bet = 100
        bankroll = 900
        result = payout(bankroll, bet, outcome)
        assert result == expected

if __name__ == "__main__":
    test_payout()
    print("All betting tests passed!")