BLACKJACK UI ASSET PACK

Generated specifically for the Tkinter Blackjack learning project.

STRUCTURE
assets/
  cards/
    AS.png ... KC.png  -> all 52 face cards
    BACK.png           -> dealer hidden-card asset
  ui/
    table_felt.png     -> 1600x1000 table background
    chip_5.png
    chip_10.png
    chip_25.png
    chip_50.png
    chip_100.png

CARD NAMING
Rank + suit code:
  S = Spades
  H = Hearts
  D = Diamonds
  C = Clubs

Examples:
  ("Q", "♥") -> QH.png
  ("10", "♠") -> 10S.png
  ("A", "♦") -> AD.png

The filenames are intentionally systematic so the Python program can construct
the correct path from card data instead of using 52 if-statements.

SUGGESTED LEARNING ORDER
1. Load one PNG into Tkinter.
2. Map one card tuple to its filename.
3. Render an entire hand from card tuples.
4. Replace the dealer's ??? with BACK.png.
5. Add table_felt.png.
6. Add chip buttons and connect them to betting state.
7. Only then add optional sounds/animations.

All included graphics were generated for this project, so no external asset
licensing is required for these files.
