# textblackjack.py
import copy
import random
import math
import pygame  # only for image-preload; CLI itself doesn’t use Pygame

# --- constants & card data --------------------------------------------------
MIN_BET = 5
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
COUNT_VALUES = dict(zip(RANKS, [1] * 5 + [0] * 3 + [-1] * 5))
CARD_VALUES = dict(zip(RANKS, [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]))
CARDS = [s + r for r in RANKS for s in ("C", "D", "H", "S")]

# preload images so the deck structure matches the GUI build; unused here
card_images = {c: pygame.image.load(f"images/{c}.png").convert() for c in CARDS}

deck = copy.deepcopy(CARDS * 2)
NUM_CARDS = len(deck)

cut = curr = running_count = 0
bet_amounts: list[int] = []
chip_stacks: list[int] = []
hand: list = []
flat_hands: list[str] = []
is_split: list[bool] = []
is_double_down: list[bool] = []


# ---------------------------------------------------------------------------#
#                                 helpers                                    #
# ---------------------------------------------------------------------------#
def shuffle() -> None:
    global cut, curr
    cut = random.randrange(NUM_CARDS // 3, NUM_CARDS * 2 // 3)
    curr = 0
    random.shuffle(deck)
    print("Deck shuffled!")


def calc_total(cards_on_table) -> int:
    total = aces = 0
    for card in cards_on_table:
        total += CARD_VALUES[card[1]]
        if card[1] == "A":
            aces += 1
    while aces and total > 21:
        aces -= 1
        total -= 10
    return total


def draw_card(target_hand, n: int = 1):
    global curr
    for _ in range(n):
        target_hand.append(deck[curr])
        curr += 1
    return target_hand


def is_blackjack(cards_on_table) -> bool:
    return len(cards_on_table) == 2 and calc_total(cards_on_table) == 21


def print_hand(cards_on_table, name: str) -> None:
    if isinstance(cards_on_table[0], list):
        for idx, sub in enumerate(cards_on_table):
            print_hand(sub, f"{name} Split {idx + 1}")
    else:
        print(f"{name}'s Hand: ", end="")
        for i, card in enumerate(cards_on_table):
            sep = "\n" if i == len(cards_on_table) - 1 else " | "
            print(card[1], end=sep)


def print_dealer() -> None:
    print(f"Dealer's Hand: {hand[0][0][1]} | ?")


def play_hand(cards_on_table, player_idx: int, label: str):
    global bet_amounts, is_split, is_double_down

    opts = ["hit", "stand"]
    if len(cards_on_table) == 2 and cards_on_table[0][1] == cards_on_table[1][1]:
        opts.append("split")
    if calc_total(cards_on_table) in (10, 11) and len(cards_on_table) == 2:
        opts.append("double down")

    print_dealer()
    print_hand(cards_on_table, label)
    print("Options: " + " | ".join(opts))

    choice = input("What would you like to do? >> ").lower()
    while choice not in opts:
        choice = input("What would you like to do? >> ").lower()

    if choice == "hit":
        cards_on_table = draw_card(cards_on_table)
        if calc_total(cards_on_table) > 21:
            print_hand(cards_on_table, label)
            print("Bust!")
        else:
            cards_on_table = play_hand(cards_on_table, player_idx, label)

    elif choice == "split":
        is_split[player_idx - 1] = True
        cards_on_table = [[cards_on_table[0]], [cards_on_table[1]]]
        cards_on_table[0] = draw_card(cards_on_table[0])
        cards_on_table[1] = draw_card(cards_on_table[1])
        cards_on_table[0] = play_hand(cards_on_table[0], player_idx, f"{label} Split 1")
        cards_on_table[1] = play_hand(cards_on_table[1], player_idx, f"{label} Split 2")

    elif choice == "double down":
        is_double_down[player_idx - 1] = True
        bet_amounts[player_idx - 1] *= 2
        cards_on_table = draw_card(cards_on_table)
        print_hand(cards_on_table, label)

    # stand or after action
    print("")
    return cards_on_table


def compare_hand(player_cards, dealer_cards, idx: int) -> None:
    global chip_stacks
    player_total, dealer_total = calc_total(player_cards), calc_total(dealer_cards)

    print(f"Player {idx}: ", end="")
    mult = 0

    if is_blackjack(player_cards) and not is_split[idx - 1]:
        if is_blackjack(dealer_cards):
            print("Blackjack Push. Keep Bet.")
        else:
            mult = 1.5
            print("Blackjack, Win 1.5x Bet.")
    elif player_total > 21:
        mult = -1
        print("Player Bust, Lose Bet.")
    else:
        if dealer_total > 21:
            mult = 1
            print("Dealer Bust, Win Bet.")
        else:
            if player_total > dealer_total:
                mult = 1
                print("Player Win, Win Bet.")
            elif player_total < dealer_total:
                mult = -1
                print("Dealer Win, Lose Bet.")
            else:
                print("Push. Keep Bet.")

    chip_stacks[idx - 1] += bet_amounts[idx - 1] * mult


def flatten_hands(stack) -> None:
    for item in stack:
        flatten_hands(item) if isinstance(item, list) else flat_hands.append(item)


# ---------------------------------------------------------------------------#
#                                main driver                                 #
# ---------------------------------------------------------------------------#
def blackjack() -> None:
    global hand, bet_amounts, chip_stacks, is_split, is_double_down
    global curr, cut, running_count

    try:
        num_players = int(input("Number of Players: "))
    except ValueError:
        num_players = 1

    bet_amounts = [MIN_BET] * num_players
    chip_stacks = [100] * num_players
    is_split = [False] * num_players
    is_double_down = [False] * num_players

    shuffle()

    while True:
        # auto-rebuy
        for p in range(num_players):
            if chip_stacks[p] < MIN_BET:
                chip_stacks[p] += 100
                print(f"Player {p + 1} rebought for $100!")

        if curr >= cut:
            shuffle()

        for p in range(num_players):
            try:
                wager = int(
                    input(
                        f"Enter your bet, Player {p + 1} (chips {chip_stacks[p]}, default {bet_amounts[p]}): "
                    )
                )
            except ValueError:
                wager = bet_amounts[p]
            if wager > chip_stacks[p] or wager < MIN_BET:
                wager = MIN_BET
            bet_amounts[p] = wager

        # initial deal -------------------------------------------------------
        hand = [[] for _ in range(num_players + 1)]  # 0 = dealer
        for i in range(num_players + 1):
            hand[i] = draw_card(hand[i], 2)

        is_split = [False] * num_players
        is_double_down = [False] * num_players

        print_dealer()
        for p in range(1, num_players + 1):
            print_hand(hand[p], f"Player {p}")
        print("")

        if calc_total(hand[0]) == 21:
            print("Dealer Blackjack!")
        else:
            for p in range(num_players):
                if calc_total(hand[p + 1]) == 21:
                    print("Player Blackjack!")
                else:
                    hand[p + 1] = play_hand(hand[p + 1], p + 1, f"Player {p + 1}")
                    print_hand(hand[p + 1], f"Player {p + 1}")
                    print("")
            print_hand(hand[0], "Dealer")
            while calc_total(hand[0]) < 17:
                hand[0] = draw_card(hand[0])
                print("Dealer Hit")
                print_hand(hand[0], "Dealer")

            if calc_total(hand[0]) > 21:
                print("Dealer Bust!")
            else:
                print("Dealer Stand")
            print("")

        # settle bets -------------------------------------------------------
        for p in range(1, num_players + 1):
            target = hand[p]
            if isinstance(target[0], list):
                for sub in target:
                    compare_hand(sub, hand[0], p)
            else:
                compare_hand(target, hand[0], p)

        # count & continue ---------------------------------------------------
        print("\nCollecting Hands ... ")
        print_hand(hand[0], "Dealer")
        for p in range(1, num_players + 1):
            print_hand(hand[p], f"Player {p}")

        flat_hands.clear()
        flatten_hands(hand)
        running_count += sum(COUNT_VALUES[c[1]] for c in flat_hands)

        if input("Reveal the count? (y/n) >> ").lower().startswith("y"):
            print(running_count)
        if input("Would you like to quit? (y/n) >> ").lower().startswith("y"):
            break


blackjack()