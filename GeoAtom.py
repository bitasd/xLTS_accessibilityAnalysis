from typing import Dict
import nx_to_arrowNet
from node import Node_
import networkx as nx

class Geoatoms(
    nx_to_arrowNet.Mixin,
    Node_
):
    def __init__(self):
        self._in_node_id: int = 100
        self._in_seg_id: int = 100
        self._in_rel_id: int = 100
        self.G : nx.MultiDiGraph
        self.nodes_dict: Dict[int, tuple] = {}

    # def get_or_add_node_id(self, nid: int) -> tuple:
    #     """
    #
    #     :param nid: id of the node
    #     :return:  latlng of the node
    #     """
    #     try:
    #         _n = self.nodes_dict[f"{float(latlng[0]):.15f}{float(latlng[1]):.15f}"]
    #         return _n.id
    #
    #     except KeyError:
    #         _id = self._in_node_id
    #         _n = Node_(id=_id, lon=latlng[0], lat=latlng[1])
    #         self.nodes_reversed_dict.update({
    #             f"{float(latlng[0]):.15f}{float(latlng[1]):.15f}": _n
    #         })
    #         self._in_node_id = _id + 1
    #         return _n.id