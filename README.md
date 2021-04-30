


The packages/modules required to run this program are as follows:

Newspaper: used to extract and curate articles from all types of news sites such as NY times, BBC, CNN, FOX News and many more. It has seamless language extraction and detection. You can find more details about this library in the following link: https://newspaper.readthedocs.io/en/latest/

NLTK: Natural Language Tool Kit

 The following commands are required to install the newspaper and nltk modules:
    - Pip3 install newspaper3k
    - Sudo pip install nltk
    - pip install requests

Enter your name once you run the program. Wait for a minute or 2 for the program to finish extracting the top 9 articles from NY times.
Once articles are summarized, you will be prompted with a message to enter a keyword for the topic you are interested in.
The code will search twitter in order to retrieve the latest tweets that contain that keyword or phrase. The only condition is for that keyword to be related to the articles retrieved after running the program. Any keyword that is not found in the article url keywords will return no results.

Functions used in this program are:
1-	get_content_string(url): This method extracts a content dictionary from an HTML outline of the NY Times Tech Section. It takes a url of the NY times technology section and returns a list of contents.
2-	Find_occurrences(content_string): finds the start and end of all correct article hyperlinks in the previously extracted content string. It takes the content string from the NY times tech section html outline and returns a list of the starting and ending indices of the hyperlinks in the content string
3-	Get_all_urls(start_indices, end_indices, content_string): Extracts all article hyperlinks from the content string. It takes the starting and ending indices of the hyperlinks in the content string and returns a list of urls.
4-	Summarize_article(url): Summarizes the article and provides valuable info including images and attributions. It takes a url and returns article.summary
5- search_twitter(query, tweet_feilds, bearer_token): retrieves the latest 10 tweets about the topic of interest found in the extracted summaries.
