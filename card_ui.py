import tkinter as tk
from time import monotonic
from pathlib import Path
import pygame

card_slide_sound = None
chip_clink_sound = None


def initialize_card_audio():
    global card_slide_sound
    # Load once at startup; playback runs alongside Tkinter's animation frames.
    try:
        pygame.mixer.init()
        sound_path = Path(__file__).parent / "blackjack_ui_assets/sounds/card_slide.wav"
        card_slide_sound = pygame.mixer.Sound(str(sound_path))
        card_slide_sound.set_volume(0.2)
    except (pygame.error, OSError) as error:
        print(f"Card audio unavailable: {error}")


def initialize_chip_audio():
    global chip_clink_sound
    if not pygame.mixer.get_init():
        return
    try:
        sound_path = Path(__file__).parent / "blackjack_ui_assets/sounds/chip_clink.wav"
        chip_clink_sound = pygame.mixer.Sound(str(sound_path))
        chip_clink_sound.set_volume(0.6)
    except (pygame.error, OSError) as error:
        print(f"Chip audio unavailable: {error}")


def play_chip_clink():
    if chip_clink_sound is not None:
        chip_clink_sound.play()


def start_background_music():
    if not pygame.mixer.get_init():
        return
    try:
        music_path = Path(__file__).parent / "blackjack_ui_assets/sounds/deadly_roulette.mp3"
        pygame.mixer.music.load(str(music_path))
        pygame.mixer.music.set_volume(0.12)  # Keep music softer than card and chip effects.
        pygame.mixer.music.play(loops=-1, fade_ms=1500)
    except (pygame.error, OSError) as error:
        print(f"Background music unavailable: {error}")


def close_card_audio():
    pygame.mixer.music.stop()
    pygame.mixer.quit()

CARD_GAP = 10 #! leaves 10 pixels between edge of one card and next
MAX_ROW_WIDTH = 600 #! keep hands within the left play area, clear of the controls
SHADOW_OFFSET = 4
SHADOW_COLOR = "#0B3B2B"

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
        "animation_timer": None,
    }

def hand_positions(hand_ui):
    # Calculate destinations without moving the cards yet.
    cards = hand_ui["cards"]
    if not cards:
        return ()

    card_width = max(card["image"].width() for card in cards)
    spacing = card_width + CARD_GAP
    if len(cards) > 1:
        spacing = min(spacing, (MAX_ROW_WIDTH - card_width) / (len(cards) - 1))
        #% don't let the cards run off-screen logic
        #% cards will overlap slightly instead of leaving the screen
    start_x = hand_ui["center_x"] - spacing * (len(cards) - 1) / 2
    return tuple((start_x + position * spacing, hand_ui["center_y"])
                 for position in range(len(cards)))


def move_card_image(hand_ui, card, x, y):
    half_width = card["image"].width() / 2
    half_height = card["image"].height() / 2
    hand_ui["canvas"].coords(card["item_id"], x, y)
    hand_ui["canvas"].coords(
        card["shadow_id"],
        x - half_width + SHADOW_OFFSET, y - half_height + SHADOW_OFFSET,
        x + half_width + SHADOW_OFFSET, y + half_height + SHADOW_OFFSET,
    )


def layout_hand(hand_ui):
    for card, (x, y) in zip(hand_ui["cards"], hand_positions(hand_ui)):
        move_card_image(hand_ui, card, x, y)
        # Keep each shadow underneath its card, including when cards overlap.
        hand_ui["canvas"].tag_raise(card["shadow_id"])
        hand_ui["canvas"].tag_raise(card["item_id"])

def display_card_image(hand, hand_ui, hide_second=False):
    clear_hand(hand_ui)#% removes any previous graphical hand
    for position, card in enumerate(hand):
        add_card_image(card, hand_ui, position, face_down=hide_second and position == 1)

def add_card_image(card, hand_ui, position, face_down=False, arrange=True):
    if face_down:
        card_image = card_back_to_image()
    else:
        card_image = card_to_image(card)

    shadow_id = hand_ui["canvas"].create_rectangle(
        0, 0, 0, 0, fill=SHADOW_COLOR, outline=""
    )
    item_id = hand_ui["canvas"].create_image( #%puts the card onto the canvas
        hand_ui["center_x"],
        hand_ui["center_y"],
        image=card_image,
        anchor="center",
    )
    # Keep the PhotoImage alive and the item ID available for movement or deletion.
    hand_ui["cards"].insert(position, {
        "item_id": item_id, "shadow_id": shadow_id, "image": card_image
    })
    if arrange:
        layout_hand(hand_ui)

def animate_card(hand_ui, position, start_x, start_y, on_complete, duration_ms=450):
    if card_slide_sound is not None:
        card_slide_sound.play()
    canvas = hand_ui["canvas"]
    cards = hand_ui["cards"]
    starts = tuple((start_x, start_y) if index == position else canvas.coords(card["item_id"])
                   for index, card in enumerate(cards))
    destinations = hand_positions(hand_ui)
    for card in cards:
        canvas.tag_raise(card["shadow_id"])
        canvas.tag_raise(card["item_id"])
    started = monotonic()

    def next_frame():
        hand_ui["animation_timer"] = None
        progress = min((monotonic() - started) * 1000 / duration_ms, 1)
        eased = 1 - (1 - progress) ** 3  # Slow gently as the card lands.
        for card, (from_x, from_y), (to_x, to_y) in zip(cards, starts, destinations):
            x = from_x + (to_x - from_x) * eased
            y = from_y + (to_y - from_y) * eased
            move_card_image(hand_ui, card, x, y)
        if progress < 1:
            hand_ui["animation_timer"] = canvas.after(16, next_frame)
        else:
            on_complete()

    next_frame()


def cancel_hand_animation(hand_ui):
    if hand_ui["animation_timer"] is not None:
        hand_ui["canvas"].after_cancel(hand_ui["animation_timer"])
        hand_ui["animation_timer"] = None


def reveal_card_image(card, hand_ui, position):
    card_image = card_to_image(card)
    rendered_card = hand_ui["cards"][position]
    hand_ui["canvas"].itemconfig(rendered_card["item_id"], image=card_image)
    rendered_card["image"] = card_image

def clear_hand(hand_ui):
    cancel_hand_animation(hand_ui)
    for card in hand_ui["cards"]:
        hand_ui["canvas"].delete(card["shadow_id"])
        hand_ui["canvas"].delete(card["item_id"])
    hand_ui["cards"].clear()

def clear_dealer_hand(hand_ui):
    clear_hand(hand_ui)
