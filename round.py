from game_logic_test import result
import time

from game_logic import computer_move, determine_winner
from score import Score

def play_round(player_choice,score):
    if player_choice not in ["Rock", "Paper", "Scissors"]:
        return None, None, "Invalid"
    

    computer_choice = computer_move()

    result = determine_winner( player_choice, computer_choice)

    score.update(result)

    return computer_choice, result, "Valid"