#!/usr/bin/env python
import os
import sys
import csvkit
import datetime
# from pprint import pprint

# import pygal

from jinja2 import Environment, FileSystemLoader

PATH = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(PATH, 'report_templates')
TEMPLATE_ENV = Environment(
    autoescape=False,
    loader=FileSystemLoader(TEMPLATE_DIR),
    trim_blocks=False)

# Data Files
#FB_PAGE_FILE = os.path.join('..', 'sample_data', 'FB-Page-Caboodles-201506-201508.csv')
#FB_POST_FILE = os.path.join('..', 'sample_data', 'FB-Post-Caboodles-201506-201508.csv')

FB_PAGE_FILE = os.path.join('..', 'sample_data', 'fb-page-bacon-fest-2015-09-24.csv')
FB_POST_FILE = os.path.join('..', 'sample_data', 'fb-post-bacon-fest-2015-09-24.csv')

# Report Templates
FB_POST_TMPL = "post_report.html"
FB_POST_REPORT_OUT_NAME = "fb_post_report_out.html"

FB_PAGE_TMPL = "page_report.html"
FB_PAGE_REPORT_OUT_NAME = "fb_page_report_out.html"


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except ValueError:
        return default


def render_template(template_filename, context):
    return TEMPLATE_ENV.get_template(template_filename).render(context)


def analyze_fb_page_data(page_file=FB_PAGE_FILE):
    print("Analying Facebook Page file {0}".format(page_file))
    DATE = 0
    TOTAL_LIKES = 1
    ENGAGED_USERS = 6
    TOTAL_REACH = 26
    IMPRESSIONS = 35

    data = list()
    with open(page_file) as f:
        csv = csvkit.reader(f)
        # skip first 2 lines
        csv.next()
        csv.next()
        for idx, r in enumerate(csv):
            data.append({
                'date': datetime.datetime.strptime(r[DATE], "%Y-%m-%d"),
                'likes': safe_cast(r[TOTAL_LIKES], int, 0),
                'engaged_users': safe_cast(r[ENGAGED_USERS], int, 0),
                'reach': safe_cast(r[TOTAL_REACH], int, 0),
                'impressions': safe_cast(r[IMPRESSIONS], int, 0)
            })

            print("Processing record {0}".format(idx+1))

    start_date = min(data, key=lambda i: i['date'])['date']
    end_date = max(data, key=lambda i: i['date'])['date']

    print "Start Date: ", start_date
    print "End Date: ", end_date

    chart_labels = [datetime.datetime.strftime(x['date'], "%m/%d/%Y") for x in data]
    reach = [x['reach'] for x in data]
    impressions = [x['impressions'] for x in data]
    engaged = [x['engaged_users'] for x in data]
    likes = [x['likes'] for x in data]

    reach.insert(0, 'Reach')
    impressions.insert(0, 'Impressions')
    engaged.insert(0, 'Engaged Users')
    likes.insert(0, 'Page Likes')

    template = render_template(FB_PAGE_TMPL,
                               {'start_date': start_date,
                                'end_date': end_date,
                                'chart_labels': chart_labels,
                                'reach': reach,
                                'impressions': impressions,
                                'engaged': engaged,
                                'likes': likes})

    template = template.encode('utf-8')

    print("Generating FB Page Report")

    with open(FB_PAGE_REPORT_OUT_NAME, "wb") as outf:
        outf.write(template)


def analyze_fb_post_data(post_file=FB_POST_FILE):
    PERMALINK = 1
    MESSAGE = 2
    POST_DATE = 6
    TOTAL_REACH = 7
    IMPRESSIONS = 10

    print("Analying Facebook Post file {0}".format(post_file))
    post_data = list()

    with open(post_file) as f:
        csv = csvkit.reader(f)
        # skip first 2 lines
        csv.next()
        csv.next()
        for idx, r in enumerate(csv):
            post_data.append({
                'permalink': r[PERMALINK],
                'pubdate': datetime.datetime.strptime(r[POST_DATE], "%m/%d/%Y %H:%M:%S %p"),
                'message': r[MESSAGE],
                'totalreach': int(r[TOTAL_REACH]),
                'impressions': int(r[IMPRESSIONS])})

            print("Processing FB Post Record {0}".format(idx+1))

    start_date = min(post_data, key=lambda i: i['pubdate'])['pubdate']
    end_date = max(post_data, key=lambda i: i['pubdate'])['pubdate']

    sorted_data = sorted(post_data, key=lambda i: i['totalreach'], reverse=True)

    template = render_template(FB_POST_TMPL,
                               {'top_posts': sorted_data[:10],
                                'start_date': start_date,
                                'end_date': end_date})

    template = template.encode('utf-8')

    print("Generating FB Post Report")

    with open(FB_POST_REPORT_OUT_NAME, "wb") as outf:
        outf.write(template)

    return 0


def main(argv=None):
    if argv is None:
        argv = sys.argv

    analyze_fb_page_data()
    analyze_fb_post_data()

    return 1


if __name__ == '__main__':
    sys.exit(main())
