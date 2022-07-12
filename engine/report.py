from engine.cpu_profile import CpuProfile
from engine.power_profile import PowerProfile

# We will need report level metadata from the config for things like what the report should be called and maybe a datetime stamp


class Report:
    def __init__(self, cpu: CpuProfile, power: PowerProfile):
        if not isinstance(cpu, CpuProfile):
            raise ValueError("Parameter is not a CpuProfile instance.")
        if not isinstance(power, PowerProfile):
            raise ValueError("Parameter is not a PowerProfile instance.")
        
        self.chronological = None
        self.node_graph = None
        
    
    # loop through cpu profile and assign power measurements, trying to only use one sample per node

    # Use path parser to generate relevant categorical data

    # covert node graph to JSON and save

    # Convert entire report to JSON and return for db class to save

    