"""Lookup for vehicles at Napsix.com."""

import re
import json
import mailgun
import common
from bs4 import BeautifulSoup


def price_to_number(price_string):
    """Convert price to integer."""
    price_digits = []
    price_as_string = '0'

    if(len(price_string)):
        for character in price_string:
            number = re.search('[0-9]', character)
            if number and number.group(0):
                price_digits.append(number.group(0))

        price_as_string = ''.join(price_digits)

    return int(price_as_string)


def fetch():
    """Fetch pick ups."""
    # Get a file-like object using urllib2.urlopen
    base_url = 'https://napsix.mdzol.com/'
    filter = 'index.php?r=search%2Fcategory&slug=vehiculos&search%5Bsort%5D=date_desc&search%5Bcategories%5D=&search%5Bcategories%5D%5B%5D=64&search%5Bcategories%5D%5B%5D=25&search%5BpriceFrom%5D=&search%5BpriceTo%5D=&search%5Battribs%5D%5B7%5D%5B%5D=Ford&search%5BmainLocation%5D=7&search%5Blocations%5D=&search%5Bfiltered%5D=1'
    html = common.fetch_html(base_url + filter)

    soup = BeautifulSoup(html, features="html.parser")

    vehicles = []
    for card_item in soup.select('div[class*="responsive-publication"]'):

        data = {}

        model = re.search(common.get_model_regex(), card_item.text, re.IGNORECASE)

        if model:

            data['model'] = model.group(0)

            link_item = card_item.select_one('a')
            id_item = card_item.select_one('div[class*="favourite"]')

            data['id'] = int(id_item['data-id'])
            data['link'] = base_url + link_item['href'][1:]

            year = re.search(common.get_year_regex(), card_item.text, re.IGNORECASE)

            if year and year.group(0):
                data['year'] = year.group(0)

            price_item = card_item.select_one('span[itemprop="price"]')
            price = re.search(
                '\$.{7,10}',
                price_item.text.strip(),
                re.IGNORECASE
            )

            data['price'] = '0'
            if price and price.group(0):
                data['price'] = price.group(0)

            numeric_price = price_to_number(data['price'])
            if 'year' in data or numeric_price >= 450000:
                vehicles.append(data)

    return vehicles


def main():
    """App controller."""
    vehicles_candidates = fetch()

    last_id = common.get_last_id('napsix')

    vehicles, new_id = common.clean_candidates(vehicles_candidates, last_id)

    print vehicles
    print last_id

    # if new vehicles...
    if len(vehicles):
        email_subject = "Nuevas camionetas Napsix"
        email_body = json.dumps(vehicles)
        mailgun.send_simple_message(email_subject, email_body)
        common.set_last_id(new_id, 'napsix')


if __name__ == '__main__':
    main()
