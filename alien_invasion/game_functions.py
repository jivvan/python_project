import sys
from time import sleep
import pygame
from alien import Alien

from bullet import Bullet
from button import Button
from game_stats import GameStats
from scoreboard import Scoreboard
from settings import Settings
from sfx import SFX
from ship import Ship


def check_events(ai_settings, stats, sb, sfx, screen, ship, aliens, bullets, play_button):
    """Respond to keypresses and mouse events"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings,
                                 screen, sfx, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, stats, sb, sfx, screen, ship,
                              aliens, bullets, play_button, mouse_x, mouse_y)


def check_play_button(ai_settings, stats, sb: Scoreboard, sfx: SFX, screen, ship, aliens, bullets, play_button: Button, mouse_x, mouse_y):
    """Start a new game when the player clicks play"""
    if play_button.rect.collidepoint(mouse_x, mouse_y) and not stats.game_active:
        # Reset the game settings
        ai_settings.initialize_dynamic_settings()
        # Hide the mouse cursor
        pygame.mouse.set_visible(False)

        stats.reset_stats()
        stats.game_active = True

        # Reset scoreboard images
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()

        # Empty the list of aliens and bullets
        aliens.empty()
        bullets.empty()

        # Play start sound
        sfx.start_sound.play()

        # Create a new fleet and center the ship
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()


def update_screen(ai_settings, stats, sb: Scoreboard, screen, ship, aliens, bullets, play_button):
    """Update images on the screen and flip to the new screen"""
    # Redraw the screen during each pass through the loop.
    screen.fill(ai_settings.bg_color)
    ship.update()
    # redraw all bullets behind ship and aliens
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)

    # draw the score information
    sb.show_score()

    # Draw the play button if the game is inactive
    if not stats.game_active:
        play_button.draw_button()

    # Make the most recently drawn screen visible.
    pygame.display.flip()


def check_keydown_events(event, ai_settings, screen, sfx, ship, bullets):
    """Respond to keypresses"""
    if event.key == pygame.K_RIGHT:
        # Move the ship to the right
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        # Move the ship to the right
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, sfx, ship, bullets)


def check_keyup_events(event, ship):
    """Respond to keyreleases"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def update_bullets(ai_settings: Settings, screen: pygame.Surface, stat: GameStats, sb: Scoreboard, sfx, ship: Ship, aliens: Alien, bullets):
    """Update position of bullets and get rid of old bullets"""
    # Update bullet positions
    bullets.update()

    # Get rid of bullets out of bounds
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collision(
        ai_settings, screen, stat, sb, sfx, ship, aliens, bullets)


def check_bullet_alien_collision(ai_settings, screen, stats, sb: Scoreboard, sfx: SFX, ship, aliens, bullets):
    # Check for any bullets that have hit aliens
    # If so, get rid of the bullet and the alien
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for aliens in collisions.values():
            sfx.alien_sound.play()
            stats.score += ai_settings.alien_points
            sb.prep_score()
        check_high_score(stats, sb)

    if len(aliens) == 0:
        # Destroy existing bullets and create new bfleet and speed up game
        bullets.empty()
        ai_settings.increase_speed()

        # Increase level
        stats.level += 1
        sb.prep_level()
        sfx.score_sound.play()

        create_fleet(ai_settings, screen, ship, aliens)


def update_aliens(ai_settings, stats, sb: Scoreboard, sfx, screen, ship, aliens, bullets):
    """Check if fleet is at an edge and then update the positions of all aliens in the fleet."""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # Look for alien-ship collisions
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, sb, sfx, screen, ship, aliens, bullets)

    # Look for aliens hitting the bottom of the screen
    check_aliens_bottom(ai_settings, stats, sb, sfx,
                        screen, ship, aliens, bullets)


def fire_bullet(ai_settings, screen, sfx: SFX, ship, bullets):
    """Fire a bullet if limit not reached"""
    # Create a new bullet and add it to group
    if(len(bullets) < ai_settings.bullets_allowed):
        sfx.bullet_sound.play()
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def create_fleet(ai_settings, screen, ship, aliens):
    """Create a full fleet of aliens"""
    # Create an alien and find the number of aliens in a row
    # Spacing between each alien is equal to one alien width
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    number_of_aliens = get_number_aliens_x(ai_settings, alien_width)
    number_rows = get_number_rows(
        ai_settings, ship.rect.height, alien.rect.height,)

    # Create fleet of aliens
    for row_number in range(number_rows):
        for alien_number in range(number_of_aliens):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def get_number_aliens_x(ai_settings, alien_width):
    """Determine the number of aliens that fit in a row"""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_of_aliens = int(available_space_x/(2 * alien_width))
    return number_of_aliens


def get_number_rows(ai_settings, ship_height, alien_height):
    """Determine the number of rows of aliens that fit on the screen"""
    available_space_y = (ai_settings.screen_height -
                         (3 * alien_height) - ship_height)
    number_rows = int(available_space_y/(2 * alien_height))
    return number_rows


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Create an alien and place it in the row"""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    alien.rect.x = alien.x
    aliens.add(alien)


def check_fleet_edges(ai_settings: Settings, aliens):
    """Respond appropriately if any aliens have reached the edge"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings: Settings, aliens):
    """Drop the entire fleet and change the direction of fleet"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def ship_hit(ai_settings: Settings, stats: GameStats, sb: Scoreboard, sfx: SFX, screen: pygame.Surface, ship: Ship, aliens: pygame.sprite.Group, bullets: pygame.sprite.Group):
    """Respond to ship being hit by alien"""
    if stats.ships_left > 1:
        # Decrement ships_left
        stats.ships_left -= 1

        # Update scoreboard
        sb.prep_ships()

        # Empty the list of aliens and bullets
        aliens.empty()
        bullets.empty()

        # Create a new fleet and center the ship
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # Pause and play sound
        sfx.dead_sound.play()
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)


def check_aliens_bottom(ai_settings, stats: GameStats, sb: Scoreboard, sfx: SFX, screen: pygame.Surface, ship, aliens: pygame.sprite.Group, bullets):
    """Check if any aliens have reached the bottom of the screen"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # Treat this the same as if the ship got hit
            ship_hit(ai_settings, stats, sb, sfx,
                     screen, ship, aliens, bullets)
            break


def check_high_score(stats: GameStats, sb: Scoreboard):
    """check to see if there's a new high score"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()
