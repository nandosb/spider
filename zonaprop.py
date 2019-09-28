"""Lookup for houses at inmoclick.com.ar."""

# import re
import json
import mailgun
import common
from bs4 import BeautifulSoup


def fetch(url):
    """Fetch pick ups."""
    # Get a file-like object using urllib2.urlopen
    base_url = 'https://www.zonaprop.com.ar/'
    filter = url
    html = common.fetch_html(base_url + filter)

    soup = BeautifulSoup(html, features="html.parser")

    houses = []
    for card_item in soup.select('div[class*="posting-card"]'):

        data = {}

        link_item = card_item['data-to-posting']
        data['link'] = base_url + link_item
        data['id'] = card_item['data-id']

        description = card_item.select_one(
            'div[class*="posting-description"]'
        )

        data['description'] = description.get_text()

        price_item = card_item.select_one('span[class*="first-price"] b')

        data['price'] = price_item.get_text()

        houses.append(data)

    return houses


def main():
    """App controller."""
    provider = 'zonaprop'
    urls = [
        'casas-alquiler-maipu-con-pileta-menos-40000-pesos.html',
        'casas-alquiler-lujan-de-cuyo-con-pileta-menos-40000-pesos.html',
        'casas-alquiler-godoy-cruz-con-pileta-menos-40000-pesos.html',
        'casas-alquiler-chacras-de-coria-con-pileta-menos-40000-pesos.html',
        'casas-alquiler-carrodilla-con-pileta-menos-40000-pesos.html',
    ]
    houses_candidates = []

    for url in urls:
        candidates = fetch(url)
        houses_candidates = houses_candidates + candidates

    known_ids = common.get_known_ids(provider)

    houses = common.clean_candidates_id_list(houses_candidates, known_ids)

    print houses
    print known_ids

    # if new houses...
    if len(houses):
        email_subject = "Nuevas casas Zonaprop"
        email_body = json.dumps(houses)
        mailgun.send_simple_message(email_subject, email_body)
        for house in houses:
            common.add_new_id(house['id'], provider)


if __name__ == '__main__':
    main()
