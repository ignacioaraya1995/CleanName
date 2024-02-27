from vars import *
import pandas as pd
import os, re
from pathlib import Path
from tqdm import tqdm  # Import tqdm for the progress bar

def process_excel_files(data_folder, output_folder, common_first_names, common_last_names):
    # Ensure output directory exists
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    excel_files = [file for file in os.listdir(data_folder) if file.endswith(".xlsx")]
    
    for file in tqdm(excel_files, desc="Processing Excel files"):
        file_path = os.path.join(data_folder, file)
        df = pd.read_excel(file_path)

        if "OWNER FULL NAME" in df.columns and "OWNER FIRST NAME" in df.columns and "OWNER LAST NAME" in df.columns:
            # Update OWNER FIRST NAME and OWNER LAST NAME columns
            names = df["OWNER FULL NAME"].apply(lambda full_name: clean_and_split_name(full_name, common_first_names, common_last_names))
            df["OWNER FIRST NAME"], df["OWNER LAST NAME"] = zip(*names)

            output_path = os.path.join(output_folder, file)
            df.to_excel(output_path, index=False)
        else:
            print(f"Required columns are missing in {file}")

def clean_and_split_name(full_name, common_first_names, common_last_names):
    business_entities = ["llc", "trust", "investment", "properties", "prop", "capital", "acquisitions", "association", "inc", "incorporated", "and", "council", "rental"]
    name_terms = ["jr", "sr", "tr", "ii", "iii", "iv", "esq", "phd", "md", "aka", "fka", "tod", "dba", "mba", "cpa", "-estate of"]

    # Clean the full name from any unwanted characters and spaces
    full_name = str(full_name).strip(" ,-.")

    # Check if the full name belongs to a business entity
    name_words = full_name.lower().split()
    if any(entity in name_words for entity in business_entities):
        first_name, last_name = full_name, full_name  # Same if a business entity
        cleaned_full_name = full_name.lower().title().replace('Llc', 'LLC')
    else:
        # Split and clean the full name from titles or single letters
        words = full_name.split()
        if 'tr' in [word.lower() for word in words]:
            last_name = words[0]
            first_name = ' '.join(words[1:-1])  # Exclude the 'tr'
        else:
            cleaned_name = re.sub(r'[^\w\s]', '', full_name)
            name_parts = cleaned_name.split()

            # Filter out single-letter words, unless they are essential parts of the name
            essential_parts = [word for word in name_parts if len(word) > 1 or (len(word) == 1 and len(name_parts) == 2)]

            if len(essential_parts) == 1:
                first_name, last_name = essential_parts[0], ''
            elif essential_parts:
                first_name, last_name = essential_parts[0], ' '.join(essential_parts[1:])
            else:
                first_name, last_name = name_parts[0], '' if name_parts else ''

        # Further cleaning for name correctness
        first_name_parts = first_name.split()
        last_name_parts = last_name.split()

        first_name = ' '.join(word for word in first_name_parts if word.lower() not in name_terms and len(word) > 1)
        last_name = ' '.join(word for word in last_name_parts if word.lower() not in name_terms and len(word) > 1)

        # Check against common names lists for order correction
        first_in_first_names = first_name.title() in common_first_names
        first_in_last_names = first_name.title() in common_last_names
        last_in_first_names = last_name.title() in common_first_names
        last_in_last_names = last_name.title() in common_last_names

        # Swap names only under specific conditions
        if (first_in_last_names and not first_in_first_names and not last_in_last_names) or \
           (last_in_first_names and not last_in_last_names and not first_in_first_names):
            first_name, last_name = last_name, first_name

    return first_name.strip(), last_name.strip()

if __name__ == '__main__':
    process_excel_files(data_folder, output_folder, common_first_names, common_last_names)