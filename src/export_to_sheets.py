import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json
def push_to_sheet(df, sheet_name):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    from datetime import datetime
    import os, json

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = json.loads(os.environ["GOOGLE"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key("1le7tQxVkznMvphgOB2T0tGyzb_ByeaOHJ4R9E5piY_A")
    worksheet = sheet.worksheet(sheet_name)

    import pytz
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")


    df = df.copy()
    df["ticker"] = df["ticker"].astype(str)

    existing_data = worksheet.get_all_values()

    rows = []

    # ✅ header only once
    if not existing_data:
        rows.append(["Stock Name", "Sentiment Score", "", "Date & Time"])

    # ✅ data
    for _, row in df.iterrows():
        rows.append([
            str(row["ticker"]),
            float(row["sentiment_score"]),
            "",
            now
        ])

    # 🔥 FIX: force append from column A
    start_row = len(existing_data) + 1
    required_rows = start_row + len(rows)

    if required_rows > worksheet.row_count:
        extra_rows = required_rows - worksheet.row_count
        worksheet.add_rows(extra_rows)
    worksheet.update(rows, f"A{start_row}")
