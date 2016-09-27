import requests
from client import slack_client as sc


URL = 'https://api.fastpokemap.se/?key=allow-all&ts=0&lat={0}&lng={1}'


HEADERS = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Origin': 'https://fastpokemap.se',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
}


COMMON = [
    "caterpie",
    "weedle",
    "pidgey",
    "rattata",
    "spearow",
    "zubat",
    "oddish",
    "paras",
    "drowzee"
]


RARE = [
    "lapras",
    "snorlax",
    "dratini",
    "dragonair",
    "dragonite",
    "porygon",
    "gyarados"
]


LOCATIONS = {
    "fountain": (40.8183, -96.70045),
    "kauffman": (40.8196729, -96.7004605),
    "bulubox": (40.8149308, -96.7023599),
    "hudl": (40.8149179, -96.7090976),
    "pba": (40.8168074, -96.7119382),
    "avery": (40.8193549, -96.7045140),
    "cba": (40.8178122, -96.7035162),
    "horseshoe": (40.8205647, -96.7025721)
}

LOCATION_GROUPS = {
    "campus": { "kauffman", "fountain", "avery", "cba", "horseshoe" },
    "haymarket": {"hudl", "pba" }
}


crontable = []
outputs = []


def hit_api(location):
    try:
        print("hitting api for {0}".format(location))
        url = URL.format(*LOCATIONS[location])
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        if 'result' not in data:
            return hit_api(location)
        return data
    except Exception:
        return hit_api(location)


def emoji(pokemon):
    return ':{0}:'.format(pokemon.lower())


def send_message(channel, message):
    sc.api_call("chat.postMessage", channel=channel, text=message, as_user=True)


def ping_location(channel, location):
    send_message(channel, ":mag: Looking for Pokemon at {0}".format(location))
    data = hit_api(location)
    pokemon = [p['pokemon_id'].lower() for p in data['result'] if 'pokemon_id' in p]
    pokemon = [p for p in pokemon if p not in COMMON]
    rare = [p for p in pokemon if p in RARE]
    pokemon = ' '.join([emoji(p) for p in pokemon])
    message = "Found near {0}: {1}".format(location, pokemon)
    if len(rare):
        rares = ' '.join([emoji(p) for p in rare])
        message += '\n@channel RARE POKEMON! {0}\n'.format(rares)
    send_message(channel, message)


def invalid_location(location):
    message = "Location '{0}' not found".format(location)
    message += "\nTry one of the following: {0}".format(', '.join(LOCATIONS))
    return message


def process_message(data):
    if '<@' in data['text'] and ' ping ' in data['text']:
        print(data['text'])
        location = data['text'].split(' ')[-1]
        if location == 'ping' or location == 'everywhere':
            print("everywhere")
            for location in LOCATIONS:
                ping_location(data['channel'], location)
        elif location in LOCATION_GROUPS:
            for location in LOCATION_GROUPS[location]:
                ping_location(data['channel'], location)
        elif location not in LOCATIONS:
            print("invalid")
            outputs.append([data['channel'], invalid_location(location)])
        else:
            print("valid")
            ping_location(data['channel'], location)
