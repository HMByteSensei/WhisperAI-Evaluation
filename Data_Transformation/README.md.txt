# Explanation

### Step 1: Run `text_normalizacija.py`

This script performs several normalization steps on the input text:

- Converts all characters to lowercase
- Removes punctuation
- Normalizes whitespace (replaces multiple spaces with a single space and trims leading/trailing spaces)

### Step 2: Run `num2words_konverter.py`

This script converts numbers in the text to their corresponding words.  
Since Python's built-in `num2words` library does not support all the specific number formats needed, some conversions are hardcoded.

### Additional Notes

- Running the first script may create additional folders.  
  For clarity, the output shown on [GitHub](https://github.com/HMByteSensei/WhisperAI-Evaluation/tree/main) has been cleaned to keep it simpler and more readable.
- You may need to update the directory paths in both scripts to match your local environment.
