import json
from collections import OrderedDict

def build_hierarchy_map(hierarchy_data):
    """
    Recursively builds a map of child-to-parent relationships from the blueprint file.
    """
    child_to_parent_map = {}

    def recurse(parent_name, children_dict):
        if not isinstance(children_dict, dict):
            return
        for child_name, sub_children in children_dict.items():
            if child_name.isdigit(): # Skip keys that are page numbers
                recurse(parent_name, sub_children)
                continue
            child_to_parent_map[child_name] = parent_name
            if isinstance(sub_children, dict) and sub_children:
                recurse(child_name, sub_children)

    for key, value in hierarchy_data.items():
        if isinstance(value, dict):
            recurse(key, value)
            
    return child_to_parent_map

def restructure_data(sorted_data, hierarchy_map):
    """
    Restructures the flat data from sorted_by_page.json into a nested hierarchy.
    """
    # 1. Flatten all organization entries into a single list
    all_org_dicts = []
    for key, value in sorted_data.items():
        if isinstance(value, dict):
            all_org_dicts.append(value)
        elif isinstance(value, list):
            all_org_dicts.extend(value)

    # 2. Create a lookup table of all organizations by their English name
    organizations_by_name = {}
    for org_dict in all_org_dicts:
        if not isinstance(org_dict, dict):
            continue
        org_name = org_dict.get("organization_name_english")
        if org_name:
            org_dict["sub_organizations"] = []
            organizations_by_name[org_name] = org_dict

    # 3. Nest sub-organizations under their correct parents
    processed_children = set()
    for org_name, org_data in organizations_by_name.items():
        
        # Find the ultimate "real" parent by traversing up the hierarchy map
        # This handles conceptual parents like "Special Committees"
        current_parent_name = hierarchy_map.get(org_name)
        while current_parent_name and current_parent_name not in organizations_by_name:
            current_parent_name = hierarchy_map.get(current_parent_name)

        # If a real parent is found, append this org as a child
        if current_parent_name and current_parent_name in organizations_by_name:
            parent_org = organizations_by_name[current_parent_name]
            parent_org["sub_organizations"].append(org_data)
            processed_children.add(org_name)

    # 4. Create the final list containing only top-level organizations
    final_data = []
    for org_name, org_data in organizations_by_name.items():
        if org_name not in processed_children:
            final_data.append(org_data)

    # 5. Sort all sub_organizations and the top_level list by page number
    for org_data in organizations_by_name.values():
        if org_data.get("sub_organizations"):
            org_data["sub_organizations"].sort(key=lambda x: x.get("source_pdf_page", 999))
            
    final_data.sort(key=lambda x: x.get("source_pdf_page", 999))
            
    return final_data

def main():
    """Main function to run the restructuring process."""
    hierarchy_file = 'hierarchy_from_book.json'
    sorted_data_file = 'sorted_by_page.json'
    output_file = 'final_hierarchical_data.json'

    try:
        with open(hierarchy_file, 'r', encoding='utf-8') as f:
            hierarchy_blueprint = json.load(f)
        
        with open(sorted_data_file, 'r', encoding='utf-8') as f:
            sorted_data = json.load(f, object_pairs_hook=OrderedDict)

        print("Building hierarchy map...")
        child_to_parent = build_hierarchy_map(hierarchy_blueprint)
        print(f"Found {len(child_to_parent)} parent-child relationships.")

        print("Restructuring data...")
        final_data = restructure_data(sorted_data, child_to_parent)
        print(f"Created final structure with {len(final_data)} top-level organizations.")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Successfully created '{output_file}' with the correct hierarchy.")

    except FileNotFoundError as e:
        print(f"Error: Could not find file '{e.filename}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()