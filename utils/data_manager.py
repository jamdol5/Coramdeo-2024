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
        """
        Get costs for a given year or return all costs if no year is specified.
        Safely handle cases where 'costs' or specific years do not exist.
        """
        costs = self.data.get("costs", {})
        if year:
            return costs.get(str(year), {})  # Return an empty dict if the year or costs are missing
        return costs

    # This method is used to add a cost event category to the in-memory data
    def add_event(self, event, year):
        """
        Add a new event to the costs data for the specified year.
        Ensures that the year and event exist in the costs data structure.
        """
        year = str(year)
        if "costs" not in self.data:
            self.data["costs"] = {}  # Ensure that 'costs' exists

        if year not in self.data["costs"]:
            self.data["costs"][year] = {}

        if event not in self.data["costs"][year]:
            self.data["costs"][year][event] = {subcategory: [] for subcategory in self.subcategories}

        self.save_data()

    # This method is used to remove a cost event category from the in-memory data
    def remove_event(self, event, year):
        """
        Remove an event from the costs data for the specified year.
        """
        year = str(year)
        if "costs" in self.data and year in self.data["costs"] and event in self.data["costs"][year]:
            del self.data["costs"][year][event]
            self.save_data()

    # This method is used to add a cost to the in-memory data
    def add_cost(self, event, subcategory, cost):
        """
        Add a cost under a specific event and subcategory for the specified year.
        """
        year = str(datetime.fromisoformat(cost["date"]).year)

        # Ensure 'costs' exists
        if "costs" not in self.data:
            self.data["costs"] = {}

        # Ensure the year exists in 'costs'
        if year not in self.data["costs"]:
            self.data["costs"][year] = {}

        # Ensure the event exists in the specified year
        if event not in self.data["costs"][year]:
            self.add_event(event, year)

        # Ensure the subcategory exists under the event
        if subcategory not in self.data["costs"][year][event]:
            self.data["costs"][year][event][subcategory] = []

        # Add the cost to the specified subcategory
        self.data["costs"][year][event][subcategory].append(cost)
        self.save_data()

    # This method is used to remove a cost from the in-memory data
    def remove_cost(self, year, event, subcategory, index):
        """
        Remove a cost at a given index from a specific event and subcategory.
        """
        year = str(year)
        if (
            "costs" in self.data and
            year in self.data["costs"] and
            event in self.data["costs"][year] and
            subcategory in self.data["costs"][year][event]
        ):
            del self.data["costs"][year][event][subcategory][index]
            self.save_data()

    # Since we are working with in-memory data, there's no file to save
    def save_data(self):
        """
        This method would normally save to a file, but since we're working with in-memory data,
        this does not perform any action.
        """
        pass  # If using in-memory data, you may persist it via another method, if necessary.
