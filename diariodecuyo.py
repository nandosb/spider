"""Test."""

import re
import json
import mailgun
import urllib2
from bs4 import BeautifulSoup


def fetch():
    """Fetch pick ups."""
    base_url = 'http://www.clasicuyo.com.ar/'
    filter = 'Busqueda.php?s=camionetas-utilitarios&r=vehiculos'

    request = urllib2.Request(base_url + filter)
    request.add_header('Referer', 'http://www.python.org/')
    request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/53')
    request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
    request.add_header('Accept-Language', 'es-US,es;q=0.9,en-US;q=0.8,en;q=0.7,es-419;q=0.6')

    html = urllib2.urlopen(request)

    soup = BeautifulSoup(html, features="html.parser")

    vehicles = []

    for card_item in soup.select_one('ul[class*="listadoBusqueda"]').children:

        info = card_item.text.strip()

        model = re.search('Amarok|Ranger|Hilux|S10|S-10', info, re.IGNORECASE)

        data = {}

        if model and model.group(0):

            data['model'] = model.group(0)

            year = re.search('2015|2016|2017|2018|2019', info, re.IGNORECASE)

            if year and year.group(0):

                data['year'] = year.group(0)

                data['other'] = info

                link = card_item.find('a')['href']

                data['link'] = base_url + link

                data['id'] = int(re.search(
                    '[0-9]{7,8}',
                    card_item.find('article')['id']).group(0)
                )

                vehicles.append(data)

    return vehicles


def get_last_id():
    """Load last known id from file."""
    id_file = open('last_known_id_diariodecuyo.txt', 'r')
    id = id_file.read()
    id_file.close()

    if len(id) == 0:
        id = 0

    return int(id)


def set_last_id(id):
    """Save last known id to file."""
    id_file = open('last_known_id_diariodecuyo.txt', 'w')
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
    last_id = get_last_id()

    vehicles, new_id = clean_candidates(vehicles_candidates, last_id)

    print vehicles
    print last_id

    # if new vehicles...
    if len(vehicles):
        email_subject = "Nuevas camionetas Diario de Cuyo"
        email_body = json.dumps(vehicles)
        mailgun.send_simple_message(email_subject, email_body)
        set_last_id(new_id)


if __name__ == '__main__':
    main()
