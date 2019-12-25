class GameStats:
    #Track statistics for Alien Invasion

    def __init__(self, ai_game):
        self.settings = ai_game.settings
        self.reset_stats()
        #Start alien invasion in active state
        self.game_active = False

    def reset_stats(self):
        #Initialize statistics that can change during the game
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
        self.high_score = 0


