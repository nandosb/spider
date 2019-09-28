"""Lookup for houses at inmoclick.com.ar."""

import re
import json
import mailgun
import common
from bs4 import BeautifulSoup


def fetch():
    """Fetch pick ups."""
    # Get a file-like object using urllib2.urlopen
    base_url = 'https://www.inmoclick.com.ar/'
    filter = 'inmuebles/alquiler/casas?favoritos=0&limit=48&returnCompleteMap=0&prevEstadoMap=&localidades=7%2C8%2C502&precio%5Bmin%5D=&precio%5Bmax%5D=40000&moneda=1&sup_cubierta%5Bmin%5D=&sup_cubierta%5Bmax%5D=&sup_total%5Bmin%5D=&sup_total%5Bmax%5D='
    html = common.fetch_html(base_url + filter)

    soup = BeautifulSoup(html, features="html.parser")

    houses = []
    for card_item in soup.select('article[class*="item"]'):

        data = {}

        pileta = re.search('pileta|piscina', card_item.text, re.IGNORECASE)

        if pileta:

            link_item = card_item.select_one('a[itemprop="url"]')

            data['id'] = card_item['usr_id'] + '-' + card_item['prp_id']
            data['link'] = base_url + link_item['href'][1:]

            description = card_item.select_one(
                'div[class*="description-hover"] p'
            )

            data['description'] = description.get_text()

            price_item = card_item['precio']

            data['price'] = price_item

            houses.append(data)

    return houses


def main():
    """App controller."""
    houses_candidates = fetch()

    known_ids = common.get_known_ids('inmoclick')

    houses = common.clean_candidates_id_list(houses_candidates, known_ids)

    print houses
    print known_ids

    # if new houses...
    if len(houses):
        email_subject = "Nuevas casas Inmoclick"
        email_body = json.dumps(houses)
        mailgun.send_simple_message(email_subject, email_body)
        for house in houses:
            common.add_new_id(house['id'], 'inmoclick')


if __name__ == '__main__':
    main()
