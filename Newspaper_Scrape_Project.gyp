import newspaper
from newspaper import Article
import time
import nltk
import json
import requests
from bs4 import BeautifulSoup as soup

my_url = "https://www.nytimes.com/section/technology"

CACHE_FILE_NAME = "news_cache.json"
CACHE_DICT = {}

def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):

    contents_to_write = json.dumps(cache)
    cache_file = open(CACHE_FILE_NAME, 'w')
    cache_file.write(contents_to_write)
    cache_file.close()


def make_request_using_cache(url):
    cache = load_cache()
    if url in cache.keys(): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

def get_content_string(url):
    '''
    Purpose:
    --------
    This method extracts a content dictionary from an HTML outline of the NY Times Tech Section.
    Paramater:
    --------
    the url of the ny times tech section
    Returns:
    -------
    a list of contents
    '''
    cache_dict_response = make_request_using_cache(url)
    page_soup = soup(cache_dict_response, 'html.parser')
    # Use the below statement as a visualizer of the HTML outline.
    # print(page_soup)
    containers = page_soup.find_all("script", {"type": "application/ld+json"})

    article_list = []
    for container in containers:
        for dictionary in container:
            article_list.append(dictionary)
    article_list[0:2] = [''.join(article_list[0:2])]
    content_string = article_list[0]
    article_index = content_string.index("itemListElement")
    content_string = content_string[article_index + 18:]
    return content_string


def find_occurrences(content_string):
    '''
    Purpose:
    ----------
    finds the start and end of all correct article hyperlinks in the previously extracted content string
    Parameters:
    -----------
    the content string from the NY tymes tech section html outline
    Returns:
    --------
    lists of the starting and ending indices of the hyperlinks in the content string
    '''

    start_indices = [i for i in range(len(content_string)) if
                     content_string.startswith('https://www.nytimes.com/2021', i)]
    end_indices = [i for i in range(len(content_string)) if content_string.startswith('.html', i)]
    end_indices = [x + 5 for x in end_indices]

    if len(start_indices) > len(end_indices):
        difference = len(start_indices) - len(end_indices)
        start_indices = start_indices[:difference]
    if len(end_indices) > len(start_indices):
        difference = len(end_indices) - (len(end_indices) - len(start_indices))
        end_indices = end_indices[:difference]
    return start_indices, end_indices




def get_all_urls(start_indices, end_indices, content_string):
    '''
    Purpose:
    --------
    Extracts all article hyperlinks from the content string
    Parameters:
    ----------
    The starting and ending indices of the hyperlinks in the content string
    Returns:
    ----------
    list of urls
    '''

    url_list = []
    for i in range(len(start_indices)):
        url_list.append(content_string[start_indices[i]:end_indices[i]])
    return url_list

def summarize_article(url):
    '''
    Purpose:
    --------
    Summarizes the article and provides valuable info including images and attritbutions
    Parameters:
    -----------
    url
    Returns:
    ---------
    article summary
    '''
    article = Article(url)

    article.download()
    article.parse()
    # Punkt is a sentence tokenizer which is useful for extracting and detecting text.
    article.download('punkt') #run commamd python -m nltk.downloader 'punkt' in terminal to download punkt
    article.nlp()

    # Gets the author or authors of the article
    author_string = "Author(s): "
    for author in article.authors:
        author_string += author  # adds all authors (if more than 1) to the author string.
    print(author_string)

    # Gets the publish date of the article
    date = article.publish_date

    # strftime() converts a tuple or struct_time representing a time to a string as specified by the format argument.
    # Here, it is used to mark the month, day, and year of the date in a readable format.
    print("Publish Date: " + str(date.strftime("%m/%d/%Y")))

    # Gets the top image of the article
    print("Top Image Url: " + str(article.top_image))

    # Gets the article images
    image_string = "All Images: "
    for image in article.images:
        image_string += "\n\t" + image  # adds a newline and a tab before each image is printed
    print(image_string)
    print()

    # Gets the article summary
    print("A Quick Article Summary")
    print("----------------------------------------")
    print(article.summary)

    return article.summary


if __name__ == "__main__":
    # Welcome Messages and Introduction
    print("Welcome to the Newspaper Scrape Project. \nIn seconds, you will have access to the latest articles "
        "in the technology section of the New York Times. \nIn addition, you will also be able to know whether the "
        "article is positive or negative and the extent of the writer's bias.")
    print()

    # Getting the user input; adding an element of personalization!
    name = input("Enter your name to get started: ")

    # Console Display
    print("Welcome " + name + "! \nYou will now see the latest technology articles in the New York Times...")
    print("Extracting article hyperlinks...")
    time.sleep(2)
    print("Retrieving summaries...")
    print()
    time.sleep(2)

    # Gets all the latest URL's from the NY Times Technology Section. (see news_extract.py for more detail)
    my_url = "https://www.nytimes.com/section/technology"
    content_string = get_content_string(my_url)
    starts, ends = find_occurrences(content_string)
    url_list = get_all_urls(starts, ends, content_string)

    # Gets the article summary and performs sentiment analysis on the chosen URL.
    for url in url_list:
        print("Article URL: " + str(url))
        article_summary = summarize_article(url)
        #news_nlp.find_sentiment(article_summary)
        print("------------------------------------------------")
        time.sleep(7)  # Allows user to get through all the text.

    # Closing Messages
    print()
    print("The articles have been successfully extracted!")
    print("In total, we were able to extract " + str(len(url_list)) + " different articles!")
    print("Thanks for participating, " + name + "!")

