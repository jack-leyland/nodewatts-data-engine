from xmlrpc import client
from pymongo import MongoClient


class Mongo_Connection:
    def __init__(self, addr='localhost', port=27017):
        #establish connection on construction
        self.addr = addr
        self.port = port
        self.client = MongoClient(addr, port);
        print("DB connection established on " + addr + " port " + str(port))
    def fetch_db_object(self, db_name: str):
        #how to handle errors?? 
        return self.client[db_name]
    
    # TODO:save new result object 
