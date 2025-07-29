1. gemini extracts from pdf to json using PRC Leader Parser 26JUL. Done in sections.
2. combine_json.py
    combines mult json files
        input: set to directory /Users/lukasfiller/dev/china_dir_outputs
        output is: combined_from_folder1.json


3a. redo_28jul.py
        input: combined_from_folder1.json
        reference input: hierarchy_from_book.json
        output: reorganized_output.xlsx

            OR

3b. create_hierarchy.py
    combined aggregated json is input
    sorts by page last
    inputs:
        example_hierarchy = 'hierarchy_from_book.json'
        sorted_data_file = 'sorted_by_page.json'
        output_file = 'final_hierarchical_data.json'