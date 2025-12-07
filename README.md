# Comprehensive Evaluation of OpenAI Whisper Models

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![OpenAI Whisper](https://img.shields.io/badge/AI-OpenAI%20Whisper-green) ![Status](https://img.shields.io/badge/Status-Evaluation%20Complete-success)

## Project Overview

This repository contains a full end-to-end pipeline for evaluating the performance of OpenAI's **Whisper Speech-to-Text (STT)** models. The project aims to benchmark various model sizes (from `tiny` to `large-v3` and `turbo`) against manually transcribed "ground truth" audio data.

A key focus of this evaluation is linguistic nuance, specifically handling **Bosnian, Croatian and Serbian** languages. The pipeline includes custom normalization scripts to normalize conversation and number-to-text transformation to ensure precise "apples-to-apples" algorithmic comparisons.

In conclusion we are testing eight WhisperAI models (`tiny`, `base`, `small`, `medium`, `large`, `large-v2`, `large-v3`, and `turbo`), on three audio files (see [The Test Dataset](#the-test-dataset)) using three languages.  

### Key Objectives
* **Transcribe** audio using the full suite of Whisper models.
* **Normalize** both machine and human output to remove formatting biases.
* **Evaluate** accuracy using Levenshtein Distance and Similarity Percentage.
* **Visualize** errors through detailed HTML difference reports and aggregated performance graphs.
* **Benchmark** Whisper against select commercial models.

## The Test Dataset

The evaluation was conducted using three distinct audio environments, designed to represent increasing levels of acoustic difficulty:

1.  **Monologue (Baseline):**
    * *Description:* Single speaker, focused on clarity and coherence of exposition with slight background noise.
    * *Purpose:* To test ideal conditions.
2.  **Dialogue (Intermediate):**
    * *Description:* Two participants interacting, featuring potential speech overlap and variations in dynamics.
    * *Purpose:* To test speaker separation and conversational flow.
3.  **Complex Scenario (Real-World Simulation):**
    * *Description:* Multiple participants with background sounds and a spontaneous conversational flow.
    * *Purpose:* This represents the "Stress Test," posing the greatest challenge for ASR systems.

| Type | Description | Difficulty | Source |
| :--- | :--- | :--- | :--- |
| **1. Monologue** | Single speaker, focused on clarity and coherence with slight background noise. | Low | [https://www.youtube.com/watch?v=gnScvTwCJtI](https://www.youtube.com/watch?v=gnScvTwCJtI) |
| **2. Dialogue** | Two participants interacting, featuring potential speech overlap and variations in dynamics. | Medium | Portion of audio that can be found at the following link [https://www.youtube.com/watch?v=PWdt88Ju4mI](https://www.youtube.com/watch?v=PWdt88Ju4mI) |
| **3. Complex** | Multiple participants, background sounds, and spontaneous conversational flow (Real-world simulation). | High | [https://www.youtube.com/watch?v=4Rte0gcNRTM](https://www.youtube.com/watch?v=4Rte0gcNRTM) |

---

## The Evaluation Pipeline

The project follows a strict data processing workflow to ensure scientific validity:

1.  **Audio Ingestion:** Raw audio files are processed.
2.  **Transcription:** Audio is passed through Whisper models (Local & Notebook-based).
3.  **Data Transformation:** Raw text is normalized (Interpunction removal, Lowercasing, Latinization, Number conversion).
4.  **Distance Calculation:** Levenshtein algorithms compare the Normalized Hypothesis (Whisper) vs. Normalized Reference (Human).
5.  **Reporting:** Generation of HTML visual diffs and summary statistics.

---

## Repository Structure & Contents

Below is a detailed breakdown of the repository's architecture.

### 1. `Audio_Transcription/`
This directory handles the core inference logic. It contains the scripts used to generate transcriptions and the resulting raw text files.

* **`python_kod_za_transkripciju.py`**: A local Python script optimized for running smaller Whisper models (`tiny`, `base`, `small`, `medium`) on standard hardware.
* **`transcription_large_models.ipynb`**: A Jupyter Notebook designed for heavy lifting, used to transcribe audio using larger, VRAM-intensive models (`large`, `large-v2`, `turbo`).
* **`transkript_results/`**: The storage vault for raw text.
    * *Original Manual Transcripts:* The human-verified ground truth.
    * *Whisper Model Results:* Raw outputs from every tested model version.

### 2. `Data_Transformation/`
To calculate an accurate Levenshtein distance, text must be stripped of stylistic differences. This directory contains the logic for this normalization.

* **`potpuna_normalizacija.py`**: The master normalization script.
* **normalization_logic**:
    * **Casing:** All text is converted to lowercase.
    * **Punctuation:** All periods, commas, and symbols are stripped.
    * **Transliteration:** Cyrillic characters are converted to Latin (critical for Serbian dataset consistency).
    * **Numeric Conversion:** Digits (e.g., "1988") are converted to words (e.g., "hiljadu devetsto osamdeset osam") to match oral pronunciation.
* **`original_finalno_normalizovano/`**: Normalized Ground Truth files.
* **`whisper_finalno_normalizovano/`**: Normalized Whisper Output files.

### 3. `Lehvenstein_Distance_Evaluation/`
This directory contains the mathematical evaluation engine.

* **`lehvenstein_distance_evaluation.py`**: Calculates the edit distance between the normalized files.
* **`rezultati_poredjenja_DMP_final/`**: The output results.
    * **HTML Visual Reports:** For *every* file pair, an HTML file is generated showing a visual "Diff." More on color coding in [Lehvenstein_Distance_Evaluation](https://github.com/HMByteSensei/WhisperAI-Evaluation/tree/main/Lehvenstein_Distance_Evaluation).
    * **`_sumarni_izvjestaj_poredjenja_DMP.txt`**: A comprehensive text summary of the entire batch.

#### Example Summary Entry:
> **Obrađeni fajl:** dijalog_Bosanski_base_transkript.txt
> **Master original:** dijalog_transkript.txt (normalizovan za poređenje)
> **Status:** Upoređeno
> **Levenshtein distanca:** 979
> **Procenat sličnosti:** 71.36%

### 4. `Graph_Results/`
Visual analytics of the evaluation data.

* **Whisper Comparison Graph:** Compares accuracy across `tiny`, `base`, `small`, `medium`, `large`, `large-v2` and `turbo`.
* **Commercial Benchmarks:** Compares Whisper against the following commercial solutions (all were set to use Bosanin language for transcription):
    * *TurboScribe*
    * *Assembly AI*
    * *Azure Speech-To-Text*
      
### 5. `Transcription_Enhancment/`
**Experimental LLM Post-Processing.** This directory investigates using Large Language Models (ChatGPT) to improve the accuracy of smaller, faster Whisper model.

* **Hypothesis:** Can post-processing `whisper-small` output with ChatGPT achieve accuracy comparable to `whisper-medium`?
* **Content:**
    * `ChatGPT_Prompts/`: The specific prompts used for A/B testing error correction.
    * `EnhancmentResults.png`: A data table showing the "Best Result" achieved across different prompting strategies and the net percentage improvement over the raw small model.

---

## Getting Started

### Prerequisites
* Python 3.8+
* FFmpeg (required for OpenAI Whisper)
* PyTorch
* OpenAI Whisper

### Installation

```bash
# Clone the repository
git clone [https://github.com/HMByteSensei/WhisperAI-Evaluation.git](https://github.com/HMByteSensei/WhisperAI-Evaluation.git)
```

# Install dependencies
pip install openai-whisper Levenshtein matplotlib
