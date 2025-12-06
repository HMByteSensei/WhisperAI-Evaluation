# Audio Transcription

This directory contains results of transcriptions and the scripts used to generate transcriptions from audio files using OpenAI's Whisper models. Due to hardware resource management, the transcription process was split between a Python script for lighter models and a Jupyter Notebook for heavier models.

## Scripts & Tools

| File | Purpose | Recommended For |
| :--- | :--- | :--- |
| **`python_kod_za_transkripciju.py`** | A standalone Python script for batch processing. | **Smaller Models** (`tiny`, `base`, `small`, `medium`). Ideal for quick local execution on standard CPUs/GPUs. |
| **`transcription_large_models.ipynb`** | An interactive Jupyter Notebook. | **Larger Models** (`large`, `large-v2`, `turbo`). Useful for managing VRAM usage and monitoring long-running tasks interactively. |

## Output Structure (`transkript_results/`)

All raw text outputs are saved here before normalization.

* **`original_transcripts/`**: Manual (My - Human) transcriptions.
* **`rezultati_20250517_202020/`**: Machine-generated transcripts labeled by:
    * audio files (e.g., `monolog`, `dijalog`, and `serija`)
    * language that were used (e.g., `_Bosanski`, `_Hrvatski` and `_Srpski`)
    * model size (e.g., `_base`, `_large-v2`).
