"""Common functions."""


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
