import whisper
import os
import time
from datetime import datetime

# --- KONFIGURACIJA ---
# Promijenite ovo listom imena vaših audio/video fajlova, kod mene su sljedeći
AUDIO_FILES = ["monolog.mp3", "dijalog.mp3", "serija.mp3"]

# Modeli koje želite testirati
MODEL_SIZES = ["tiny", "base", "small", "medium"]

# Jezici nad kojim ću testirati
LANGUAGES = {
    "Bosanski": "bs",
    "Hrvatski": "hr",
    "Srpski": "sr"
}

# Naziv poddirektorija za spremanje rezultata
TIMESTAMP_DIR = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_BASE_DIRECTORY = "transkript_rezultati"
OUTPUT_DIRECTORY = os.path.join(OUTPUT_BASE_DIRECTORY, f"rezultati_{TIMESTAMP_DIR}")
# --- KRAJ KONFIGURACIJE ---

def format_time(seconds):
    """Formatira vrijeme u minute i sekunde."""
    if seconds < 0: # U slučaju greške
        return "N/A"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.2f}s"

def save_result_files(output_dir, base_filename, lang_name, model_name,
                      transcription_time_seconds, formatted_time, transcription_text, error_occurred=False):
    """Sprema rezultate transkripcije ili grešku u odgovarajuće fajlove."""
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if error_occurred:
            error_filename = f"{base_filename}_{lang_name}_{model_name}_GREŠKA.txt"
            error_filepath = os.path.join(output_dir, error_filename)
            with open(error_filepath, 'w', encoding='utf-8') as f_error:
                f_error.write(f"Došlo je do greške tokom transkripcije.\n")
                f_error.write(f"Audio fajl: {base_filename}\n")
                f_error.write(f"Model: {model_name}\n")
                f_error.write(f"Jezik: {lang_name}\n")
                f_error.write(f"Poruka greške: {transcription_text}\n") # transcription_text ovdje sadrži poruku greške
            print(f"      Informacije o grešci spremljene u: {error_filepath}")
        else:
            time_filename = f"{base_filename}_{lang_name}_{model_name}_vrijeme.txt"
            transcript_filename = f"{base_filename}_{lang_name}_{model_name}_transkript.txt"

            time_filepath = os.path.join(output_dir, time_filename)
            transcript_filepath = os.path.join(output_dir, transcript_filename)

            # Spremanje vremena
            with open(time_filepath, 'w', encoding='utf-8') as f_time:
                f_time.write(f"Audio fajl: {base_filename}\n")
                f_time.write(f"Model: {model_name}\n")
                f_time.write(f"Jezik: {lang_name}\n")
                f_time.write(f"Vrijeme transkripcije (s): {transcription_time_seconds:.2f}\n")
                f_time.write(f"Formatirano vrijeme: {formatted_time}\n")
            print(f"      Vrijeme transkripcije spremljeno u: {time_filepath}")

            # Spremanje transkripta
            with open(transcript_filepath, 'w', encoding='utf-8') as f_transcript:
                f_transcript.write(transcription_text)
            print(f"      Transkript spremljen u: {transcript_filepath}")

    except IOError as e:
        print(f"      GREŠKA pri spremanju fajla za {base_filename}_{lang_name}_{model_name}: {e}")
    except Exception as e:
        print(f"      Nepoznata GREŠKA pri spremanju fajla za {base_filename}_{lang_name}_{model_name}: {e}")


def main():
    # Kreiranje glavnog output direktorija ako ne postoji
    if not os.path.exists(OUTPUT_BASE_DIRECTORY):
        os.makedirs(OUTPUT_BASE_DIRECTORY)
        print(f"Kreiran osnovni direktorij za rezultate: {OUTPUT_BASE_DIRECTORY}")

    # Kreiranje jedinstvenog poddirektorija za ovaj run
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    print(f"Rezultati će biti spremljeni u: {OUTPUT_DIRECTORY}")


    print("\n--- Pokretanje procesa transkripcije ---")

    for audio_file_full_path in AUDIO_FILES:
        if not os.path.exists(audio_file_full_path):
            print(f"GREŠKA: Fajl '{audio_file_full_path}' nije pronađen. Preskačem.")
            continue

        # Dobijanje imena fajla bez ekstenzije za korištenje u imenima output fajlova
        audio_filename_base = os.path.splitext(os.path.basename(audio_file_full_path))[0]
        print(f"\n>>> Obrada fajla: {audio_file_full_path} (Baza za output: {audio_filename_base}) <<<")

        for model_name in MODEL_SIZES:
            print(f"  Učitavanje modela: {model_name}...")
            model = None # Resetiraj model
            try:
                model = whisper.load_model(model_name)
                print(f"  Model '{model_name}' uspješno učitan (device: {'GPU' if model.device.type == 'cuda' else 'CPU'}).")
            except Exception as e:
                print(f"    GREŠKA pri učitavanju modela {model_name}: {e}")
                print(f"    Preskačem sve jezike za model '{model_name}' i fajl '{audio_filename_base}'.")
                # Zabilježi grešku za ovaj model i audio fajl (može ići u poseban log fajl)
                error_msg = f"GREŠKA pri učitavanju modela {model_name} za fajl {audio_filename_base}: {e}"
                save_result_files(OUTPUT_DIRECTORY, audio_filename_base, "N/A", model_name,
                                  -1.0, "N/A", error_msg, error_occurred=True)
                continue # Preskoči na sljedeći model

            for lang_display_name, lang_code in LANGUAGES.items():
                print(f"    Transkribiranje koristeći model '{model_name}' na jeziku '{lang_display_name}' ({lang_code})...")

                transcription_text = "GREŠKA PRI TRANSKRIPCIJI"
                transcription_time_seconds = -1.0
                error_in_transcription = False

                try:
                    start_time = time.time()
                    result = model.transcribe(audio_file_full_path, language=lang_code, task="transcribe")
                    end_time = time.time()

                    transcription_time_seconds = end_time - start_time
                    transcription_text = result["text"].strip()

                    print(f"      Vrijeme transkripcije: {format_time(transcription_time_seconds)}")

                except Exception as e:
                    print(f"      GREŠKA tokom transkripcije sa modelom '{model_name}' i jezikom '{lang_display_name}': {e}")
                    transcription_text = f"GREŠKA: {e}"
                    error_in_transcription = True
                
                # Naziv jezika za fajl će biti npr. "Bosanski", "Hrvatski", "Srpski"
                save_result_files(
                    OUTPUT_DIRECTORY,
                    audio_filename_base,
                    lang_display_name, # Koristimo čitljivo ime jezika za ime fajla
                    model_name,
                    transcription_time_seconds,
                    format_time(transcription_time_seconds),
                    transcription_text,
                    error_occurred=error_in_transcription
                )

            # Opcionalno: oslobodite memoriju modela ako imate vrlo malo RAM/VRAM-a
            # i ako obrađujete mnogo fajlova. Ovo će usporiti proces jer
            # će se model morati ponovo učitavati za svaki novi audio fajl.
            # import gc; import torch
            # if model: del model
            # gc.collect()
            # if torch.cuda.is_available():
            #    torch.cuda.empty_cache()

    print(f"\n--- Transkripcija završena. ---")
    print(f"Svi rezultati su spremljeni u direktorij: {OUTPUT_DIRECTORY}")
    print("\nSve gotovo!")

if __name__ == "__main__":
    main()