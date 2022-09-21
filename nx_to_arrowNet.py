"""functions for transforming spatial data into edge network where every link is associated with a unique
id (uniq_id) and treated as a node. Each edge of this network is a traffic movement (pair of roads segments) and
 """


import geopandas
import networkx as nx
from movement_lookup import crossing_lookup, calculate_xlts, assign_bearing_in_junc
# from funcs import midpoint, make_route_line


def diGraph_to_arrowNet(G: nx.MultiDiGraph, xlts_gdf: geopandas.GeoDataFrame) -> nx.MultiDiGraph:

    G_ = nx.MultiDiGraph()
    for i, node in enumerate(list(G.nodes(data=True))):
        # print(i, node)
        out_edges = list(G.out_edges(node[0], True, True))
        in_edges = list(G.in_edges(node[0], True, True))

        for inl in in_edges:  # a tuple with the third item as a dictionary of segment attributes, second item is the other end of the link

            attr_in = inl[3]
            from_id = attr_in['ID_TRC_int']
            from_unid = attr_in['uniq_id']
            attr_r = attr_in.copy()

            for outl in out_edges:

                attr_out = outl[3]
                to_id = attr_out['ID_TRC_int']
                to_unid = attr_out['uniq_id']

                if from_id != to_id:

                    attr_r.update({'f_ID_TRC': attr_in['ID_TRC_int'], 't_ID_TRC': attr_out['ID_TRC_int'],
                                   # 'lts_final': max(attr_in['lts_final'], attr_out['lts_final']),

                                   # 'length': (attr_in['length']+ attr_out['length'])/2

                                   # , 'geometry': make_route_line([infirst, outlast])
                                   })
                    # Checking if the relation exists in the simple crossings layer (xLTS)
                    crossing_row, jid, jdf = crossing_lookup(attr_r, xlts_gdf)
                    if jid != -9999 and not jdf.empty:
                        xlts = calculate_xlts(
                            assign_bearing_in_junc(jdf, from_id),
                            assign_bearing_in_junc(jdf, to_id),
                            jdf
                        )
                    elif jid== -9999: # didn't find a junction, so the xlts should be 0 (two consecutive segments)
                        xlts = 0

                    attr_r.update({'xLTS': xlts})

                    G_.add_edge(from_unid, to_unid, **attr_r)

                else:
                    pass

    return G_