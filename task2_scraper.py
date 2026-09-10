import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time
import re

BASE_URL = "https://www.lexaloffle.com"
START_URL = "https://www.lexaloffle.com/bbs/?cat=7"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_soup(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def clean(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def get_game_links(soup):
    """
    Get individual PICO-8 thread/game links.
    The BBS listing uses ?tid=XXXX.
    """

    links = []

    for a in soup.find_all("a", href=True):

        href = a["href"]

        if "?tid=" in href or "&tid=" in href:

            url = urljoin(BASE_URL, href)

            if url not in links:
                links.append(url)

    return links


def scrape_game(url):

    print("Scraping:", url)

    soup = get_soup(url)

    
    game_name = ""

    h1 = soup.find("h1")

    if h1:
        game_name = clean(h1.get_text())

    if not game_name:
        title = soup.find("title")
        if title:
            game_name = clean(title.get_text())



    author = ""

    # The page has:
    # Game Name
    # by
    # Author

    for a in soup.find_all("a", href=True):

        href = a.get("href", "")

        if "uid=" in href:

            author = clean(a.get_text())

            if author:
                break



    artwork = ""

    for img in soup.find_all("img", src=True):

        src = img["src"]

        if src:

            full_url = urljoin(BASE_URL, src)

            # Avoid tiny UI images
            if "avatar" not in src.lower():
                artwork = full_url
                break




    game_code = ""

    for a in soup.find_all("a", href=True):

        href = a["href"]
        text = clean(a.get_text()).lower()

        if (
            "cart" in text
            or ".p8" in href.lower()
            or "cartfile" in text
        ):

            game_code = urljoin(BASE_URL, href)
            break



    license_name = ""

    page_text = clean(
        soup.get_text(" ", strip=True)
    )

    match = re.search(
        r"License:\s*([^|]+)",
        page_text,
        re.IGNORECASE
    )

    if match:
        license_name = clean(match.group(1))




    like_count = ""



    for element in soup.find_all(string=True):

        text = clean(element)

        if text.isdigit():

            number = int(text)

            # Ignore very large unrelated numbers
            if 0 <= number <= 100000:

                like_count = text
                break



    description = ""

    

    candidates = soup.find_all(
        ["p", "div"]
    )

    for element in candidates:

        text = clean(
            element.get_text(" ", strip=True)
        )

        if len(text) >= 40:

            lower = text.lower()

            # Ignore navigation / metadata
            ignored = [
                "subscribe to this thread",
                "receive email notifications",
                "mark as spam",
                "mark as abuse",
                "log in",
                "pin to profile"
            ]

            if not any(
                word in lower
                for word in ignored
            ):

                description = text
                break




    comments = []

    # Comments are usually text blocks following
    # user/date information.

    for element in soup.find_all(["p", "div"]):

        text = clean(
            element.get_text(" ", strip=True)
        )

        if (
            20 <= len(text) <= 2000
        ):

            lower = text.lower()

            ignored = [
                "subscribe to this thread",
                "receive email notifications",
                "mark as spam",
                "mark as abuse",
                "pin to profile",
                "log in to post"
            ]

            if any(
                word in lower
                for word in ignored
            ):
                continue

            if text not in comments:
                comments.append(text)

    top_comments = comments[:5]


    return {
        "Name of game": game_name,
        "Name of author": author,
        "Game artwork": artwork,
        "Game code": game_code,
        "License": license_name,
        "Like count": like_count,
        "Game description": description,
        "Top-5 comments": " || ".join(top_comments)
    }




print("=" * 70)
print("PICO-8 GAME SCRAPER")
print("=" * 70)

games = []
visited = set()

page_number = 1

while len(games) < 100:

    if page_number == 1:
        url = START_URL
    else:
        url = f"{START_URL}&page={page_number}"

    print(
        f"\nReading page {page_number}: {url}"
    )

    try:

        soup = get_soup(url)

    except Exception as e:

        print("Could not load page:", e)
        break


    game_links = get_game_links(soup)

    print(
        "Game links found:",
        len(game_links)
    )


    if not game_links:
        print("No more game links found.")
        break


    for game_url in game_links:

        if len(games) >= 100:
            break

        if game_url in visited:
            continue

        visited.add(game_url)

        try:

            data = scrape_game(game_url)

            games.append(data)

            print(
                f"[{len(games)}/100] "
                f"{data['Name of game']}"
            )

        except Exception as e:

            print(
                "Failed:",
                game_url,
                "|",
                e
            )

        time.sleep(0.5)


    page_number += 1

    # Safety limit
    if page_number > 20:
        break



print("\n" + "=" * 70)
print("CREATING CSV")
print("=" * 70)

df = pd.DataFrame(games)

df = df.head(100)

output_file = "pico8_games_100.csv"

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("\nSCRAPING COMPLETED")
print("------------------")

print(
    "Total games collected:",
    len(df)
)

print(
    "CSV:",
    output_file
)

print("\nColumns:")

for column in df.columns:
    print("-", column)