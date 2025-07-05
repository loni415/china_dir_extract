import fitz  # PyMuPDF
import json
import sys
import os
import re

# ==============================================================================
# 1. THE COMPREHENSIVE SYSTEM PROMPT
# ==============================================================================
# This is the instruction set we developed, telling the LLM its role and rules.
SYSTEM_PROMPT = """
You are an expert data extraction system. Your sole function is to parse the provided text from a single page of a Chinese party-state leadership directory and convert its contents into a valid JSON array. Adhere strictly to the schema and parsing rules. Produce only the final JSON array as your output, without any commentary, apologies, or markdown code fences.

The input text is from a two-column document. I have pre-processed it by merging lines from the left and right columns. A "||" separator often indicates the split between the columns.

**Required Output JSON Schema:**
[
  {
    "organization_name_english": "string",
    "organization_name_chinese": "string",
    "document_section_title": "string | null",
    "metadata": {},
    "sub_organizations": [],
    "positions": [
      {
        "title_english": "string",
        "title_chinese": "string",
        "metadata": { "count": "integer | null", "list_order_note": "string | null" },
        "personnel": [
          {
            "name_pinyin": "string",
            "name_chinese": "string",
            "dob_year": "integer | null",
            "dob_month": "integer | null",
            "assumed_office_date": "YYYY-MM-DD" | "YYYY-MM" | "YYYY" | null,
            "cross_reference_symbols": ["string"],
            "gender": "male" | "female",
            "ethnicity": "string",
            "rank": "string | null",
            "rank_chinese": "string | null",
            "other_notes": ["string"]
          }
        ]
      }
    ]
  }
]

**Detailed Parsing Rules:**
- **Hierarchy:** Capture the nested structure of organizations, sub-organizations, and positions.
- **`dob_year` / `dob_month`**: Parse from `(YY.MM)`. A `YY` < 30 is 20xx; otherwise, it's 19xx.
- **`assumed_office_date`**: Parse from the `YY.MM.DD` format into ISO 8601 `YYYY-MM-DD`.
- **`cross_reference_symbols`**: Collect any leading `☆`, `※`, `◎`, `○` symbols.
- **`gender`**: If `(f)` or `(女)` is present, set to "female". **Default is "male".**
- **`ethnicity`**: If an ethnicity like `(Mongolian)` or `(蒙古族)` is present, record it. **Default is "Han".**
- **`rank` & `rank_chinese`**: Map abbreviations like `(Gen)` to `rank` and the Chinese `(上将)` to `rank_chinese`. **Default is `null` if no rank is specified.**
- **`other_notes`**: Place any other parenthetical notes like `(executive)` or `(SPC)` here.
- **Continuations:** If the page seems to continue a list from a previous page (e.g., starts with a list of names without a new header), structure the JSON as if it belongs to the last-mentioned organization/position. The top-level object in your response should reflect this context.
"""

# ==============================================================================
# 2. PDF PRE-PROCESSING FUNCTION
# ==============================================================================
def preprocess_pdf_page(page):
    """
    Extracts text from a PDF page and attempts to reconstruct the two-column layout
    into a single, coherent text block for the LLM.
    """
    blocks = page.get_text("blocks")
    # Sort blocks primarily by top-coordinate, then left-coordinate
    blocks.sort(key=lambda b: (b[1], b[0]))

    lines = []
    for b in blocks:
        # Each block can have multiple lines
        block_text = b[4]
        lines.extend(block_text.strip().split('\n'))

    # A simple heuristic: assume the page center divides the columns
    page_center = page.rect.width / 2
    merged_lines = {}

    for b in blocks:
        # Use the vertical center of the block for y-coordinate
        y0, y1 = b[1], b[3]
        y_center = (y0 + y1) / 2
        # Round to group lines that are vertically close
        y_key = round(y_center / 10) * 10

        text = b[4].strip().replace('\n', ' ')
        if not text:
            continue

        if y_key not in merged_lines:
            merged_lines[y_key] = {'left': [], 'right': []}

        # Decide if block is in left or right column
        if b[0] < page_center:
            merged_lines[y_key]['left'].append(text)
        else:
            merged_lines[y_key]['right'].append(text)

    # Combine left and right parts for each line
    processed_text = []
    for y_key in sorted(merged_lines.keys()):
        left_text = " ".join(merged_lines[y_key]['left'])
        right_text = " ".join(merged_lines[y_key]['right'])
        
        if left_text and right_text:
            processed_text.append(f"{left_text} || {right_text}")
        elif left_text:
            processed_text.append(left_text)
        elif right_text:
            processed_text.append(right_text)

    return "\n".join(processed_text)

# ==============================================================================
# 3. LLM INTERACTION AND JSON CLEANING
# ==============================================================================
def get_json_from_llm(page_text, model_name):
    """
    Sends the pre-processed page text to the Ollama model and gets a JSON response.
    """
    try:
        response = ollama.chat(
            model=model_name,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': page_text}
            ],
            # Ask the model to output JSON directly
            options={'temperature': 0.0},
            format='json'
        )
        content = response['message']['content']
        
        # The 'json' format in Ollama should return valid JSON, but we clean just in case
        # Clean potential markdown fences
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        content = content.strip()
        
        return json.loads(content)

    except Exception as e:
        print(f"   - Error processing with LLM: {e}")
        print(f"   - Raw response content: {response.get('message', {}).get('content', 'N/A')}")
        return None

# ==============================================================================
# 4. JSON STITCHING LOGIC
# ==============================================================================
def stitch_json_results(all_pages_data):
    """
    Merges the list of JSON objects from each page into a single,
    hierarchically correct JSON structure.
    """
    if not all_pages_data:
        return []

    final_data = []
    for page_data in all_pages_data:
        if not page_data:
            continue

        for org_data in page_data:
            # Check if this organization is a continuation of the previous one
            if (final_data and 
                final_data[-1]['organization_name_english'] == org_data['organization_name_english']):
                
                # This is a continuation, merge sub-organizations and positions
                last_org = final_data[-1]
                
                # Merge positions
                if org_data.get('positions'):
                    if (last_org['positions'] and org_data['positions'] and
                        last_org['positions'][-1]['title_english'] == org_data['positions'][0]['title_english']):
                        # Continuation of a personnel list
                        last_org['positions'][-1]['personnel'].extend(org_data['positions'][0]['personnel'])
                        # Append any other new positions from the page
                        last_org['positions'].extend(org_data['positions'][1:])
                    else:
                        # Not a continuation of a specific list, just new positions in the same org
                        last_org['positions'].extend(org_data['positions'])

                # Merge sub-organizations (less common but possible)
                if org_data.get('sub_organizations'):
                    last_org['sub_organizations'].extend(org_data.get('sub_organizations', []))

            else:
                # This is a new organization, just append it
                final_data.append(org_data)

    return final_data

# ==============================================================================
# 5. MAIN EXECUTION BLOCK
# ==============================================================================
def main():
    if len(sys.argv) != 4:
        print("Usage: python parse_directory.py <path_to_pdf> <output_json_file> <ollama_model_name>")
        print("Example: python parse_directory.py cpc_directory.pdf output.json llama3:8b-instruct")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2]
    model_name = sys.argv[3]

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at '{pdf_path}'")
        sys.exit(1)

    print(f"Processing '{pdf_path}' with model '{model_name}'...")

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF file: {e}")
        sys.exit(1)

    num_pages = len(doc)
    all_pages_data = []

    for i, page in enumerate(doc):
        print(f"- Processing Page {i + 1} of {num_pages}...")
        page_text = preprocess_pdf_page(page)
        
        if not page_text.strip():
            print("  - Page is empty, skipping.")
            continue
        
        # print(f"  - Pre-processed Text:\n---\n{page_text}\n---") # Uncomment for debugging
        page_json = get_json_from_llm(page_text, model_name)
        
        if page_json:
            print(f"  - Successfully extracted JSON from page {i+1}.")
            all_pages_data.append(page_json)
        else:
            print(f"  - Failed to extract JSON from page {i+1}. Skipping.")

    print("\nStitching JSON data from all pages...")
    final_stitched_data = stitch_json_results(all_pages_data)

    print(f"Writing final structured data to '{output_path}'...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_stitched_data, f, ensure_ascii=False, indent=2)

    print("\nProcessing complete!")


if __name__ == "__main__":
    main()