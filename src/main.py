import argparse

from progress.progress_saver import ProgressSaver
from scrapers.data_scraper import DataScraper

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Select one of the arguments to run the scraper.')
    parser.add_argument('-o', '--org', action='store_true',
                        help='Scrape or continue scraping the organization level information')
    parser.add_argument('-c', '--campus', action='store_true',
                        help='Scrape or continue scraping the campus level information')
    parser.add_argument('-r', '--reset', action='store_true',
                        help='Reset the current progress of the currently scraped organizations and campuses. '
                             'Do this if you want to run another iteration of scrapign to update the information.')
    parser.add_argument('-x', '--recheck_campus', action='store_true',
                        help='Try grabbing the information from the campuses missed in the first run.')
    parser.add_argument('-y', '--recheck_org', action='store_true',
                        help='Try grabbing the information from the organizations missed in the first run.')
    args = vars(parser.parse_args())

    if not any(args.values()):
        parser.error('No arguments provided. You need to select at least one argument to run the scraper. \n'
                     'Run the scraper with -h flag to see the available options.')
        exit(0)
    args = parser.parse_args()

    if args.org:
        print('Scraping Organizations')
        scraper = DataScraper()
        scraper.scrape_organizations(file_path='src/output/Organization_Information.csv')
    elif args.campus:
        print('Scraping Campuses to get organizations')
        scraper = DataScraper()
        scraper.scrape_campuses(links_file='src/input/links.txt')
    elif args.reset:
        progress_saver = ProgressSaver()
        progress_saver.reset_progress(True, True)
        print('Progress Reset')
    elif args.recheck_campus:
        print('Re-scraping failed campuses')
        scraper = DataScraper()
        scraper.scrape_campuses(links_file='src/logs/recheck_campus.txt')
    elif args.recheck_org:
        print('Re-scraping failed organizations')
        scraper = DataScraper()
        scraper.scrape_organizations(file_path='src/logs/recheck_organization.csv')
    else:
        parser.error('No arguments provided. You need to select at least one argument to run the scraper. \n'
                     'Run the scraper with -h flag to see the available options.')
        exit(0)
