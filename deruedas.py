"""Lookup for vehicles at DeRuedas.com."""

import re
import json
import mailgun
import common
from bs4 import BeautifulSoup


def fetch():
    """Fetch pick ups."""
    # Get a file-like object using urllib2.urlopen
    base_url = 'https://www.deruedas.com.ar/'
    filter = 'busDR.asp'

    print (base_url + filter)

    html = common.fetch_html(base_url + filter)

    soup = BeautifulSoup(html, features="html.parser")

    vehicles = []
    # Loop over all <tr> elements with class 'ec_bg1_tr' or 'ec_bg2_tr'
    for div in soup.find_all(id=re.compile('car_')):
        card = div

        data = {}

        data['id'] = int(div['id'][4:])

        brand = re.search(
            common.get_brand_regex(),
            card.text,
            re.IGNORECASE
        )

        if brand:
            data['brand'] = brand.group(0)

            model = re.search(
                common.get_model_regex(),
                card.text,
                re.IGNORECASE
            )

            if model:
                data['link'] = base_url + 'result.asp?cod={}'.format(data['id'])

                data['model'] = model.group(0)

                year = re.search(
                    common.get_year_regex(),
                    card.text,
                    re.IGNORECASE
                )

                if year:
                    data['year'] = year.group(0)

                price = re.search(
                    '\$ [0-9]{3}.{3,4}',
                    card.text,
                    re.IGNORECASE
                )
                if price:
                    data['price'] = price.group(0)

                    vehicles.append(data)
    return vehicles


def main():
    """App controller."""
    vehicles_candidates = fetch()

    last_id = common.get_last_id('deruedas')

    vehicles, new_id = common.clean_candidates(vehicles_candidates, last_id)

    print(vehicles)
    print(last_id)

    # if new vehicles...
    if len(vehicles):
        email_subject = "Nuevas camionetas DeRuedas"
        email_body = json.dumps(vehicles)
        mailgun.send_simple_message(email_subject, email_body)
        common.set_last_id(new_id, 'deruedas')


if __name__ == '__main__':
    main()
