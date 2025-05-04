# Import necessary libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
import json
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser
from credentials import username
from credentials import password

chrome_options = Options()
today = datetime.today()
profile_url = 'https://www.linkedin.com/in/lwastuargo/'

browser = webdriver.Chrome(options=chrome_options)

browser.get('https://www.linkedin.com/login')

elementID = browser.find_element(By.ID, "username")
elementID.send_keys(username)
elementID = browser.find_element(By.ID, "password")
elementID.send_keys(password)
elementID.submit()

time.sleep(3)

activity_page = profile_url + 'recent-activity/shares/'
activity_page = activity_page.replace('//', '/')
browser.get(activity_page)

profile_name = profile_url.rstrip('/').split('/')[-1].replace('-', ' ').title()
print(f"Scraping posts from: {profile_name}")

SCROLL_PAUSE_TIME = 2.5
MAX_SCROLLS = 30
last_height = browser.execute_script("return document.body.scrollHeight")
scrolls = 0
no_change_count = 0

while True:
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = browser.execute_script("return document.body.scrollHeight")
    no_change_count = no_change_count + 1 if new_height == last_height else 0
    if no_change_count >= 3 or (MAX_SCROLLS and scrolls >= MAX_SCROLLS):
        break
    last_height = new_height
    scrolls += 1
    print(f"Scroll {scrolls}/{MAX_SCROLLS}")

profile_page = browser.page_source
linkedin_soup = bs(profile_page.encode("utf-8"), "html.parser")

with open(f"{profile_name}_soup.txt", "w+", encoding='utf-8') as t:
    t.write(linkedin_soup.prettify())

def extract_date_text(container):
    """
    Extract date text from various potential elements in a LinkedIn post container
    """
    selectors = [
        {"tag": "span", "attrs": {"class": re.compile("feed-shared-actor__sub-description")}},
        {"tag": "span", "attrs": {"class": re.compile("visually-hidden")}},
        {"tag": "time", "attrs": {}},
        {"tag": "span", "attrs": {"class": re.compile("t-black--light|t-12|t-normal")}},
        {"tag": "div", "attrs": {"class": re.compile("feed-shared-actor__description")}},
    ]
    
    for selector in selectors:
        tag = selector["tag"]
        attrs = selector["attrs"]
        
        elements = container.find_all(tag, attrs) if attrs else container.find_all(tag)
        
        for element in elements:
            text = element.text.strip()
            if re.search(r'(hour|day|week|month|year|min|sec|\d+[hm]|\d+d|\d+w|\d+y)', text.lower()):
                date_part = re.split(r'\s*•\s*', text)[0].strip()
                return date_part
            
            if tag == "time" and element.has_attr("datetime"):
                return element["datetime"]
    
    all_text_elements = container.find_all(text=True)
    for text in all_text_elements:
        text = text.strip()
        if re.search(r'(hour|day|week|month|year|min|sec|\d+[hm]|\d+d|\d+w|\d+y)', text.lower()):
            return text
    
    return None

def parse_relative_date(date_text):
    """
    Convert relative date text (e.g., '3d', '2w', '1mo') to an actual date
    """
    if not date_text:
        return None
    
    date_text = date_text.lower().strip()
    
    try:
        if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', date_text):
            return parser.parse(date_text).date()
    except:
        pass
    
    now = datetime.now()
    
    if 'min' in date_text or 'm' in date_text:
        match = re.search(r'(\d+)', date_text)
        if match:
            minutes = int(match.group(1))
            return (now - timedelta(minutes=minutes)).date()
        return now.date()
    
    elif 'hour' in date_text or 'hr' in date_text or 'h' in date_text:
        match = re.search(r'(\d+)', date_text)
        if match:
            hours = int(match.group(1))
            return (now - timedelta(hours=hours)).date()
        return now.date()
    
    elif 'day' in date_text or 'd' in date_text:
        match = re.search(r'(\d+)', date_text)
        if match:
            days = int(match.group(1))
            return (now - timedelta(days=days)).date()
        return now.date()
    
    elif 'week' in date_text or 'w' in date_text:
        match = re.search(r'(\d+)', date_text)
        if match:
            weeks = int(match.group(1))
            return (now - timedelta(weeks=weeks)).date()
        return now.date()
    
    elif 'month' in date_text or 'mo' in date_text:
        match = re.search(r'(\d+)', date_text)
        if match:
            months = int(match.group(1))
            return (now - relativedelta(months=months)).date()
        return now.date()
    
    elif 'year' in date_text or 'yr' in date_text or 'y' in date_text:
        match = re.search(r'(\d+)', date_text)
        if match:
            years = int(match.group(1))
            return (now - relativedelta(years=years)).date()
        return now.date()
    
    try:
        parsed_date = parser.parse(date_text, fuzzy=True)
        if parsed_date.date() > now.date() and 'year' not in date_text and 'y' not in date_text:
            parsed_date = parsed_date.replace(year=parsed_date.year - 1)
        return parsed_date.date()
    except:
        return None

def extract_engagement_metrics(container):
    """
    Extract likes, comments, and shares counts from a LinkedIn post container
    """
    metrics = {
        "likes_text": "0",
        "comments_text": "0", 
        "shares_text": "0"
    }
    
    social_counts = container.find("div", {"class": re.compile("social-details-social-counts")})
    if social_counts:
        likes_element = social_counts.find("span", {"class": re.compile("reactions-count")})
        if likes_element:
            metrics["likes_text"] = likes_element.text.strip()
    
    if metrics["likes_text"] == "0":
        like_buttons = container.find_all("button", string=lambda s: s and re.search(r'like|reaction', s.lower()))
        for button in like_buttons:
            count_match = re.search(r'(\d+(?:[,.]\d+)?[KMB]?)', button.text)
            if count_match:
                metrics["likes_text"] = count_match.group(1)
                break
    
    comment_buttons = container.find_all("button", string=lambda s: s and 'comment' in s.lower())
    for button in comment_buttons:
        count_match = re.search(r'(\d+(?:[,.]\d+)?[KMB]?)', button.text)
        if count_match:
            metrics["comments_text"] = count_match.group(1)
            break
    
    share_buttons = container.find_all("button", string=lambda s: s and ('repost' in s.lower() or 'share' in s.lower()))
    for button in share_buttons:
        count_match = re.search(r'(\d+(?:[,.]\d+)?[KMB]?)', button.text)
        if count_match:
            metrics["shares_text"] = count_match.group(1)
            break
    
    return metrics

def convert_to_number(text):
    """
    Convert text like '1.5K' or '2M' to numeric values
    """
    if not text or text == "0":
        return 0
    
    try:
        text = text.strip().upper()
        
        if 'K' in text:
            return int(float(text.replace('K', '')) * 1000)
        elif 'M' in text:
            return int(float(text.replace('M', '')) * 1000000)
        elif 'B' in text:
            return int(float(text.replace('B', '')) * 1000000000)
        else:
            return int(float(text))
    except:
        return 0

def get_media_type(container):
    """
    Determine the type of media in the post (image, video, article, etc.)
    """
    media_types = [
        {"selector": "div.update-components-image", "type": "Image"},
        {"selector": "div.update-components-video", "type": "Video"},
        {"selector": "div.update-components-linkedin-video", "type": "LinkedIn Video"},
        {"selector": "article.update-components-article", "type": "Article"},
        {"selector": "div.feed-shared-external-video__meta", "type": "YouTube Video"},
        {"selector": "div.feed-shared-poll", "type": "Poll"},
        {"selector": "div.feed-shared-document", "type": "Document"}
    ]
    
    for media in media_types:
        if container.select_one(media["selector"]):
            link = container.select_one(media["selector"] + " a[href]")
            if link and link.get('href'):
                return media["type"], link['href']
            return media["type"], "None"
    
    article_link = container.select_one("a.feed-shared-article__link")
    if article_link and article_link.get('href'):
        return "Article", article_link['href']
    
    return "Unknown", "None"

def extract_post_data(container):
    """
    Extract all relevant data from a LinkedIn post container
    """
    post_text_element = container.find("div", {"class": "feed-shared-update-v2__description-wrapper"})
    if not post_text_element:
        post_text_element = container.find("span", {"class": "break-words"})
    
    post_text = post_text_element.text.strip() if post_text_element else ""
    
    date_text = extract_date_text(container)
    post_date = parse_relative_date(date_text)
    post_date_str = post_date.strftime('%Y-%m-%d') if post_date else "Unknown"
    media_type, media_link = get_media_type(container)
    metrics = extract_engagement_metrics(container)
    likes_numeric = convert_to_number(metrics["likes_text"])
    comments_numeric = convert_to_number(metrics["comments_text"])
    shares_numeric = convert_to_number(metrics["shares_text"])
    
    return {
        "profile": profile_name,
        "post_date": post_date_str,
        "post_date_raw": date_text or "Unknown",
        "post_date_obj": post_date or datetime.now().date(), 
        "post_text": post_text,
        "media_type": media_type,
        "media_link": media_link,
        "likes": metrics["likes_text"],
        "likes_numeric": likes_numeric,
        "comments": metrics["comments_text"],
        "comments_numeric": comments_numeric,
        "shares": metrics["shares_text"],
        "shares_numeric": shares_numeric
    }

post_containers = linkedin_soup.find_all("div", {"class": re.compile("feed-shared-update-v2|occludable-update")})

posts_data = []
for container in post_containers:
    activity_type = container.get('data-urn', '')
    if not activity_type or ('activity' not in activity_type and ':share:' not in activity_type):
        continue
    
    post_data = extract_post_data(container)
    if post_data["post_text"].strip(): 
        posts_data.append(post_data)
        print(f"Extracted post with date: {post_data['post_date']}, likes: {post_data['likes']}")

browser.quit()

posts_data.sort(key=lambda x: x["post_date_obj"], reverse=True)

simplified_posts = []
for post in posts_data:
    simplified_posts.append({
        "post": post["post_text"],
        "likes": post["likes_numeric"]
    })

for post in posts_data:
    del post["post_date_obj"]

full_json_file = f"{profile_name}_full_posts.json"
with open(full_json_file, 'w', encoding='utf-8') as f:
    json.dump(posts_data, f, ensure_ascii=False, indent=4)

simplified_json_file = f"{profile_name}_simplified_posts.json"
with open(simplified_json_file, 'w', encoding='utf-8') as f:
    json.dump(simplified_posts, f, ensure_ascii=False, indent=4)

print(f"Full data exported to {full_json_file}")
print(f"Simplified data exported to {simplified_json_file}")
print(f"Total posts scraped: {len(posts_data)}")