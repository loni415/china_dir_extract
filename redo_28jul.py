


#python redo_28jul.py combined_from_folder1.json hierarchy_from_book.json reorganized_output.xlsx
import json
import pandas as pd
import argparse
import sys
from typing import List, Dict, Any, Optional

def parse_hierarchy(hierarchy_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Parses the official hierarchy JSON into a DataFrame that defines the
    correct final structure and order.
    """
    structured_list = []

    def recurse(org_dict: Dict, parent_name: Optional[str] = None):
        for name, sub_orgs in org_dict.items():
            if name.isdigit():
                recurse(sub_orgs)
                continue
            
            if parent_name:
                structured_list.append({"organization_name_english": parent_name, "sub_organization_name_english": name})
            else:
                 structured_list.append({"organization_name_english": name, "sub_organization_name_english": ""})

            if isinstance(sub_orgs, dict) and sub_orgs:
                recurse(sub_orgs, parent_name=name)

    recurse(hierarchy_data)
    return pd.DataFrame(structured_list).drop_duplicates().reset_index(drop=True)

def create_personnel_lookup(organizations: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Flattens the data JSON into a simple lookup table where each row is a person
    tied only to the immediate parent organization in which they were found.
    """
    all_rows = []

    def process_org(org_data: Dict):
        if not isinstance(org_data, dict): return
            
        current_org_en = org_data.get("organization_name_english")
        if not current_org_en: return # Skip if the org object is malformed

        for position in org_data.get("positions", []):
            personnel = position.get("personnel", [])
            base_info = {
                "immediate_parent_org": current_org_en,
                "title_english": position.get("title_english"),
                "title_chinese": position.get("title_chinese"),
            }
            if not personnel:
                all_rows.append(base_info) # Add position even if empty
            else:
                for person in personnel:
                    row = base_info.copy()
                    row.update(person)
                    all_rows.append(row)
        
        for sub_org in org_data.get("sub_organizations", []):
            process_org(sub_org)

    for org in organizations:
        process_org(org)
        
    return pd.DataFrame(all_rows)

def reorganize_data(data_json_path: str, hierarchy_json_path: str, output_xlsx_path: str):
    """
    Reorganizes a large data JSON file based on an official hierarchy JSON file.
    """
    # --- 1. Load and Process Source Files ---
    print(f"Loading official hierarchy from: {hierarchy_json_path}")
    try:
        with open(hierarchy_json_path, 'r', encoding='utf-8') as f:
            hierarchy_json = json.load(f)
    except Exception as e:
        print(f"Error loading hierarchy file: {e}"); sys.exit(1)
    
    print(f"Loading and flattening data from: {data_json_path}")
    try:
        with open(data_json_path, 'r', encoding='utf-8') as f:
            data_json = json.load(f)
    except Exception as e:
        print(f"Error loading data file: {e}"); sys.exit(1)

    hierarchy_df = parse_hierarchy(hierarchy_json)
    data_list = list(data_json.values()) if isinstance(data_json, dict) else data_json
    personnel_lookup_df = create_personnel_lookup(data_list)

    # --- 2. Reorganize Data and Track Missing Info ---
    print("Reorganizing data...")
    final_rows = []
    missing_info_report = [] # List to hold names of orgs with no data

    for _, h_row in hierarchy_df.iterrows():
        org_name = h_row['organization_name_english']
        sub_org_name = h_row['sub_organization_name_english']
        target_name = sub_org_name if sub_org_name else org_name
        
        matching_personnel = personnel_lookup_df[personnel_lookup_df['immediate_parent_org'] == target_name]

        if not matching_personnel.empty:
            for _, p_row in matching_personnel.iterrows():
                new_row = h_row.to_dict()
                new_row.update(p_row.to_dict())
                final_rows.append(new_row)
        else:
            # If no personnel found, add to missing report and add blank row to Excel
            missing_info_report.append(h_row.to_dict())
            final_rows.append(h_row.to_dict())

    final_df = pd.DataFrame(final_rows)
    if 'immediate_parent_org' in final_df.columns:
        final_df.drop(columns=['immediate_parent_org'], inplace=True)
    
    # --- 3. Write to Excel ---
    print(f"Writing reorganized data to: {output_xlsx_path}")
    try:
        final_df = pd.merge(hierarchy_df, final_df, on=['organization_name_english', 'sub_organization_name_english'], how='left')
        final_df.to_excel(output_xlsx_path, index=False, engine='openpyxl')
        print(f"\n✅ Success! The reorganized file '{output_xlsx_path}' has been created.")
    except Exception as e:
        print(f"\n❌ Error writing to Excel: {e}")

    # --- 4. Print Missing Info Report ---
    if missing_info_report:
        print("\n--------------------------------------------------")
        print("⚠️  The following organizations from the hierarchy")
        print("    had no personnel data in the source file:")
        print("--------------------------------------------------")
        for item in missing_info_report:
            org = item['organization_name_english']
            sub_org = item['sub_organization_name_english']
            if sub_org:
                print(f"- {org}  >>  {sub_org}")
            else:
                print(f"- {org}")
        print("--------------------------------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reorganize a large JSON data file based on an official JSON hierarchy template.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("data_json", help="Path to the large, raw JSON data file (e.g., 'combined_from_folder1.json').")
    parser.add_argument("hierarchy_json", help="Path to the official hierarchy JSON file (e.g., 'hierarchy_from_book.json').")
    parser.add_argument("output_xlsx", help="Path for the final, reorganized Excel file (e.g., 'reorganized_output.xlsx').")
    
    args = parser.parse_args()
    
    data_json_path = args.data_json.strip()
    hierarchy_json_path = args.hierarchy_json.strip()
    output_xlsx_path = args.output_xlsx.strip()

    reorganize_data(data_json_path, hierarchy_json_path, output_xlsx_path)