import json
import pandas as pd

def extract_xinhua_data(file_path='input_data.json'):
    """
    Extracts data for Xinhua News Agency and its sub-organizations from a JSON file
    and returns it as a list of dictionaries.

    Args:
        file_path (str): The path to the input JSON file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row of data.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
        return []

    output_data = []
    
    # Define the target organization and sub-organizations
    target_organization = "Xinhua News Agency"
    target_sub_organizations = [
        "Xinhua General Office", 
        "Xinhua General Editorial Office", 
        "Xinhua Foreign Affairs Bureau"
    ]

    # Find the Xinhua News Agency data in the JSON
    xinhua_org = next((org for org in data if org.get("organization_name_english") == target_organization), None)

    if not xinhua_org:
        print(f"Could not find '{target_organization}' in the data.")
        return []

    # --- Process the main organization's personnel ---
    org_name_en = xinhua_org.get("organization_name_english")
    org_name_cn = xinhua_org.get("organization_name_chinese")

    for position in xinhua_org.get("positions", []):
        for person in position.get("personnel", []):
            row = {
                'organization_name_english': org_name_en,
                'organization_name_chinese': org_name_cn,
                'sub_organization_name_english': '', # No sub-org for top-level positions
                'sub_organization_name_chinese': '', # No sub-org for top-level positions
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
            output_data.append(row)

    # --- Process the sub-organizations' personnel ---
    for sub_org in xinhua_org.get("sub_organizations", []):
        sub_org_name_en = sub_org.get("organization_name_english")
        
        # We only care about specific sub-organizations
        if sub_org_name_en in target_sub_organizations:
            sub_org_name_cn = sub_org.get("organization_name_chinese")
            for position in sub_org.get("positions", []):
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
                    output_data.append(row)

    return output_data

def export_to_excel(data, filename='xinhua_data.xlsx'):
    """
    Exports a list of dictionaries to an Excel file.

    Args:
        data (list): The list of data rows to export.
        filename (str): The name of the output Excel file.
    """
    if not data:
        print("No data to export. Excel file will not be created.")
        return

    # Create a pandas DataFrame
    df = pd.DataFrame(data)

    # Reorder columns to match the requested format
    column_order = [
        'organization_name_english', 'organization_name_chinese', 
        'sub_organization_name_english', 'sub_organization_name_chinese',
        'title_english', 'title_chinese', 'name_pinyin', 'name_chinese',
        'birth_year', 'birth_month', 'birth_day', 'gender', 'ethnicity',
        'assumed_office_date'
    ]
    df = df[column_order]

    # Export the DataFrame to an Excel file
    try:
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Successfully exported data to '{filename}'")
    except Exception as e:
        print(f"An error occurred while exporting to Excel: {e}")


if __name__ == "__main__":
    # 1. Extract the data from the JSON file
    extracted_data = extract_xinhua_data('input_data.json')
    
    # 2. Export the extracted data to an Excel spreadsheet
    export_to_excel(extracted_data)
