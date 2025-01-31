import pygame
import cv2
import numpy as np
import asyncio
import random
from loguru import logger


class Visualizer:
    """
    A class for the infinite looping avatar visualizer with separate update functions.
    """

    def __init__(self, video_path: str, width: int = 1000, height: int = 700):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Infinite Looping Avatar")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 72)

        # Load video
        self.video = cv2.VideoCapture(video_path)
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.frames = self._load_video_frames()

        # Particle system
        self.particles = []

        # Thread synchronization
        self.running = True
        self.audio_detected=False

    def _load_video_frames(self):
        """Load all video frames into memory."""
        frames = []
        while True:
            ret, frame = self.video.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frames.append(frame)
        logger.info(f"Loaded {len(frames)} video frames.")
        return frames

    async def _run_video_loop(self):
        """Async infinite loop that updates video frames dynamically."""
        frame_index = 0

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    self.running = False

            # Update frame index
            frame_index = self._update_frame(frame_index)

            # Render frame
            self._render_frame(frame_index)
            self._render_fps()
            # Audio-visual reaction
            if self.audio_detected:
                # Glowing ring effect
                for i in range(5):  # Five concentric rings
                    alpha = max(0, 255 - i * 50)
                    radius = 50 + i * 20
                    overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    pygame.draw.circle(
                        overlay,
                        (128, 0, 255, alpha),  # Glowing purple
                        (self.width // 2, self.height // 2),
                        radius,
                        5  # Thickness
                    )
                    self.screen.blit(overlay, (0, 0))

                # Emit particles
                self.emit_particles()
            # Update particles (if externally triggered)
            self._update_particles()
            self._render_particles()

            # Update display
            self._update_display()

            # Control frame rate
            # await asyncio.sleep(1 / self.fps)
            self.clock.tick(self.fps)
            await asyncio.sleep(0)
            # await asyncio.sleep(max(0.001, 1 / self.fps - 0.001)) 

        self.cleanup()

    def _update_frame(self, frame_index: int) -> int:
        """Handles video looping and updates the frame index."""
        return 0 if frame_index >= len(self.frames) - 1 else frame_index + 1

    def _render_fps(self):
        """Renders the FPS counter onto the screen."""
        fps_text = f"FPS: {int(self.clock.get_fps())}"  # Get the FPS value
        text_surface = self.font.render(fps_text, True, (255, 255, 255))  # Render white text
        self.screen.blit(text_surface, (10, 10))  # Position at (10, 10)

    def _render_frame(self, frame_index: int):
        """Renders the current frame onto the Pygame screen."""
        frame = self.frames[frame_index]
        surf = pygame.surfarray.make_surface(frame)
        surf = pygame.transform.scale(surf, (self.width, self.height))
        self.screen.blit(surf, (0, 0))

    def emit_particles(self):
        """Emit particles when audio is detected."""
        for _ in range(5):  # Emit 5 particles per frame when triggered
            self.particles.append({
                'x': self.width / 2,
                'y': self.height / 2,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'size': random.randint(2, 5),
                'color': (random.randint(200, 255), 0, random.randint(200, 255)),
                'lifetime': random.randint(20, 50)  # Frames to live
            })

    def _update_particles(self):
        """Updates positions and lifetimes of particles."""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)

    def _render_particles(self):
        """Draws particles on the screen."""
        for particle in self.particles:
            pygame.draw.circle(self.screen, particle['color'], (int(particle['x']), int(particle['y'])), particle['size'])

    def _update_display(self):
        """Updates the Pygame display."""
        pygame.display.flip()

    def cleanup(self):
        """Cleanup resources when the loop exits."""
        pygame.quit()
        self.video.release()
        logger.info("Visualizer ended.")


async def main():
    visualizer = Visualizer("orb.mp4")
    await visualizer._run_video_loop()  # Call it externally

if __name__ == "__main__":
    asyncio.run(main())
