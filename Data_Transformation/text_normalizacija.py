import os
import re
from num2words import num2words # Zahtijeva: pip install num2words
import shutil

# --- Funkcije za normalizaciju teksta ---

def convert_numbers_to_words(text, lang='hr'):
    """
    Pretvara sve brojeve u tekstu u riječi.
    Koristi 'hr' kao podrazumijevani jezik, što je dobra aproksimacija 
    za bosanski/srpski za brojeve.
    """
    def replace_match(match):
        number_str = match.group(0)
        try:
            # Provjera da li je broj predugačak, num2words može imati limite
            if len(number_str) > 15: # Proizvoljan limit, prilagodite ako treba
                return number_str # Vrati originalni ako je predugačak
            number_int = int(number_str)
            return num2words(number_int, lang=lang)
        except ValueError: # Ako nije validan int (npr. ako regex uhvati nešto čudno)
            return number_str 
        except Exception as e: # Bilo koja druga greška iz num2words
            # print(f"  Greška pri konverziji broja '{number_str}' u riječi: {e}")
            return number_str # Vrati originalni broj u slučaju greške
    # Regex koji pronalazi samo cjelobrojne brojeve
    return re.sub(r'\b\d+\b', replace_match, text) # \b osigurava da su cijele riječi (brojevi)

def remove_punctuation(text, punctuation_chars=".,?!"):
    """
    Uklanja specificirane interpunkcijske znakove iz teksta.
    """
    if not punctuation_chars:
        return text
    
    # Budući su znakovi jednostavni, možemo ih direktno staviti u klasu karaktera
    regex_pattern = f"[{punctuation_chars}]"
    return re.sub(regex_pattern, '', text)

def fully_normalize_text_content(text_content):
    """
    Primjenjuje sve korake normalizacije na dati string:
    1. Mala slova
    2. Brojevi u riječi
    3. Uklanjanje interpunkcije
    4. Normalizacija razmaka (višestruki u jedan, trimovanje)
    """
    if not text_content:
        return ""
    
    # 1. Mala slova
    text_lower = text_content.lower()
    
    # 2. Brojevi u riječi
    text_numbers_as_words = convert_numbers_to_words(text_lower)
    
    # 3. Uklanjanje interpunkcije (npr. ",", ".", "?", "!")
    # Možete proširiti string punctuation_to_remove po potrebi
    punctuation_to_remove = ".,?!" 
    text_no_punctuation = remove_punctuation(text_numbers_as_words, punctuation_to_remove)
    
    # 4. Normalizacija razmaka
    # Zamjena višestrukih whitespace karaktera (uključujući nove redove) jednim razmakom
    text_normalized_whitespace = re.sub(r'\s+', ' ', text_no_punctuation)
    return text_normalized_whitespace.strip() # Ukloni vodeće/prateće razmake

# --- Funkcija za obradu foldera ---

def process_folder_for_full_normalization(input_folder_path, output_folder_path):
    """
    Obrađuje sve .txt fajlove iz ulaznog foldera, primjenjuje potpunu normalizaciju
    i snima ih u izlazni folder.
    """
    if not os.path.exists(input_folder_path):
        print(f"Greška: Ulazni folder '{input_folder_path}' ne postoji.")
        return
    
    if os.path.exists(output_folder_path):
        print(f"Info: Izlazni folder '{output_folder_path}' već postoji. Postojeći fajlovi sa istim imenom će biti prepisani.")
        # Opciono za obrisati folder ako želite čist start
        # shutil.rmtree(output_folder_path)
        # os.makedirs(output_folder_path)
        # print(f"Info: Postojeći izlazni folder '{output_folder_path}' je obrisan i ponovo kreiran.")
    else:
        os.makedirs(output_folder_path)
        print(f"Kreiran izlazni folder: '{output_folder_path}'")

    processed_files_count = 0
    failed_files_count = 0

    for filename in os.listdir(input_folder_path):
        if filename.endswith(".txt"):
            input_file = os.path.join(input_folder_path, filename)
            output_file = os.path.join(output_folder_path, filename) # Isto ime u novom folderu

            print(f"--- Obrada fajla: {filename} ---")
            try:
                # Čitanje fajla (pokušaj sa više enkodinga)
                content = None
                encodings_to_try = ['utf-8', 'cp1250', 'latin-1']
                for enc in encodings_to_try:
                    try:
                        with open(input_file, 'r', encoding=enc) as f:
                            content = f.read()
                        # print(f"  Pročitan sa {enc}")
                        break 
                    except UnicodeDecodeError:
                        continue 
                
                if content is None:
                    print(f"  Greška: Nije moguće pročitati fajl '{filename}' ni sa jednim od pokušanih enkodinga.")
                    failed_files_count += 1
                    continue

                # Potpuna normalizacija sadržaja
                normalized_content = fully_normalize_text_content(content)

                # Snimanje normalizovanog sadržaja u UTF-8
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(normalized_content)
                
                print(f"  Fajl '{filename}' uspješno normalizovan i sačuvan u '{output_folder_path}'.")
                processed_files_count += 1

            except Exception as e:
                print(f"  Neočekivana greška pri obradi fajla '{filename}': {e}")
                failed_files_count += 1
        print("--- Završena obrada fajla ---")
                
    print("\nNormalizacija završena.")
    print(f"Ukupno fajlova obrađeno: {processed_files_count}")
    print(f"Broj neuspješnih obrada: {failed_files_count}")


# --- Glavni dio skripte ---
if __name__ == "__main__":
    # --- KONFIGURACIJA ---
    # Lista ulaznih foldera koje treba obraditi
    folders_to_process_config = [
        {
            "input": "..\\Audio_Transcription\\transkript_results\\original_transkript", # Folder sa vašim master originalima
            "output": "original_finalno_normalizovano" # Novi folder za super-normalizovane mastere
        },
        {
            "input": "..\\Audio_Transcription\\transkript_results\\rezultati_20250517_202020", # Folder sa Whisper transkriptima
            "output": "whisper_finalno_normalizovano" # Novi folder za super-normalizovane Whisper transkripte
        }
        # Možete dodati još foldera ako je potrebno
    ]
    # --- KRAJ KONFIGURACIJE ---

    # Provjera potrebnih biblioteka
    try:
        from num2words import num2words
    except ImportError:
        print("Greška: Biblioteka 'num2words' nije instalirana.")
        print("Molimo instalirajte je sa: pip install num2words")
        exit()

    for folder_config in folders_to_process_config:
        input_dir = folder_config["input"]
        output_dir = folder_config["output"]
        
        print(f"\n>>> Pokrećem normalizaciju za ulazni folder: '{input_dir}' >>>")
        print(f"    Izlazni folder će biti: '{output_dir}'")
        
        process_folder_for_full_normalization(input_dir, output_dir)
        print(f"<<< Završena normalizacija za '{input_dir}' <<<\n")
    
    print("Svi konfigurisani folderi su obrađeni.")