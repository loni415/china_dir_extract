import json

def build_nested_structure(hierarchy_node, data_map):
    """
    Recursively builds a nested dictionary by following the hierarchy
    and pulling data from the data_map.
    """
    nested_orgs = {}
    for org_name, sub_hierarchy in hierarchy_node.items():
        # Find the corresponding data object for the current organization
        # The key in the data_map includes the page number for uniqueness
        page = sub_hierarchy.get("source_pdf_page", 0)
        data_key = f"{org_name}_{page}"
        
        # Start with the data from the data_map if it exists, otherwise create a base object
        if data_key in data_map:
            new_org_node = data_map[data_key].copy() # Use a copy to avoid modifying the original map
        else:
            # Create a placeholder if no specific personnel data exists (e.g., for parent categories)
            new_org_node = {
                "source_pdf_page": page,
                "organization_name_english": org_name,
                "organization_name_chinese": "", # Placeholder, as this isn't in the hierarchy file
                "metadata": {"warnings": []},
                "positions": [],
                "sub_organizations": []
            }

        # If there are sub-organizations in the hierarchy, recurse
        if "sub_organizations" in sub_hierarchy and sub_hierarchy["sub_organizations"]:
            # Recursively build the children and replace the existing (flat) sub_organizations
            new_org_node["sub_organizations"] = build_nested_structure(sub_hierarchy["sub_organizations"], data_map)
        
        nested_orgs[org_name] = new_org_node
        
    # The output should be a list of top-level organization objects, not a dict
    return list(nested_orgs.values())

# --- Main Script ---

# 1. Load the files
with open('dir2024_p5-50_hierarchy.json', 'r', encoding='utf-8') as f:
    hierarchy_data = json.load(f)

with open('china_dir_2024-p5-50.json', 'r', encoding='utf-8') as f:
    flat_data_list = json.load(f)

# 2. Create a lookup map from the flat data for efficient access
# The key is a combination of name and page to handle duplicate names
data_map = {}
for item in flat_data_list:
    # Handle the main organization
    main_org_name = item.get("organization_name_english")
    main_org_page = item.get("source_pdf_page")
    if main_org_name:
        data_map[f"{main_org_name}_{main_org_page}"] = item

    # Add any sub-organizations from the flat file to the map as well
    for sub_org in item.get("sub_organizations", []):
        sub_org_name = sub_org.get("organization_name_english")
        sub_org_page = sub_org.get("source_pdf_page")
        if sub_org_name:
            data_map[f"{sub_org_name}_{sub_org_page}"] = sub_org


# 3. Recursively build the final, nested structure
correctly_nested_data = build_nested_structure(hierarchy_data, data_map)

# 4. Save the new, corrected JSON file
output_filename = 'china_dir_2024_corrected_hierarchy.json'
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(correctly_nested_data, f, ensure_ascii=False, indent=2)

print(f"Successfully created '{output_filename}' with the correct nested hierarchy.")