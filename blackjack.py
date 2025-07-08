# blackjack.py
import copy
import random
import pygame

pygame.init()

# --- screen / timing --------------------------------------------------------
WIDTH, HEIGHT, FPS = 450, 600, 60
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Blackjack")
clock = pygame.time.Clock()

# --- fonts ------------------------------------------------------------------
font = pygame.font.Font("freesansbold.ttf", 25)
font_underline = pygame.font.Font("freesansbold.ttf", 25)
font_underline.set_underline(True)

# --- card data --------------------------------------------------------------
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
COUNT_VALUES = dict(zip(ranks, [1] * 5 + [0] * 3 + [-1] * 5))
CARD_VALUES = dict(zip(ranks, [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]))

cards = [s + r for r in ranks for s in ("C", "D", "H", "S")]
card_images = {c: pygame.image.load(f"images/{c}.png").convert() for c in cards}
face_down = pygame.image.load("images/card_face_down.png")

# --- game constants ---------------------------------------------------------
MIN_BET, REBUY_AMOUNT = 5, 100
NUM_PLAYERS = 2
TOP_OFFSET = [50, 16, 12]  # visual tweak by player-count (don’t touch)

# --- state containers -------------------------------------------------------
deck = copy.deepcopy(cards * 2)
cut, curr, running_count = 0, 0, 0
flat_hands: list[str] = []
options: list[str] = []

chips = [100 for _ in range(NUM_PLAYERS)]
bet = MIN_BET
new_bet = MIN_BET
is_double_down = [False] * NUM_PLAYERS
hand_to_player = [i + 1 for i in range(NUM_PLAYERS)]
hand = [[] for _ in range(NUM_PLAYERS + 1)]  # 0 = dealer
messages = [""] * (NUM_PLAYERS + 1)

# --- round flags ------------------------------------------------------------
running = True
active = False
editing_bet = False
first_deal = True
first_finished = False
turn = 1


# ---------------------------------------------------------------------------#
#                               helper functions                             #
# ---------------------------------------------------------------------------#
def shuffle() -> None:
    """Reshuffle and cut the shoe."""
    global cut, deck, curr, running_count, messages
    cut = random.randrange(len(deck) // 2, len(deck) * 2 // 3)
    curr = running_count = 0
    random.shuffle(deck)
    messages[0] = "Deck Shuffled!"


def calc_total(cards_on_table: list[str]) -> int:
    total = aces = 0
    for card in cards_on_table:
        total += CARD_VALUES[card[1]]
        if card[1] == "A":
            aces += 1
    while aces and total > 21:
        aces -= 1
        total -= 10
    return total


def draw_card(target_hand: list[str], n: int = 1) -> list[str]:
    global curr
    for _ in range(n):
        target_hand.append(deck[curr])
        curr += 1
    return target_hand


def is_blackjack(cards_on_table: list[str]) -> bool:
    return len(cards_on_table) == 2 and calc_total(cards_on_table) == 21


def compare_hand(player, dealer, idx) -> str:
    global bet, chips, is_double_down, hand_to_player
    player_total, dealer_total = calc_total(player), calc_total(dealer)
    mult, outcome = 0, ""

    if is_blackjack(player):
        if is_blackjack(dealer):
            outcome = "BJ Push."
        else:
            mult, outcome = 1.5, "Player BJ!"
    elif is_blackjack(dealer) or player_total > 21:
        mult, outcome = -1, "Player Lose"
    else:
        if dealer_total > 21 or player_total > dealer_total:
            mult, outcome = 1, "Player Win"
        elif player_total < dealer_total:
            mult, outcome = -1, "Player Lose"
        else:
            outcome = "Push"

    if is_double_down[idx - 1]:
        mult *= 2
    chips[hand_to_player[idx - 1] - 1] += bet * mult
    return outcome


def flatten_hands(h) -> None:
    global flat_hands
    for item in h:
        flatten_hands(item) if isinstance(item, list) else flat_hands.append(item)


def reset_options(active_hand: list[str]) -> None:
    global options
    options = ["hit", "stand"]
    if len(active_hand) == 2 and active_hand[0][1] == active_hand[1][1]:
        options.append("split")
    if calc_total(active_hand) in (10, 11) and len(active_hand) == 2:
        options.append("double down")


# ---------------------------------------------------------------------------#
#                               drawing routine                              #
# ---------------------------------------------------------------------------#
def draw_game():
    global hand, active, options, messages, turn, chips, hand_to_player, editing_bet
    buttons = []

    # ----- button set -------------------------------------------------------
    if active and 0 < turn <= len(hand_to_player):
        reset_options(hand[turn])
    elif editing_bet:
        options = ["confirm", "1", "5", "25", "clear"]
    else:
        options = ["deal", "reveal count", "change bet"]

    for i, label in enumerate(options):
        length = (WIDTH - 20 - 6 * len(options)) / len(options)
        btn_top = HEIGHT - HEIGHT / 5
        rect = pygame.draw.rect(
            screen, "white", [13 + i * (length + 6), btn_top - 15, length, HEIGHT / 5], 0, 5
        )
        pygame.draw.rect(
            screen, "black", [13 + i * (length + 6), btn_top - 15, length, HEIGHT / 5], 3, 5
        )

        txt_parts = ["con", "firm"] if label == "confirm" else label.split()
        for j, part in enumerate(txt_parts):
            y_off = (btn_top / 30 * len(txt_parts)) * (j - 0.5) if len(txt_parts) > 1 else 0
            text = font.render(part, True, "black")
            text_rect = text.get_rect(
                center=(13 + i * (length + 6) + length / 2, btn_top + btn_top / 10 + y_off)
            )
            screen.blit(text, text_rect)

        if editing_bet and 1 <= i <= 3:
            chip = pygame.image.load(f"images/chip{label}.png")
            screen.blit(pygame.transform.scale(chip, (60, 60)), (13 + i * (length + 6) + 10, btn_top + 15))
        buttons.append(rect)

    # ----- card dimensions --------------------------------------------------
    lane_h = 440 / (len(hand_to_player) + 1)
    card_h = min(lane_h - 30, 100)
    card_w = card_h / face_down.get_height() * face_down.get_width()

    # ----- dealer -----------------------------------------------------------
    screen.blit(font.render("Dealer's Hand", True, "black"), (10, 10))
    screen.blit(font.render(messages[0], True, "black"), (200, 10))
    for i, card in enumerate(hand[0]):
        img = face_down if active and i == 1 else card_images[card]
        img = pygame.transform.scale(img, (card_w, card_h))
        screen.blit(img, (i * card_w + 10, 25 + TOP_OFFSET[NUM_PLAYERS - 1]))

    # ----- players ----------------------------------------------------------
    for idx in range(len(hand_to_player)):
        p_num = hand_to_player[idx]
        title_font = font_underline if active and idx + 1 == turn else font
        y_base = 15 + lane_h * (idx + 1)

        screen.blit(title_font.render(f"Player {p_num}'s Hand", True, "black"), (10, y_base))
        screen.blit(
            font.render(f"${chips[p_num - 1]} {messages[idx + 1]}", True, "black"), (215, y_base)
        )

        for c_idx, card in enumerate(hand[idx + 1]):
            img = pygame.transform.scale(card_images[card], (card_w, card_h))
            screen.blit(img, (c_idx * card_w + 10, lane_h * (idx + 1) + 30 + TOP_OFFSET[len(hand_to_player) - 1]))

    return buttons


# ---------------------------------------------------------------------------#
#                                round reset                                 #
# ---------------------------------------------------------------------------#
def reset():
    global hand, curr, bet, active, first_deal, messages, turn
    global new_bet, is_double_down, hand_to_player, first_finished

    turn = 1
    active = True
    first_deal = False
    bet = new_bet
    messages = [""] * (NUM_PLAYERS + 1)

    # auto-rebuy
    for idx in range(NUM_PLAYERS):
        if chips[idx] < MIN_BET:
            chips[idx] += REBUY_AMOUNT
            messages[idx + 1] = f"Rebought for ${REBUY_AMOUNT}"

    is_double_down = [False] * NUM_PLAYERS
    hand_to_player = [i + 1 for i in range(NUM_PLAYERS)]
    first_finished = False

    if curr >= cut:
        shuffle()

    if bet < MIN_BET or any(ch < bet for ch in chips):
        bet = MIN_BET

    hand[:] = [[] for _ in range(NUM_PLAYERS + 1)]
    for i in range(NUM_PLAYERS + 1):
        hand[i] = draw_card(hand[i], 2)

    reset_options(hand[1])

    if calc_total(hand[0]) == 21:
        active = False


# ---------------------------------------------------------------------------#
#                                main loop                                   #
# ---------------------------------------------------------------------------#
while running:
    clock.tick(FPS)
    screen.fill("white")
    buttons = draw_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONUP:
            if not active and not editing_bet:
                if buttons[0].collidepoint(event.pos):
                    reset()
                elif buttons[1].collidepoint(event.pos):
                    messages[0] = f"Count: {running_count}"
                elif buttons[2].collidepoint(event.pos):
                    editing_bet = True
                    new_bet = bet

            elif editing_bet:
                if buttons[0].collidepoint(event.pos):
                    editing_bet = False
                elif buttons[1].collidepoint(event.pos):
                    new_bet += 1
                elif buttons[2].collidepoint(event.pos):
                    new_bet += 5
                elif buttons[3].collidepoint(event.pos):
                    new_bet += 25
                elif buttons[4].collidepoint(event.pos):
                    new_bet = MIN_BET

            else:  # active hand
                messages[0] = ""
                if buttons[0].collidepoint(event.pos):
                    hand[turn] = draw_card(hand[turn])
                    if calc_total(hand[turn]) > 21:
                        messages[turn] = "bust"
                        turn += 1

                elif buttons[1].collidepoint(event.pos):
                    messages[turn] = "stand"
                    turn += 1

                elif (
                    len(buttons) > 2
                    and buttons[2].collidepoint(event.pos)
                    and options[2] == "split"
                ):
                    hand_to_player.insert(turn, hand_to_player[turn - 1])
                    hand.insert(turn, [hand[turn].pop(0)])
                    is_double_down.insert(turn, False)
                    messages.insert(turn, "")
                    hand[turn] = draw_card(hand[turn])
                    hand[turn + 1] = draw_card(hand[turn + 1])
                    messages[turn] = messages[turn + 1] = "split"

                elif (
                    (len(buttons) > 2 and buttons[2].collidepoint(event.pos) and options[2] == "double down")
                    or (len(buttons) > 3 and buttons[3].collidepoint(event.pos) and options[3] == "double down")
                ):
                    is_double_down[turn - 1] = True
                    hand[turn] = draw_card(hand[turn])
                    messages[turn] = "double down"
                    turn += 1

    if turn > len(hand_to_player):
        active = False

    if active and is_blackjack(hand[turn]):
        messages[turn] = "blackjack!"
        turn += 1

    if editing_bet:
        messages[0] = f"New Bet: ${new_bet}"

    if not active and not first_deal and not first_finished:
        while calc_total(hand[0]) < 17:
            hand[0] = draw_card(hand[0])
        for i in range(1, len(hand_to_player) + 1):
            messages[i] = compare_hand(hand[i], hand[0], i)

        flat_hands.clear()
        flatten_hands(hand)
        running_count += sum(COUNT_VALUES[c[1]] for c in flat_hands)
        first_finished = True

    pygame.display.flip()

pygame.quit()