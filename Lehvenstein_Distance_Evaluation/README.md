# Levenshtein Distance Evaluation

This directory contains the evaluation logic and the detailed results of the comparison between the normalized original text and the normalized Whisper transcriptions.

## The Script: `lehvenstein_distance_evaluation.py`

This script serves as the evaluation engine. When executed, it **automatically generates** the `rezultati_poredjenja_DMP_final` directory and populates it with the results.

**It performs the following actions automatically:**
1.  Reads the normalized text files.
2.  Calculates the edit distance.
3.  **Creates** the output folder (if it doesn't exist).
4.  Generates the visual HTML reports and the text summary.

## Metrics Used

* **Levenshtein Distance:** The minimum number of single-character edits (insertions, deletions, or substitutions) required to change the Whisper transcript into the Original transcript. Lower is better.
* **Similarity Percentage:** A derived metric indicating how close the match is (0% to 100%).

## Output Results: `rezultati_poredjenja_DMP_final`

This folder is the direct output of the script mentioned above.

### 1. HTML Visual Reports
For every file pair, an HTML file is generated. These provide a "diff" view to visualize exactly where the model failed.

* **HTML Structure:** The files present a combined view of both transcripts to highlight differences inline.
* **Color Coding Key:**
    * **No Color (Standard Text):** **Matches.** The Whisper transcript perfectly matches the Ground Truth original (my human) transcript.
    * <span style="color:green">**Green:**</span> **Hallucinations / Insertions.** Words that Whisper included/added that **do not exist** in the original audio (or were interpreted incorrectly).
    * <span style="color:red">**Red:**</span> **Missed Content / Deletions.** Words that exist in the original human transcript but are **missing** from the Whisper transcript.
      
### 2. Summary Report (`_sumarni_izvjestaj_poredjenja_DMP.txt`)
A text file containing the aggregated statistics for the entire batch.

**Example Entry:**
```text
Obrađeni fajl: dijalog_Bosanski_base_transkript.txt
Master original: dijalog_transkript.txt (normalizovan za poređenje)
Status: Upoređeno
Levenshtein distanca: 979
Procenat sličnosti: 71.36%
```
