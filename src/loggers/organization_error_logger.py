import csv


class OrganizationErrorLogger:
    """
    Log errors along with the corresponding URL that caused the error
    """

    def __init__(self, csv_file_path):
        self.file = open(csv_file_path, 'a')
        self.writer = csv.writer(self.file)

    def log_error(self, data, error):
        self.writer.writerow(data)
        print(error)
