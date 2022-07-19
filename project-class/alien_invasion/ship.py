import pygame


class Ship():

    def __init__(self, ai_settings, screen):
        """Initialize the ship and set its starting position"""
        self.screen = screen
        self.ai_settings = ai_settings

        # load the ship image and get its rect
        self.image = pygame.image.load("images/ship.bmp")
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

        # start each new ship at the bottom ceter of screen
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom

        # Movement flag
        self.moving_right = False
        self.moving_left = False

        # Store a decimal value for the ship's center
        self.center = float(self.rect.centerx)

    def blitme(self):
        """Draw the ship at its current location"""
        self.screen.blit(self.image, self.rect)

    def update(self):
        """Update the ship's position based on movement flag"""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.center += self.ai_settings.ship_speed_factor
        elif self.moving_left and self.rect.left > self.screen_rect.left:
            self.center -= self.ai_settings.ship_speed_factor

        # Update rect object with self.center
        self.rect.centerx = self.center