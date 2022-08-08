import pygsheets
import os
from datetime import datetime


def save_to_sheet(data):
    LINK_SHEET = os.getenv('LINK_SHEET')
    gc = pygsheets.authorize(
            service_account_env_var='GDRIVE_API_CREDENTIALS'
            )
    worksheet = gc.open_by_url(LINK_SHEET).worksheet_by_title('Траты')
    data['datetime'] = datetime.today().strftime('%d.%m.%Y %H:%M')
    record = []
    record.append(data.get('datetime'))
    record.append(data.get('value'))
    record.append(data.get('currency'))
    record.append(data.get('category'))
    index = len(worksheet.get_col(1, include_tailing_empty=False)) + 1
    worksheet.update_row(index, record)
