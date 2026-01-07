# We will use Jupyter to help run tiny segments
# of the game, as well as for our drafts.

# Draft:

# Predefined variables & functions
import random
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
        return drawncard
    return drawncard

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

        

        player_hand.append(drawncard)
    # if it's AO's turn:
    else:  
        AO_hand.append(random.choice(deck))
def Stay():
    if PlayerTurn == True:
        PlayerTurn = False 
    else:
        print("GAME OVER")
    

Error1 = "Error: User input does not match given choice. Ending game..."
print("Welcome user.\nHit (h) or stay (s)?")
gamechoice = input()
    if gamechoice == "h":
        Hit
    elif gamechoice == "s":
        Stay
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