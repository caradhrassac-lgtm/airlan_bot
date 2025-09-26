# sheets_client.py
import os, json
import gspread
from google.oauth2.service_account import Credentials
from typing import List

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

class SheetClient:
    def __init__(self, sheet_name: str):
        svc_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not svc_json:
            raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT_JSON env var (paste JSON content).")
        info = json.loads(svc_json)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        self.gc = gspread.authorize(creds)

        sheet_id = os.getenv("GSPREAD_SHEET_ID")  # <- NUEVO
        if sheet_id:
            self.sh = self.gc.open_by_key(sheet_id)     # abre por ID (no crea)
        else:
            try:
                self.sh = self.gc.open(sheet_name)      # abre por nombre
            except gspread.SpreadsheetNotFound:
                sa = info.get("client_email", "<service-account>")
                raise RuntimeError(
                    f"No se encontró la hoja '{sheet_name}'. "
                    f"Créala en tu Drive y compártela con {sa} como Editor, "
                    f"o define GSPREAD_SHEET_ID con el ID de la hoja."
                )
        self.ws = self.sh.sheet1

    def ensure_header(self, headers: List[str]):
        values = self.ws.get_all_values()
        if not values:
            self.ws.append_row(headers, value_input_option="RAW")

    def read_column_values(self, col_index: int) -> List[str]:
        col = self.ws.col_values(col_index)
        return col[1:] if len(col) > 1 else []

    def append_rows(self, rows: List[List[str]]):
        self.ws.append_rows(rows, value_input_option="RAW")
