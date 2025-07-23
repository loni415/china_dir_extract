import json
import pandas as pd
import os
import argparse
import glob

def extract_all_organization_data(file_path):
    """
    Extracts data for all organizations from a JSON file.
    """
    print(f"Attempting to read data from: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Check if data is a dictionary (single org), and if so, wrap it in a list
        if isinstance(data, dict):
            print("Note: Input file contains a single organization object. Converting to list format.")
            data = [data]
            
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
        return None

    output_data = []
    # Track the organization order
    for org_index, org in enumerate(data):
        org_name_en = org.get("organization_name_english")
        org_name_cn = org.get("organization_name_chinese")
        source_pdf_page = org.get("source_pdf_page")  # Get the page number
        
        if not org_name_en:
            continue

        # Add order tracking for positions within main organization
        main_org_positions = org.get("positions", [])
        for pos_index, position in enumerate(main_org_positions):
            # Add order metadata to position
            position['_org_order'] = org_index
            position['_position_order'] = pos_index
        
        output_data.extend(process_personnel(main_org_positions, org_name_en, org_name_cn, source_pdf_page))

        # Process sub-organizations with order tracking
        for sub_org_index, sub_org in enumerate(org.get("sub_organizations", [])):
            sub_org_name_en = sub_org.get("organization_name_english")
            sub_org_name_cn = sub_org.get("organization_name_chinese")
            sub_org_positions = sub_org.get("positions", [])
            
            # Add order tracking for positions within sub-organization
            for pos_index, position in enumerate(sub_org_positions):
                # Add order metadata to position
                position['_org_order'] = org_index
                position['_sub_org_order'] = sub_org_index
                position['_position_order'] = pos_index
            
            output_data.extend(process_personnel(sub_org_positions, org_name_en, org_name_cn, 
                                               source_pdf_page, sub_org_name_en, sub_org_name_cn))

    return output_data

def process_personnel(positions, org_name_en, org_name_cn, source_pdf_page, sub_org_name_en='', sub_org_name_cn=''):
    """
    Helper function to process a list of positions and extract personnel data.
    """
    personnel_list = []
    for position in positions:
        # Get order metadata
        org_order = position.get('_org_order', 0)
        sub_org_order = position.get('_sub_org_order', 0)
        position_order = position.get('_position_order', 0)
        
        for person_index, person in enumerate(position.get("personnel", [])):
            row = {
                'source_pdf_page': source_pdf_page,  # Add source page number
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
                'assumed_office_date': person.get("assumed_office_date"),
                # Add order tracking fields
                '_org_order': org_order,
                '_sub_org_order': sub_org_order,
                '_position_order': position_order,
                '_person_order': person_index
            }
            personnel_list.append(row)
    return personnel_list

def process_directory(directory_path):
    """
    Process all JSON files in a directory and return combined data.
    """
    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist.")
        return None
    
    # Find all JSON files in the directory
    json_files = glob.glob(os.path.join(directory_path, "*.json"))
    
    if not json_files:
        print(f"No JSON files found in directory: {directory_path}")
        return None
    
    print(f"Found {len(json_files)} JSON files to process:")
    for file in json_files:
        print(f"  - {os.path.basename(file)}")
    
    # Process each file and combine the results
    all_data = []
    processed_count = 0
    
    for file_path in json_files:
        print(f"\nProcessing file {processed_count + 1} of {len(json_files)}: {os.path.basename(file_path)}")
        file_data = extract_all_organization_data(file_path)
        
        if file_data:
            all_data.extend(file_data)
            processed_count += 1
            print(f"  - Added {len(file_data)} personnel records")
        else:
            print(f"  - No data extracted from this file")
    
    print(f"\nFinished processing {processed_count} files. Total personnel records: {len(all_data)}")
    return all_data

def export_to_excel(data, filename):
    """
    Exports data to an Excel file, sorted by source_pdf_page.
    If the file exists, it appends the new data, removes duplicates,
    and sorts everything by page number.
    """
    if data is None or not data:
        print("No new data was extracted to process.")
        return

    # Define the desired column order - add source_pdf_page to the columns
    column_order = [
        'source_pdf_page',  # Added to ensure this column is preserved
        'organization_name_english', 'organization_name_chinese',
        'sub_organization_name_english', 'sub_organization_name_chinese',
        'title_english', 'title_chinese', 'name_pinyin', 'name_chinese',
        'birth_year', 'birth_month', 'birth_day', 'gender', 'ethnicity',
        'assumed_office_date'
    ]
    
    # Create a DataFrame for the new data and ensure it has the correct columns
    new_df = pd.DataFrame(data)
    
    # Ensure source_pdf_page is numeric for proper sorting
    new_df['source_pdf_page'] = pd.to_numeric(new_df['source_pdf_page'], errors='coerce')
    
    # Sort the new data by source_pdf_page
    new_df = new_df.sort_values(by='source_pdf_page')
    
    # Reorder columns
    new_df = new_df[column_order]

    # Check if the output file already exists
    if os.path.exists(filename):
        print(f"File '{filename}' already exists. Reading existing data to append.")
        try:
            # Read the existing data from the Excel sheet
            existing_df = pd.read_excel(filename)
            
            # Ensure the existing data has the source_pdf_page column
            if 'source_pdf_page' not in existing_df.columns:
                print("Adding source_pdf_page column to existing data")
                existing_df['source_pdf_page'] = None
            
            # Ensure source_pdf_page is numeric in existing data
            existing_df['source_pdf_page'] = pd.to_numeric(existing_df['source_pdf_page'], errors='coerce')
            
            # Combine the old and new data
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # --- Deduplication Step ---
            # Define columns that identify a unique record to prevent duplicates
            unique_cols = [
                'organization_name_english', 'sub_organization_name_english', 
                'title_english', 'name_pinyin', 'assumed_office_date'
            ]
            
            # Drop duplicates, keeping the last entry (useful for updating records)
            combined_df = combined_df.drop_duplicates(subset=unique_cols, keep='last')
            
            # Sort the combined data by source_pdf_page
            final_df = combined_df.sort_values(by='source_pdf_page')
            
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
        print(f"Success! Data saved to '{os.path.abspath(filename)}', sorted by page number.")
    except Exception as e:
        print(f"An error occurred while writing to Excel: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract organization data from JSON files and append to an Excel file.")
    parser.add_argument("input", nargs='?', default=None, help="Path to the input JSON file or directory containing JSON files.")
    parser.add_argument("output_file", nargs='?', default=None, help="Path for the output Excel file.")
    parser.add_argument("--dir", action="store_true", help="Process all JSON files in the input directory")
    args = parser.parse_args()

    # Set default filenames here if no command-line arguments are provided.
    default_input = 'input_data.json'
    default_output_excel = 'cumulative_organization_data.xlsx'

    input_path = args.input if args.input else default_input
    output_excel_file = args.output_file if args.output_file else default_output_excel
    
    # Determine if we're processing a directory or a single file
    if args.dir or (os.path.isdir(input_path) and not os.path.isfile(input_path)):
        print(f"Processing all JSON files in directory: {input_path}")
        extracted_data = process_directory(input_path)
    else:
        # Process a single file
        print(f"Processing single JSON file: {input_path}")
        extracted_data = extract_all_organization_data(input_path)
    
    export_to_excel(extracted_data, output_excel_file)
