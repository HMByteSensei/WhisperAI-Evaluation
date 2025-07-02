import os
import re
import shutil
import traceback
try:
    from num2words import num2words
except ImportError:
    print("GREŠKA: Biblioteka 'num2words' nije instalirana.")
    print("Molimo instalirajte je sa: pip install num2words")
    exit()

# --- FUNKCIJE ZA POJEDINAČNE KORAKE NORMALIZACIJE ---

def convert_specific_hardcoded_numbers(text_content, number_map):
    """
    Zamjenjuje samo specifične, unaprijed definisane brojeve njihovim riječima.
    """
    if not text_content or not number_map:
        return text_content
    
    sorted_number_keys = sorted(number_map.keys(), key=len, reverse=True)
    
    processed_text = text_content
    for num_key in sorted_number_keys:
        word_value = number_map[num_key]
        regex_pattern = r'\b' + re.escape(num_key) + r'\b'
        processed_text = re.sub(regex_pattern, word_value, processed_text)
        
    return processed_text

def convert_remaining_numbers_to_words(text, lang='hr'):
    """
    Pretvara SVE preostale brojeve u tekstu u riječi koristeći num2words.
    """
    def replace_match(match):
        number_str = match.group(0)
        try:
            return num2words(int(number_str), lang=lang)
        except Exception:
            return number_str
            
    return re.sub(r'\b\d+\b', replace_match, text)

def remove_punctuation(text, punctuation_chars):
    """
    Uklanja SVE specificirane interpunkcijske znakove iz teksta.
    """
    if not punctuation_chars:
        return text
    # re.escape osigurava da se specijalni karakteri (kao što su -, [, ]) tretiraju ispravno
    return re.sub(f"[{re.escape(punctuation_chars)}]", '', text)


# --- GLAVNA FUNKCIJA - KOMPLETNA NORMALIZACIJA ---

def fully_normalize_text(text_content, hardcoded_map, punctuation_to_remove):
    """
    Primjenjuje sve korake normalizacije na dati string u ispravnom redoslijedu.
    """
    if not text_content:
        return ""
    
    # Korak 1: Sve u mala slova
    text_lower = text_content.lower()
    
    # Korak 2: Zamjena specifičnih, hardkodiranih brojeva (VAŠ PRIORITET)
    text_hardcoded_replaced = convert_specific_hardcoded_numbers(text_lower, hardcoded_map)
    
    # Korak 3: Zamjena svih preostalih brojeva koristeći num2words
    text_all_numbers_replaced = convert_remaining_numbers_to_words(text_hardcoded_replaced)
    
    # <<< IZMJENA: Sada koristi proširenu listu znakova za uklanjanje
    # Korak 4: Uklanjanje interpunkcije
    text_no_punctuation = remove_punctuation(text_all_numbers_replaced, punctuation_to_remove)
    
    # Korak 5: Normalizacija svih vrsta razmaka (višestruki, novi redovi) u jedan razmak
    text_normalized_whitespace = re.sub(r'\s+', ' ', text_no_punctuation)
    
    return text_normalized_whitespace.strip()


# --- FUNKCIJA ZA OBRADU CIJELOG FOLDERA ---

def process_folder(input_folder_path, output_folder_path, hardcoded_map, punctuation_to_remove):
    """
    Obrađuje sve .txt fajlove iz ulaznog foldera, primjenjuje potpunu normalizaciju
    i snima ih u izlazni folder.
    """
    if not os.path.exists(input_folder_path):
        print(f"Greška: Ulazni folder '{input_folder_path}' ne postoji.")
        return
    
    if os.path.exists(output_folder_path):
        print(f"Info: Izlazni folder '{output_folder_path}' već postoji. Postojeći fajlovi će biti prepisani.")
    else:
        os.makedirs(output_folder_path)
        print(f"Kreiran izlazni folder: '{output_folder_path}'")

    processed_files_count = 0
    failed_files_count = 0

    for filename in os.listdir(input_folder_path):
        if filename.endswith(".txt"):
            input_file = os.path.join(input_folder_path, filename)
            output_file = os.path.join(output_folder_path, filename)

            try:
                content = None
                encodings_to_try = ['utf-8', 'cp1250', 'latin-1']
                for enc in encodings_to_try:
                    try:
                        with open(input_file, 'r', encoding=enc) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    print(f"  Greška: Nije moguće pročitati fajl '{filename}' ni sa jednim od pokušanih enkodinga.")
                    failed_files_count += 1
                    continue

                # <<< IZMJENA: Proslijeđuje se lista znakova za uklanjanje
                normalized_content = fully_normalize_text(content, hardcoded_map, punctuation_to_remove)

                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(normalized_content)
                
                processed_files_count += 1

            except Exception as e:
                print(f"  Neočekivana GREŠKA pri obradi fajla '{filename}': {type(e).__name__} - {e}")
                traceback.print_exc()
                failed_files_count += 1
                
    print(f"\nObrada foldera '{input_folder_path}' završena.")
    print(f"  - Uspješno obrađeno: {processed_files_count} fajlova.")
    print(f"  - Neuspješno: {failed_files_count} fajlova.")


# --- GLAVNI DIO SKRIPTE (POKRETANJE) ---
if __name__ == "__main__":
    
    # --- JEDINO MJESTO ZA KONFIGURACIJU ---

    # 1. Definišite vaše specifične brojeve koje želite ručno zamijeniti
    HARDCODED_NUMBERS_MAP = {
        "15": "petnaest",
        "200": "dvjesto",
        "185": "sto osamdeset pet",
        "25": "dvadeset pet",
        "50": "pedeset",
        "21": "dvadeset jedan",
        "27": "dvadeset sedam",
        "23": "dvadeset tri",
        "2008": "dvije hiljade osam"
    }
    
    # <<< GLAVNA IZMJENA OVDJE >>>
    # 2. Definišite SVE znakove interpunkcije koje želite ukloniti.
    #    Dodao sam zagrade, apostrofe, navodnike, crtice, itd.
    PUNCTUATION_TO_REMOVE = ".,?!()'\"-:;"
    
    # 3. Definišite koje foldere želite obraditi
    FOLDERS_TO_PROCESS_CONFIG = [
        {
            "input": "original_obradjeno",
            "output": "original_finalno_normalizovano"
        },
        {
            "input": "rezultati_20250517_202020_obradjeno",
            "output": "whisper_finalno_normalizovano"
        }
    ]
    
    # --- KRAJ KONFIGURACIJE ---


    print("="*50)
    print("Pokrećem skriptu za potpunu normalizaciju teksta...")
    print("="*50)

    for folder_config in FOLDERS_TO_PROCESS_CONFIG:
        input_dir = folder_config["input"]
        output_dir = folder_config["output"]
        
        print(f"\n>>> Pokrećem obradu za ulazni folder: '{input_dir}'")
        print(f"    Izlazni folder će biti: '{output_dir}'")
        
        # <<< IZMJENA: Proslijeđujemo novu konfiguraciju funkciji
        process_folder(input_dir, output_dir, HARDCODED_NUMBERS_MAP, PUNCTUATION_TO_REMOVE)
    
    print("\nSvi konfigurisani folderi su obrađeni.")