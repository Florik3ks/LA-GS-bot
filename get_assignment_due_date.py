from PyPDF2 import PdfReader
import re
from datetime import datetime

time_pattern = ".*Abgabe[ ]?der[ ]?Lösungen[ ]?bis[ ]?zum[ ]?(\\d\\d.\\d\\d.\\d\\d\\d\\d)[ ]?um.*"
discord_timestamp = "<t:{timestamp}:D>"
def get_due_date(path):
    pdf_reader = PdfReader(path)
    
    page_1 = pdf_reader.pages[0]
    x = page_1.extract_text().splitlines()
    for line in x:
        if re.match(time_pattern, line):
            date = re.match(time_pattern, line).group(1)
            actual_date = datetime.strptime(date, "%d.%m.%Y")
            return discord_timestamp.format(timestamp=int(actual_date.timestamp()))