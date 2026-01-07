"""
Simple Blackjack (CLI)

Rules implemented:
- Single player vs dealer
- Standard 52-card deck, shuffled each round
- Player starts with chips, places a bet each hand
- Deal: two cards to player (both visible), two to dealer (one visible)
- Player actions: hit, stand, double down (double bet, take one card, then stand)
- Dealer reveals hole card and hits until reaching 17 or higher.
  Dealer stands on soft 17.
- Blackjack (natural 21 with first two cards) pays 3:2
- Push returns the bet.
- No splitting, no insurance, no surrender
- Aces count as 1 or 11 (best value <= 21)
"""

import random
import sys
try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog
except Exception:
    tk = None

RANKS = "23456789TJQKA"
SUITS = "♠♥♦♣"
RANK_TO_VALUE = {r: i+2 for i, r in enumerate(RANKS)}  # 2->2 ... T->10 J->11 Q->12 K->13 A->14 (we'll treat A specially)

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank}{self.suit}"

    def __repr__(self):
        return str(self)

class Deck:
    def __init__(self):
        self.cards = [Card(r, s) for r in RANKS for s in SUITS]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, n=1):
        return [self.cards.pop() for _ in range(n)]

def hand_value(cards):
    """
    Return (best_value, is_soft)
    best_value is the highest value <= 21 if possible, otherwise the minimal bust value.
    is_soft is True if the hand counts an Ace as 11.
    """
    values = []
    total = 0
    aces = 0
    for c in cards:
        if c.rank == 'A':
            aces += 1
            total += 11
        elif c.rank in 'TJQK':
            total += 10
        else:
            total += int(c.rank)
    # reduce Aces from 11 to 1 as needed
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    is_soft = any(c.rank == 'A' for c in cards) and total + 0 <= 21 and any((c.rank == 'A') for c in cards) and total != sum_card_values_as_ace_one(cards)
    return total, (any(c.rank == 'A' for c in cards) and total + 0 <= 21 and any(c.rank == 'A' for c in cards) and total - 10 >= 1 and total - 10 < total)

def sum_card_values_as_ace_one(cards):
    s = 0
    for c in cards:
        if c.rank == 'A':
            s += 1
        elif c.rank in 'TJQK':
            s += 10
        else:
            s += int(c.rank)
    return s

def is_blackjack(cards):
    """True if exactly two cards and value is 21"""
    if len(cards) != 2:
        return False
    v, _ = hand_value(cards)
    return v == 21

def print_hand(label, cards, hide_second=False):
    if hide_second and len(cards) >= 2:
        print(f"{label}: {cards[0]} [hidden]")
    else:
        print(f"{label}: {' '.join(str(c) for c in cards)} (value: {hand_value(cards)[0]})")

def prompt_bet(chips):
    while True:
        try:
            bet = input(f"You have {chips} chips. Enter bet (minimum 1): ").strip()
            if bet.lower() in ('q', 'quit'):
                return None
            bet = int(bet)
            if 1 <= bet <= chips:
                return bet
        except Exception:
            pass
        print("Invalid bet. Enter an integer between 1 and your chip count, or 'q' to quit.")

def prompt_action(can_double, to_call=None):
    opts = ["(h)it", "(s)tand"]
    if can_double:
        opts.append("(d)ouble")
    prompt = " / ".join(opts) + ": "
    while True:
        choice = input(prompt).strip().lower()
        if choice in ('h', 'hit'):
            return "hit"
        if choice in ('s', 'stand'):
            return "stand"
        if can_double and choice in ('d', 'double'):
            return "double"
        print("Invalid choice. Enter h, s, or d (if available).")

def dealer_play(deck, dealer_cards):
    # Dealer reveals and hits until 17 or higher.
    # Dealer stands on soft 17.
    while True:
        v, _ = hand_value(dealer_cards)
        # Check for soft 17: if value==17 and there is an Ace counted as 11, that's soft 17
        # We'll compute minimal value with Aces as 1 to detect softness
        min_val = sum_card_values_as_ace_one(dealer_cards)
        is_soft = any(c.rank == 'A' for c in dealer_cards) and (v - min_val) >= 10 and v == 17
        if v < 17:
            dealer_cards += deck.deal(1)
        elif v == 17 and is_soft:
            # stands on soft 17 (common rule). If you'd prefer hit on soft 17, change to hit here.
            break
        else:
            break
    return dealer_cards

def compare_outcome(player_cards, dealer_cards):
    pv, _ = hand_value(player_cards)
    dv, _ = hand_value(dealer_cards)
    if pv > 21:
        return "player_bust"
    if dv > 21:
        return "dealer_bust"
    if pv > dv:
        return "player_win"
    if dv > pv:
        return "dealer_win"
    return "push"

def play_round(chips):
    deck = Deck()
    player_cards = deck.deal(2)
    dealer_cards = deck.deal(2)
    bet = prompt_bet(chips)
    if bet is None:
        return None, chips  # user chose to quit
    original_bet = bet

    print()
    print_hand("Dealer", dealer_cards, hide_second=True)
    print_hand("Your hand", player_cards)

    # Check for naturals
    player_natural = is_blackjack(player_cards)
    dealer_natural = is_blackjack(dealer_cards)

    if player_natural or dealer_natural:
        # Reveal dealer
        print_hand("Dealer (revealed)", dealer_cards)
        if player_natural and not dealer_natural:
            payout = int(1.5 * bet)  # win 3:2
            chips += bet + payout
            print(f"Blackjack! You win {payout} (3:2).")
        elif dealer_natural and not player_natural:
            chips -= bet
            print("Dealer has blackjack. You lose.")
        else:
            print("Both have blackjack. Push.")
        return True, chips

    # Player actions
    doubled = False
    while True:
        can_double = (chips - bet) >= bet  # enough chips to double
        action = prompt_action(can_double)
        if action == "hit":
            player_cards += deck.deal(1)
            print_hand("Your hand", player_cards)
            if hand_value(player_cards)[0] > 21:
                print("You busted!")
                chips -= bet
                return True, chips
            continue
        elif action == "double":
            # double down: double bet, take one card, then stand
            chips -= bet  # remove additional bet immediately
            bet *= 2
            doubled = True
            player_cards += deck.deal(1)
            print_hand("Your hand (after double)", player_cards)
            if hand_value(player_cards)[0] > 21:
                print("You busted after doubling!")
                chips -= (0)  # bet already deducted
                # on bust we already deducted the bet; ensure final accounting:
                # we've subtracted the extra bet; net effect below will subtract original bet when returned false
                # To keep it simple: treat as losing bet already accounted
                return True, chips
            break
        elif action == "stand":
            break

    # Dealer plays
    print()
    print_hand("Dealer (revealed)", dealer_cards)
    dealer_cards = dealer_play(deck, dealer_cards)
    print_hand("Dealer (final)", dealer_cards)

    # Determine outcome
    outcome = compare_outcome(player_cards, dealer_cards)
    if outcome == "player_bust":
        print("You busted. You lose your bet.")
        chips -= bet
    elif outcome == "dealer_bust":
        print("Dealer busted. You win!")
        chips += bet
    elif outcome == "player_win":
        print("You win!")
        chips += bet
    elif outcome == "dealer_win":
        print("Dealer wins. You lose your bet.")
        chips -= bet
    else:
        print("Push. Your bet is returned.")
        # no chip change

    return True, chips

def main():
    print("Simple Blackjack (CLI)")
    print("Type 'q' when prompted for a bet to quit.\n")
    chips = 100
    while True:
        if chips <= 0:
            print("You're out of chips. Game over.")
            break
        cont, chips = play_round(chips)
        if cont is None:
            print("Goodbye!")
            break
        print(f"\nChips: {chips}")
        cmd = input("Press Enter to play next hand, or 'q' to quit: ").strip().lower()
        if cmd == 'q':
            print("Exiting game.")
            break

class BlackjackGUI:
    def __init__(self):
        if tk is None:
            raise RuntimeError("Tkinter is not available in this environment")
        self.root = tk.Tk()
        self.root.title("Blackjack")
        self.chips = 100
        self.deck = None
        self.player = []
        self.dealer = []
        self.bet = 0

        top = tk.Frame(self.root)
        top.pack(padx=10, pady=8)

        self.info_label = tk.Label(top, text=f"Chips: {self.chips}")
        self.info_label.pack()

        self.dealer_lbl = tk.Label(self.root, text="Dealer:")
        self.dealer_lbl.pack()
        self.dealer_text = tk.Label(self.root, text="", font=("Consolas", 12))
        self.dealer_text.pack()

        self.player_lbl = tk.Label(self.root, text="Player:")
        self.player_lbl.pack()
        self.player_text = tk.Label(self.root, text="", font=("Consolas", 12))
        self.player_text.pack()

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=8)
        self.hit_btn = tk.Button(btn_frame, text="Hit", command=self.hit, state=tk.DISABLED, width=10)
        self.hit_btn.grid(row=0, column=0, padx=4)
        self.stand_btn = tk.Button(btn_frame, text="Stand", command=self.stand, state=tk.DISABLED, width=10)
        self.stand_btn.grid(row=0, column=1, padx=4)
        self.double_btn = tk.Button(btn_frame, text="Double", command=self.double, state=tk.DISABLED, width=10)
        self.double_btn.grid(row=0, column=2, padx=4)
        self.new_btn = tk.Button(btn_frame, text="New Round", command=self.new_round, width=10)
        self.new_btn.grid(row=0, column=3, padx=4)

        self.status_lbl = tk.Label(self.root, text="")
        self.status_lbl.pack(pady=6)

    def run(self):
        self.new_round()
        self.root.mainloop()

    def update_display(self, hide_dealer=True):
        if hide_dealer and len(self.dealer) >= 2:
            dealer_display = f"{self.dealer[0]} [hidden]"
        else:
            dealer_display = ' '.join(str(c) for c in self.dealer)
        player_display = ' '.join(str(c) for c in self.player)
        self.dealer_text.config(text=f"{dealer_display}  (value: {hand_value(self.dealer)[0] if not hide_dealer else '??'})")
        self.player_text.config(text=f"{player_display}  (value: {hand_value(self.player)[0]})")
        self.info_label.config(text=f"Chips: {self.chips}   Bet: {self.bet}")

    def new_round(self):
        self.deck = Deck()
        self.player = self.deck.deal(2)
        self.dealer = self.deck.deal(2)
        # ask for bet
        bet = simpledialog.askinteger("Bet", f"You have {self.chips} chips. Enter bet (min 1):", minvalue=1, maxvalue=self.chips, parent=self.root)
        if bet is None:
            return
        self.bet = bet
        # enable action buttons
        self.hit_btn.config(state=tk.NORMAL)
        self.stand_btn.config(state=tk.NORMAL)
        if self.chips - self.bet >= self.bet:
            self.double_btn.config(state=tk.NORMAL)
        else:
            self.double_btn.config(state=tk.DISABLED)
        self.status_lbl.config(text="")
        self.update_display(hide_dealer=True)

        # check naturals
        player_natural = is_blackjack(self.player)
        dealer_natural = is_blackjack(self.dealer)
        if player_natural or dealer_natural:
            self.hit_btn.config(state=tk.DISABLED)
            self.stand_btn.config(state=tk.DISABLED)
            self.double_btn.config(state=tk.DISABLED)
            self.update_display(hide_dealer=False)
            if player_natural and not dealer_natural:
                payout = int(1.5 * self.bet)
                self.chips += self.bet + payout
                messagebox.showinfo("Result", f"Blackjack! You win {payout} (3:2)")
            elif dealer_natural and not player_natural:
                self.chips -= self.bet
                messagebox.showinfo("Result", "Dealer has blackjack. You lose.")
            else:
                messagebox.showinfo("Result", "Both have blackjack. Push.")
            self.info_label.config(text=f"Chips: {self.chips}")

    def hit(self):
        self.player += self.deck.deal(1)
        self.update_display(hide_dealer=True)
        if hand_value(self.player)[0] > 21:
            self.chips -= self.bet
            self.end_round("You busted. You lose your bet.")

    def stand(self):
        self.hit_btn.config(state=tk.DISABLED)
        self.stand_btn.config(state=tk.DISABLED)
        self.double_btn.config(state=tk.DISABLED)
        self.update_display(hide_dealer=False)
        self.dealer = dealer_play(self.deck, self.dealer)
        self.update_display(hide_dealer=False)
        outcome = compare_outcome(self.player, self.dealer)
        if outcome == "player_bust":
            self.chips -= self.bet
            self.end_round("You busted. You lose your bet.")
        elif outcome == "dealer_bust":
            self.chips += self.bet
            self.end_round("Dealer busted. You win!")
        elif outcome == "player_win":
            self.chips += self.bet
            self.end_round("You win!")
        elif outcome == "dealer_win":
            self.chips -= self.bet
            self.end_round("Dealer wins. You lose your bet.")
        else:
            self.end_round("Push. Your bet is returned.")

    def double(self):
        if self.chips >= self.bet:
            self.chips -= self.bet
            self.bet *= 2
            self.player += self.deck.deal(1)
            self.update_display(hide_dealer=True)
            if hand_value(self.player)[0] > 21:
                self.chips -= 0
                self.end_round("You busted after doubling!")
            else:
                self.stand()

    def end_round(self, msg):
        self.status_lbl.config(text=msg)
        messagebox.showinfo("Round Result", msg)
        self.hit_btn.config(state=tk.DISABLED)
        self.stand_btn.config(state=tk.DISABLED)
        self.double_btn.config(state=tk.DISABLED)
        self.info_label.config(text=f"Chips: {self.chips}")


if __name__ == "__main__":
    try:
        if "--gui" in sys.argv:
            if tk is None:
                print("Tkinter not available; falling back to CLI.")
                main()
            else:
                BlackjackGUI().run()
        else:
            main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)

        mport random
drawncard = 0
PlayerTurn = True
player_hand = []
AO_hand = []
deck = ["A",2,3,4,5,6,7,8,9,10,"J","Q","K"]
Error1 = "Error: User input does not match given choice. Ending game..."

def Draw():
    drawncard = random.choice(deck)
    if drawncard == "A":
        drawncard = input("Please choose the Ace's value (1 or 11):")
        if drawncard != 1 or drawncard != 11:
            print(Error1)
    if drawncard == "J" or drawncard == "Q" or drawncard == "K":
        drawncard = 10
        
return Draw()

def Hit():
    Draw
    if PlayerTurn == True:
        player_hand.append(drawncard)
        print("Your hand: " + player_hand)
        if sum(player_hand) > 21:
            print("BUST! You lose.")
    else:
        AO_hand.append(drawncard)
        print("Your hand: " + player_hand + ". \nAO's hand: " + AO_hand + ".")
        if sum(player_hand) > 21:
            print("BUST! AO loses. You Win!")
return Hit()
        



Error1 = "Error: User input does not match given choice. Ending game..."
print("Welcome user.\nHit (h) or stay (s)?")
gamechoice = input()
    if gamechoice == "h":
        Hit()
    elif gamechoice == "s":
        Stay()
    else:
        print(Error1)
Welcome user.
Hit or stay?
# test Draw function

import random
drawncard = 0
PlayerTurn = True
player_hand = []
AO_hand = []
deck = ["A",2,3,4,5,6,7,8,9,10,"J","Q","K"]
Error1 = "Error: User input does not match given choice. Ending game..."

def Draw():
    drawncard = random.choice(deck)
    print("Drawn Card: " + drawncard)
    if drawncard == "A":
        drawncard = input("Please choose the Ace's value (1 or 11):")
        if drawncard != 1 or drawncard != 11:
            print(Error1)
    if drawncard == "J" or drawncard == "Q" or drawncard == "K":
        drawncard = 10
        return drawncard
    return drawncard


Draw
Draw