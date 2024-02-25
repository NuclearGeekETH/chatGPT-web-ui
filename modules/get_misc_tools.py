import requests
import xml.etree.ElementTree as ET
from .get_journals import get_soup_from_internet, get_books

def annas_response(text, history, content, filetype, sort):
    """
    Use Annas API to perform a journal search.
    """
    try:
  
        url_base = "https://annas-archive.org/search?"

        title = text.replace(" ", "+")

        final_url = f"{url_base}index=&q={title}&content={content}&ext={filetype}&sort={sort}&lang=en"

        json_response = get_books(get_soup_from_internet(final_url))

        message = []

        for key in json_response:
            item = json_response[key]
            
            message.append({
                "title": item["title"],
                "authors": item["authors"],
                "href": item["href"]
            })

        formatted_message = f"{final_url}\n\n"

        for book in message:
            authors = book["authors"].replace(";", ", ")  # Simplify the authors string
            
            book_entry = f"📖  {book['title']}\n" \
                        f"👥  {authors}\n" \
                        f"🔗 **www.annas-archive.org{book['href']}**\n\n" \
                        
            formatted_message += book_entry

        return formatted_message

    except Exception as ex:
        return f"Something went wrong: {ex}"

def parse_indeed_feed(text, history, location):
    """
    Fetch and parse the Indeed jobs RSS feed, returning jobs in a chatbot-friendly format.
    """

    # Replace 'your_rss_feed_url' with your actual RSS feed URL
    rss_feed_url = f"https://www.indeed.com/rss?q={text}&l={location}&sort=date"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        # Fetch the RSS feed data
        response = requests.get(rss_feed_url, headers=headers)
        response.raise_for_status()
        
        # Parse the XML from the response content
        root = ET.fromstring(response.content)
        
        messages = []  # Will hold our job postings formatted for the chatbot
        
        # Iterate over each item in the feed
        for item in root.findall('.//item'):
            title = item.find('title').text
            link = item.find('link').text
            description = item.find('description').text.replace('&lt;br&gt;', '\n').replace('&amp;#8230;', '...')
            
            # Construct the message
            message = F"📖 {title}\n" \
                      F"🔗 {link}\n" \
                      F"📃 {description}\n\n"
            
            messages.append(message)
            
        return ' '.join(messages)
    
    except Exception as ex:
        return F"Something went wrong: {ex}"

def edit_image(im):
    return [im["background"].size, im["background"], im["layers"][0], im["composite"]]

