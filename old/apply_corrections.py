import pandas as pd
import json

def build_parent_lookup(node, path, lookup_map):
    """
    Recursively walks through the nested dictionary from the JSON file
    and creates a simple {organization: [parent1, parent2...]} lookup map.
    """
    # For each item at the current level of the hierarchy
    for org_name, children in node.items():
        # Store the correct path for the current organization
        lookup_map[org_name] = path
        
        # If this organization has children, go one level deeper
        if isinstance(children, dict) and children:
            build_parent_lookup(children, path + [org_name], lookup_map)

def main():
    """
    Main function to load files, apply corrections, and save the new Excel file.
    """
    source_excel_file = 'organizations_with_serials-v1.xlsx'
    json_hierarchy_file = 'corrected_hierarchy.json'
    output_excel_file = 'organizations_corrected.xlsx'

    print("🚀 Starting the correction process...")

    try:
        # 1. Load the corrected hierarchy from the JSON file
        with open(json_hierarchy_file, 'r', encoding='utf-8') as f:
            hierarchy_data = json.load(f)
        print(f"✅ Successfully loaded '{json_hierarchy_file}'")

        # 2. Load the original Excel file into a pandas DataFrame
        # We assume the file has no header row, so we use header=None
        df = pd.read_excel(source_excel_file, header=None)
        print(f"✅ Successfully loaded '{source_excel_file}'")
        
        # 3. Build the {organization: [parents...]} lookup map
        parent_lookup = {}
        build_parent_lookup(hierarchy_data, [], parent_lookup)
        print("🗺️  Correct hierarchy map has been built.")

        # 4. Iterate through the DataFrame and update the parent columns
        print("✍️  Updating rows with correct hierarchy...")
        updated_rows = 0
        for index, row in df.iterrows():
            # Get the organization name from Column E (index 4)
            org_name = str(row[4]).strip()

            if org_name in parent_lookup:
                correct_path = parent_lookup[org_name]
                
                # Update Column B (index 1) with the Level 1 Parent
                df.iat[index, 1] = correct_path[0] if len(correct_path) > 0 else None
                
                # Update Column C (index 2) with the Level 2 Parent
                df.iat[index, 2] = correct_path[1] if len(correct_path) > 1 else None
                
                updated_rows += 1
        
        print(f"👍 {updated_rows} rows were checked and updated.")

        # 5. Save the modified DataFrame to a new Excel file
        # index=False prevents pandas from writing row numbers into the file
        df.to_excel(output_excel_file, index=False, header=False)
        print(f"\n🎉 Success! Corrected file has been saved as '{output_excel_file}'")

    except FileNotFoundError as e:
        print(f"\n❌ ERROR: File not found. Make sure '{e.filename}' is in the same directory as the script.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")


if __name__ == '__main__':
    main()