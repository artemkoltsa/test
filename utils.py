from fuzzywuzzy import process

class CityRepository:
    def __init__(self):
        self.fuzzy_coef = 75
        with open('files/cities.txt') as f:
            self.city_list = f.readlines()

    def try_get_city(self, city_name):
        return process.extractOne(city_name, self.city_list, score_cutoff=self.fuzzy_coef)[0]
