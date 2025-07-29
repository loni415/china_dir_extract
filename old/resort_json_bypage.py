import json
from collections import OrderedDict

def get_sort_key(item):
    """
    Determines the sorting key (page number) for a top-level JSON item.

    This function handles two main data structures found in the input file:
    1. A dictionary representing a single organization.
    2. A list of dictionaries, where each dictionary is an organization.

    Args:
        item (tuple): A tuple containing the key and value of a top-level
                      item from the original JSON object.

    Returns:
        int: The source_pdf_page number to sort by. Returns a very large
             number (infinity) if no page number can be found, ensuring
             these items are placed at the end.
    """
    key, value = item
    # A very large number to use for items without a page number,
    # effectively sorting them to the end.
    max_int = float('inf')

    if isinstance(value, dict):
        # If the item is a dictionary, get 'source_pdf_page' or default to infinity.
        return value.get('source_pdf_page', max_int)
    elif isinstance(value, list) and value:
        # If the item is a non-empty list, check the first element.
        first_element = value[0]
        if isinstance(first_element, dict):
            # Get 'source_pdf_page' from the first element or default to infinity.
            return first_element.get('source_pdf_page', max_int)
    
    # Return infinity for any other cases (e.g., empty lists, other data types).
    return max_int

def sort_json_by_page(input_filepath, output_filepath):
    """
    Reads a JSON file, sorts its top-level entries by 'source_pdf_page',
    and writes the result to a new JSON file.

    Args:
        input_filepath (str): The path to the input JSON file.
        output_filepath (str): The path where the sorted JSON file will be saved.
    """
    try:
        # Step 1: Read the input JSON file
        with open(input_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Step 2: Sort the items from the dictionary using the custom sort key
        # The items() method returns a view object of (key, value) tuples.
        sorted_items = sorted(data.items(), key=get_sort_key)

        # Step 3: Create a new OrderedDict to preserve the sorted order
        # An OrderedDict remembers the order that keys were first inserted.
        sorted_data = OrderedDict(sorted_items)

        # Step 4: Write the sorted data to the output file
        with open(output_filepath, 'w', encoding='utf-8') as f:
            # Use indent=2 for pretty-printing the JSON output
            json.dump(sorted_data, f, ensure_ascii=False, indent=2)

        print(f"Successfully sorted the data and saved it to '{output_filepath}'")

    except FileNotFoundError:
        print(f"Error: The file '{input_filepath}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file '{input_filepath}'. Please check its format.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- How to use the script ---
if __name__ == "__main__":
    # Define the input and output file names
    # Make sure 'combined_from_folder1.json' is in the same directory as this script,
    # or provide the full path to it.
    input_file = 'combined_from_folder1.json'
    output_file = 'sorted_by_page.json'

    # Run the sorting function
    sort_json_by_page(input_file, output_file)
