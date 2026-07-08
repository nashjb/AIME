# AiMe

AiMe is an experimental emotional-intelligence interface that combines a wearable BCI-style hat with an attached camera system to detect, interpret, and respond to human emotional states.

The goal of AiMe is to explore how brain-computer interfaces, computer vision, and AI can work together to create a more intuitive way for humans and technology to interact. Instead of relying only on keyboards, touchscreens, or voice commands, AiMe aims to understand signals such as facial expression, visual context, and potentially brain or physiological data to estimate a person's emotional state.

## How it works

At a high level, AiMe is made up of three main parts:

- **Wearable BCI Hat** — A head-mounted device designed to collect signals from the user. This may include brain activity or related biometric data, depending on the sensors used.
- **Camera System** — A camera attached to the wearable device captures visual information, such as the user's environment, facial expressions, or interaction context.
- **AI Integration Layer** — The collected sensor and camera data is processed through AI models to detect emotional patterns and provide meaningful outputs. These outputs could be used for feedback, logging, adaptive interfaces, assistive technology, or future human-computer interaction experiments.

## Repository structure

- **`3 Wire EEG/`** — KiCad hardware design for the 3-wire EEG board (schematic, PCB layout, and symbol libraries) used by the wearable hat.
- **`AI-Model/`** — Python scripts for streaming and capturing EEG data over LSL (`eeg_view.py`, `capture_gui_and_backend.py`) and early model experiments, plus recorded session data.
- **`Tazer/`** — Experimental automation server, separate from the core emotion-detection pipeline.
- **`data/`** — Captured EEG samples, organized by labeled emotional state (e.g. `happy`).

## Status

AiMe is currently a prototype and research-focused project. It is not intended to diagnose mental health conditions or provide medical advice. Instead, it is a platform for experimenting with emotion-aware computing, wearable interfaces, and multimodal AI systems.

## Vision

The long-term vision for AiMe is to build a device that can help technology better understand human emotion and context, making digital systems feel more responsive, personal, and human-aware.
