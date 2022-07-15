from . import __version__ as nwengine_version
from .db import Database
from .cpu_profile import CpuProfile
from .error import EngineError
from .power_profile import PowerProfile
from .report import Report
from .config import Config
from . import log
import argparse
import sys

def create_cli_parser():
    parser = argparse.ArgumentParser(description='internal argument interface for nodewatts')
    parser.add_argument('--internal_db_addr', type=str, default='localhost')
    parser.add_argument('--internal_db_port', type=int, default=27017)
    parser.add_argument('--export_raw', type=bool, default=False, required=False)
    parser.add_argument('--out_db_addr', type=str, default='localhost', required=False)
    parser.add_argument('--out_db_port', type=int, default=27017, required=False)
    parser.add_argument('--out_db_name', type=str, default="nodewatts", required=False)
    parser.add_argument('--profile_id', type=str, required=True)
    parser.add_argument('--report_name', type=str, required=True)
    parser.add_argument('--sensor_start', type=int, required=True)
    parser.add_argument('--sensor_end', type=int, required=True)
    parser.add_argument('--verbose', type=bool, required=False, default=False)
    return parser

def run_engine(args: Config or dict) -> None:
    if not isinstance(args, Config):
        config = Config(args)

    logger = log.setup_logger(config.verbose, "Engine")

    db = Database(config.internal_db_addr, config.internal_db_port)
    if config.export_raw:
        db.connect_to_export_db(config.out_db_addr, config.out_db_port, config.out_db_name)

    # Calling program will ensure that these collections are not empty before starting engine
    prof_raw = db.get_cpu_prof_by_id(config.profile_id)
    cpu = CpuProfile(prof_raw)

    if config.sensor_start and config.sensor_end:
        power_sample_start = config.sensor_start
        power_sample_end = config.sensor_end
    else:
        # May delete this fallback with further testing, more of a hack for development
        power_sample_start = cpu.start_time - 2000
        power_sample_end = cpu.end_time + 2000

    if power_sample_start > cpu.start_time or power_sample_end < cpu.end_time:
        raise EngineError("Insufficient sensor data to compute power report.")

    power_raw = db.get_power_samples_by_range(power_sample_start, power_sample_end)
    power = PowerProfile(power_raw)
    report = Report(config.report_name, cpu, power)
    formatted = report.to_json()
    db.save_report_to_internal(formatted)

    if config.export_raw:
        db.export_report(formatted)

    logger.info("Data processing complete.")



if __name__ == "__main__":
    config = Config()
    parser = create_cli_parser()
    parser.parse_args(namespace=config)
    run_engine(config)
    sys.exit(0)