# AiMe

AiMe is an experimental emotional-intelligence interface that combines a wearable BCI-style hat with an attached camera system to detect, interpret, and respond to human emotional states.

The goal of AiMe is to build an AI model of a specific person — you. Not a generic emotion classifier, but a model that understands who you are: what makes you happy, what makes you sad, who makes you happy, who makes you sad, and when those states tend to show up. It aims to capture the full picture of a person's emotional life, not just labeled expressions.

## What it captures

AiMe is designed to record, over a bounded window of time (roughly a month), the raw material a model would need to understand a person:

- **What was said, and how it was said** — the words themselves plus tone, delivery, and the emotional/physiological signal underneath them.
- **What others said, and how they said it** — the other side of every conversation, including its tone and delivery.
- **Conflicts** — disagreements and tense interactions, captured with enough fidelity to know what was actually said and how it unfolded, not just that a conflict occurred.
- **Emotional context** — who a person's key emotional triggers are (positive and negative), and the situations and timing around when those emotions occur.

After that collection window, this data is fed into a model whose job is to understand the person behind it — building something closer to a persistent model of a specific person's emotional identity, rather than a general-purpose emotion detector.

## How it works

At a high level, AiMe is made up of three main parts:

- **Wearable BCI Hat** — A head-mounted device designed to collect signals from the user. This may include brain activity or related biometric data, depending on the sensors used.
- **Camera System** — A camera attached to the wearable device captures visual information, such as the user's environment, facial expressions, and interaction context.
- **AI Integration Layer** — The collected sensor and camera data is processed through AI models to detect emotional patterns and provide meaningful outputs. During the capture window, this layer is focused on recording and labeling; afterward, it's used to train the personal model described above.

## Repository structure

- **`3 Wire EEG/`** — KiCad hardware design for the current 3-wire EEG board (schematic, PCB layout, and symbol libraries) used by the wearable hat.
- **`Research Paper Active Electrode/`** — A future hardware revision based on the active dry-electrode approach described in [this research paper](https://www.mdpi.com/1424-8220/19/20/4572), explored as a next-generation replacement for the 3-wire design.
- **`AI-Model/`** — Python scripts for streaming and capturing EEG data over LSL (`eeg_view.py`, `capture_gui_and_backend.py`) and early model experiments, plus recorded session data.
- **`Tazer/`** — Experimental automation server, separate from the core emotion-detection pipeline.
- **`data/`** — Captured EEG samples, organized by labeled emotional state (e.g. `happy`).

## Status

AiMe is currently a prototype and research-focused project. It is not intended to diagnose mental health conditions or provide medical advice. Instead, it is a platform for experimenting with emotion-aware computing, wearable interfaces, and multimodal AI systems trained on one person's own data.

## Vision

The long-term vision for AiMe is to build a device that can help technology better understand human emotion and context, making digital systems feel more responsive, personal, and human-aware.
