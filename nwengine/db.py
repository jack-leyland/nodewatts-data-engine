from pymongo import MongoClient
from bson.objectid import ObjectId
import logging
from .error import EngineError
logger = logging.getLogger("Engine")


class DatabaseError(EngineError):
    def __init__(self, msg, *args, **kwargs):
        prefix = "Engine Database Error: "
        super().__init__(prefix + msg, *args, **kwargs)


class Database:
    def __init__(self, uri="mongodb://localhost:27017"):
        self.internal_uri = uri
        try:
            self.internal_client = MongoClient(uri)
        except Exception as e:
            raise Database("Failed to connect to internal database") from None
        finally:
            logger.debug(
                "Connection established to internal DB at uri %s", uri)

    # internal db name is not intended to be configurable
    def get_cpu_prof_by_id(self, id: str) -> dict:
        objId = ObjectId(id)
        try:
            res = self.internal_client["nodewatts"]["cpu"].find_one({
                                                                    "_id": objId})
        except Exception as e:
            raise DatabaseError("Failed to fetch cpuprofile") from None
        return res

    def get_power_samples_by_range(self, start: int, end: int) -> dict:
        try:
            res = self.internal_client["nodewatts"]["power"].find({"timestamp":
                                                                   {"$gt": start, "$lt": end}}).sort("timestamp", 1)
        except Exception as e:
            raise DatabaseError("Failed to fetch smartwatts data") from None
        return res

    def save_report_to_internal(self, report: dict) -> None:
        try:
            self.internal_client["nodewatts"]["reports"].insert_one(report)
        except Exception as e:
            raise DatabaseError("Failed to save report - internal") from None

    def export_report(self, report: dict, ) -> None:
        try:
            self.internal_client[self.export_db_name]["exports"].insert_one(
                report)
        except Exception as e:
            raise DatabaseError("Failed to export report") from None

    def connect_to_export_db(self, uri: str, name='nodewatts') -> None:
        try:
            self.export_client = MongoClient(uri)
        except Exception as e:
            raise Database("Failed to connect to internal database") from None
        finally:
            logger.debug("Connection established to export DB at uri %s", uri)
        self.export_db_name = name
