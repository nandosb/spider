"""Test."""

import re
import json
import mailgun
import common
from bs4 import BeautifulSoup


def fetch():
    """Fetch pick ups."""
    base_url = 'https://clasificados.losandes.com.ar'
    filter = '/mira/sSearch/m/automotores'

    print (base_url + filter)

    html = common.fetch_html(base_url + filter)

    soup = BeautifulSoup(html, features="html.parser")

    vehicles = []

    for card_item in soup.select('div[class*="public-ad"]'):
        info = card_item.find('h5', {'class': 'font-bold'}).text.strip()

        model = re.search(common.get_model_regex(), info, re.IGNORECASE)

        data = {}

        if model and model.group(0):
            data['model'] = model.group(0)

            year = re.search(common.get_year_regex(), info, re.IGNORECASE)

            if year and year.group(0):

                data['year'] = year.group(0)

                data['other'] = info

                link = card_item.find('a')['href']

                data['link'] = base_url + link

                data['id'] = int(re.search('[0-9]{6,7}', link).group(0))

                vehicles.append(data)

    return vehicles


def main():
    """App controller."""
    vehicles_candidates = fetch()

    last_id = common.get_last_id('losandes')

    vehicles, new_id = common.clean_candidates(vehicles_candidates, last_id)

    print(vehicles)
    print(last_id)

    # if new vehicles...
    if len(vehicles):
        email_subject = "Nuevas camionetas Los Andes"
        email_body = json.dumps(vehicles)
        mailgun.send_simple_message(email_subject, email_body)
        common.set_last_id(new_id, 'losandes')


if __name__ == '__main__':
    main()
