import os
import Levenshtein 
from diff_match_patch import diff_match_patch
import re # OSTAJE - Neophodan za normalizaciju razmaka

# --- Pomoćne funkcije ---

def read_file_content_lines(file_path, filename_for_error_msg="fajla"):
    """
    Čita sadržaj fajla i vraća ga kao listu linija.
    """
    encodings_to_try = ['utf-8', 'cp1250', 'latin-1']
    for enc in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.readlines()
        except UnicodeDecodeError:
            pass
        except Exception as e:
            print(f"    Greška pri čitanju fajla '{filename_for_error_msg}' ({file_path}) sa {enc}: {type(e).__name__} - {e}")
            return None
    print(f"  Greška: Nije moguće pročitati fajl '{filename_for_error_msg}'.")
    return None

def normalize_text_for_comparison(text_lines_list):
    """
    Finalno priprema tekst za poređenje: spaja linije i unificira sve razmake.
    Ovo je ključno čak i ako je sadržaj (slova, brojevi) već normalizovan.
    """
    if not text_lines_list:
        return ""
    
    full_text = "".join(text_lines_list)
    # KLJUČNI KORAK: Sve sekvence praznog prostora (razmaci, prijelomi reda)
    # zamjenjuje jednim jedinim razmakom. Ovo je neophodno za ispravno poređenje.
    processed_text = re.sub(r'\s+', ' ', full_text)
    return processed_text.lower().strip()

def get_master_original_filename(processed_filename):
    """
    Određuje ime master originalnog fajla na osnovu imena obrađenog fajla.
    """
    if processed_filename.startswith("dijalog_"):
        return "originalni dijalog.txt"
    elif processed_filename.startswith("monolog_"):
        return "originalni monolog.txt"
    elif processed_filename.startswith("serija_"):
        return "originalni serija.txt"
    return None

# --- Glavna funkcija za poređenje ---

def compare_processed_to_master_originals_dmp(master_originals_folder, 
                                            processed_folder, 
                                            comparison_output_folder):
    """
    Upoređuje dva foldera sa već potpuno normalizovanim transkriptima.
    """
    if not os.path.exists(master_originals_folder):
        print(f"Greška: Folder sa master originalima '{master_originals_folder}' ne postoji.")
        return
    if not os.path.exists(processed_folder):
        print(f"Greška: Obrađeni folder '{processed_folder}' ne postoji.")
        return

    if not os.path.exists(comparison_output_folder):
        os.makedirs(comparison_output_folder)
        print(f"Kreiran izlazni folder za poređenje: '{comparison_output_folder}'")
    else:
        print(f"Info: Izlazni folder za poređenje '{comparison_output_folder}' već postoji.")

    summary_report = []
    dmp = diff_match_patch() 

    # Učitavanje i priprema master originala
    master_originals_normalized_text = {}
    master_files_to_find = ["originalni dijalog.txt", "originalni monolog.txt", "originalni serija.txt"]
    
    for master_filename in master_files_to_find:
        master_file_path = os.path.join(master_originals_folder, master_filename)
        if os.path.exists(master_file_path):
            content_lines = read_file_content_lines(master_file_path, master_filename)
            if content_lines:
                master_originals_normalized_text[master_filename] = normalize_text_for_comparison(content_lines)
                print(f"Master original '{master_filename}' uspješno učitan i normalizovan.")
            else:
                print(f"UPOZORENJE: Nije moguće pročitati sadržaj mastera '{master_filename}'.")
        else:
            print(f"UPOZORENJE: Master fajl '{master_filename}' nije pronađen u '{master_originals_folder}'.")
    
    if not master_originals_normalized_text:
        print("Greška: Nijedan master fajl nije uspješno učitan. Prekidam.")
        return
    
    for processed_filename in os.listdir(processed_folder):
        if "_transkript.txt" not in processed_filename:
            continue

        master_original_name = get_master_original_filename(processed_filename)

        if not master_original_name or master_original_name not in master_originals_normalized_text:
            print(f"UPOZORENJE: Nije pronađen par za '{processed_filename}'. Preskačem.")
            continue
        
        print(f"\n--- Poređenje: '{processed_filename}' sa master originalom '{master_original_name}' ---")
        
        master_text_to_compare = master_originals_normalized_text[master_original_name]
        
        processed_file_path = os.path.join(processed_folder, processed_filename)
        processed_lines = read_file_content_lines(processed_file_path, processed_filename) 

        if processed_lines is None:
            print(f"  Nije moguće pročitati '{processed_filename}'. Preskačem.")
            continue
            
        processed_text_to_compare = normalize_text_for_comparison(processed_lines)

        distance = Levenshtein.distance(master_text_to_compare, processed_text_to_compare)
        max_len = max(len(master_text_to_compare), len(processed_text_to_compare))
        similarity_percentage = (1 - (distance / max_len if max_len > 0 else 0)) * 100

        print(f"  Levenshtein distanca (nakon normalizacije): {distance}")
        print(f"  Procenat sličnosti: {similarity_percentage:.2f}%")
        
        summary_report.append({
            "processed_file": processed_filename,
            "master_file": master_original_name + " (normalizovan za poređenje)",
            "status": "Upoređeno",
            "lev_distance": distance,
            "similarity_percent": f"{similarity_percentage:.2f}%"
        })
        
        diffs = dmp.diff_main(master_text_to_compare, processed_text_to_compare)
        dmp.diff_cleanupSemantic(diffs) 
        html_diff_output = dmp.diff_prettyHtml(diffs)

        # <<< VRATIO SAM STARI, DETALJNI HTML FORMAT >>>
        full_html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Poređenje (DMP): {master_original_name} vs {processed_filename}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.5; }}
                h1 {{ text-align: center; color: #333; }}
                .info {{ background-color: #f9f9f9; border: 1px solid #ddd; padding: 10px; margin-bottom: 20px; border-radius: 5px; }}
                .diff-container {{ 
                    border: 1px solid #ccc; 
                    padding: 20px; 
                    white-space: pre-wrap; 
                    word-wrap: break-word; 
                    font-size: 1.1em;
                    background-color: #fff;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                del {{ 
                    background-color: #ffdddd; text-decoration: line-through; 
                    color: #a00000; padding: 0.1em 0;
                }}
                ins {{ 
                    background-color: #ddffdd; text-decoration: none; 
                    color: #006400; padding: 0.1em 0;
                }}
            </style>
        </head>
        <body>
            <h1>Poređenje transkripata (diff-match-patch)</h1>
            <div class="info">
                <p><b>Master Original (normalizovan za poređenje):</b> {master_original_name}</p>
                <p><b>Obrađeni transkript:</b> {processed_filename}</p>
                <p><b>Levenshtein distanca:</b> {distance} | <b>Sličnost:</b> {similarity_percentage:.2f}%</p>
            </div>
            <hr>
            <h3>Vizuelni prikaz razlika:</h3>
            <div class="diff-container">{html_diff_output}</div>
        </body>
        </html>
        """

        # <<< VRATIO SAM STARI NAZIV HTML FAJLA >>>
        base_processed_filename = os.path.splitext(processed_filename)[0]
        output_html_filename = f"dmp_compare_master_vs_{base_processed_filename}.html"
        output_html_path = os.path.join(comparison_output_folder, output_html_filename)

        try:
            with open(output_html_path, 'w', encoding='utf-8') as f_out:
                f_out.write(full_html_content)
            print(f"  HTML diff (DMP) sačuvan u: {output_html_path}")
        except Exception as e:
            print(f"  Greška pri čuvanju HTML diff-a: {e}")

    # <<< VRATIO STARI FORMAT ISPISA SUMARNOG IZVJEŠTAJA >>>
    summary_file_path = os.path.join(comparison_output_folder, "_sumarni_izvjestaj_poredjenja_DMP.txt")
    with open(summary_file_path, 'w', encoding='utf-8') as f_summary:
        f_summary.write("Sumarni izvještaj poređenja obrađenih transkripata sa master originalima (DMP):\n")
        f_summary.write("=================================================================================\n\n")
        for report_item in summary_report:
            f_summary.write(f"Obrađeni fajl: {report_item['processed_file']}\n")
            f_summary.write(f"  Master original: {report_item['master_file']}\n")
            f_summary.write(f"  Status: {report_item['status']}\n")
            f_summary.write(f"  Levenshtein distanca: {report_item['lev_distance']}\n")
            f_summary.write(f"  Procenat sličnosti: {report_item['similarity_percent']}\n\n")
    print(f"\nSumarni izvještaj sačuvan u: {summary_file_path}")


# --- Glavni dio skripte ---
if __name__ == "__main__":
    # --- KONFIGURACIJA ---
    master_originals_folder = "original_finalno_normalizovano" 
    processed_scripts_folder = "whisper_finalno_normalizovano" 
    comparison_results_folder_dmp = "rezultati_poredjenja_DMP_final"
    # --- KRAJ KONFIGURACIJE ---
    
    compare_processed_to_master_originals_dmp(
        master_originals_folder, 
        processed_scripts_folder, 
        comparison_results_folder_dmp
    )
    
    print(f"\nZavršeno generisanje DMP HTML poređenja.")