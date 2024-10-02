import json
import os
from datetime import datetime

class DataManager:
    #this class is used to manage the data in the accounting_data.json file
    def __init__(self, filename="data/accounting_data.json"):
        self.filename = filename
        self.data = self.load_data()
        self.subcategories = ["Food", "Supplies","Clothing","Transportation","Rent","Equipment", "Miscellaneous"]

    #this method is used to load the data from the accounting_data.json file
    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        else:
            return {"revenues": {}, "costs": {}}
    
    #this method is used to save the data to the accounting_data.json file
    def save_data(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=2)

    #this method is used to get the revenues from the accounting_data.json file
    def get_revenues(self, year=None):
        revenues = self.data.get("revenues",{})
        if year:
            return revenues.get(str(year), [])
        else:
            all_revenues = []
            for year_revenues in revenues.values():
                all_revenues.extend(year_revenues)
            return all_revenues
    
     # This method is used to add a revenue to the accounting_data.json file
    def add_revenue(self, revenue):
        year = str(datetime.fromisoformat(revenue["date"]).year)
        if year not in self.data["revenues"]:
            self.data["revenues"][year] = []
        self.data["revenues"][year].append(revenue)
        self.save_data()

 # This method is used to remove a revenue from the accounting_data.json file
    def remove_revenue(self, year, index):
        year_str = str(year)
        if year_str in self.data["revenues"] and 0 <= index < len(self.data["revenues"][year_str]):
            del self.data["revenues"][year_str][index]
            self.save_data()

    #this method is used to get the costs from the accounting_data.json file
    def get_costs(self, year=None):
        if year:
            return self.data["costs"].get(str(year),{})
        return self.data["costs"]

    #this method is used to add a cost category to the accounting_data.json file
    def add_event(self, event, year):
        year = str(year)
        if year not in self.data["costs"]:
            self.data["costs"][year] = {}
        if event not in self.data["costs"][year]:
            self.data["costs"][year][event] = {subcategory: [] for subcategory in self.subcategories}
            self.save_data()

    #this method is used to remove a cost category from the accounting_data.json file
    def remove_event(self,event,year):
        year = str(year)
        if year in self.data["costs"] and event in self.data["costs"][year]:
            del self.data["costs"][year][event]
            self.save_data()

    #this method is used to add a cost to the accounting_data.json file
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
        
    #this method is used to remove a cost from the accounting_data.json file
    def remove_cost(self, year, event, subcategory, index):
        del self.data["costs"][str(year)][event][subcategory][index]
        self.save_data()

