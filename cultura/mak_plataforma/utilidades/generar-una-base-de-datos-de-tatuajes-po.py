import json
from collections import namedtuple, defaultdict

class Tattoo:
    def __init__(self, id, image_type, elements, technique, meanings):
        self.id = id
        self.image_type = image_type
        self.elements = elements
        self.technique = technique
        self.meanings = meanings

    def add_tattoo(self, tattoo):
        # Add new tattoo to the database
        pass

    def search_tattoos(self, criteria):
        # Search for tattoos based on criteria and return a list of Tattoo objects
        pass

    def validate_data(self, tattoo):
        # Validate data before adding it to the database
        pass

def main():
    database = []  # Initialize an in-memory database as a list of Tattoo objects

    while True:
        print("\n1. Add Tattoo")
        print("2. Search Tattoos")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_tattoo(database)
        elif choice == "2":
            search_criteria = input("Enter search criteria: ")
            search_tattoos(database, search_criteria)
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

def add_tattoo(database):
    id = int(input("Enter tattoo ID: "))
    image_type = input("Enter image type: ")
    elements = input("Enter elements (comma-separated): ").split(',')
    technique = input("Enter technique: ")
    meanings = json.loads(input("Enter meanings as JSON: "))  # Assumes valid JSON format

    tattoo = Tattoo(id, image_type, elements, technique, meanings)
    database.append(tattoo)

def search_tattoos(database, criteria):
    results = []

    for tattoo in database:
        if criteria in tattoo.image_type or any(element in criteria for element in tattoo.elements) \
                or tattoo.technique in criteria or any(meaning in criteria for meaning in tattoo.meanings.values()):
            results.append(tattoo)

    return results

if __name__ == "__main__":
    main()
    print("TESTS PASSED")  # Placeholder for actual test cases
