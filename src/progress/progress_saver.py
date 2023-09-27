import pickle


class ProgressSaver:
    """
    Save the progress of scraped URLs
    """

    def __init__(self, file_path='src/input/progress.pkl'):
        """
        Initialize the progress saver
        :param file_path: the file path to the  pickle file where the progress of the current scraping is saved.
        """

        self.file = file_path
        self.progress_variables = pickle.load(open(self.file, 'rb'))

    def save_progress(self, org_count=None, campus_count=None):
        """
        Function to save the progress of currently scraped organizations or campuses
        :param org_count: the count of organizations that have been scraped successfully
        :param campus_count: the count of campuses that have been scraped successfully
        """
        if org_count is not None:
            self.progress_variables['organization'] = org_count
        if campus_count is not None:
            self.progress_variables['campus'] = campus_count

        # Save the progress in the pickle file
        with open(self.file, 'wb') as f:
            pickle.dump(self.progress_variables, f)

    def reset_progress(self, org_flag=False, campus_flag=False):
        """
        Functionality to reset the progress and start scraping again.
        :param org_flag: flag that denotes whether the organization progress should be reset.
        :param campus_flag: flag that denotes whether the campus progress should be reset.
        """
        if org_flag:
            self.progress_variables['organization'] = 0
        if campus_flag:
            self.progress_variables['campus'] = 0

        # Reset the progress in the pickle file
        with open(self.file, 'wb') as f:
            pickle.dump(self.progress_variables, f)

    def get_campus_progress(self):
        return self.progress_variables['campus']

    def get_organization_progress(self):
        return self.progress_variables['organization']
