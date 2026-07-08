"""
audio.py - centralised audio playback for the kiosk.

Each sound is mapped to a specific interaction event so the audio design
can be reasoned about independently of the visuals (see README / design
rationale for the HCI justification of each mapping).
"""
import os
import pygame

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")


class AudioManager:
    def __init__(self):
        self.enabled = True
        self.muted = False
        self._sounds = {}
        self.ambient_channel = None

        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"[audio] No audio device available, running muted: {e}")
            self.enabled = False
            return

        for name in ["click", "confirm", "whoosh", "tick", "ambient", "step_up", "step_down"]:
            path = os.path.join(ASSET_DIR, f"{name}.wav")
            if os.path.exists(path):
                try:
                    self._sounds[name] = pygame.mixer.Sound(path)
                except pygame.error as e:
                    print(f"[audio] Could not load {name}.wav: {e}")

        if "ambient" in self._sounds:
            self._sounds["ambient"].set_volume(0.22)
            self.ambient_channel = self._sounds["ambient"].play(loops=-1)

    def play(self, name):
        if not self.enabled or self.muted:
            return
        snd = self._sounds.get(name)
        if snd:
            snd.play()

    def toggle_mute(self):
        self.muted = not self.muted
        if self.ambient_channel:
            self.ambient_channel.set_volume(0.0 if self.muted else 0.22)

    def quit(self):
        if self.enabled:
            pygame.mixer.quit()
