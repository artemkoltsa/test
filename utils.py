from fuzzywuzzy import process

class CityRepository:
    def __init__(self):
        self.fuzzy_coef = 75
        with open('files/cities.txt') as f:
            self.city_list = set(f.readlines())

    def try_get_city(self, city_name):
        city = process.extractOne(city_name, self.city_list, score_cutoff=self.fuzzy_coef)
        return city[0] if city is not None else None
