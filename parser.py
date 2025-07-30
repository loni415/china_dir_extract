import json
import pandas as pd

def flatten_data(org_data, parent_orgs=[]):
    """
    Recursively flattens the nested organization data into a list of records.
    Each record represents one person.
    """
    rows = []
    
    # Get the current organization's name and create the hierarchy path
    current_org_name = org_data.get("organization_name_english", "N/A")
    current_org_path = parent_orgs + [current_org_name]
    
    # Process personnel in the current organization
    if "positions" in org_data:
        for position in org_data["positions"]:
            if "personnel" in position:
                for person in position["personnel"]:
                    # Start building a flat record for each person
                    record = {
                        "Name_Pinyin": person.get("name_pinyin"),
                        "Name_Chinese": person.get("name_chinese"),
                        "Position_Title_English": position.get("title_english"),
                        "Position_Title_Chinese": position.get("title_chinese"),
                        "Assumed_Office_Date": person.get("assumed_office_date"),
                        "Birth_Year": person.get("birth_year"),
                        "Birth_Month": person.get("birth_month"),
                        "Birth_Day": person.get("birth_day"),
                        "Gender": person.get("gender"),
                        "Ethnicity": person.get("ethnicity"),
                        "Rank_English": person.get("rank_english"),
                        "Rank_Chinese": person.get("rank_chinese"),
                        "Cross_Reference_Symbol": person.get("cross_reference_symbol"),
                        "Source_PDF_Page": org_data.get("source_pdf_page")
                    }
                    
                    # Add organizational hierarchy as separate columns (up to 5 levels)
                    for i in range(5):
                        if i < len(current_org_path):
                            record[f"Organization_L{i+1}"] = current_org_path[i]
                        else:
                            record[f"Organization_L{i+1}"] = None
                            
                    rows.append(record)

    # Recursively process sub-organizations
    if "sub_organizations" in org_data:
        for sub_org in org_data["sub_organizations"]:
            rows.extend(flatten_data(sub_org, current_org_path))
            
    return rows

def main():
    """
    Main function to load JSON, process data, and save to XLSX.
    """
    # --- CONFIGURATION ---
    # Change this to the JSON file you want to process
    input_json_file = '30jul_extracts/gem_30jul.json' 
    # Change this to your desired output Excel file name
    output_xlsx_file = 'prc_leader_data_stud.xlsx' 
    
    print(f"Loading data from '{input_json_file}'...")
    try:
        with open(input_json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{input_json_file}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{input_json_file}' is not a valid JSON file.")
        return

    print("Processing hierarchical data...")
    # Flatten the data starting from the root of the JSON object
    flattened_records = flatten_data(data)
    
    if not flattened_records:
        print("No personnel records were found in the JSON file.")
        return

    # Create a pandas DataFrame from the list of records
    df = pd.DataFrame(flattened_records)
    
    # Define the desired column order for the final Excel file
    column_order = [
        "Organization_L1", "Organization_L2", "Organization_L3", 
        "Organization_L4", "Organization_L5",
        "Position_Title_English", "Position_Title_Chinese",
        "Name_Pinyin", "Name_Chinese", "Assumed_Office_Date",
        "Birth_Year", "Birth_Month", "Birth_Day", "Gender", "Ethnicity",
        "Rank_English", "Rank_Chinese", "Cross_Reference_Symbol", "Source_PDF_Page"
    ]
    
    # Reorder the DataFrame columns
    df = df[column_order]
    
    print(f"Saving data to '{output_xlsx_file}'...")
    # Save the DataFrame to an Excel file, without the index column
    df.to_excel(output_xlsx_file, index=False)
    
    print("Done! The Excel file has been created successfully. ✨")

if __name__ == "__main__":
    main()

#run by parser.y and change name of input and output