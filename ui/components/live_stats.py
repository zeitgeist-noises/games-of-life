import pygame
import numpy as np
import collections
from scipy.ndimage import uniform_filter


class LiveStats:
    def __init__(self, max_history=400):
        self.prev_grid = None
        self.activity_ema = None
        
        # pop out data points if max time has been reached
        self.pop_history = collections.deque(maxlen=max_history)
        self.font = pygame.font.Font(None, 24)

    def reset(self):
        self.prev_grid = None
        self.activity_ema = None
        self.pop_history.clear()

    def update(self, grid):
        # track the population
        pop = np.sum(grid)
        pct = pop / grid.size
        self.pop_history.append(pct)

        # tracks the local switching activity
        if self.prev_grid is None or self.prev_grid.shape != grid.shape:
            self.prev_grid = grid.copy()
            self.activity_ema = np.zeros(grid.shape, dtype=float)
        else:
            # mask of cells that switched
            switched = (grid != self.prev_grid).astype(float)
            
            # calculate exponential moving average
            self.activity_ema = 0.15 * switched + 0.85 * self.activity_ema
            self.prev_grid = grid.copy()

    def draw(self, screen, x, y, w, h):
        if not self.pop_history:
            return

        # split area into heatmap and population tracker
        hm_w = int(w * 0.4)
        graph_w = w - hm_w
        
        self._draw_heatmap(screen, x, y, hm_w, h)
        self._draw_graph(screen, x + hm_w, y, graph_w, h)

    def _draw_heatmap(self, screen, x, y, w, h):
        screen.blit(self.font.render("activity heatmap", True, (180, 180, 180)), (x + 10, y + 5))
        
        # smooth ema graph
        filter_size = max(3, self.activity_ema.shape[0] // 10)
        local_activity = uniform_filter(self.activity_ema, size=filter_size)
        
        # normalize
        max_act = np.max(local_activity)
        if max_act > 0.001:
            norm_act = local_activity / max_act
        else:
            norm_act = local_activity

        # map to rgb
        heatmap_rgb = np.zeros((norm_act.shape[0], norm_act.shape[1], 3), dtype=np.uint8)
        heatmap_rgb[..., 0] = (norm_act * 255).astype(np.uint8)          # red dominates
        heatmap_rgb[..., 1] = ((norm_act ** 2) * 220).astype(np.uint8)   # green comes in later
        heatmap_rgb[..., 2] = ((norm_act ** 3) * 100).astype(np.uint8)   # blue only at the very peaks

        # render to surface and scale
        hm_surf = pygame.Surface((heatmap_rgb.shape[1], heatmap_rgb.shape[0]))
        # Transpose needed because Pygame expects (width, height, channels)
        pygame.surfarray.blit_array(hm_surf, heatmap_rgb.transpose(1, 0, 2))
        
        scaled_hm = pygame.transform.scale(hm_surf, (w - 20, h - 35))
        screen.blit(scaled_hm, (x + 10, y + 25))
        pygame.draw.rect(screen, (80, 80, 80), (x + 10, y + 25, w - 20, h - 35), 1)

    def _draw_graph(self, screen, x, y, w, h):
        # population stats readout
        curr_pct = self.pop_history[-1] * 100
        peak_pct = max(self.pop_history) * 100
        txt = f"population: {curr_pct:.1f}%   (peak: {peak_pct:.1f}%)"
        screen.blit(self.font.render(txt, True, (180, 180, 180)), (x + 10, y + 5))

        # graph panel
        g_x, g_y = x + 10, y + 25
        g_w, g_h = w - 10, h - 35
        pygame.draw.rect(screen, (20, 25, 30), (g_x, g_y, g_w, g_h))
        pygame.draw.rect(screen, (80, 80, 80), (g_x, g_y, g_w, g_h), 1)

        # plot line
        pts = []
        max_p = max(self.pop_history) if self.pop_history else 1
        if max_p == 0:
            max_p = 1
        
        for i, p in enumerate(self.pop_history):
            # x coordinate mapped to deque length
            px = g_x + int((i / self.pop_history.maxlen) * g_w)
            # y coordinate mapped to current maximum peak
            py = g_y + g_h - int((p / max_p) * g_h)
            pts.append((px, py))
            
        if len(pts) > 1:
            pygame.draw.lines(screen, (0, 255, 150), False, pts, 2)
