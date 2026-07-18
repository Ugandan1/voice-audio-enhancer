"""Audio-processing functions used by the Streamlit application."""

from __future__ import annotations

from pathlib import Path

import noisereduce as nr
import numpy as np
from pydub import AudioSegment, effects
from pydub.exceptions import CouldntDecodeError


class AudioProcessingError(RuntimeError):
    """A clear error shown when an uploaded file cannot be processed."""


def _reduce_noise(audio: AudioSegment) -> AudioSegment:
    """Denoise each channel independently while retaining the input's channel layout."""
    # Convert first so NumPy's sample conversion is predictable and avoids 24-bit handling.
    working_audio = audio.set_sample_width(2)
    samples = np.array(working_audio.get_array_of_samples(), dtype=np.float32)
    channels = working_audio.channels
    samples = samples.reshape((-1, channels))

    # noisereduce expects floating point samples. Per-channel processing is compatible
    # with mono and stereo recordings and avoids mixing channels together.
    denoised = np.empty_like(samples)
    for channel in range(channels):
        denoised[:, channel] = nr.reduce_noise(
            y=samples[:, channel],
            sr=working_audio.frame_rate,
            stationary=False,
            prop_decrease=0.8,
        )

    clipped = np.clip(denoised, -32768, 32767).astype(np.int16)
    return working_audio._spawn(clipped.reshape(-1).tobytes())


def _boost_bass(audio: AudioSegment, cutoff_hz: int = 150, boost_db: float = 6.0) -> AudioSegment:
    """Add a clean approximately +6 dB low-frequency boost below ``cutoff_hz``."""
    low_band = audio.low_pass_filter(cutoff_hz)
    return audio.overlay(low_band.apply_gain(boost_db))


def process_audio(input_path: str | Path, output_path: str | Path) -> Path:
    """Reduce noise, boost bass, normalize, and export in the original file format.

    Args:
        input_path: Source MP3 or WAV file.
        output_path: Destination with the same extension as the source.

    Returns:
        The output path after a successful export.
    """
    source = Path(input_path)
    destination = Path(output_path)
    extension = source.suffix.lower()

    if extension not in {".mp3", ".wav", ".mp4", ".m4a"}:
       raise AudioProcessingError("Only MP3, WAV, MP4, and M4A files are supported.")
    if destination.suffix.lower() != extension:
        raise AudioProcessingError("The output file must use the same format as the uploaded file.")

    try:
        audio = AudioSegment.from_file(source, format=extension[1:])
    except (CouldntDecodeError, FileNotFoundError) as error:
        raise AudioProcessingError(
            "This file could not be read. For MP3 files, confirm that FFmpeg is installed."
        ) from error

    if len(audio) == 0:
        raise AudioProcessingError("The uploaded audio file is empty.")

    try:
        enhanced = _reduce_noise(audio)
        enhanced = _boost_bass(enhanced)
        # Peak normalization leaves a little headroom, reducing the chance of clipping.
        enhanced = effects.normalize(enhanced, headroom=0.5)
        destination.parent.mkdir(parents=True, exist_ok=True)
        enhanced.export(destination, format=extension[1:])
    except Exception as error:
        raise AudioProcessingError(
            "Processing failed. For MP3 files, confirm that FFmpeg is installed and on your PATH."
        ) from error

    return destination
