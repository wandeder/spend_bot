import pygsheets
import os
from datetime import datetime


def save_to_sheet(data):
    link_sheet = os.getenv('LINK_SHEET')
    gc = pygsheets.authorize(
            service_account_env_var='GDRIVE_API_CREDENTIALS'
            )
    worksheet = gc.open_by_url(link_sheet).worksheet_by_title('Траты')
    data['datetime'] = datetime.today().strftime('%d.%m.%Y')
    record = [
        data.get('datetime'),
        data.get('value'),
        data.get('currency'),
        data.get('category'),
        data.get('comment'),
        data.get('bank'),
    ]

    index = len(worksheet.get_col(1, include_tailing_empty=False)) + 1
    worksheet.update_row(index, record)
