from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Node_:
    id: int
    lon: float
    lat: float

    # dual_name_to_nodeid: Dict = field(default_factory=dict)
    # incident_segments: List = field(default_factory=list)
    # cc_ordered_incident_segments: List = field(default_factory=list)
    # is_on_a_dual_carjwy: List = field(default_factory=list)
    # has_traffic_signal: List = field(default_factory=list)
    # has_other_attributes: List = field(default_factory=list)
    # is_multinode_processed: List = field(default_factory=list)
