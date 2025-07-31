{
  "source_pdf_page": 0, // integer
  "organization_name_english": "string",
  "organization_name_chinese": "string",
  "positions": [
    {
      "title_english": "string",
      "title_chinese": "string",
      "personnel": [
        {
          "name_pinyin": "string",
          "name_chinese": "string",
          "assumed_office_date": "string | null",
          "birth_year": 0, // integer | null
          "birth_month": 0, // integer | null
          "birth_day": 0, // integer | null
          "cross_reference_symbol": "string | null",
          "gender": "string | null", // e.g., "female"
          "ethnicity": "string | null", // e.g., "Mongol", "Manchu"
          "rank_english": "string | null",
          "rank_chinese": "string | null"
        }
      ]
    }
  ],
  "sub_organizations": [
    // This section will contain more organization objects, following this same structure.
  ]
}

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
