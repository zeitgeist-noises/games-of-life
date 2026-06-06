class Scene:
    def __init__(self, app):
        self.app = app

    def on_enter(self):
        """called when transitioning to this scene."""
        pass

    def handle_event(self, event):
        """process pygame events (keyboard, mouse)."""
        pass

    def update(self):
        """simulation logic step."""
        pass

    def draw(self, screen):
        """render scene elements to the screen."""
        pass
        
    def on_ca_changed(self):
        """called if the master app loads a new ca genome/grid."""
        pass
