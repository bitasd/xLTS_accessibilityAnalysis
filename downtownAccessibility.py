"""

"""

# x = crossings.loc[crossings['Junction_i']==22264][['from_cc', 'to_cc', 'cross_cc', 'xlts', 'f_ID_TRC', 't_ID_TRC']]

from typing import Tuple, Dict
import networkx as nx
import geopandas
# from shapely.geometry import LineString

geopandas.options.display_precision = 9



class NetworkPath:
    def __init__(self, G: nx.MultiDiGraph, source: Tuple, id_hashmap: Dict, geo_hashmap: Dict):
        # self.SG = None
        self.G = G
        self.source = source
        self.id_hashmap = id_hashmap
        self.geo_hashmap = geo_hashmap

    def subgraphGetter(self, attr_lts: str, cutoff_lts: int,
                           attr_xlts: str, cutoff_xlts: int,
                           attr_sl: str = None, cutoff_sl: float = None)-> nx.MultiDiGraph:
        """
        :param cutoff_xlts: crossing LTS qualifier
        :param attr_xlts:
        :param attr_lts: name of the lts related field (String)
        :param cutoff_lts: the cutoff value for lts (int)
        :param attr_sl: name of the SL related field (String)
        :param cutoff_sl: the value for SL (3.5, 5)
        :return: a subgraph that satisfies the filters of LTS and SL
        """
        if attr_sl:
            SG = nx.MultiDiGraph([(u,v,d) for u, v, d in self.G.edges(data=True) if d[attr_lts] <= cutoff_lts and
                                d[attr_sl]<= cutoff_sl and d[attr_xlts]<= cutoff_xlts])
        # only crossing and segment lts restriction
        elif not attr_sl:
            SG = nx.MultiDiGraph([(u, v, d) for u, v, d in self.G.edges(data=True) if d[attr_lts] <= cutoff_lts and
                                d[attr_xlts] <= cutoff_xlts])
        return SG

    # def points_toLineString(path_dict: Dict):
    #
    #     geometry, trcids = [], []
    #     for k, v in path_dict.items():
    #         trcids.append(id_hashmap[k])
    #         this_coords = []
    #         for uid in v:
    #             this_coords.extend([*list(geo_hashmap[uid].coords)])
    #         geometry.append(LineString(this_coords))


########################################################################################################################
    def calc_access(self, fname: str):

        print("Computing Shortest Path LTS 1...")
        scenario_name = "lts1"
        subG_A1 = self.subgraphGetter(attr_lts="lts_final", cutoff_lts=1, attr_xlts="xLTS", cutoff_xlts=4)
        dist_dict, path_dict = nx.single_source_dijkstra(subG_A1, source=self.source, target=None, weight="length")
        nx.set_node_attributes(self.G, dist_dict, scenario_name)


        print("Computing Shortest Path LTS 1 and xLTS 1...")
        scenario_name = "lts1_x"
        subG_A2 = self.subgraphGetter(attr_lts="lts_final", cutoff_lts=1, attr_xlts="xLTS", cutoff_xlts=1)
        dist_dict, path_dict = nx.single_source_dijkstra(subG_A2, source=self.source, target=None, weight="length")
        nx.set_node_attributes(self.G, dist_dict, scenario_name)


        print("Computing Shortest Path LTS 2...")
        scenario_name = "lts2"
        subG_B1 = self.subgraphGetter(attr_lts="lts_final", cutoff_lts=2, attr_xlts="xLTS", cutoff_xlts=4)
        dist_dict, path_dict = nx.single_source_dijkstra(subG_B1, source=self.source, target=None, weight="length")
        nx.set_node_attributes(self.G, dist_dict, scenario_name)


        print("Computing Shortest Path LTS 2 and xLTS 2...")
        scenario_name = "lts2_x"
        subG_B2 = self.subgraphGetter(attr_lts="lts_final", cutoff_lts=2, attr_xlts="xLTS", cutoff_xlts=2)
        dist_dict, path_dict = nx.single_source_dijkstra(subG_B2, source=self.source, target=None, weight="length")
        nx.set_node_attributes(self.G, dist_dict, scenario_name)

        unids, id_trcs, geoms, lts1s, lts1_xs, lts2s, lts2_xs = [], [], [], [], [], [], []
        for n, attrs in self.G.nodes(data=True):
            unids.append(n)
            id_trcs.append(self.id_hashmap[n])
            geoms.append(self.geo_hashmap[n])

            try:
                lts1s.append(attrs['lts1'])
            except KeyError:
                lts1s.append(999999)
            try:
                lts1_xs.append(attrs['lts1_x'])
            except KeyError:
                lts1_xs.append(999999)
            try:
                lts2s.append(attrs['lts2'])
            except KeyError:
                lts2s.append(999999)
            try:
                lts2_xs.append(attrs['lts2_x'])
            except KeyError:
                lts2_xs.append(999999)

        access_gdf = geopandas.GeoDataFrame(
            {'unid': unids, 'id_trc': id_trcs, 'geometry': geoms, 'lts1': lts1s, 'lts1_x': lts1_xs, 'lts2': lts2s,
             'lts2_x': lts2_xs}, crs="EPSG:4326")
        access_gdf.to_file(
            f'C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\x_accessiblity\\data\\test\\{fname}.gpkg')
########################################################################################################################
