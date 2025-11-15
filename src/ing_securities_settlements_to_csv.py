import pathlib
import csv
import sys
import datetime
from ing.extract import SecuritySettlementExtractor
from financial.format import MoneyFormatter


if __name__ == "__main__":
    files_pattern = sys.argv[1]

    parent_folder = pathlib.Path(__file__).parent.absolute()

    result = {}

    for file in parent_folder.glob(files_pattern):
        extractor = SecuritySettlementExtractor.create_from_pdf(file)
        security_settlement = extractor.extract_to_model()
        pk = f"{security_settlement.execution_time.timestamp()}{security_settlement.isin}"
        result[pk] = security_settlement

    sorted_result = dict(sorted(result.items()))

    money_formatter = MoneyFormatter(4)
    output_entries = []
    for security_settlement in list(sorted_result.values()):
        provision_str = (
            money_formatter.format(security_settlement.provision)
            if security_settlement.provision
            else ""
        )

        output_entries.append({
            "execution time": security_settlement.execution_time,
            "transaction type": security_settlement.transaction_type.value,
            "isin": security_settlement.isin,
            "wkn": security_settlement.wkn,
            "shares": f"{security_settlement.shares:.6f}",
            "price_per_share": money_formatter.format(security_settlement.price_per_share),
            "market_value": money_formatter.format(security_settlement.market_value),
            "provision": provision_str,
            "payment_direction": security_settlement.payment_direction.value,
            "final_amount": money_formatter.format(security_settlement.final_amount),
        })
 
    ts = int(datetime.datetime.now(datetime.UTC).timestamp() * 1e3)

    with open(f"../private/output/output_{ts}.csv", 'w', newline='') as csvfile:
        fieldnames = output_entries[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(output_entries)
