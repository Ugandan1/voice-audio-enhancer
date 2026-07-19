"""Streamlit interface for the Voice Audio Enhancer."""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from audio_processing import AudioProcessingError, process_audio


MAX_UPLOAD_BYTES = 50 * 1024 * 1024

st.set_page_config(page_title="Voice Audio Enhancer", page_icon="🎙️", layout="centered")

st.title("🎙️ Voice Audio Enhancer")
st.write(
    "Upload a WAV or MP3 recording to reduce background noise, add a clean low-end "
    "boost, and normalize its volume."

)

uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "m4a", "mp4", "amr"]), help="Maximum file size: 50 MB.")

if uploaded_file is not None:
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        st.error("That file is larger than 50 MB. Please choose a smaller file.")
        st.stop()

    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in {".mp3", ".wav", ".mp4", ".m4a"}:
        st.error("Please upload an MP3, WAV, MP4, or M4A file.")
        st.stop()

    st.subheader("Original audio")
    st.audio(uploaded_file.getvalue(), format=f"audio/{suffix[1:]}")

    if st.button("Process audio", type="primary"):        
        with st.spinner("Reducing noise and enhancing the recording…"):
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    input_path = Path(temp_dir) / f"input{suffix}"
                    output_path = Path(temp_dir) / f"enhanced_{Path(uploaded_file.name).stem}{suffix}"
                    input_path.write_bytes(uploaded_file.getvalue())

                    process_audio(input_path, output_path)
                    output_bytes = output_path.read_bytes()
            except AudioProcessingError as error:
                st.error(str(error))
            except Exception as error:  # Keep unexpected processing errors understandable in the UI.
                st.error(f"The audio could not be processed: {error}")
            else:
                st.success("Your enhanced audio is ready.")
                st.subheader("Enhanced audio")
                st.audio(output_bytes, format=f"audio/{suffix[1:]}")
                st.download_button(
                    "Download enhanced audio",
                    data=output_bytes,
                    file_name=output_path.name,
                    mime="audio/mpeg" if suffix == ".mp3" else "audio/wav",
                )

st.caption("MP3 import and export require FFmpeg. See the README for installation help.")
