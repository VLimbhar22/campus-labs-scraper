import csv


class DataSaver:
    """
    Save scraped data to a CSV file
    """

    def __init__(self, csv_file_path):
        f = open(csv_file_path, 'a')
        self.writer = csv.writer(f)

    def save_to_csv(self, data):
        self.writer.writerow(data)
