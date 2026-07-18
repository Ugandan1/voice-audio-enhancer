# Voice Audio Enhancer

A streamlined web application built with Streamlit that enhances voice recordings by automatically reducing background noise, applying a clean low-end bass boost, and normalizing audio levels for a professional output.

## Features
* **Background Noise Reduction:** Automatically filters out stationary and environmental background noise.
* **Low-End Bass Boost:** Applies a clean frequency boost below 150 Hz to give voice recordings more warmth and depth.
* **Peak Normalization:** Automatically adjusts overall volume levels to ensure clear playback without clipping.
* **Multi-Format Support:** Accepts `.mp3`, `.wav`, `.mp4`, and `.m4a` files.
* **Direct Web Downloads:** Save your enhanced audio track directly through your browser.

## Tech Stack
* **Frontend:** Streamlit
* **Audio Processing:** Pydub, NoiseReduce, NumPy
