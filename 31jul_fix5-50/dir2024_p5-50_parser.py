import json
import pandas as pd

def flatten_json_to_rows(org_data, parent_chain=[]):
    """
    Recursively traverses the nested JSON and creates a flat list of rows,
    with one row per person, formatted with dynamic 'Org Level X' columns.
    """
    rows = []
    
    # 1. Establish the current organization's full hierarchical path
    current_org_name = org_data.get("organization_name_english", "Unknown Org")
    current_chain = parent_chain + [current_org_name]
    
    # 2. Process only the personnel listed in the current organization
    # This loop is the only place where rows are created.
    for position in org_data.get("positions", []):
        for personnel in position.get("personnel", []):
            # Start a new dictionary for this person's row
            row_data = {}
            
            # Add Org Level columns based on the current path
            for i, org_name in enumerate(current_chain):
                row_data[f"Org Level {i+1}"] = org_name
            
            # Add the position and personnel details after the org levels
            row_data.update({
                "Title (English)": position.get("title_english", ""),
                "Title (Chinese)": position.get("title_chinese", ""),
                "Name (Pinyin)": personnel.get("name_pinyin", ""),
                "Name (Chinese)": personnel.get("name_chinese", ""),
                "Assumed Office Date": personnel.get("assumed_office_date", ""),
                "Birth Year": personnel.get("birth_year", ""),
                "Birth Month": personnel.get("birth_month", ""),
                "Gender": personnel.get("gender", ""),
                "Ethnicity": personnel.get("ethnicity", ""),
                "Rank (English)": personnel.get("rank_english", ""),
                "Rank (Chinese)": personnel.get("rank_chinese", "")
            })
            
            rows.append(row_data)
            
    # 3. Recurse into this organization's children, passing down the updated path
    for sub_org in org_data.get("sub_organizations", []):
        rows.extend(flatten_json_to_rows(sub_org, parent_chain=current_chain))
        
    return rows

# --- Main Script Execution ---

try:
    # Load the main, corrected JSON file with the full hierarchy
    with open('china_dir_2024_corrected_hierarchy.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Flatten the entire dataset using the recursive function
    all_rows = []
    for top_level_org in data:
        all_rows.extend(flatten_json_to_rows(top_level_org, parent_chain=[]))

    if all_rows:
        # Dynamically determine the maximum number of Org Level columns needed
        max_depth = 0
        for row in all_rows:
            depth = sum(1 for key in row if key.startswith("Org Level"))
            if depth > max_depth:
                max_depth = depth

        # Define the final column order
        org_columns = [f"Org Level {i+1}" for i in range(max_depth)]
        personnel_columns = [
            "Title (English)", "Title (Chinese)", "Name (Pinyin)", "Name (Chinese)",
            "Assumed Office Date", "Birth Year", "Birth Month", "Gender",
            "Ethnicity", "Rank (English)", "Rank (Chinese)"
        ]
        final_columns = org_columns + personnel_columns

        # Create DataFrame
        df = pd.DataFrame(all_rows)
        
        # Ensure all columns exist and are in the correct order, filling missing ones with ""
        df = df.reindex(columns=final_columns, fill_value="")
        
        output_filename = 'china_dir_2024-p5-50.xlsx'
        df.to_excel(output_filename, index=False)
        
        print(f"Success! Data has been parsed into the desired format and saved to '{output_filename}'")
    else:
        print("No personnel data found in the JSON file.")

except FileNotFoundError:
    print("Error: 'china_dir_2024_corrected_hierarchy.json' not found. Please ensure the file is in the same directory as the script.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")