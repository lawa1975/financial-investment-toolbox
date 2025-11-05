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
        pdf_text = SecuritySettlementExtractor.create_from_pdf(file) 
        security_settlement = pdf_text.extract_to_model()
        pk = f"{security_settlement.execution_time.timestamp()}{security_settlement.isin}"
        result[pk] = security_settlement

    sorted_result = dict(sorted(result.items()))

    output_entries = []
    for security_settlement in list(sorted_result.values()):
        provision_str = (
            f"{security_settlement.provision.amount:.4f} {security_settlement.provision.currency.value}"
            if security_settlement.provision
            else ""
        )

        output_entries.append({
            "execution time": security_settlement.execution_time,
            "transaction type": security_settlement.transaction_type.value,
            "isin": security_settlement.isin,
            "wkn": security_settlement.wkn,
            "shares": f"{security_settlement.shares:.6f}",
            "price_per_share": f"{security_settlement.price_per_share.amount:.4f} {security_settlement.price_per_share.currency.value}",
            "market_value": f"{security_settlement.market_value.amount:.4f} {security_settlement.market_value.currency.value}",
            "provision": provision_str,
            "payment_direction": security_settlement.payment_direction.value,
            "final_amount": f"{security_settlement.final_amount.amount:.4f} {security_settlement.final_amount.currency.value}",
        })
 
    ts = int(datetime.datetime.now(datetime.UTC).timestamp() * 1e3)

    with open(f"private/output/output_{ts}.csv", 'w', newline='') as csvfile:
        fieldnames = output_entries[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(output_entries)
