import networkx as nx


# Sample array from profiler includes only the node id integer. This class expands it to include additional timing data.
# node_idx provides an index into the nodes list within the profile class. 
class Sample:
    def __init__(self, node_idx: int, delta_to_last: int,  cum_ts: int, elapsed_time: int):
        self.node_idx = node_idx
        self.delta_to_last = delta_to_last
        self.cum_ts = cum_ts
        self.elapsed_time = elapsed_time

# Utility class that provides various parsing functionalty for callframe paths
class PathParser:
    @classmethod
    def split_path(path: str) -> str:
        return path.split("/")
    
    @classmethod
    def is_node_prefixed(path: str) -> bool:
        if not path: return False

        if path[0:4] == "node:": 
            return True
        else: return False
    
    @classmethod
    def is_npm_package(path: str) -> bool:
        split = PathParser.split_path(path)
        if "node_modules" in split:
            return True
        else: return False

    #returns blank string if the path provided is not from a package
    @classmethod
    def get_package_name(path: str) -> str:
        split = PathParser.split_path(path)
        if "node_modules" not in split: return ""
        return split[split.index("node_modules")+1]


# Holds Node data. A Node represents a function/stack frame in the profile. 
class ProfileNode:
    def __init__(self, hit_count: int, call_frame: dict, children: list):
        self.hit_count = hit_count
        self.call_frame= call_frame
        self.children = children
        self.total_execution_time = None
        self.avg_power_draw_watts = None
        self.consumption_joules = None

# Holds all data structures related to a cpu profile. Generates addional analytic data upon construction given a profile dictonary pulled from the db
class CpuProfile:
    def __init__(self, prof_raw: dict):
        self.sample_timeline = []
        self.start_time = prof_raw["startTime"]
        self.end_time = prof_raw["endTime"]
        self.runtime_from_timestamps = prof_raw["endTime"] - prof_raw["startTime"]
        self.runtime_from_deltas = None
        self.compressed_timeline = None
        self.node_map  = None
        self.node_dir_graph = None
        # May need meta info about the graph to avoid recalc
        # Maps 
        self.call_frame_map = None
        
        
        self._generate_timeline(prof_raw)
        self._validate_runtime_difference()
        self._compress_adjacent_samples()
        self._build_maps(prof_raw)
        self._build_directed_node_graph()


    def _generate_timeline(self, raw: dict) -> None:
        cum_ts = raw["startTime"] 
        elapsed_time = 0

        for i, s in enumerate(raw["samples"]):
            cum_ts += raw["timeDeltas"][i]
            elapsed_time += raw["timeDeltas"][i]
            self.sample_timeline.append(
                Sample(s, raw["timeDeltas"][i], cum_ts, elapsed_time)
        )

        self.runtime_from_deltas = elapsed_time;
    
    # Remains to be seen if this matters at all but putting it here for awareness
    def _validate_runtime_difference(self) -> None:
        if abs(self.runtime_from_deltas - self.runtime_from_timestamps) > 1000:
            print("Profile calculated runtime differs by more than 1ms.")

    # This needs to be tested (number of unique sample ids should be the same, runtime from deltas same, )
    def _compress_adjacent_samples(self) -> None:
        compressed = [self.sample_timeline[0]]
        comp_idx = 0
        curr_node_idx = self.sample_timeline[0].node_idx
        for i,s in enumerate(self.sample_timeline, 1):
            if s.node_idx == curr_node_idx:
                compressed[comp_idx].delta_to_last += s.delta_to_last
                compressed[comp_idx].cum_ts = s.cum_ts
                compressed[comp_idx].elapsed_time = s.elapsed_time
            else:
                comp_idx += 1
                curr_node_idx = s.node_idx
                compressed.append(s)

        self.compressed_timeline = compressed

    # Puts profile nodes into a dictionary indexed by profilerId.
    # A call frame dict is also built alongside the node_map.
    # Neither function name (sometimes blank, no guarantee of uniquenes across files)
    # , url (sometimes blank)
    def _build_maps(self, raw: dict) -> None:
        node_map = {}

        for node in raw["nodes"]:
            node_map[node["profilerId"]] = ProfileNode(node["hitCount"], node["callFrame"], node["children"]) 
        
        self.node_map = node_map

    # Graph nodes are only the profileId int, corresponding objects can be retrieved from node_map using the id
    # All nodes in the graph are reachable from node 1 (root), there are no cycles, and all nodes except node 1
    # have an in degree of 1 and a 0-N out degree.  
    def _build_directed_node_graph(self) -> None:
        node_graph = nx.DiGraph()
        node_graph.add_nodes_from(self.node_map.keys())
        for id,node in self.node_map.items():
            if len(node.children) > 0:
                node_graph.add_edges_from(([(id,child) for child in node.children]))
        
        self.node_dir_graph = node_graph


