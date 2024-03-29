from bs4 import BeautifulSoup, Comment
import requests

def get_soup_from_internet(url):

    if "https://annas-archive" not in url:
        return "Not valid url"

    response = requests.get(url).text

    if len(response) != 0:
        soup = BeautifulSoup(response, 'html.parser')
        return soup

    else:
        return None

def extract_from_comments(soup):
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    all_data = []
    for comment in comments:
        comment_soup = BeautifulSoup(comment, 'html.parser')
        elements = comment_soup.find_all("a", class_="js-vim-focus")
        all_data.extend(elements)
    return all_data

def get_books(page):

    if page == "Not valid url":
        return {"message": "Not valid url"}

    elif page is None:
        return {"message": "internal error"}
       
    a = extract_from_comments(page)

    if len(a) == 0:
        return {"message": "No books found"}

    result = {}

    for i, a_tag in enumerate(a[:51]):
        title = a_tag.find("h3").get_text() if a_tag.find("h3") else "No Title Found"

        authors = a_tag.find(attrs={"class": "italic"}).get_text() if a_tag.find(attrs={"class": "italic"}) else "No Authors Found"

        href = a_tag["href"]

        result_piece = {
            "title": title,
            "authors": authors,
            "href": href
        }

        result[i] = result_piece

    return result
