import sys
from time import sleep

import pygame

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
        #Class to manage game behavior
    
    def __init__(self):
        #initialize pygame
        pygame.init()
        self.settings = Settings()
        
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        #Create gme instance to store game statistics and create a scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self.create_fleet()

        #Make the Play button
        self.play_button = Button(self, "Play")
        
        #Set the background color
        self.bg_color = (230, 230, 230)
    
    def run_game(self):
        #validate and start game
        while True:
            self.check_events()

            if self.stats.game_active:
                self.ship.update()
                self.update_bullets()
                self.update_aliens()

            self.update_screen()

    def check_events(self):
        #Watch for keyboard and mouse
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self.check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.check_play_button(mouse_pos)

    def check_play_button(self, mouse_pos):
        #Start a new game when the player clicks Play
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            #Reset the game settings
            self.settings.initialize_dynamic_settings()

            #Rest the game statistics
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            #Hide mouse cursor
            pygame.mouse.set_visible(False)

            #Remove any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            #Create a new fleet and center the ship
            self.create_fleet()
            self.ship.center_ship()

    def check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            #Move ship to the right
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.fire_bullet()

    def check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def fire_bullet(self):
        #Create new bullet and add it to the bullet Group
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def update_bullets(self):
        self.bullets.update()
        #Update bullets position and get rid of bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        #Check for any bullets that have hit aliens
        #If hit remove bullet and alien
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.prep_high_score()

        #Destroy existing bullets and create new fleet
        if not self.aliens:
            self.bullets.empty()
            self.create_fleet()
            self.settings.increase_speed()

            #Increase level
            self.stats.level += 1
            self.sb.prep_level()

    def ship_hit(self):
        #Respond to ship hit

        #Decrement ships left
        if self.stats.ships_left > 0:
            #Decrement ships_left and update scoreboard
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            #Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            #Create new fleet and center the ship
            self.create_fleet()
            self.ship.center_ship()

            #Pause
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def update_aliens(self):
        self.aliens.update()
        #Check if fleet is at an edge
        self.check_fleet_edges()

        #Check for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self.ship_hit()

        #Check for aliens hitting bottom of screen
        self.check_aliens_bottom()

    def check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self.change_fleet_direction()
                break

    def change_fleet_direction(self):
        #Drop fleet and change direction
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def check_aliens_bottom(self):
        #Check if aliens have reached the bottom
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self.ship_hit()
                break

    def create_fleet(self):
        #Create fleet of aliens
        #Create an alien and find the number of aliens in a row
        #Spacing between each alien is one alien width
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        #Determine the number of rows that fit on the screen
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        #Create fleet of aliens
        for row_number in range(number_rows):
            #Create first row of aliens
            for alien_number in range(number_aliens_x):
                self.create_alien(alien_number, row_number)

    def create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def update_screen(self):
        #Redraw the creen during each pass through the loop
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        #Draw the score information
        self.sb.show_score()

        #Draw the play button if the game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()
            
        #Make most recent drawn screen visible
        pygame.display.flip()
    
if __name__ == '__main__':
    #Create game instance and run game
    ai = AlienInvasion()
    ai.run_game()