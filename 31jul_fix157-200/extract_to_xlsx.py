import json
import pandas as pd
import os

def parse_organization(org_data, parent_orgs=[]):
    """
    Recursively parses an organization and its sub-organizations,
    returning a flat list of personnel records.
    """
    rows = []
    
    # Current organization's path
    current_org_path = parent_orgs + [org_data.get('organization_name_english')]

    # Process personnel in the current organization
    for position in org_data.get('positions', []):
        for person in position.get('personnel', []):
            row = {
                'org_path': current_org_path,
                'Title (English)': position.get('title_english'),
                'Title (Chinese)': position.get('title_chinese'),
                'Name (Pinyin)': person.get('name_pinyin'),
                'Name (Chinese)': person.get('name_chinese'),
                'Assumed Office Date': person.get('assumed_office_date'),
                'Birth Year': person.get('birth_year'),
                'Birth Month': person.get('birth_month'),
                'Gender': person.get('gender'),
                'Ethnicity': person.get('ethnicity'),
                'Rank (English)': person.get('rank_english'),
                'Rank (Chinese)': person.get('rank_chinese'),
                'Cross_Reference_Symbol': person.get('cross_reference_symbol')
            }
            rows.append(row)
            
    # Recursively process sub-organizations
    for sub_org in org_data.get('sub_organizations', []):
        rows.extend(parse_organization(sub_org, current_org_path))
        
    return rows

def main():
    """
    Main function to load JSON, parse it, and save as XLSX.
    """
    input_json_file = 'china_dir_2024-p157-200.json'
    output_xlsx_file = 'china_directory_parsed.xlsx'

    if not os.path.exists(input_json_file):
        print(f"Error: Input file '{input_json_file}' not found.")
        return

    print(f"Loading and parsing JSON data from '{input_json_file}'...")
    with open(input_json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_personnel_rows = []
    # The input JSON is a list of top-level organizations
    for top_level_org in data:
        all_personnel_rows.extend(parse_organization(top_level_org))
    
    if not all_personnel_rows:
        print("No personnel records found in the JSON file.")
        return
        
    print("Creating DataFrame from parsed data...")
    df = pd.DataFrame(all_personnel_rows)

    # Split the organization path list into separate 'Org Level' columns
    org_levels_df = df['org_path'].apply(pd.Series)
    max_depth = len(org_levels_df.columns)
    org_levels_df.columns = [f'Org Level {i+1}' for i in range(max_depth)]

    # Combine the new org level columns with the main dataframe
    df = pd.concat([org_levels_df, df.drop('org_path', axis=1)], axis=1)

    # Define the final column order as specified
    final_column_order = [
        'Org Level 1', 'Org Level 2', 'Org Level 3', 'Org Level 4', 
        'Title (English)', 'Title (Chinese)',
        'Name (Pinyin)', 'Name (Chinese)',
        'Assumed Office Date',
        'Birth Year', 'Birth Month',
        'Gender', 'Ethnicity',
        'Rank (English)', 'Rank (Chinese)',
        'Cross_Reference_Symbol'
    ]
    
    # Ensure all required columns exist, adding any missing ones with empty values
    # This handles cases where the max org depth is less than 4
    for col in final_column_order:
        if col not in df.columns:
            df[col] = None

    # Reorder the dataframe columns
    df = df[final_column_order]

    print(f"Writing data to '{output_xlsx_file}'...")
    # Write the DataFrame to an Excel file without the index column
    df.to_excel(output_xlsx_file, index=False)

    print(f"\nSuccessfully created '{output_xlsx_file}' with {len(df)} records.")

if __name__ == '__main__':
    main()