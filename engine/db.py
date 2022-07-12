from xmlrpc import client
from report import Report
from pymongo import MongoClient
from bson.objectid import ObjectId


class Database:
    def __init__(self, addr='localhost', port=27017):
        #establish connection on construction
        self.internal_addr = addr
        self.internal_port = port
        self.internal_client = MongoClient(addr, port)
        #debug or info??
        print("DB connection established on " + addr + " port " + str(port))

    #internal db name is not intended to be configurable 
    def get_cpu_prof_by_id(self, id: str) -> dict:
        objId = ObjectId(id)
        return self.internal_client["nodewatts"]["cpu"].find_one({"_id": objId})

    def get_power_samples_by_range(self, start, end):
        return self.internal_client["nodewatts"]["power"].find({"timestamp": {"$gt": start, "$lt": end}}).sort("timestamp", 1)
    
    def save_report(self, report: Report, export=False) -> None:
        self.internal_client["nodewatts"]["reports"].insert_one(report)
