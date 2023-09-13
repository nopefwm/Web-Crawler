import requests
import json
import uuid
from bs4 import BeautifulSoup
from azure.cosmos import CosmosClient

endpoint = "" # azure cosmos endpoint
key = "" # azure cosmos db key
database_name = "Search"
container_name = "Results"

client = CosmosClient(endpoint, key)
database = client.get_database_client(database_name)
container = database.create_container_if_not_exists(id=container_name, partition_key="/URLs")

def crawl_webpage(url, depth, max_depth):
    if depth > max_depth:
        return

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            siteTitle = soup.find("title")
            titleArray = siteTitle.contents if siteTitle else ""
            titleStr = json.dumps(titleArray)
            title = titleStr[2:-2]

            description_tag = soup.find("meta", attrs={"name": "description"})
            description = description_tag.get("content") if description_tag else ""

            keywords_tag = soup.find("meta", attrs={"name": "keywords"})
            keywords = keywords_tag.get("content") if keywords_tag else ""

            id = str(uuid.uuid4()).replace("-", "")

            document = {
                "id": (f"{id}"),
                "partition_key_path": "/URLs",
                "url": url,
                "title": title,
                "description": description,
                "keywords": keywords,
            }

            container.upsert_item(body=document)

            for link in soup.find_all('a'):
                href = link.get('href')
                if href and href.startswith('http'):
                    crawl_webpage(href, depth + 1, max_depth)
        else:
            print(f"Failed to fetch {url} with status code {response.status_code}")

    except UnicodeEncodeError as e:
        print(f"UnicodeEncodeError occurred: {str(e)}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def crawl(seed_url, max_depth):
    crawl_webpage(seed_url, 0, max_depth)

url = start # the beginning URL

crawl(url, 3) # goes to the specified url, gathers all urls in the page, goes to those urls, repeat until max_depth is reached