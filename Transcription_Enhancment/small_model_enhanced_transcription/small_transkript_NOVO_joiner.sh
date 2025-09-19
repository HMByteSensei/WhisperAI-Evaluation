#!/bin/bash

# fajl u koji se sve spaja
output="svi_transkripti.txt"

# isprazni izlazni fajl ako već postoji
> "$output"

# redoslijed fajlova
files=(
  "dijalog_Bosanski_ChatGPT_small_transkript.txt"  
  "dijalog_Hrvatski_ChatGPT_small_transkript.txt" 
  "dijalog_Srpski_ChatGPT_small_transkript.txt"    
  "monolog_Bosanski_ChatGPT_small_transkript.txt"  
  "monolog_Srpski_ChatGPT_small_transkript.txt"
  "monolog_Hrvatski_ChatGPT_small_transkript.txt"
  "serija_Bosanski_ChatGPT_small_transkript.txt"
  "serija_Hrvatski_ChatGPT_small_transkript.txt"
  "serija_Srpski_ChatGPT_small_transkript.txt"
)

for f in "${files[@]}"; do
  echo "$f" >> "$output"
  echo "---------------------------------------------------------------------------------------------------------" >> "$output"
  cat "$f" >> "$output"
  echo -e "\n---------------------------------------------------------------------------------------------------------\n-----------------------------------------------------------------------------------------------------------------\n" >> "$output"
done

