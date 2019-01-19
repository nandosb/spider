"""Lookup for vehicles at DeRuedas.com."""

import re
import json
import mailgun
import common
from urllib2 import urlopen
from bs4 import BeautifulSoup


def fetch():
    """Fetch pick ups."""
    # Get a file-like object using urllib2.urlopen
    base_url = 'https://www.deruedas.com.ar/'
    html = urlopen(base_url + 'bus.asp?segmento=0')

    soup = BeautifulSoup(html, features="html.parser")

    vehicles = []
    # Loop over all <tr> elements with class 'ec_bg1_tr' or 'ec_bg2_tr'
    for div in soup.find_all(id=re.compile('car_')):
        card = div.find('a', {'class': 'titulo'}).parent.parent.parent

        data = {}

        data['id'] = int(div['id'][4:])

        brand = re.search(
            'Renault',
            card.text,
            re.IGNORECASE
        )

        if brand:
            data['brand'] = brand.group(0)
            model = re.search('Duster', card.text, re.IGNORECASE)

            if model:
                data['model'] = model.group(0)
                year = re.search('201[2-7]', card.text, re.IGNORECASE)

                if year:
                    data['year'] = year.group(0)
                    data['link'] = base_url + 'result.asp?cod={}'.format(data['id'])

                    price = re.search(
                        '\$ [0-9]{6,7}',
                        card.text,
                        re.IGNORECASE
                    )

                    if price:
                        data['price'] = price.group(0)

                    vehicles.append(data)

    return vehicles


def get_last_id():
    """Load last known id from file."""
    id_file = open('last_known_id.txt', 'r')
    id = id_file.read()
    id_file.close()

    if len(id) == 0:
        id = 0

    return int(id)


def set_last_id(id):
    """Save last known id to file."""
    id_file = open('last_known_id.txt', 'w')
    id_file.write(str(id))
    id_file.close()


def clean_candidates(vehicles, last_known_id):
    """Only report new vehicles."""
    results = []
    last_id = last_known_id

    for vehicle in vehicles:
        if vehicle['id'] > last_known_id:
            results.append(vehicle)
            if vehicle['id'] > last_id:
                last_id = vehicle['id']

    return (results, last_id)


def main():
    """App controller."""
    vehicles_candidates = fetch()

    last_id = common.get_last_id('deruedas')

    vehicles, new_id = common.clean_candidates(vehicles_candidates, last_id)

    print vehicles
    print last_id

    # if new vehicles...
    if len(vehicles):
        email_subject = "Nuevas camionetas DeRuedas"
        email_body = json.dumps(vehicles)
        mailgun.send_simple_message(email_subject, email_body)
        common.set_last_id(new_id, 'deruedas')

if __name__ == '__main__':
    main()
