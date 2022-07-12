from db import Mongo_Connection
from cpu_profile import CpuProfile
from power_profile import PowerProfile

# Config file/cli will have to define the name of the database along with address and port
# This looks ugly but allows for more flexible use?
# Once config is figured out later could just pull the collection all in one go 
# right from the db class

try:
    conn = Mongo_Connection('localhost', 27017)
    db = conn.fetch_db_object("test")
    profile_collection = db["profiles"]
    power_collection = db["outputs"]
except Exception as e:
    print("Error fetching data from DB")
    print(e)

# We assume that the objectID is passed to the engine from the profiler
# ObjID will be used to fetch the correct profile in case there's multiple 
# Under normal operation there won't be anything cause the tool will
# delete the entire mongodb when done

# this is just a test one
prof_raw = profile_collection.find_one({"userProvidedName": "1657135061183"})

cpu = CpuProfile(prof_raw);

# The config needs to provide start and end timestamps for the power profile taken from the program running the sensor
# These stamps will be used for the preliminary check that the timelines actually overlap sufficently

# This might change once the above comment is implemented, for the time being, we pad the CPU profile start and end times
# by 2ms to ensure we have enough data to shift so it matches up with the CPU profile
power_sample_start = cpu.start_time - 2000
power_sample_end = cpu.end_time + 2000

power_raw = power_collection.find({"timestamp": {"$gt": power_sample_start, "$lt": power_sample_end}}).sort("timestamp", 1)

power = PowerProfile(power_raw)
if power._assert_chronological(power._rapl_timeline): print("Sorting works")

#calculate time deltas and compare



# May need to check memory use if we are reading everything into memory, should be fine though





