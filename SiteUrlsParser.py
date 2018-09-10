
from log import log as log
import time
from datetime import datetime
import random
from bs4 import BeautifulSoup as soup
from DiscordWebhooks import Webhook
from threading import Thread
import psycopg2
import requests
from bs4 import BeautifulSoup as soup
import requests


class Product():
    def __init__(self, title, link, stock, keyword):
        '''
        Takes |str, str, bool, str| for object constructor
        '''
        # Setup product object
        self.title = title
        self.stock = stock
        self.link = link
        self.keyword = keyword


def readTXT(path):
    '''
    (None) -> list of str
    Loads up all sites from the sitelist.txt file in the root directory.
    Returns the sites as a list
    '''

    # Initialize variables
    siteInfo = []
    lines = []
    # Load data and raise error if no file
    try:
        tempFile = open(path, "r")
        siteInfo = tempFile.readlines()
        tempFile.close()
    except:
        log('e', "Couldn't find " + path + ".")
        raise FileNotFound()

    if(len(siteInfo) == 0):
        raise NoDataLoaded()

    # Parse the data
    for line in siteInfo:
        lines.append(line.strip("\n"))

    # Return the data
    return lines


def sendToDataBase(product):
    '''
    Takes a Product as a paremeter and returns bool
    representing if discord notification is sent
    '''

    # Initialize variables
    title = product.title
    stock = str(product.stock)
    link = product.link
    keyword = product.keyword
    alert = False

    # Connect to Database (postgreSql)
    connString = "host='localhost' dbname='$$$' user ='postgres' password='$$$'"
    conn = pyscopg2.connect(connString)
    c = conn.cursor()
    print('DB: {} Connected').format(conn)
    c.execute("""CREATE TABLE IF NOT EXISTS products(title TEXT, link TEXT UNIQUE, stock TEXT, keywords TEXT)""")

    # Add product to database if it's unique
    try:
        c.execute("""INSERT INTO products (title, link, stock, keywords) VALUES (?, ?, ?, ?)""", (title, link, stock, keyword))
        log('s', "Found new product with keyword " + keyword + ". Link = " + link)
        alert = True
    except:
        log('i', 'Found keyword ' + keyword +' but it was already found before')
    # Close connection to the database
    conn.commit()
    c.close()
    conn.close()

    # Return whether or not it's a new product
    return alert


def send_embed(product):
    '''
    Takes a aProduct object
    Sends a discord alert based on info parsed.
    '''

    url = 'https://discordapp.com/api/webhooks/$$$$$$$$$$$$$'
    #embed discord based on DenrysEmbedded discord hooks
    embed = Webhook(url, color=123123)

    embed.set_author(name='Philly')
    embed.set_desc("Found possible product based on keyword " + product.keyword)

    embed.add_field(name="Link", value=product.link)

    embed.set_footer(text='philly_bot', ts=True)

    embed.post()


def monitor(link, keywords):
    '''
    the URL(string) is scanned and alerts
    are sent via Discord when a new product containing a keyword(list) is detected.
    '''

    log('i', "Checking site |" + link + "|...")

    # Parse the site from the link
    HTTPS = link.find("https://")
    HTTP = link.find("http://")

    if(HTTPS == 0):
        site = link[8:]
        end = site.find("/")
        if(end != -1):
            site = site[:end]
        site = "https://" + site
    else:
        site = link[7:]
        end = site.find("/")
        if(end != -1):
            site = site[:end]
        site = "http://" + site

    # Get all the links on the "New Arrivals" page
    try:
        r = requests.get(link, timeout=5, verify=False)
    except:
        log('e', "Connection to URL <" + link + "> failed. Retrying...")
        time.sleep(5)
        try:
            r = requests.get(link, timeout=8, verify=False)
        except:
            log('e', "Connection to URL| " + link + " |failed...")
            return

    page = soup(r.text, "html.parser")

    raw_links = page.findAll("a")
    hrefs = []

    for raw_link in raw_links:
        try:
            hrefs.append(raw_link["href"])
        except:
            pass

    # Check for links matching keywords
    for href in hrefs:
        found = False
        for keyword in keywords:
            if(keyword.upper() in href.upper()):
                found = True
                if("http" in href):
                    product_page = href
                else:
                    product_page = site + href
                product = Product("N/A", product_page, True, keyword)
                alert = sendToDataBase(product)

                if(alert):
                    send_embed(product)

if(__name__ == "__main__"):
    # Keywords (seperated by -)
    keywords = [
        "pharrell",
        "yeezy",
        "ovo-air-jordan",
        "ovo-jordan",
        "NMD",
        "presto",
    ]

    # Load sites from file
    sites = readTXT("Sites.txt")

    # Start monitoring sites
    while(True):
        threads = []
        for site in sites:
            timeToStart = Thread(target=monitor, args=(site, keywords))
            threads.append(t)
            timeToStart.start()
            time.sleep(2)  # 2 second delay before going to the next site
