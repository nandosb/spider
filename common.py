"""Common functions."""
import urllib2
import ssl


def get_last_id(provider):
    """Load last known id from file."""
    filename = ('last_known_id_{}.txt').format(provider)

    try:
        with open(filename, 'r') as (id_file):
            id = id_file.read()
            id_file.close()
            if len(id) == 0:
                id = 0
            return int(id)
    except:
        initial_value = '0'
        with open(filename, 'w+') as (id_file):
            id_file.write(initial_value)
            id_file.close()
            return int(initial_value)


def set_last_id(id, provider):
    """Save last known id to file."""
    with open(('last_known_id_{}.txt').format(provider), 'w') as (id_file):
        id_file.write(str(id))


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


def fetch_html(url):
    """open an URL an retrieves the HTML"""
    context = ssl._create_unverified_context()
    request = urllib2.Request(url)
    request.add_header('Referer', 'http://www.python.org/')
    request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/53')
    request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
    request.add_header('Accept-Language', 'es-US,es;q=0.9,en-US;q=0.8,en;q=0.7,es-419;q=0.6')

    html = urllib2.urlopen(request, context=context).read()

    return html
