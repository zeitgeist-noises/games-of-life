import pygame
import math
import numpy as np
from ui.scenes.base_scene import Scene
from engine.genome import Genome


class EditScene(Scene):
    def __init__(self, app, initial_genome):
        super().__init__(app)
        
        self.kernel = initial_genome.kernel.copy()
        self.rule_table = initial_genome.rule_table.copy()
        self.sparsity = initial_genome.sparsity
        
        self.state = "IDLE"
        
        self.k_cx, self.k_cy = 0, 0
        self.r_cx, self.r_cy = 0, 0
        
        self.last_input_time = pygame.time.get_ticks()
        
        self.font_large = pygame.font.SysFont('Consolas', 24)
        self.font_small = pygame.font.SysFont('Consolas', 16)
        
        self.update_command_info()
    
    def on_enter(self):
        self.app.terminal.set_commands_info(self.commands_info)
        self._update_title()

    def _update_title(self):
        pygame.display.set_caption(f"Genome Workspace | Mode: {self.state} | Sparsity: {self.sparsity:.3f}")

    def update_command_info(self):
        if self.state == "IDLE":
            self.commands_info = [
                "[k]     edit kernel",
                "[r]     edit rules",
                "[s]     edit sparsity",
                "[esc]   exit editor / apply"
            ]
        elif self.state == "KERNEL":
            self.commands_info = [
                "[arrows] move cursor",
                "[space]  toggle cell",
                "[ [ ]    shrink kernel",
                "[ ] ]    grow kernel",
                "[esc]    exit"
            ]
        elif self.state == "RULE":
            self.commands_info = [
                "[arrows] move cursor",
                "[space]  toggle value",
                "[esc]    exit"
            ]
            
        self.app.terminal.set_commands_info(self.commands_info)
    
    def _update_rule_table_size(self):
        S_new = int(np.sum(self.kernel))
        S_old = self.rule_table.shape[1] - 1
        
        if S_new > S_old:
            padding = np.zeros((2, S_new - S_old), dtype=np.uint8)
            self.rule_table = np.hstack((self.rule_table, padding))
        elif S_new < S_old:
            self.rule_table = self.rule_table[:, :S_new + 1]
            
        self.r_cx = min(self.r_cx, S_new)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            
            if self.state == "IDLE":
                if event.key == pygame.K_k:
                    self.state = "KERNEL"
                    self.app.terminal.log("entered kernel edit mode.")
                    self.update_command_info()
                elif event.key == pygame.K_r:
                    self.state = "RULE"
                    self.app.terminal.log("entered rule edit mode.")
                    self.update_command_info()
                elif event.key == pygame.K_s:
                    self.app.terminal.start_prompt(
                        prompt_text=f"enter new sparsity (current: {self.sparsity:.3f}): ",
                        options=[],
                        callback=self._set_sparsity
                    )
                elif event.key == pygame.K_ESCAPE:
                    new_genome = Genome(self.kernel, self.rule_table, self.sparsity)
                    self.app.ca.genome = new_genome
                    self.app.ca.grid = self.app.ca.reset_grid()
                    self.app.change_scene("MAIN")
                    self.app.terminal.log("genome changes applied.")
                    
            elif self.state == "KERNEL":
                N = self.kernel.shape[0]
                if event.key == pygame.K_ESCAPE:
                    self.state = "IDLE"
                    self.update_command_info()
                elif event.key == pygame.K_LEFT:
                    self.k_cx = (self.k_cx - 1) % N
                    self.last_input_time = pygame.time.get_ticks()
                elif event.key == pygame.K_RIGHT:
                    self.k_cx = (self.k_cx + 1) % N
                    self.last_input_time = pygame.time.get_ticks()
                elif event.key == pygame.K_UP:
                    self.k_cy = (self.k_cy - 1) % N
                    self.last_input_time = pygame.time.get_ticks()
                elif event.key == pygame.K_DOWN:
                    self.k_cy = (self.k_cy + 1) % N
                    self.last_input_time = pygame.time.get_ticks()
                elif event.key == pygame.K_SPACE:
                    # don't allow changes to center
                    if not (self.k_cx == N // 2 and self.k_cy == N // 2):
                        self.kernel[self.k_cy, self.k_cx] = 1 - self.kernel[self.k_cy, self.k_cx]
                        self._update_rule_table_size()
                elif event.key == pygame.K_RIGHTBRACKET:
                    new_kernel = np.zeros((N + 2, N + 2), dtype=np.uint8)
                    new_kernel[1:-1, 1:-1] = self.kernel
                    self.kernel = new_kernel
                    self.k_cx += 1
                    self.k_cy += 1
                    self._update_rule_table_size()
                elif event.key == pygame.K_LEFTBRACKET:
                    if N > 3:
                        self.kernel = self.kernel[1:-1, 1:-1]
                        self.k_cx = max(0, self.k_cx - 1)
                        self.k_cy = max(0, self.k_cy - 1)
                        self._update_rule_table_size()
                        
            elif self.state == "RULE":
                S = self.rule_table.shape[1] - 1
                if event.key == pygame.K_ESCAPE:
                    self.state = "IDLE"
                    self.update_command_info()
                elif event.key == pygame.K_LEFT:
                    self.r_cx = (self.r_cx - 1) % (S + 1)
                    self.last_input_time = pygame.time.get_ticks()
                elif event.key == pygame.K_RIGHT:
                    self.r_cx = (self.r_cx + 1) % (S + 1)
                    self.last_input_time = pygame.time.get_ticks()
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    self.r_cy = 1 - self.r_cy
                    self.last_input_time = pygame.time.get_ticks()
                elif event.key == pygame.K_SPACE:
                    self.rule_table[self.r_cy, self.r_cx] = 1 - self.rule_table[self.r_cy, self.r_cx]
                    self.last_input_time = pygame.time.get_ticks()

            self._update_title()

    def _set_sparsity(self, input_str):
        try:
            val = float(input_str)
            self.sparsity = max(0.0, min(val, 1.0))
            self.app.terminal.log(f"sparsity updated to {self.sparsity:.3f}")
            self._update_title()
        except ValueError:
            self.app.terminal.log("invalid sparsity input. must be a float.")

    def update(self):
        pass

    def draw(self, screen):
        W = self.app.screen_width
        H = self.app.screen_height - self.app.terminal.rect.height
        
        self._draw_kernel(screen, W, H)
        self._draw_rules(screen, W, H)

    def _draw_kernel(self, screen, W, H):
        N = self.kernel.shape[0]

        max_box_size = min(W * 0.5, H * 0.45)
        cell_size = int(max_box_size / max(N, 1))
        
        k_size = N * cell_size
        
        start_x = (W - k_size) // 2
        start_y = 40
        
        title_color = (0, 255, 100) if self.state == "KERNEL" else (150, 150, 150)
        screen.blit(self.font_large.render("kernel", True, title_color), (start_x, 10))

        for r in range(N):
            for c in range(N):
                rect = (start_x + c * cell_size, start_y + r * cell_size, cell_size, cell_size)
                
                if r == N // 2 and c == N // 2:
                    pygame.draw.rect(screen, (50, 50, 50), rect)
                    pygame.draw.line(screen, (100, 100, 100), (rect[0], rect[1]), (rect[0]+cell_size, rect[1]+cell_size))
                    pygame.draw.line(screen, (100, 100, 100), (rect[0]+cell_size, rect[1]), (rect[0], rect[1]+cell_size))
                else:
                    if self.kernel[r, c] == 1:
                        pygame.draw.rect(screen, (220, 220, 220), rect)
                
                pygame.draw.rect(screen, (80, 80, 80), rect, 1)
        
        time_since_input = pygame.time.get_ticks() - self.last_input_time

        if self.state == "KERNEL" and (time_since_input % 1000 < 500):
            cursor_rect = (start_x + self.k_cx * cell_size, start_y + self.k_cy * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, (0, 255, 100), cursor_rect, 3)

    def _draw_rules(self, screen, W, H):
        S = self.rule_table.shape[1] - 1
        start_y = (H // 2) + 20
        
        title_color = (0, 255, 100) if self.state == "RULE" else (150, 150, 150)
        screen.blit(self.font_large.render("rule table", True, title_color), ((W // 2) - 50, start_y))
        
        start_y += 40
        chunk_size = 15
        num_chunks = math.ceil((S + 1) / chunk_size)
        
        cell_w = 40
        
        for chunk in range(num_chunks):
            start_idx = chunk * chunk_size
            end_idx = min(start_idx + chunk_size, S + 1)
            chunk_len = end_idx - start_idx
            
            chunk_w = chunk_len * cell_w + 100
            start_x = (W - chunk_w) // 2
            
            screen.blit(self.font_small.render("neighbors", True, (150, 150, 150)), (start_x, start_y))
            screen.blit(self.font_small.render("survive", True, (200, 200, 255)), (start_x, start_y + 25))
            screen.blit(self.font_small.render("birth", True, (255, 200, 200)), (start_x, start_y + 50))
            
            x_offset = start_x + 100
            
            for i in range(start_idx, end_idx):
                num_surf = self.font_small.render(str(i), True, (200, 200, 200))
                screen.blit(num_surf, (x_offset + (cell_w - num_surf.get_width()) // 2, start_y))
                
                marker_s = "O" if self.rule_table[0, i] else "-"
                surf_s = self.font_small.render(marker_s, True, (200, 200, 255))
                screen.blit(surf_s, (x_offset + (cell_w - surf_s.get_width()) // 2, start_y + 25))
                
                marker_b = "O" if self.rule_table[1, i] else "-"
                surf_b = self.font_small.render(marker_b, True, (255, 200, 200))
                screen.blit(surf_b, (x_offset + (cell_w - surf_b.get_width()) // 2, start_y + 50))
                
                time_since_input = pygame.time.get_ticks() - self.last_input_time
                
                if self.state == "RULE" and self.r_cx == i and (time_since_input % 1000 < 500):
                    cursor_y = start_y + 25 if self.r_cy == 0 else start_y + 50
                    pygame.draw.rect(screen, (0, 255, 100), (x_offset+5, cursor_y-2, cell_w-10, 20), 2)
                    
                x_offset += cell_w
                
            start_y += 90
