from db import Database
from cpu_profile import CpuProfile
from power_profile import PowerProfile
from report import Report
import argparse
import json
import pprint

# Config file/cli will have to define the name of the database along with address and port
# This looks ugly but allows for more flexible use?
# Once config is figured out later could just pull the collection all in one go 
# right from the db class

class Config:
    pass

config = Config()

parser = argparse.ArgumentParser(description='internal argument interface for nodewatts')
parser.add_argument('--internal_db_addr', type=str, default='localhost')
parser.add_argument('--internal_db_port', type=int, default=27017)
parser.add_argument('--export_raw', type=bool, default=False, required=False)
parser.add_argument('--out_db_addr', type=str, default='localhost', required=False)
parser.add_argument('--out_db_port', type=int, default=27017, required=False)
parser.add_argument('--profile_id', type=str, required=True)
parser.add_argument('--report_name', type=str, required=True)
parser.add_argument('--sensor_start', type=int, required=False)
parser.add_argument('--sensor_end', type=int, required=False)

parser.parse_args(namespace=config)

try:
    db = Database(config.internal_db_addr, config.internal_db_port)
except Exception as e:
    print("Error establishing DB connection")
    print(e)

#Need this try/catch?
try:
    prof_raw = db.get_cpu_prof_by_id(config.profile_id)
    # this is just a test one, use config values and fallback to this if needed
    cpu = CpuProfile(prof_raw)
    power_sample_start = cpu.start_time - 2000
    power_sample_end = cpu.end_time + 2000
    power_raw = db.get_power_samples_by_range(power_sample_start, power_sample_end)
except Exception as e:
    print("Error fetching input data")
    print(e)

power = PowerProfile(power_raw)
report = Report(config.report_name,cpu, power)

try:
    db.save_report(vars(report.__dict__))
except Exception as e:
    print("Error saving")
    print(e)



