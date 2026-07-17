from datetime import datetime
import pandas as pd
def normalize_ticker(ticker):
        return ticker.strip().upper()


def normalize_year(year_value):
        year = str(year_value).strip() # Clean whitespaces 

         # TTM(Trailing twelve months)- Not a real date
        if year.upper() == "TTM":
                return "TTM"

        # try format- "Jan-23"
        try:
                d = datetime.strptime(year, "%b-%y")
                return f"{d.year}-{d.month:02d}"
        except ValueError:
                pass
        # try format - "Jan-2023"
        try:
                d = datetime.strptime(year, "%b-%Y")
                return f"{d.year}-{d.month:02d}"
        except ValueError:
                pass

        # try format- "Dec 2023"
        try:
                d = datetime.strptime(year, "%b %Y")
                return f"{d.year}-{d.month:02d}"
        except ValueError:
                pass
        # try format- "2023"
        
        try:
                year_only = int(year)
                return f"{year_only}-01"
        except ValueError:
                pass
        

        return "PARSE-ERROR"

