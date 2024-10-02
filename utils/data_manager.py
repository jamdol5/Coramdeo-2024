import json
from datetime import datetime

class DataManager:
    # This class is used to manage the data in-memory instead of from a file
    def __init__(self, data):
        """
        Initialize DataManager with the provided in-memory data (from Streamlit secrets).
        The `data` should be a dictionary representing the accounting data.
        """
        self.data = data
        self.subcategories = ["Food", "Supplies", "Clothing", "Transportation", "Rent", "Equipment", "Miscellaneous"]

    # This method is no longer needed to load data from a file but we keep it for compatibility
    def load_data(self):
        """
        Returns the already loaded in-memory data.
        Since data is passed during initialization, we return that.
        """
        return self.data

    # Since we are working with in-memory data, there's no file to save
    def save_data(self):
        """
        This method would normally save to a file, but since we're working with in-memory data,
        this does not perform any action.
        """
        # In a real scenario, you might want to log or handle in-memory data persistence if needed.
        pass

    # This method is used to get the revenues from the in-memory data
    def get_revenues(self, year=None):
        revenues = self.data.get("revenues", {})
        if year:
            return revenues.get(str(year), [])
        else:
            all_revenues = []
            for year_revenues in revenues.values():
                all_revenues.extend(year_revenues)
            return all_revenues

    # This method is used to add a revenue to the in-memory data
    def add_revenue(self, revenue):
        year = str(datetime.fromisoformat(revenue["date"]).year)
        if year not in self.data["revenues"]:
            self.data["revenues"][year] = []
        self.data["revenues"][year].append(revenue)
        self.save_data()

    # This method is used to remove a revenue from the in-memory data
    def remove_revenue(self, year, index):
        year_str = str(year)
        if year_str in self.data["revenues"] and 0 <= index < len(self.data["revenues"][year_str]):
            del self.data["revenues"][year_str][index]
            self.save_data()

    # This method is used to get the costs from the in-memory data
    def get_costs(self, year=None):
        if year:
            return self.data["costs"].get(str(year), {})
        return self.data["costs"]

    # This method is used to add a cost event category to the in-memory data
    def add_event(self, event, year):
        year = str(year)
        if year not in self.data["costs"]:
            self.data["costs"][year] = {}
        if event not in self.data["costs"][year]:
            self.data["costs"][year][event] = {subcategory: [] for subcategory in self.subcategories}
            self.save_data()

    # This method is used to remove a cost event category from the in-memory data
    def remove_event(self, event, year):
        year = str(year)
        if year in self.data["costs"] and event in self.data["costs"][year]:
            del self.data["costs"][year][event]
            self.save_data()

    # This method is used to add a cost to the in-memory data
    def add_cost(self, event, subcategory, cost):
        year = str(datetime.fromisoformat(cost["date"]).year)
        if year not in self.data["costs"]:
            self.data["costs"][year] = {}
        if event not in self.data["costs"][year]:
            self.add_event(event, year)
        if subcategory not in self.data["costs"][year][event]:
            self.data["costs"][year][event][subcategory] = []
        self.data["costs"][year][event][subcategory].append(cost)
        self.save_data()

    # This method is used to remove a cost from the in-memory data
    def remove_cost(self, year, event, subcategory, index):
        del self.data["costs"][str(year)][event][subcategory][index]
        self.save_data()
