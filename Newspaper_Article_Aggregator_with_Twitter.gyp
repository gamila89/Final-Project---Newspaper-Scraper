import newspaper
from newspaper import Article
import time
import nltk
import json
import requests
from bs4 import BeautifulSoup as soup
from requests_oauthlib import OAuth1
import secrets

CACHE_FILENAME = "twitter_cache.json"
CACHE_DICT = {}

client_key = secrets.TWITTER_API_KEY
client_secret = secrets.TWITTER_API_SECRET
access_token = secrets.TWITTER_ACCESS_TOKEN
access_token_secret = secrets.TWITTER_ACCESS_TOKEN_SECRET
bearer_token = secrets.BEARER_TOKEN

oauth = OAuth1(client_key,
            client_secret=client_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret)

def test_oauth():
    ''' Helper function that returns an HTTP 200 OK response code and a 
    representation of the requesting user if authentication was 
    successful; returns a 401 status code and an error message if 
    not. Only use this method to test if supplied user credentials are 
    valid. Not used to achieve the goal of this assignment.'''

    url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    auth = OAuth1(client_key, client_secret, access_token, access_token_secret)
    authentication_state = requests.get(url, auth=auth).json()
    return authentication_state


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params
    AUTOGRADER NOTES: To correctly test this using the autograder, use an underscore ("_") 
    to join your baseurl with the params and all the key-value pairs from params
    E.g., baseurl_key1_value1
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key


def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    r = requests.get(baseurl, params, auth=oauth)
    return r.json()


def make_request_with_cache(baseurl, query, count):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    AUTOGRADER NOTES: To test your use of caching in the autograder, please do the following:
    If the result is in your cache, print "fetching cached data"
    If you request a new result using make_request(), print "making new request"
    Do no include the print statements in your return statement. Just print them as appropriate.
    This, of course, does not ensure that you correctly retrieved that data from your cache, 
    but it will help us to see if you are appropriately attempting to use the cache.
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    hashtag: string
        The hashtag to search for
    count: integer
        The number of results you request from Twitter
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    params = {'q':query,
            'count': count
            }
    new_key_list = []
    CACHE_DICT = open_cache() #checks that the cahce dictionary os open
    key_for_request = construct_unique_key(baseurl, params)
    if key_for_request in CACHE_DICT.keys():
        return CACHE_DICT[key_for_request]
    else:
        response = make_request(baseurl,params)
        CACHE_DICT[key_for_request] = response
        return CACHE_DICT[key_for_request]



my_url = "https://www.nytimes.com/section/technology"

CACHE_FILE_NAME = "news_cache.json"
CACHE_DICT = {}

def make_request_using_cache(url):
    cache = open_cache()
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


def search_twitter(query, tweet_fields, bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}".format(
        query, tweet_fields
    )
    response = requests.request("GET", url, headers=headers)

    print(response.status_code)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

if __name__ == "__main__":
    # Welcome Messages and Introduction
    print()
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
        print("------------------------------------------------")
        time.sleep(7)  # Allows user to get through all the text.

    print()
    print("The articles have been successfully extracted!")
    print("In total, we were able to extract " + str(len(url_list)) + " different articles!")
    
    #Retrieves the latest 10 tweets related to the keyword or phrase entered by the user
    query = input("Enter a keyword for the topic you are interested in from these articles to get their latest tweets: ")
    if not client_key or not client_secret:
        print("You need to fill in CLIENT_KEY and CLIENT_SECRET in secrets.py.")
        exit()
    if not access_token or not access_token_secret:
        print("You need to fill in ACCESS_TOKEN and ACCESS_TOKEN_SECRET in secrets.py.")
        exit()

    CACHE_DICT = open_cache()
    
    baseurl = "https://api.twitter.com/1.1/search/tweets.json"
    tweet_fields = "tweet.fields=text"
    count = 10

    make_request_with_cache(baseurl, query, count)
    
    for url in url_list:
        if query in url:
            tweet_data = search_twitter(query=query, tweet_fields=tweet_fields, bearer_token=bearer_token)
            print(tweet_data)
            print("Thanks for participating, " + name + "!")
