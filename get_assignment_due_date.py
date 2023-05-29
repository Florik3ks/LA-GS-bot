from PyPDF2 import PdfReader
import re
from datetime import datetime

time_pattern = ".*zum[ ]?(\\d\\d.\\d\\d.\\d\\d\\d\\d)[ ]?um[ ]?(\\d\\d)[ ]?Uhr"
discord_timestamp = "<t:{timestamp}:D> (<t:{timestamp}:R>)"
def get_due_date(path):
    pdf_reader = PdfReader(path)
    
    page_1 = pdf_reader.pages[0]
    lines = page_1.extract_text().splitlines()
    for line in lines:
        if re.match(time_pattern, line):
            date = re.match(time_pattern, line).group(1)
            time = re.match(time_pattern, line).group(2)
            actual_date = datetime.strptime(date + " " + time, "%d.%m.%Y %H")
            return discord_timestamp.format(timestamp=int(actual_date.timestamp()))