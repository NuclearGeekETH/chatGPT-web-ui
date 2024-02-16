import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

subscription_key = os.getenv('BING_SEARCH_V7_SUBSCRIPTION_KEY')
search_endpoint =  "https://api.bing.microsoft.com/v7.0/search"
news_endpoint =  "https://api.bing.microsoft.com/v7.0/news/search"

def bing_search(text, history):
    """
    Use Bing API to perform a web search and return the first 10 snippets.
    """
    # Query term(s) to search for. 
    # Construct a request
    params = {'q': text}
    headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

    # Call the API
    try:
        response = requests.get(search_endpoint, headers=headers, params=params)
        response.raise_for_status()

        # Parse the response JSON
        search_results = response.json()

        # Check if there are webPages results available
        if 'webPages' in search_results and 'value' in search_results['webPages']:

            message_response = []

            for result in search_results['webPages']['value']:
                name = result["name"] 
                url = result["url"]
                snippet = result["snippet"]

                message = F"📖 {name}\n" \
                    F"🔗 {url}\n" \
                    F"📃 {snippet}\n\n"


                message_response.append(message)

            concatenated_message = ' '.join(message_response)

            return concatenated_message

        else:
            return "No web page results found."
    
    except Exception as ex:
        return F"Something went wrong: {ex}"

def bing_news(text, history):
    """
    Use Bing API to perform a news search and return the first snippet.
    """
    # Query term(s) to search for. 
    # Construct a request
    params = {'q': text}
    headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

    # Call the API
    try:
        response = requests.get(news_endpoint, headers=headers, params=params)
        response.raise_for_status()

        # Parse the response JSON
        search_results = response.json()

        # Check if there are webPages results available
        if 'value' in search_results:
            
            message_response = []

            for article in search_results["value"]:
                name = article["name"]
                url = article["url"]
                description = article["description"]
                date_published = article["datePublished"]

                date_obj = datetime.fromisoformat(date_published.replace('Z', '+00:00'))

                # Format the datetime object into a more readable string
                # For example: "January 09, 2024 at 21:18"
                readable_date = date_obj.strftime("%B %d, %Y at %H:%M")

                message = F"📖 {name}\n" \
                    F"🔗 {url}\n" \
                    F"📅 {readable_date}\n" \
                    F"📃 {description}\n\n"

                message_response.append(message)


            concatenated_snippets = ' '.join(message_response)

            return concatenated_snippets

        else:
            return "No news results found."
    
    except Exception as ex:
        return f"Something went wrong: {ex}"

