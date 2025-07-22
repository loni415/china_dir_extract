import json
import pandas as pd
import os
import argparse

def process_personnel(positions, org_name_en, org_name_cn, sub_org_name_en='', sub_org_name_cn=''):
    """
    Helper function to process a list of positions and extract personnel data.
    """
    personnel_list = []
    for position in positions:
        for person in position.get("personnel", []):
            row = {
                'organization_name_english': org_name_en,
                'organization_name_chinese': org_name_cn,
                'sub_organization_name_english': sub_org_name_en,
                'sub_organization_name_chinese': sub_org_name_cn,
                'title_english': position.get("title_english"),
                'title_chinese': position.get("title_chinese"),
                'name_pinyin': person.get("name_pinyin"),
                'name_chinese': person.get("name_chinese"),
                'birth_year': person.get("birth_year"),
                'birth_month': person.get("birth_month"),
                'birth_day': person.get("birth_day"),
                'gender': person.get("gender"),
                'ethnicity': person.get("ethnicity"),
                'assumed_office_date': person.get("assumed_office_date")
            }
            personnel_list.append(row)
    return personnel_list

def extract_all_organization_data(file_path):
    """
    Extracts data for all organizations from a JSON file.
    """
    print(f"Attempting to read data from: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
        return None

    output_data = []
    for org in data:
        org_name_en = org.get("organization_name_english")
        org_name_cn = org.get("organization_name_chinese")
        if not org_name_en:
            continue

        main_org_positions = org.get("positions", [])
        output_data.extend(process_personnel(main_org_positions, org_name_en, org_name_cn))

        for sub_org in org.get("sub_organizations", []):
            sub_org_name_en = sub_org.get("organization_name_english")
            sub_org_name_cn = sub_org.get("organization_name_chinese")
            sub_org_positions = sub_org.get("positions", [])
            output_data.extend(process_personnel(sub_org_positions, org_name_en, org_name_cn, sub_org_name_en, sub_org_name_cn))

    return output_data

def export_to_excel(data, filename):
    """
    Exports data to an Excel file. If the file exists, it appends the new data
    and removes duplicates. Otherwise, it creates a new file.
    """
    if data is None or not data:
        print("No new data was extracted to process.")
        return

    # Define the desired column order
    column_order = [
        'organization_name_english', 'organization_name_chinese',
        'sub_organization_name_english', 'sub_organization_name_chinese',
        'title_english', 'title_chinese', 'name_pinyin', 'name_chinese',
        'birth_year', 'birth_month', 'birth_day', 'gender', 'ethnicity',
        'assumed_office_date'
    ]
    
    # Create a DataFrame for the new data and ensure it has the correct columns
    new_df = pd.DataFrame(data)
    new_df = new_df[column_order]

    # Check if the output file already exists
    if os.path.exists(filename):
        print(f"File '{filename}' already exists. Reading existing data to append.")
        try:
            # Read the existing data from the Excel sheet
            existing_df = pd.read_excel(filename)
            
            # Combine the old and new data
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # --- Deduplication Step ---
            # Define columns that identify a unique record to prevent duplicates
            unique_cols = [
                'organization_name_english', 'sub_organization_name_english', 
                'title_english', 'name_pinyin', 'assumed_office_date'
            ]
            
            # Drop duplicates, keeping the last entry (useful for updating records)
            final_df = combined_df.drop_duplicates(subset=unique_cols, keep='last')
            
            print(f"Original rows: {len(existing_df)}. New rows from source: {len(new_df)}. Total rows after append & deduplication: {len(final_df)}.")

        except Exception as e:
            print(f"Error reading existing Excel file: {e}. Overwriting the file with new data instead.")
            final_df = new_df # Fallback to just writing the new data
    else:
        print(f"Creating new file: '{filename}'")
        final_df = new_df

    # Write the final DataFrame to the Excel file
    try:
        final_df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Success! Data saved to '{os.path.abspath(filename)}'")
    except Exception as e:
        print(f"An error occurred while writing to Excel: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract organization data from JSON and append to an Excel file.")
    parser.add_argument("input_file", nargs='?', default=None, help="Path to the input JSON file.")
    parser.add_argument("output_file", nargs='?', default=None, help="Path for the output Excel file.")
    args = parser.parse_args()

    # Set default filenames here if no command-line arguments are provided.
    default_input_json = 'input_data.json'
    default_output_excel = 'cumulative_organization_data.xlsx'

    input_json_file = args.input_file if args.input_file else default_input_json
    output_excel_file = args.output_file if args.output_file else default_output_excel
    
    extracted_data = extract_all_organization_data(input_json_file)
    
    export_to_excel(extracted_data, output_excel_file)
