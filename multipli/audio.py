"""
Gestionnaire d'effets sonores natifs utilisant GStreamer.
Synthétise de doux carillons mélodieux pour les succès sans nécessiter de fichiers audio externes.
"""

import threading
import time

try:
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    Gst.init(None)
    GST_AVAILABLE = True
except Exception:
    GST_AVAILABLE = False


class SoundManager:
    _instance = None

    def __init__(self):
        self.enabled = True

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def _play_pipeline(self, pipeline_str: str):
        if not self.enabled or not GST_AVAILABLE:
            return

        def run():
            try:
                pipeline = Gst.parse_launch(pipeline_str)
                pipeline.set_state(Gst.State.PLAYING)
                bus = pipeline.get_bus()
                bus.timed_pop_filtered(
                    Gst.CLOCK_TIME_NONE,
                    Gst.MessageType.ERROR | Gst.MessageType.EOS
                )
                pipeline.set_state(Gst.State.NULL)
            except Exception:
                pass

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def play_success(self):
        """Son joyeux de bonne réponse (carillon doux 2 notes montantes)."""
        if not self.enabled:
            return

        def run():
            # Note 1 : Sol 5 (784 Hz)
            self._play_tone_sync(783.99, duration_ms=100, volume=0.25)
            time.sleep(0.04)
            # Note 2 : Do 6 (1046 Hz)
            self._play_tone_sync(1046.50, duration_ms=160, volume=0.30)

        threading.Thread(target=run, daemon=True).start()

    def play_error(self):
        """Son discret et doux pour une erreur (onde douce basse)."""
        if not self.enabled:
            return
        # Mi bémol grave doux (311 Hz)
        pipeline_str = "audiotestsrc wave=sine freq=311.13 num-buffers=12 ! volume volume=0.18 ! audioconvert ! audioresample ! autoaudiosink"
        self._play_pipeline(pipeline_str)

    def play_level_complete(self):
        """Fanfare de victoire (arpeggio ascendant Do-Mi-Sol-Do)."""
        if not self.enabled:
            return

        def run():
            notes = [523.25, 659.25, 783.99, 1046.50]
            for freq in notes:
                self._play_tone_sync(freq, duration_ms=130, volume=0.3)
                time.sleep(0.04)

        threading.Thread(target=run, daemon=True).start()

    def _play_tone_sync(self, freq: float, duration_ms: int = 120, volume: float = 0.25):
        if not GST_AVAILABLE:
            return
        buffers = max(1, int(44100 * (duration_ms / 1000.0) / 1024))
        pipeline_str = (
            f"audiotestsrc wave=sine freq={freq} num-buffers={buffers} "
            f"! volume volume={volume} ! audioconvert ! audioresample ! autoaudiosink"
        )
        try:
            pipeline = Gst.parse_launch(pipeline_str)
            pipeline.set_state(Gst.State.PLAYING)
            bus = pipeline.get_bus()
            bus.timed_pop_filtered(
                Gst.CLOCK_TIME_NONE,
                Gst.MessageType.ERROR | Gst.MessageType.EOS
            )
            pipeline.set_state(Gst.State.NULL)
        except Exception:
            pass
