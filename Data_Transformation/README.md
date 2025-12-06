# Data Transformation & Normalization

This directory handles the pre-processing of text data. To ensure a scientifically accurate comparison using Levenshtein distance, both the human transcripts and the Whisper AI transcripts must be brought to a "common denominator" to remove formatting biases.

## The Script: `potpuna_normalizacija.py`

This script takes raw text files and applies a strict normalization rules.

## Normalization Rules

The script performs the following transformations, specifically tuned for **Bosnian/Croatian/Serbian** language evaluation:

1.  **Lowercase:** All text is converted to lowercase to ignore capitalization errors.
2.  **Punctuation Removal:** All commas, periods, question marks, and other symbols are stripped.
3.  **Transliteration (Cyrillic to Latin):**
    * Since Whisper often outputs Cyrillic for Serbian audio, and my(human) transcripts is in Latin, all text is converted into **Latin** letters to allow character-by-character comparison using online tools.
4.  **Number Conversion (Digits to Text):**
    * *Input:* "100"
    * *Output:* "sto"
    * *Reasoning:* If a human types "100" and Whisper types "sto", Levenshtein distance considers them completely different. Converting numbers to their phonetic word representation solves this.

## Output Directories

| Directory | Content |
| :--- | :--- |
| **`original_finalno_normalizovano/`** | The "Ground Truth" text, fully normalized. |
| **`whisper_finalno_normalizovano/`** | The Whisper model outputs, fully normalized and ready for the evaluation algorithm. |
