class NamedEntitiesRepository:
    def __init__(self):
        with open('files/cities.txt') as f:
            self.city_list = set(city.lower().strip() for city in f.readlines())
        with open('files/names.txt') as names_file:
            self.names_list = set(name.lower().strip() for name in names_file.readlines())

    def try_get_city(self, sentence):
        return NamedEntitiesRepository._find_in_list(sentence, self.city_list)

    def try_get_name(self, sentence):
        return NamedEntitiesRepository._find_in_list(sentence, self.names_list)

    @staticmethod
    def _find_in_list(sentence, object_list):
        for word in sentence.split():
            print(word.lower() in object_list)
            if word.lower() in object_list:
                return word

        return None


def filter_stop_words(lemmas):
    return [item for item in lemmas if len(item) > 3]
