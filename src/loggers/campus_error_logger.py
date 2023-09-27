class CampusErrorLogger:
    """
    Log errors along with the corresponding URL that caused the error
    """

    def __init__(self, file_path):
        self.file = open(file_path, 'a')

    def log_error(self, url, error):
        self.file.write(url)
        print(error)
