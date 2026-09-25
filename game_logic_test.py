from game_logic import computer_move, determine_winner


print("Testing computer choice:")

for _ in range(10):
    print(computer_move())


print("\nTesting winner logic:")

test_cases = [
    ("Rock", "Scissors"),
    ("Paper", "Rock"),
    ("Scissors", "Paper"),
    ("Rock", "Rock"),
    ("Rock", "Paper"),
    ("Paper", "Scissors"),
    ("Scissors", "Rock"),
]


for player, computer in test_cases:

    result = determine_winner(player, computer)

    print(
        f"Player: {player:8} | "
        f"Computer: {computer:8} | "
        f"Result: {result}"
    )