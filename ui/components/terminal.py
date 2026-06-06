import pygame


class Terminal:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

        # terminal left: input/log		terminal right: commands/options
        self.left_rect = pygame.Rect(x, y, int(w * 0.7), h)
        self.right_rect = pygame.Rect(x + int(w * 0.7), y, int(w * 0.3), h)
        
        # font
        pygame.font.init()
        self.font = pygame.font.SysFont('Consolas', 16)
        
        # state
        self.active = False
        self.prompt_text = ""
        self.input_buffer = ""
        self.logs = ["welcome to games of life."]
        
        # callbacks and autocomplete
        self.callback = None
        self.options = []
        self.current_commands = []
        self.tab_index = -1
        self.matches = []
    
    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 7:
            self.logs.pop(0)
    
    def set_commands_info(self, commands_list):
        self.current_commands = commands_list
    
    def start_prompt(self, prompt_text, options, callback):
        self.active = True
        self.prompt_text = prompt_text
        self.options = options
        self.callback = callback
        self.input_buffer = ""
        self.tab_index = -1
        self.matches = []
        self._update_matches()
    
    def _update_matches(self):
        if not self.options:
            self.matches = []
            return
        
        search_str = self.input_buffer.lower()
        self.matches = [opt for opt in self.options if search_str in opt.lower()]
        self.tab_index = -1
    
    def handle_event(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active = False
                self.log("action cancelled.")
                
            elif event.key == pygame.K_RETURN:
                self.active = False
                if self.callback:
                    self.callback(self.input_buffer.strip())
                    
            elif event.key == pygame.K_BACKSPACE:
                self.input_buffer = self.input_buffer[:-1]
                self._update_matches()
                
            elif event.key == pygame.K_TAB:
                if self.matches:
                    self.tab_index = (self.tab_index + 1) % len(self.matches)
                    self.input_buffer = self.matches[self.tab_index]
            else:
                # Append standard printable characters
                if event.unicode.isprintable() and event.unicode != "":
                    self.input_buffer += event.unicode
                    self._update_matches()
                
            return True
            
        return False
    
    def draw(self, screen):
        # draw background panels
        pygame.draw.rect(screen, (10, 10, 15), self.left_rect)
        pygame.draw.rect(screen, (25, 25, 30), self.right_rect)
        
        # borders
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2)
        pygame.draw.line(screen, (100, 100, 100), (self.right_rect.x, self.rect.y), (self.right_rect.x, self.rect.bottom), 2)

        # left panel: logs and input
        y_offset = self.left_rect.y + 10
        for msg in self.logs:
            text_surf = self.font.render(msg, True, (180, 180, 180))
            screen.blit(text_surf, (self.left_rect.x + 10, y_offset))
            y_offset += 20

        if self.active:
            # draw input line at the bottom of the left panel
            input_y = self.left_rect.bottom - 30
            prompt_surf = self.font.render(f"{self.prompt_text}{self.input_buffer}_", True, (0, 255, 100))
            screen.blit(prompt_surf, (self.left_rect.x + 10, input_y))

        # right panel: current options
        r_y = self.right_rect.y + 10
        if self.active:
            # show options / autocomplete matches
            title = self.font.render("available options:", True, (200, 150, 50))
            screen.blit(title, (self.right_rect.x + 10, r_y))
            r_y += 25
            
            display_list = self.matches if self.input_buffer else self.options
            
            for i, opt in enumerate(display_list[:6]):  # limit items shown
                color = (0, 255, 100) if i == self.tab_index else (180, 180, 180)
                text_surf = self.font.render(f"- {opt}", True, color)
                screen.blit(text_surf, (self.right_rect.x + 10, r_y))
                r_y += 20
                
            if len(display_list) > 6:
                screen.blit(self.font.render(f"...and {len(display_list)-6} more", True, (100, 100, 100)), (self.right_rect.x + 10, r_y))
        else:
            # show standard scene commands
            title = self.font.render("hotkeys:", True, (200, 150, 50))
            screen.blit(title, (self.right_rect.x + 10, r_y))
            r_y += 25
            for cmd in self.current_commands:
                text_surf = self.font.render(cmd, True, (150, 200, 255))
                screen.blit(text_surf, (self.right_rect.x + 10, r_y))
                r_y += 20
