import pathlib
import csv
import sys
import datetime
from typing import Optional
from ing.extract import SecuritySettlementExtractor


def defaults_to_zero_amount(str: Optional[str]) -> str:
    return str if str else "0,00"


if __name__ == "__main__":
    files_pattern = sys.argv[1]

    parent_folder = pathlib.Path(__file__).parent.absolute()

    result = {}

    for file in parent_folder.glob(files_pattern):
        extracted = SecuritySettlementExtractor.create_from_pdf(file).extract()
        az = extracted["ausfuehrzeit"]
        isin = extracted["isin"]
        if az and isin:
            pk = f"{az[6:10]}{az[3:5]}{az[0:2]}{az[14:16]}{az[17:19]}{az[20:22]}{isin}"
            result[pk] = extracted

    sorted_result = dict(sorted(result.items()))

    output_entries = []
    for extracted in list(sorted_result.values()):
        az = extracted["ausfuehrzeit"]
        if az:
            output_entries.append({
                "ausfuehrzeit": az.replace(" um", "").replace(" Uhr", ""),
                "isin": extracted["isin"],
                "kauf_verkauf": extracted["kauf_verkauf"],
                "nominale": extracted["nominale"],
                "kurs": extracted["kurs"],
                "kurswert": extracted["kurswert"],
                "provision": defaults_to_zero_amount(extracted["provision"]),
                "endbetrag_lasten": defaults_to_zero_amount(extracted["endbetrag_lasten"]),
                "endbetrag_gunsten": defaults_to_zero_amount(extracted["endbetrag_gunsten"])        
            })
 
    ts = int(datetime.datetime.now(datetime.UTC).timestamp() * 1e3)

    with open(f"private/output/output_{ts}.csv", 'w', newline='') as csvfile:
        fieldnames = output_entries[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(output_entries)
