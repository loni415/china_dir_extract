import json
import os
import glob

def combine_json_from_folder(folder_path="/Users/lukasfiller/dev/china_dir_outputs"):
    """
    Finds all .json files in a specified folder, combines them
    into a single JSON object, and saves the result to a new file.
    """
    # Check if the source folder exists
    if not os.path.isdir(folder_path):
        print(f"❌ Error: The folder '{folder_path}' was not found.")
        print("Please create it and place your JSON files inside.")
        return

    # Find all files ending with .json in the specified folder
    json_files = glob.glob(os.path.join(folder_path, '*.json'))

    if not json_files:
        print(f"🤷 No .json files were found in the '{folder_path}' folder.")
        return

    combined_data = {}
    output_filename = "combined_from_folder1.json"

    print(f"Found {len(json_files)} JSON files to merge. Starting process...")

    for file_path in json_files:
        # Generate a key from the filename (e.g., "health_commission.json" -> "health_commission")
        base_name = os.path.basename(file_path)
        key_name, _ = os.path.splitext(base_name)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                combined_data[key_name] = json.load(f)
                print(f"✅ Successfully loaded '{base_name}'")
        except json.JSONDecodeError:
            print(f"⚠️ Warning: Could not decode JSON from '{base_name}'. Skipping.")
        except Exception as e:
            print(f"❌ An unexpected error occurred with file '{base_name}': {e}")

    # Write the combined data to the output file
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)

    print(f"\n🚀 Success! All files have been combined into '{output_filename}'.")

if __name__ == "__main__":
    # The script will look for a subfolder named "source_json_files"
    combine_json_from_folder()