import pandas as pd
import json

def create_nested_structure(df):
    """
    Processes a DataFrame and creates a nested dictionary representing the organizational hierarchy,
    applying specific rules to correct known errors in the source file.
    """
    
    # --- START: HIERARCHY CORRECTION RULES ---

    # 1. Define a mapping for organizations that are incorrectly parented in the XLSX.
    parent_overrides = {
        "Information Office of State Council": "Central Publicity Department",
        "Press & Publication Office (State Copyright Bureau)": "Central Publicity Department",
        "State Film Bureau": "Central Publicity Department",
        "State Administration of Religious Affairs": "Central United Front Work Department",
        "Overseas Chinese Affairs Office of State Council": "Central United Front Work Department",
        "Office for Taiwan Affairs (Taiwan Affairs Office of State Council)": "Central Leading Group for Taiwan Affairs",
        "Central Office for H.K. & Macao Affairs (H.K. & Macao Affairs Office of State Council)": "Central Leading Group for H.K. & Macao Affairs",
        "State Administration of Civil Service": "Central Organization Department"
    }

    # 2. Define lists of organizations that need to be grouped under a new, non-existent parent.
    npc_special_committees = [
        "Ethnic Affairs Committee", "Constitution and Law Committee", "Supervision and Judicial Affairs Committee",
        "Financial and Economic Affairs Committee", "Education, Science, Culture and Public Health Committee",
        "Foreign Affairs Committee", "Overseas Chinese Affairs Committee", "Environment Protection and Resources Conservation Committee",
        "Agriculture and Rural Affairs Committee", "Social Building Committee"
    ]
    
    cppcc_special_committees = [
        "Motions Committee", "Economic Committee", "Agriculture and Rural Affairs Committee",
        "Population, Resources and Environment Committee", "Education, Science, Health & Sports Committee",
        "Social and Legislative Committee", "Ethnic and Religious Committee", "H.K., Macao, Taiwan and Overseas Chinese Committee",
        "Foreign Affairs Committee", "Culture, History and Study Committee"
    ]

    mass_org_friendship = [
        "Chinese People's Association for Friendship with Foreign Countries", "China-Japan Friendship Association",
        "China Association for International Friendly Contacts", "Chinese People's Institute of Foreign Affairs",
        "China Association for International Understanding (CAFIU)", "China Council for Promoting Peaceful Reunification",
        "Association for Relations Across the Taiwan Straits"
    ]
    
    mass_org_general = [
        "Red Cross Society of China", "China Disabled Persons' Federation"
    ]

    mass_org_religious = [
        "Buddhist Association of China", "China Taoist Association", "China Islamic Association",
        "China Patriotic Catholic Association", "Chinese Catholic Bishops College",
        "Three Self Patriotic Movement Committee of Protestant Churches of China", "Christian Council of China"
    ]

    # --- END: HIERARCHY CORRECTION RULES ---

    hierarchy = {}

    for _, row in df.iterrows():
        level_b = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None
        level_c = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None
        level_e = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else None

        current_level = hierarchy
        path = []

        org_name = level_e or level_c or level_b
        if not org_name:
            continue

        parent_from_file = level_c if level_e else level_b
        
        # --- APPLY CORRECTION LOGIC ---
        
        if org_name in parent_overrides:
            final_parent_path = [parent_overrides[org_name]]
        elif org_name in npc_special_committees:
            final_parent_path = ["NATIONAL PEOPLE'S CONGRESS", "Special Committees"]
        elif org_name in cppcc_special_committees:
            final_parent_path = ["CHINESE PEOPLE'S POLITICAL CONSULTATIVE CONFERENCE", "Special Committees"]
        elif org_name in mass_org_friendship:
            final_parent_path = ["MASS ORGANIZATIONS", "* Friendship Associations and Committees"]
        elif org_name in mass_org_general:
            final_parent_path = ["MASS ORGANIZATIONS", "* General Organizations"]
        elif org_name in mass_org_religious:
            final_parent_path = ["MASS ORGANIZATIONS", "* Religious Associations"]
        else:
            final_parent_path = [p for p in [level_b, level_c] if p and p != org_name]

        # --- CONSTRUCT HIERARCHY ---

        for part in final_parent_path:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

        if org_name not in current_level:
            current_level[org_name] = {}

    return hierarchy

def main():
    """
    Main function to run the script.
    """
    input_file = 'organizations_with_serials-v1.xlsx'
    output_file = 'corrected_hierarchy.json' # Define the output filename

    try:
        df = pd.read_excel(input_file, sheet_name='Sheet1', usecols=[1, 2, 4], header=None)
        df.columns = ['LevelB', 'LevelC', 'LevelE']

        nested_dict = create_nested_structure(df)
        json_output = json.dumps(nested_dict, indent=2, ensure_ascii=False)
        
        # **FIX**: Write the JSON output to a file instead of printing it
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_output)
        
        print(f"✅ Success! Corrected hierarchy has been saved to '{output_file}'")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()