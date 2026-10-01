# Asset-building tool only: requires Pillow and the listed macOS fonts.
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops

SOURCE = Path(__file__).resolve().parent
OUTPUT = SOURCE.parent / 'cards'
OUTPUT.mkdir(exist_ok=True)
RANK_FONT = '/System/Library/Fonts/Supplemental/Georgia Bold.ttf'
SUIT_FONT = '/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf'
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
SUITS = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}


def paper_template(filename):
    image = Image.open(SOURCE / filename).convert('RGBA')
    red, green, blue, alpha = image.split()
    paper = ImageChops.darker(ImageChops.darker(red, green), blue).point(lambda v: 255 if v > 180 else 0)
    paper = ImageChops.multiply(paper, alpha.point(lambda v: 255 if v > 230 else 0))
    left, top, right, bottom = paper.getbbox()
    # Keep the thin physical edge and shadow, with only a small transparent margin.
    bounds = (max(0, left - 5), max(0, top - 5), min(image.width, right + 20), min(image.height, bottom + 20))
    return image.crop(bounds).resize((960, 1344), Image.Resampling.LANCZOS)


def ink_glyph(text, font_path, size, color, maximum=None):
    font = ImageFont.truetype(font_path, size)
    bounds = font.getbbox(text)
    mask = Image.new('L', (bounds[2] - bounds[0], bounds[3] - bounds[1]))
    ImageDraw.Draw(mask).text((-bounds[0], -bounds[1]), text, font=font, fill=255)
    if maximum:
        mask.thumbnail(maximum, Image.Resampling.LANCZOS)
    glyph = Image.new('RGBA', mask.size, color)
    glyph.putalpha(mask)
    return glyph


blank = paper_template('paper_template_source.png')
back = paper_template('card_back_source.png')
blank.save(SOURCE / 'paper_template.png')

for code, symbol in SUITS.items():
    color = '#171717' if code in ('S', 'C') else '#B51F30'
    for rank in RANKS:
        image = blank.copy()
        corner = Image.new('RGBA', (158, 340))
        rank_ink = ink_glyph(rank, RANK_FONT, 225, color, (156, 170))
        if rank == '10':
            # Condense the two digits horizontally instead of shrinking their height.
            rank_ink = ink_glyph(rank, RANK_FONT, 225, color)
            rank_ink = rank_ink.resize((156, min(170, rank_ink.height)), Image.Resampling.LANCZOS)
        corner.alpha_composite(rank_ink, ((158 - rank_ink.width) // 2, 0))
        suit_ink = ink_glyph(symbol, SUIT_FONT, 210, color, (138, 145))
        corner.alpha_composite(suit_ink, ((158 - suit_ink.width) // 2, 192))
        image.alpha_composite(corner, (60, 72))
        image.alpha_composite(corner.transpose(Image.Transpose.ROTATE_180), (960 - 60 - 158 - 14, 1344 - 72 - 340 - 14))
        centre = ink_glyph(symbol, SUIT_FONT, 480, color, (300, 370))
        image.alpha_composite(centre, ((960 - centre.width) // 2 - 7, (1344 - centre.height) // 2 - 7))
        image.resize((240, 336), Image.Resampling.LANCZOS).save(OUTPUT / f'{rank}{code}.png')

back.resize((240, 336), Image.Resampling.LANCZOS).save(OUTPUT / 'BACK.png')

# Review all cards at their actual in-game size, arranged by suit and rank.
sheet = Image.new('RGB', (13 * 136, 5 * 200), '#145C3E')
draw = ImageDraw.Draw(sheet)
for row, code in enumerate(SUITS):
    for column, rank in enumerate(RANKS):
        card = Image.open(OUTPUT / f'{rank}{code}.png').resize((120, 168), Image.Resampling.LANCZOS)
        sheet.paste(card, (column * 136 + 8, row * 200 + 8), card)
        draw.text((column * 136 + 12, row * 200 + 180), f'{rank}{code}', fill='white')
card = Image.open(OUTPUT / 'BACK.png').resize((120, 168), Image.Resampling.LANCZOS)
sheet.paste(card, (8, 808), card)
sheet.save(SOURCE / 'deck_review.png')
print('Created all 52 faces, matching back, paper template, and review sheet:', OUTPUT)
