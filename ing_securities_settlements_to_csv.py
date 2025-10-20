import pymupdf
import pathlib
import csv
import sys
import datetime


def defaults_to_zero_amount(str):
    return str if str else "0,00"


def extract_data(filename):
    with pymupdf.open(filename) as doc:
        txt = doc[0].get_text()
        arr = txt.split("\n")

        result = {}
        
        kauf_verkauf_label = "Wertpapierabrechnung"
        kauf_verkauf_index = arr.index(kauf_verkauf_label)
        result["kauf_verkauf"] = arr[kauf_verkauf_index + 1] 

        isin_wkn_label = "ISIN (WKN)"
        isin_wkn_index = arr.index(isin_wkn_label)
        isin_wkn_value = arr[isin_wkn_index + 1]
        result["isin"], result["wkn"] = isin_wkn_value.replace("(", "").replace(")", "").split(" ")

        nominale_label = "Nominale"
        nominale_index = arr.index(nominale_label)
        result["nominale"] = arr[nominale_index + 2]

        kurs_label = "Kurs"
        kurs_index = arr.index(kurs_label)
        result["kurs_waehrung"] = arr[kurs_index + 1]
        result["kurs"] = arr[kurs_index + 2]
        
        kurswert_label = "Kurswert"
        kurswert_index = arr.index(kurswert_label)
        result["kurswert_waehrung"] = arr[kurswert_index + 1]
        result["kurswert"] = arr[kurswert_index + 2]        

        ausfuehrzeit_label = "Ausführungstag / -zeit"
        ausfuehrzeit_index = arr.index(ausfuehrzeit_label)
        result["ausfuehrzeit"] = arr[ausfuehrzeit_index + 1]
        
        provision_label = "Provision"
        try:
            provision_index = arr.index(provision_label)
            provision_waehrung_value = arr[provision_index + 1]
            provision_value = arr[provision_index + 2]
        except ValueError:
            provision_waehrung_value = None
            provision_value = None
        result["provision_waehrung"] = provision_waehrung_value
        result["provision"] = provision_value

        endbetrag_label = "Endbetrag zu Ihren Lasten"
        try:
            endbetrag_index = arr.index(endbetrag_label)
            endbetrag_waehrung_value = arr[endbetrag_index + 1]
            endbetrag_value = arr[endbetrag_index + 2]
        except ValueError:
            endbetrag_waehrung_value = None
            endbetrag_value = None
        result["endbetrag_lasten_waehrung"] = endbetrag_waehrung_value
        result["endbetrag_lasten"] = endbetrag_value

        endbetrag_label = "Endbetrag zu Ihren Gunsten"
        try:
            endbetrag_index = arr.index(endbetrag_label)
            endbetrag_waehrung_value = arr[endbetrag_index + 1]
            endbetrag_value = arr[endbetrag_index + 2]
        except ValueError:
            endbetrag_waehrung_value = None
            endbetrag_value = None
        result["endbetrag_gunsten_waehrung"] = endbetrag_waehrung_value
        result["endbetrag_gunsten"] = endbetrag_value

        return result


if __name__ == "__main__":
    files_pattern = sys.argv[1] # example: files/levin/*_IE00BD45KH83_*.pdf"

    parent_folder = pathlib.Path(__file__).parent.absolute()

    result = {}

    for file in parent_folder.glob(files_pattern):
        extracted = extract_data(file)
        az = extracted["ausfuehrzeit"]
        isin = extracted["isin"]
        pk = f"{az[6:10]}{az[3:5]}{az[0:2]}{az[14:16]}{az[17:19]}{az[20:22]}{isin}"
        result[pk] = extracted

    sorted_result = dict(sorted(result.items()))

    output_entries = []
    for extracted in list(sorted_result.values()):
        output_entries.append({
            "ausfuehrzeit": extracted["ausfuehrzeit"].replace(" um", "").replace(" Uhr", ""),
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
