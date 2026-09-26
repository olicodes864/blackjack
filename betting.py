
#% end of round payout
def payout(bankroll, bet, outcome):
    if outcome == "win":
        bankroll += 2 * bet
    elif outcome == "draw":
        bankroll += bet
    elif outcome == "blackjack":
        bankroll += bet * 2.5
    return bankroll