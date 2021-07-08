# %%
import html
import json
import logging as log
import os.path
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple
from urllib.request import urlopen

import pandas as pd
from dateutil.relativedelta import relativedelta
from pandasql import sqldf
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chromedriver_location = "/Users/belliott/Downloads/chromedriver"
start_date = "2000-01-01"
end_date = "2021-07-01"
search_keywords = [
    "data engineer",
    "software engineer",
    "full stack",
    "fullstack",
    "ruby",
    "python",
    "hadoop",
    "snowflake",
    "ipo",
    "laid off",
    "remote",
]

# %%
# logging settings
log.getLogger().setLevel(log.INFO)
log.basicConfig(
    level=log.INFO,
    format="%(asctime)s %(levelname)-6s | %(lineno)+4s:%(funcName)-20s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log.info("Starting...")

# %%
# skip / debug
# Avoid running this accidentally outside of Interactive Mode in Visual Studio
log.error("Exiting...run this in Interactive Mode in Visual Studio...")
sys.exit(1)


# %%
def get_first_hn_link(month_to_search: str) -> str:
    """For a given month + year, find the first google result, return the url
    Args:
        month_to_search: YYYY-MM-01
    """
    log.info(f"month_to_search: {month_to_search}")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    browser = webdriver.Chrome(chromedriver_location, options=options)

    search_string = f'"Ask HN: Who is hiring? ({datetime.strptime(month_to_search, "%Y-%m-%d").strftime("%B %Y")})"'
    url = f"https://www.google.com/search?q={search_string}"
    browser.get(url)

    weblinks = browser.find_elements_by_xpath("//div[@class='g']//a[not(@class)]")

    browser.close()

    first_text = weblinks[0].text.split(" | ")[0]
    first_link = weblinks[0].get_attribute("href")

    # make sure the first link we pull matches the link we want
    if first_text.lower() != search_string.lower().replace('"', ""):
        log.error(
            f"Unable to find correct HN link, url: {url}, month_to_search: {month_to_search}, search_string: {search_string}, first_text: {first_text}"
        )
        sys.exit(1)

    return first_link


# %%
# skip / debug
curr_date = end_date
curr_hn_link = get_first_hn_link(curr_date)

hn_item_id = curr_hn_link.split("=")[1]


# %%
def get_string_stats(content: str, search_string: str) -> Tuple[int, int]:
    """Given a content string, return count of matches for search_string and number of unique matches"""
    cnt_total = content.lower().count(search_string.lower())
    cnt_unique = 1 if cnt_total > 0 else 0
    return cnt_total, cnt_unique


# %%
def get_post_ids(hn_item_id: str) -> List[str]:
    """For a given hn link_id, return a list of all post_id values"""
    hn_response = urlopen(
        "https://hacker-news.firebaseio.com/v0/item/" + hn_item_id + ".json"
    )
    hn_json = json.load(hn_response)
    post_ids = hn_json["kids"]
    log.info(f"Number of post_ids found: {len(post_ids)}")
    post_ids.sort(reverse=True)
    return post_ids


# %%
def get_post_data(
    post_id: str, search_keywords: List[str]
) -> Tuple[str, str, str, str, dict]:
    """For an hn link, structure the data, returning the:
    - company_name
    - location_name
    - frequency count for each search_keyword
    """
    url = f"https://hacker-news.firebaseio.com/v0/item/{str(post_id)}.json"
    log.info(f"Extracting structured data from url: {url}")
    hn_post_response = urlopen(url)
    hn_post_json = json.load(hn_post_response)

    search_results = {}
    for search_keyword in search_keywords:
        search_results[search_keyword] = {}
        search_results[search_keyword]["cnt_total"] = 0
        search_results[search_keyword]["cnt_unique"] = 0
    company_name = location = position_type = position_name = ""

    # verify hn_post_json has valid data
    if (
        (hn_post_json is not None)
        and not ("deleted" in hn_post_json and hn_post_json["deleted"])
        and ("text" in hn_post_json.keys())
    ):
        post = hn_post_json["text"]
        post_unescape = html.unescape(post)
        post_fulltext = post_unescape.replace("\n", " ")
        post_header = post_fulltext.split("<p>")[0].split(" | ")
        company_name = post_header[0] if len(post_header) > 0 else ""
        location = post_header[1] if len(post_header) > 1 else ""
        position_type = post_header[2] if len(post_header) > 2 else ""
        position_name = post_header[3] if len(post_header) > 3 else ""
        for search_keyword in search_keywords:
            if search_keyword > "":
                cnt_total = post_fulltext.lower().count(search_keyword.lower())
                search_results[search_keyword]["cnt_total"] += cnt_total
                search_results[search_keyword]["cnt_unique"] += (
                    1 if cnt_total > 0 else cnt_total
                )

    return company_name, location, position_type, position_name, search_results


# %%
# skip / debug
post_ids = get_post_ids(hn_item_id)

# %%
# skip / debug
post_id = post_ids[0]

get_post_data(post_id, search_keywords)
# company_name, location, position_type, position_name, search_results = get_post_data(post_id, search_keywords)

# %%
# skip / debug
company_names = []
locations = []
position_types = []
position_names = []
search_results = {}
for post_id in post_ids[0:10]:
    (
        company_name,
        location,
        position_type,
        position_name,
        search_results,
    ) = get_post_data(post_id, search_keywords)
    company_names.append(company_name)
    locations.append(location)
    position_types.append(position_type)
    position_names.append(position_name)

# %%
# skip / debug
d_company_names = {i: company_names.count(i) for i in set(company_names)}
d_locations = {i: locations.count(i) for i in set(locations)}
d_position_types = {i: position_types.count(i) for i in set(position_types)}
d_position_names = {i: position_names.count(i) for i in set(position_names)}

hn_metrics = {}
hn_metrics[curr_date] = {}
hn_metrics[curr_date]["company_names"] = d_company_names
hn_metrics[curr_date]["locations"] = d_locations
hn_metrics[curr_date]["position_types"] = d_position_types
hn_metrics[curr_date]["position_names"] = d_position_names
hn_metrics[curr_date]["search_results"] = search_results


# %%
# load previously saved hn_metrics
hn_metrics_file = "hn_metrics.json"
saved_hn_metrics = {}
if os.path.isfile(hn_metrics_file):
    f = open(hn_metrics_file)
    saved_hn_metrics = json.load(f)


# %%
# update hn_metrics with new data
def update_hn_metrics(
    start_date: str, end_date: str, curr_date: str, hn_metrics: dict
) -> Dict:
    """Update hn_metrics with data.  Processes most recent months first.
    Args:
        start_date: Date to start, "YYYY-MM-DD"
        end_date: Date to end, "YYYY-MM-DD"
        curr_date: Used as an override, begin looping through data on this month, "YYYY-MM-DD"
        hn_metrics: Dict containing existing data, if any
    Return:
        dict: Contains any found data
    """

    log.info("Starting update_hn_metrics()")

    curr_date = end_date if curr_date is None else curr_date

    # skip dates that have already been populated
    dates_to_skip = list(saved_hn_metrics.keys())
    log.info(
        f"start_date: {start_date}, end_date: {end_date}, dates_to_skip: {len(dates_to_skip)}"
    )

    while curr_date >= start_date:
        if curr_date not in dates_to_skip:
            log.info(f"Processing date {curr_date}...")

            hn_link = get_first_hn_link(curr_date)

            try:
                hn_item_id = re.findall(r".*id=(\d+).*", hn_link)[0]
            except Exception as e:
                log.error(f"Unable to parse {hn_link}, exception: {e}")
                sys.exit(1)
            post_ids = get_post_ids(hn_item_id)

            # placeholders to accumualte new data
            company_names = []
            locations = []
            position_types = []
            position_names = []
            saved_search_results = {}
            for search_keyword in search_keywords:
                saved_search_results[search_keyword] = {}
                saved_search_results[search_keyword]["cnt_total"] = 0
                saved_search_results[search_keyword]["cnt_unique"] = 0

            post_cnt = 0
            for post_id in post_ids:
                log.info(f"Loading {curr_date}: {post_cnt} / {len(post_ids)}")
                (
                    company_name,
                    location,
                    position_type,
                    position_name,
                    search_results,
                ) = get_post_data(post_id, search_keywords)
                # minor sanity check to clean up the surplus of garbage data
                if company_name > "":
                    company_names.append(company_name)
                    locations.append(location)
                    position_types.append(position_type)
                    position_names.append(position_name)
                    for search_keyword in search_keywords:
                        saved_search_results[search_keyword][
                            "cnt_total"
                        ] += search_results[search_keyword]["cnt_total"]
                        saved_search_results[search_keyword][
                            "cnt_unique"
                        ] += search_results[search_keyword]["cnt_unique"]

                post_cnt += 1

            # copy new data to our main dict
            hn_metrics[curr_date] = {}
            # company_names
            hn_metrics[curr_date]["company_names"] = {
                i: company_names.count(i) for i in set(company_names)
            }
            # locations
            hn_metrics[curr_date]["locations"] = {
                i: locations.count(i) for i in set(locations)
            }
            # position_types
            hn_metrics[curr_date]["position_types"] = {
                i: position_types.count(i) for i in set(position_types)
            }
            # position_names
            hn_metrics[curr_date]["position_names"] = {
                i: position_names.count(i) for i in set(position_names)
            }
            # search_results
            hn_metrics[curr_date]["search_results"] = saved_search_results

            log.info(f"Finished date {curr_date}...")

            with open("hn_metrics.json", "w") as outfile:
                json.dump(hn_metrics, outfile)
        else:
            log.info(f"Skipping date {curr_date}...")

        curr_date = (
            datetime.strptime(curr_date, "%Y-%m-%d") - relativedelta(months=1)
        ).strftime("%Y-%m-%d")

    log.info("No dates left process...")
    return hn_metrics


# %%
# update hn_metrics
hn_metrics = update_hn_metrics(
    start_date=start_date,
    end_date=end_date,
    curr_date=None,
    hn_metrics=saved_hn_metrics,
)

# %%
# Save hn_metrics to disk
with open("hn_metrics.json", "w") as outfile:
    json.dump(hn_metrics, outfile)

# %%
# Denormalize the data
denormalized_data = []
columns = [
    "start_date",
    "category",
    "value",
    "cnt",
    "cnt_total",
    "cnt_unique",
]
for start_date in sorted(hn_metrics.keys()):
    # denormalize company_names
    cnt_total = cnt_unique = 0
    for company_name in hn_metrics[start_date]["company_names"]:
        cnt = hn_metrics[start_date]["company_names"][company_name]
        new_row = [
            start_date,
            "company_names",
            company_name,
            cnt,
            cnt_total,
            cnt_unique,
        ]
        denormalized_data.append(new_row)
    # denormalize locations
    for location in hn_metrics[start_date]["locations"]:
        cnt = hn_metrics[start_date]["locations"][location]
        new_row = [
            start_date,
            "locations",
            location,
            cnt,
            cnt_total,
            cnt_unique,
        ]
        denormalized_data.append(new_row)
    # denormalize position_types
    for position_type in hn_metrics[start_date]["position_types"]:
        cnt = hn_metrics[start_date]["position_types"][position_type]
        new_row = [
            start_date,
            "position_types",
            position_type,
            cnt,
            cnt_total,
            cnt_unique,
        ]
        denormalized_data.append(new_row)
    # denormalize position_names
    for position_name in hn_metrics[start_date]["position_names"]:
        cnt = hn_metrics[start_date]["position_names"][position_name]
        new_row = [
            start_date,
            "position_names",
            position_name,
            cnt,
            cnt_total,
            cnt_unique,
        ]
        denormalized_data.append(new_row)
    # denormalize search_results
    for search_result in hn_metrics[start_date]["search_results"].keys():
        cnt = 0
        cnt_total = hn_metrics[start_date]["search_results"][search_result]["cnt_total"]
        cnt_unique = hn_metrics[start_date]["search_results"][search_result][
            "cnt_unique"
        ]
        new_row = [
            start_date,
            "search_results",
            search_result,
            cnt,
            cnt_total,
            cnt_unique,
        ]
        denormalized_data.append(new_row)

df = pd.DataFrame(data=denormalized_data, columns=columns)

# %%
title = "HN Who's Hiring posts over time"
sql = """
SELECT
    start_date AS start_date,
    SUM(cnt)   AS sum_cnt
FROM
    df
WHERE
    category = 'company_names'
GROUP BY
    start_date
ORDER BY
    start_date ASC
"""

sqldf(sql).plot("start_date", "sum_cnt", title=title)


# %%
title = "Frequency of Data Engineer over time"
sql = """
SELECT
    start_date, SUM(cnt_total) AS sum_cnt_total, SUM(cnt_unique) AS sum_cnt_unique
FROM
    df
WHERE
    category = 'search_results'
AND value = 'data engineer'
AND start_date >= '2013-01-01'
GROUP BY start_date
ORDER BY start_date
"""

sqldf(sql).plot("start_date", "sum_cnt_total", title=title)


# %%
# How has "remote" factored into job descriptions since covid?
title = "Frequency of Remote over time"
sql = """
SELECT
    start_date, SUM(cnt_total) AS sum_cnt_total, SUM(cnt_unique) AS sum_cnt_unique
FROM
    df
WHERE
    category = 'search_results'
AND value = 'remote'
AND start_date >= '2013-01-01'
GROUP BY start_date
ORDER BY start_date
"""

sqldf(sql).plot("start_date", "sum_cnt_total", title=title)


# %%
# What companies have been posting the most to HN Who's Hiring threads over time?
title = "Frequency of popular companies over time"
sql = """
SELECT
    start_date AS start_date,
    SUM(cnt)   AS sum_cnt
FROM
    df
WHERE
    category = 'company_names'
GROUP BY
    start_date
"""

sqldf(sql).plot("start_date", "sum_cnt_total", title=title)


# %%
# test sql

sqldf("SELECT * FROM df LIMIT 10")

# %%
# test graph w/SQL

sql = """
SELECT
    value           AS company_name,
    SUM(cnt)        AS sum_cnt,
    MIN(start_date) AS min_start_date,
    MAX(start_date) AS max_start_date
FROM
    df
WHERE
    category = 'company_names'
GROUP BY
    value
ORDER BY
    SUM(cnt) DESC
LIMIT 10
"""

sqldf(sql)

# %%
# test graph w/SQL

sql = """
SELECT
    start_date, SUM(cnt_total) AS sum_cnt_total, SUM(cnt_unique) AS sum_cnt_unique
FROM
    df
WHERE
    category = 'search_results'
GROUP BY start_date
ORDER BY start_date
"""

sqldf(sql).plot("start_date", "sum_cnt_total")

# %%
