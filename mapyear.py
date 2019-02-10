from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium


def add_dct(dct, words):
    """
    (dct, str) -> dct
    Adds to the dictionary a movie and its location

    e.g.
    {"The Wizard of Oz (1939)" : ["Culver City"}
    """
    dct[words[0]] = [words[0]]
    locations = words[-1].strip().split(",")
    loc = locations[0]
    dct[words[0]].append(loc)
    return dct


def collect_movies(filename, given_years, from_line=""):
    """
    (str, str) -> dct
    Creates the dictionary of movies released in 2018 and its location.

    e.g.
    {"The Wizard of Oz (1939)" : ["Culver City"}
    """
    movies_0 = {}
    movies_1 = {}
    movies_2 = {}
    year = 0
    with open(filename, encoding='utf-8', errors='ignore') as f:
        for line in f:
            if from_line != "":
                if line.startswith(from_line):
                    from_line = ""
                continue
            words = line.strip().split("\t")
            if len(words) >= 2:
                for i in range(len(words[0])):
                    if words[0][i] == "(":
                        year = words[0][i+1:i+5]
                        break
                if year == given_years[0]:
                    movies_0 = add_dct(movies_0, words)
                elif year == given_years[1]:
                    movies_1 = add_dct(movies_1, words)
                elif year == given_years[2]:
                    movies_2 = add_dct(movies_2, words)
    return movies_0, movies_1, movies_2


def movies_loc(movies):
    """
    (dct) -> dct
    Creates new dictionary of movies
    and its location's latitude and longitude
    """
    new_movies = {}

    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    for movie in movies:
        loc = movies[movie][1]
        name = movies[movie][0]
        try:
            location = geolocator.geocode(loc)
            new_movies[movie] = [name, location.address,
                                 (location.latitude, location.longitude)]
        except AttributeError:
            continue
    return new_movies


def map_create(movies, year):
    """
    (dct, str) -> folium.map.FeatureGroup
    Creates one layer of the map
    """

    l_name = year + "'s year films"
    fg = folium.FeatureGroup(name=l_name)
    for movie in movies:
        loc = movies[movie][-1]
        lat = loc[0]
        lon = loc[1]
        name_loc = movies[movie][0] + "\n" + movies[movie][1]
        fg.add_child(folium.Marker(location=[lat, lon],
                                   popup=name_loc,
                                   icon=folium.Icon()))
    return fg


def start():
    """
    Asks for 3 years which need to be analysed.
    Calls all other functions and creates a map.
    """
    years = []
    n = input("Please enter a year: ")
    years.append(n)
    m = input("Please enter a second year:")
    years.append(m)
    k = input("Please enter a third year:")
    years.append(k)
    movies_0, movies_1, movies_2 = collect_movies("locations.list",
                                                  years, "LOCATIONS LIST")
    movies_loc_0 = movies_loc(movies_0)
    movies_loc_1 = movies_loc(movies_1)
    movies_loc_2 = movies_loc(movies_2)

    layer0 = map_create(movies_loc_0, years[0])
    layer1 = map_create(movies_loc_1, years[1])
    layer2 = map_create(movies_loc_2, years[2])
    map = folium.Map()
    map.add_child(layer0)
    map.add_child(layer1)
    map.add_child(layer2)
    map.add_child(folium.LayerControl())
    map.save('Map_y1.html')


start()
