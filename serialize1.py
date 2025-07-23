import pandas as pd
import numpy as np

def assign_serial_numbers(input_filepath, output_filepath):
    """
    Reads a CSV file, assigns unique serial numbers to organization/sub-organization
    pairs, and saves the result to a new CSV.

    Args:
        input_filepath (str): The path to the input CSV file.
        output_filepath (str): The path where the output CSV file will be saved.
    """
    try:
        # Read the provided CSV file into a pandas DataFrame
        df = pd.read_excel(input_filepath)

        # A dictionary to keep track of unique organization combinations and their assigned serial number
        # The key will be a tuple: (organization_name, sub_organization_name)
        # The value will be the serial number string, e.g., 'O_0000001'
        org_serial_map = {}
        
        # A counter to generate new serial numbers
        serial_counter = 1
        
        # A list to hold the generated serial numbers for each row
        serial_numbers_column = []

        # Iterate over each row in the DataFrame to generate the serial numbers
        for index, row in df.iterrows():
            # Get the organization and sub-organization names
            # Fill NaN (blank) sub-organization values with an empty string for consistent keying
            org_name = row['organization_name_english']
            sub_org_name = row['sub_organization_name_english']
            
            # Handle cases where sub_org_name might be NaN or other non-string types
            if pd.isna(sub_org_name):
                sub_org_name = ""
            else:
                sub_org_name = str(sub_org_name)

            # Create a unique key for the combination of organization and sub-organization
            org_key = (org_name, sub_org_name)

            # If we haven't seen this combination before, assign a new serial number
            if org_key not in org_serial_map:
                # Format the serial number as 'O_' followed by a 7-digit number with leading zeros
                new_serial = f"O_{serial_counter:07d}"
                org_serial_map[org_key] = new_serial
                serial_counter += 1
            
            # Append the correct serial number for the current row to our list
            serial_numbers_column.append(org_serial_map[org_key])

        # Insert the new 'serial_number' column at the beginning (position 0) of the DataFrame
        df.insert(0, 'serial_number', serial_numbers_column)

        # Save the modified DataFrame to a new CSV file
        df.to_excel(output_filepath, index=False)
        
        print(f"Successfully processed the file.")
        print(f"Output saved to: {output_filepath}")
        print(f"Total unique organization/sub-organization pairs found: {len(org_serial_map)}")

    except FileNotFoundError:
        print(f"Error: The file '{input_filepath}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Execution ---
# Define the input and output file paths
# The input file is the one you uploaded.
input_file = 'try5.xlsx'
output_file = 'organizations_with_serials.xlsx'

# Call the function to perform the task
assign_serial_numbers(input_file, output_file)
