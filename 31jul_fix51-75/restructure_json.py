import json

def create_data_lookup(flat_data):
    """
    Converts the flat list of organization data into a dictionary for fast lookups.
    The key is the organization_name_english.
    """
    lookup = {}
    for item in flat_data:
        org_name = item.get("organization_name_english")
        if org_name:
            lookup[org_name] = item
    return lookup

def build_nested_structure(hierarchy_node, data_lookup):
    """
    Recursively traverses the hierarchy blueprint.

    - If a node in the hierarchy has corresponding data, it creates the node
      and recursively populates its children.
    - If a node is purely structural (e.g., "ASIA"), it skips creating a node
      for it and instead adds its children directly to the current level.
    """
    # The output at each level of recursion will be a list of organizations
    built_nodes_list = []

    for org_name, sub_hierarchy in hierarchy_node.items():
        # Check if this organization exists in our data file
        org_data = data_lookup.get(org_name)

        if org_data:
            # --- This is a DATA node ---
            # It exists in the data file, so we create a node for it.
            new_node = org_data.copy()

            # If the hierarchy expects this node to have children, recurse.
            if "sub_organizations" in sub_hierarchy and sub_hierarchy["sub_organizations"]:
                new_node["sub_organizations"] = build_nested_structure(
                    sub_hierarchy["sub_organizations"],
                    data_lookup
                )
            else:
                # Ensure the sub_organizations key is an empty list if no subs exist
                new_node["sub_organizations"] = []

            built_nodes_list.append(new_node)
        else:
            # --- This is a STRUCTURAL node (or genuinely missing) ---
            # It's a grouping like 'ASIA', so we don't create a node for it.
            # Instead, we process its children and add them to the current list.
            print(f"Info: Structural node '{org_name}' found. Processing its children.")

            if "sub_organizations" in sub_hierarchy and sub_hierarchy["sub_organizations"]:
                # The recursive call returns a list of child nodes.
                children_nodes = build_nested_structure(
                    sub_hierarchy["sub_organizations"],
                    data_lookup
                )
                # Extend the current list with the returned children.
                built_nodes_list.extend(children_nodes)

    return built_nodes_list

def main():
    # Define file paths
    flat_data_file = 'china_dir_2024-p51-75.json'
    hierarchy_file = 'dir2024_p51-75_hierarchy.json'
    output_file = 'china_dir_2024-p51-75_corrected.json'

    # 1. Load the JSON files
    try:
        with open(flat_data_file, 'r', encoding='utf-8') as f:
            flat_data = json.load(f)
        with open(hierarchy_file, 'r', encoding='utf-8') as f:
            hierarchy_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: Could not find file {e.filename}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from a file: {e}")
        return

    # 2. Create the fast lookup dictionary from the flat data
    data_lookup = create_data_lookup(flat_data)

    # 3. Recursively build the new, nested structure.
    # The function now directly returns the final list of top-level organizations.
    final_structure_list = build_nested_structure(hierarchy_data, data_lookup)

    # 4. Save the corrected structure to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_structure_list, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Successfully restructured JSON. Output saved to '{output_file}'")

if __name__ == '__main__':
    main()