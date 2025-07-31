
Method 1

extract_all.py
    full process but not sure if works 100% correctly
    sorts by page as more rows added
    input: extracted json file or files in directory
    output: combined_data.xlsx

apply_corrections.py
    fixes hierarchy in excel output based on legend from source book
    source_excel_file = 'organizations_with_serials-v1.xlsx'
    json_hierarchy_file = 'corrected_hierarchy.json'
    output_excel_file = 'organizations_corrected.xlsx'

Method 2

combine_json.py
    combines mult json files
        input: set to directory /Users/lukasfiller/dev/china_dir_outputs
        output is: combined_from_folder1.json

resort_json_bypage.py
    input is: combined_from_folder1.json
    output is: sorted_by_page.json


Method 3
**note need to copy section that combines all json files in a dir to start here**

create_hierarchy.py
    combined aggregated json is input
    sorts by page last
    inputs:
        example_hierarchy = 'hierarchy_from_book.json'
        sorted_data_file = 'sorted_by_page.json'
        output_file = 'final_hierarchical_data.json'


hierarchy_from_book.json
    hierarchy as structured in front of China Dir 2024




china_dir_2024_example.json
    provides example of desired json structure using China Dir 2024 excerpt

serialize1.py
    adds column with serial #s for all rows
    takes 'final' xlsx and creates new one with serials

    REDO
    redo_28jul.py
    input: all jsons in one file
    reference input: json structure from directory source