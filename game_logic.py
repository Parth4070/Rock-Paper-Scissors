import random

CHOICES = ["Rock", "Paper", "Scissors"]

def computer_move():
    return random.choice(CHOICES)

def determine_winner(player, computer):

    if player == computer:
        return "Draw"
    
    if (
        (player == "Rock" and computer == "Scissors") or
        (player == "Paper" and computer == "Rock") or
        (player == "Scissors" and computer == "Paper")
    ):
        return "Player"
    
    return "Computer"