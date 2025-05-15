import csv


def read_row_from_csv_file(path: str, num: int = 0) -> list:
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        return [row[num] for row in list(reader)[1:]]
