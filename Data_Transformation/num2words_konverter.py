import os
import re
import shutil

# --- Funkcija za zamjenu samo hardkodiranih brojeva, jer num2words nema implementirane
#     brojeve koji nama trebaju ---

def convert_specific_hardcoded_numbers(text_content):
    """
    Zamjenjuje samo specifične hardkodirane brojeve njihovim riječima.
    Ne dira mala/velika slova, interpunkciju ili druge brojeve.
    """
    if not text_content:
        return ""

    hardcoded_numbers_map = {
        "15": "petnaest",
        "200": "dvjesto", # ili "dvije stotine"?
        "185": "sto osamdeset pet",
        "25": "dvadeset pet",
        "50": "pedeset",
        "21": "dvadeset jedan",
        "27": "dvadeset sedam",
        "23": "dvadeset tri",
        "2008": "dvije hiljade osam"
        # Dodajte ili izmijenite po potrebi. Ključ je string broja.
    }

    # Kreiramo funkciju koja će biti pozvana za svaki pronađeni broj
    def replace_match(match):
        number_str = match.group(0) # Uhvaćeni string (broj)
        
        # Provjeri da li je ovaj broj u našoj mapi
        if number_str in hardcoded_numbers_map:
            replacement_word = hardcoded_numbers_map[number_str]
            # print(f"    Zamjenjujem '{number_str}' sa '{replacement_word}'") # DEBUG
            return replacement_word
        else:
            # Ako broj nije u mapi, vrati ga nepromijenjenog
            return number_str 

    # Regex koji pronalazi SAMO CIJELE RIJEČI koje su brojevi.
    # Ovo je važno da ne bismo mijenjali npr. "150" ako samo "15" i "50" imamo u mapi.
    # Iteriramo kroz ključeve mape (brojeve) sortirane po dužini, od najdužeg ka najkraćem.
    # Ovo pomaže da se izbjegnu problemi gdje bi kraći broj (npr. "20") bio zamijenjen
    # unutar dužeg broja (npr. "2008") prije nego što duži broj dobije šansu.
    
    # Prvo, napravimo kopiju teksta na kojoj ćemo raditi zamjene
    processed_text = text_content

    # Sortiraj ključeve (brojeve) po dužini, opadajuće, da se duži brojevi prvo zamijene
    # Npr. "2008" prije "200" ili "8"
    # Ovo je bitno ako bismo imali preklapajuće brojeve u mapi, npr. "20" i "200".
    # U mom (HM) skupu nema ovakvih brojeva, ali je podešeno ako nekome bude trebalo više
    sorted_number_keys = sorted(hardcoded_numbers_map.keys(), key=len, reverse=True)

    for num_key in sorted_number_keys:
        word_value = hardcoded_numbers_map[num_key]
        # Koristimo \b da osiguramo da mijenjamo samo cijele brojeve
        # num_key mora biti string, što jeste jer su ključevi rječnika stringovi
        # re.escape(num_key) nije striktno potrebno jer su brojevi, ali je sigurnije
        regex_pattern = r'\b' + re.escape(num_key) + r'\b'
        processed_text = re.sub(regex_pattern, word_value, processed_text)
        
    return processed_text


# --- Funkcija za obradu foldera ---

def process_folder_for_specific_numbers(input_folder_path, output_folder_path):
    """
    Obrađuje sve .txt fajlove iz ulaznog foldera, primjenjuje zamjenu samo
    specifičnih hardkodiranih brojeva i snima ih u izlazni folder.
    """
    if not os.path.exists(input_folder_path):
        print(f"Greška: Ulazni folder '{input_folder_path}' ne postoji.")
        return
    
    if os.path.exists(output_folder_path):
        print(f"Info: Izlazni folder '{output_folder_path}' već postoji. Postojeći fajlovi sa istim imenom će biti prepisani.")
    else:
        os.makedirs(output_folder_path)
        print(f"Kreiran izlazni folder: '{output_folder_path}'")

    processed_files_count = 0
    failed_files_count = 0

    for filename in os.listdir(input_folder_path):
        if filename.endswith(".txt"):
            input_file = os.path.join(input_folder_path, filename)
            output_file = os.path.join(output_folder_path, filename) 

            # print(f"--- Obrada fajla: {filename} ---") # Smanjujem output
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

                # Primjena konverzije samo za specifične brojeve
                modified_content = convert_specific_hardcoded_numbers(content)

                # Snimanje modifikovanog sadržaja u UTF-8
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                processed_files_count += 1

            except Exception as e:
                print(f"  Neočekivana GREŠKA pri obradi fajla '{filename}': {type(e).__name__} - {e}")
                traceback.print_exc() 
                failed_files_count += 1
                
    print(f"\nObrada foldera '{input_folder_path}' završena.")
    print(f"Ukupno fajlova obrađeno: {processed_files_count}")
    print(f"Broj neuspješnih obrada: {failed_files_count}")


# --- Glavni dio skripte ---
if __name__ == "__main__":
    folders_to_process_config = [
        {
            "input": "original_finalno_normalizovano", 
            "output": "original_samo_brojevi_zamijenjeni" 
        },
        {
            "input": "whisper_finalno_normalizovano", 
            "output": "whisper_samo_brojevi_zamijenjeni"
        }
    ]
    # PAŽNJA: Riječi za brojeve su definisane unutar funkcije convert_specific_hardcoded_numbers.
    # Ažurirajte ih tamo prema vašem jeziku/stilu.

    print("Pokrećem skriptu za zamjenu samo specifičnih hardkodiranih brojeva...")
    for folder_config in folders_to_process_config:
        input_dir = folder_config["input"]
        output_dir = folder_config["output"]
        
        print(f"\n>>> Pokrećem obradu za ulazni folder: '{input_dir}' >>>")
        print(f"    Izlazni folder će biti: '{output_dir}'")
        
        process_folder_for_specific_numbers(input_dir, output_dir)
        # print(f"<<< Završena obrada za '{input_dir}' <<<\n")
    
    print("\nSvi konfigurisani folderi su obrađeni.")