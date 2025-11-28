import pygame
from datetime import datetime
from warnings import warn


class Footer:
    def __init__(self, screen, font, height, text_colour,
                 inset=0, background_colour=None,
                 border_width=None, border_colour=None):
        
        self.screen = screen
        self.font = font
        self.height = height

        self.text_colour = text_colour
        self.background_colour = background_colour
        self.inset = inset
        self.border_width = border_width
        self.border_colour = border_colour

    def create_surface(self):
        """Create the inner drawing surface (inset applied)."""
        width = 320 - self.inset*2
        height = self.height - self.inset*2
        return pygame.Surface((width, height), pygame.SRCALPHA)

    def render(self):
        """Full render pipeline: background → content → border → blit."""
        
        surface = self.create_surface()

        # Fill background (if provided)
        if self.background_colour is not None:
            surface.fill(self.background_colour)

        # Let subclass draw text or icons
        self.render_content(surface)

        # Draw border (if enabled)
        if self.border_width and self.border_colour:
            pygame.draw.rect(
                surface,
                self.border_colour,
                surface.get_rect(),
                self.border_width
            )

        # Blit final footer surface to bottom of screen
        y = 480 - self.height + self.inset
        self.screen.blit(surface, (self.inset, y))

    def render_content(self, surface):
        """Subclasses override this only."""
        raise NotImplementedError
        

class MinimalFooter(Footer):
    def render_content(self, surface):
        text = self.font.render(datetime.now().strftime("%d/%m/%Y %H:%M"),
                                True, self.text_colour)

        if text.get_height() > surface.get_height():
            warn("Footer text is larger than footer height")

        text_rect = text.get_rect(center=(surface.get_width()//2,
                                          surface.get_height()//2))
        surface.blit(text, text_rect)