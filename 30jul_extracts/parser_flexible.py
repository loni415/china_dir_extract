
import json
import pandas as pd

def flatten_data_dict(org_data, parent_orgs=[]):
    """
    Recursively flattens dictionary-style hierarchical data.
    """
    rows = []

    current_org_name = org_data.get("organization_name_english", "N/A")
    current_org_path = parent_orgs + [current_org_name]

    if "positions" in org_data:
        for position in org_data["positions"]:
            if "personnel" in position:
                for person in position["personnel"]:
                    record = {
                        "Name_Pinyin": person.get("name_pinyin"),
                        "Name_Chinese": person.get("name_chinese"),
                        "Position_Title_English": position.get("title_english"),
                        "Position_Title_Chinese": position.get("title_chinese"),
                        "Assumed_Office_Date": person.get("assumed_office_date"),
                        "Birth_Year": person.get("birth_year"),
                        "Birth_Month": person.get("birth_month"),
                        "Birth_Day": person.get("birth_day"),
                        "Gender": person.get("gender"),
                        "Ethnicity": person.get("ethnicity"),
                        "Rank_English": person.get("rank_english"),
                        "Rank_Chinese": person.get("rank_chinese"),
                        "Cross_Reference_Symbol": person.get("cross_reference_symbol"),
                        "Source_PDF_Page": org_data.get("source_pdf_page")
                    }
                    for i, level in enumerate(current_org_path):
                        record[f"Organization_L{i+1}"] = level
                    rows.append(record)

    sub_orgs = org_data.get("sub_organizations", {})
    if isinstance(sub_orgs, dict):
        for sub_name, sub_org in sub_orgs.items():
            if isinstance(sub_org, dict):
                sub_org["organization_name_english"] = sub_name
                rows.extend(flatten_data_dict(sub_org, current_org_path))
    elif isinstance(sub_orgs, list):
        for sub_org in sub_orgs:
            rows.extend(flatten_data_dict(sub_org, current_org_path))

    return rows

def process_data(data):
    all_rows = []
    if isinstance(data, dict):
        for top_level_name, top_level_org in data.items():
            top_level_org["organization_name_english"] = top_level_name
            all_rows.extend(flatten_data_dict(top_level_org, []))
    elif isinstance(data, list):
        for top_level_org in data:
            all_rows.extend(flatten_data_dict(top_level_org, []))
    return all_rows

def main():
    input_json_file = 'restructured_stud_30jul.json'  # or 'restructured_stud_30jul.json'
    output_xlsx_file = 'output_leadership_flexible.xlsx'

    print(f"Loading JSON from {input_json_file}...")
    with open(input_json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Processing hierarchy...")
    rows = process_data(data)

    df = pd.DataFrame(rows)
    print(f"Saving to Excel: {output_xlsx_file}")
    df.to_excel(output_xlsx_file, index=False)

if __name__ == "__main__":
    main()
