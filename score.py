class Score:
    def __init__(self):
        self.player_score = 0
        self.computer_score = 0
        self.draws = 0
    
    def update(self, result):
        if result == "Player":
            self.player_score += 1
        elif result == "Computer":
            self.computer_score += 1
        else:
            self.draws += 1
    
    def display(self):
        print(f"Player: {self.player_score} | Computer: {self.computer_score} | Draws: {self.draws}")