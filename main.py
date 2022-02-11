"""
Creates a map with 10 locations where films where created in chosen year
"""
import folium, argparse
from geopy.geocoders import Nominatim
from math import sqrt, sin, cos, asin, radians


def get_arguments():
    """
    Gets arguments from command line
    :return: args: arguments from a command line
    """
    parser = argparse.ArgumentParser(description='Creates map with locations, '
                                                 'where films where created')
    parser.add_argument("year",
                        type=str,
                        help="Year, when films were created")
    parser.add_argument("latitude",
                        type=str,
                        help="Latitude of location")
    parser.add_argument("longitude",
                        type=str,
                        help="Longitude of location")
    parser.add_argument("path_to_dataset",
                        type=str,
                        help="Path to dataset with films")
    return parser.parse_args()


def read_file(path: str) -> list:
    """
    Read a content of dataframe
    :param path: path to file
    :return: content of file line by line
    """
    with open(path, encoding='iso-8859-1') as file:
        content = file.read().split("\n")
    return content


def get_films(file_content, year, coordinates):
    """
    Find ten places where films where made chosen year
    :param file_content: list with lines of file
    :param year: str
    :param coordinates: tuple with latitude and longitude
    :return: list with lists of 10 films, locations where they where createn and
    coordinate
    >>> get_films(['LOCATIONS LIST','==============',\
    '"#1 Single" (2006)\\tLos Angeles, California, USA',\
    '"#1 Single" (2006)\\tNew York City, New York, USA)'],\
    "2006", (45.7597, 4.8422))
    [['"#1 Single" (2006)', 'New York City, New York, USA)', \
6146.7769944449665, (40.7127281, -74.0060152)], ['"#1 Single" (2006)', \
'Los Angeles, California, USA', 9461.273402587134, (34.0536909, -118.242766)]]
    """
    films = []
    for line in file_content:
        if not ("(" + year) in line:
            continue
        film_inform = list(filter(None, line.split("\t")))
        coordinates_2 = get_geolocation(film_inform)
        if coordinates_2 is None:
            continue
        distance = haversine(coordinates, coordinates_2)
        films.append(film_inform[:2] + [distance] + [coordinates_2])
    return sorted(films, key=lambda x: x[2])[:10]


def chornobyl_films(file_content):
    """
    Find all films createn in Chornobyl
    :param file_content: list with lines of file
    :return: list with lists with information about filmes
    >>> chornobyl_films(['"Extreme" (2009) {Tours}\\tChernobyl, Ukraine',\
    '"10" (2009)\\tKuala Lumpur, Malaysia	(on location)'])
    [['"Extreme" (2009) {Tours}', 'Chernobyl, Ukraine', \
(51.2705477, 30.2195609)]]
    """
    ch_films = []
    for line in file_content:
        if (not "Chernobyl, Ukraine" in line) and \
                (not "Pripyat, Ukraine" in line):
            continue
        film_inform = list(filter(None, line.split("\t")))
        coordinates_2 = get_geolocation(film_inform)
        if coordinates_2 is None:
            continue
        ch_films.append(film_inform[:2] + [coordinates_2])
    return ch_films


def get_geolocation(film_inform):
    """
    Find coordinates where films was created
    :param film_inform: film and place where it was created
    :return: tuple with latitude and longitude
    """
    try:
        geolocator = Nominatim(user_agent="geopyLab")
        location = geolocator.geocode(film_inform[1])
        while location is None:
            if len(film_inform[1].split(", ")) > 2:
                film_inform[1] = film_inform[1].split(", ")[-2].join(", ")
                location = geolocator.geocode(film_inform[1])
            elif len(film_inform[1].split(", ")) == 2:
                film_inform[1] = film_inform[1][-1]
                location = geolocator.geocode(film_inform[1])
            else:
                break
        if location is not None:
            coordinates = (location.latitude, location.longitude)
            return coordinates
    except TimeoutError:
        return None

def haversine(coordinate_1, coordinate_2):
    """
    Calculate distance between two dots on sphere
    :param coordinate_1: latituted and longitude of first dot
    :param coordinate_2: latituted and longitude of second dot
    :return: distance
    >>> haversine((45.7597, 4.8422), (48.8567, 2.3508))
    392.21671780659625
    """
    latitude_1 = radians(coordinate_1[0])
    longitude_1 = radians(coordinate_1[1])
    latitude_2 = radians(coordinate_2[0])
    longitude_2 = radians(coordinate_2[1])
    earth_radius = 6371
    result = 2 * earth_radius * asin(sqrt(sin((latitude_2 - latitude_1) / 2)
                                          ** 2 + cos(latitude_1) *
                                          cos(latitude_2) *
                                          sin((longitude_2 - longitude_1) / 2)
                                          ** 2))
    return result


def create_map(year, close_films, ch_films, coordinates):
    """
    Creates html file with map
    :param year: year, when films were created
    :param close_films: list with information about films
    :param ch_films: list with information about chornobyl films
    :param coordinates: coordinates where you want to start the map
    :return: None
    """
    map = folium.Map(location=list(coordinates),
                     zoom_start=10)
    closest_places = folium.FeatureGroup(name=year + " Films")
    previous_film = 0
    previous_film_coordinate = 0
    for film in close_films:
        if film[-1] == previous_film:
            film[-1] = list(film[-1])
            film[-1][0] = previous_film_coordinate[0] + 0.0001
        else:
            previous_film = film[-1]
        previous_film_coordinate = film[-1]
        closest_places.add_child(folium.Marker(location=list(film[-1]),
                                               popup=film[0],
                                               icon=folium.Icon()))
    map.add_child(closest_places)
    chornobyl = folium.FeatureGroup(name="Chornobyl Films")
    iterator = 0
    for film in ch_films:
        chornobyl.add_child(folium.Marker(location=[film[-1][0] + (-1) **
                                                    iterator * iterator *
                                                    0.0001, film[-1][1] + (-1)
                                                    ** iterator * iterator *
                                                    0.0001],
                                          popup=film[0],
                                          icon=folium.Icon()))
        iterator  += 1
    map.add_child(chornobyl)
    map.add_child(folium.LayerControl())
    map.save('film_map.html')


def main():
    """
    Main function
    :return: None
    """
    args = get_arguments()
    year = args.year
    latitude = args.latitude
    longitude = args.longitude
    path = args.path_to_dataset
    content = read_file(path)
    films = get_films(content, year, (float(latitude), float(longitude)))
    ch_films = chornobyl_films(content)
    create_map(year, films, ch_films, (float(latitude), float(longitude)))


if __name__ == "__main__":
    main()
