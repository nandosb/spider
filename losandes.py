"""Test."""

import re
import json
import mailgun
import common
from bs4 import BeautifulSoup


def fetch():
    """Fetch pick ups."""
    base_url = 'https://clasificados.losandes.com.ar'
    filter = '/mira/sSearch?m=automotores#filter-sidebar'

    html = common.fetch_html(base_url + filter)

    soup = BeautifulSoup(html, features="html.parser")

    vehicles = []

    for card_item in soup.select('div[class*="public-ad"]'):
        info = card_item.find('h5', {'class': 'font-bold'}).text.strip()

        model = re.search('HR-?V', info, re.IGNORECASE)

        data = {}

        if model and model.group(0):
            data['model'] = model.group(0)

            year = re.search('201[7-9]', info, re.IGNORECASE)

            if year and year.group(0):

                data['year'] = year.group(0)

                data['other'] = info

                link = card_item.find('a')['href']

                data['link'] = base_url + link

                data['id'] = int(re.search('[0-9]{6,7}', link).group(0))

                vehicles.append(data)

    return vehicles


def get_last_id():
    """Load last known id from file."""
    id_file = open('last_known_id_losandes.txt', 'r')
    id = id_file.read()
    id_file.close()

    if len(id) == 0:
        id = 0

    return int(id)


def set_last_id(id):
    """Save last known id to file."""
    id_file = open('last_known_id_losandes.txt', 'w')
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

    last_id = common.get_last_id('losandes')

    vehicles, new_id = common.clean_candidates(vehicles_candidates, last_id)

    print vehicles
    print last_id

    # if new vehicles...
    if len(vehicles):
        email_subject = "Nuevas camionetas Los Andes"
        email_body = json.dumps(vehicles)
        mailgun.send_simple_message(email_subject, email_body)
        common.set_last_id(new_id, 'losandes')

if __name__ == '__main__':
    main()
