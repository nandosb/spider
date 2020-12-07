"""Common functions."""
import urllib2
import ssl


def get_brand_regex():
    return "Ford|Hyundai|Renault|Kia|Honda"


def get_model_regex():
    return "kuga|eco(\s)?sport|Tucson|kwid|Sorento|[h|c]r[-|\s]?v"


def get_year_regex():
    return "201[1-7]"


def get_known_ids(provider):
    """Get all the knonw ids for a provider."""
    filename = ('known_ids_{}.txt').format(provider)

    try:
        ids = []
        with open(filename, 'r') as (id_file):
            raw_ids = id_file.readlines()
            id_file.close()
            for raw_id in raw_ids:
                ids.append(raw_id[:-1])
            return ids
    except:
        initial_value = ''
        with open(filename, 'w+') as (id_file):
            id_file.write(initial_value)
            id_file.close()
            return []


def add_new_id(id, provider):
    """Add new id to the list of known ids."""
    with open(('known_ids_{}.txt').format(provider), 'a+') as (id_file):
        id_file.write(str(id) + '\n')


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


def clean_candidates_id_list(candidates, known_ids):
    """Filter already known properties."""
    new_elements = []
    for candidate in candidates:
        if not candidate['id'] in known_ids:
            new_elements.append(candidate)

    return new_elements


def fetch_html(url):
    """Open an URL an retrieves the HTML."""
    context = ssl._create_unverified_context()
    request = urllib2.Request(url)
    request.add_header('Referer', 'http://www.python.org/')
    request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/53')
    request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
    request.add_header('Accept-Language', 'es-US,es;q=0.9,en-US;q=0.8,en;q=0.7,es-419;q=0.6')

    html = urllib2.urlopen(request, context=context).read()

    return html
