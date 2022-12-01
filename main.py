
from build_nx import gdf_to_nx
from nx_to_arrowNet import diGraph_to_arrowNet
from calcSteepnessLevel import calc_SL, sl_signage
import geopandas
import pandas
import numpy
import warnings
from downtownAccessibility import NetworkPath
warnings.filterwarnings('ignore')

geopandas.options.display_precision = 9



if __name__ == "__main__":

    # street network + paths with dual carriageways merged at intersections
    streets = geopandas.read_file(
        # "C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\x_accessiblity\\data\\test\\merged_sample.gpkg"
        # "C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\x_accessiblity\\data\\merged_at_X\\merge_1.gpkg"
        # "C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\x_accessiblity\\data\\accessibility_input\\base_mergedNet2.gpkg"
        "C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\x_accessiblity\\data\\accessibility_input\\west_island4.gpkg"
    )

    print("number of lines: ", len(streets))

    streets[['lts', 'lts_c', 'lts_negD', 'length', 'slope', 'slope_edit']] = streets[
        ['lts', 'lts_c', 'lts_negD', 'length', 'slope', 'slope_edit']].replace(numpy.nan, 0)
    streets['slope_edit'] = streets['slope_edit'].replace(-8888, 0)
    # streets['slope_edit'] = streets['slope_edit'].replace([-8888, numpy.nan], 0)  # or

    print("Computing Steepness Level...")
    streets[['sl_35', 'sl_5', 'sl_65']] = streets.apply(
        lambda row: pandas.Series(calc_SL(row['length'], row['slope_edit'])),
        axis=1)

    streets['unsigned_sl'] = streets.apply(lambda row: min(row['sl_35'], row['sl_5'], row['sl_65']), axis=1)
    streets['signed_sl'] = streets.apply(lambda row: sl_signage(row['slope'], row['unsigned_sl']), axis=1)

    crossings = geopandas.read_file(
        "C:\\Users\\bitas\\folders\\Research\\Montreal\\QGIS_projects\\dec10\\xLTS_edited.gpkg"

    )

    crossings[['f_ID_TRC_1', 'f_ID_TRC_2', 't_ID_TRC_1', 't_ID_TRC_2', 'xlts', 'Junction_i', 'from_cc', 'to_cc',
              'cross_cc']] = \
        crossings[['f_ID_TRC_1', 'f_ID_TRC_2', 't_ID_TRC_1', 't_ID_TRC_2', 'xlts', 'Junction_i', 'from_cc', 'to_cc',
                  'cross_cc']].astype(int)

    print("Transforming to unidirectional networkX...")
    G = gdf_to_nx(streets)


    # Assigning a uniq id to all edges in the unidirectional G network and creating a Map between roads geometry and
    # id_trc to the uniq_id
    geo_hashmap, id_hashmap = dict(), dict()
    i = 0
    for u, v, a in G.edges(data=True):
        i += 1
        a['uniq_id'] = i
        geo_hashmap[i] = a['geometry']
        id_hashmap[i] = a['ID_TRC_int']


    print("Transforming to Edge networkX...")
    G_ = diGraph_to_arrowNet(G, crossings)
    # with open('C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\network_w_crossings\\all_G_.pickle', 'wb') as file:
    #     # dump information to that file
    #     pickle.dump(G_, file)
    G__ = G_.copy() # to make sure there's no errors

    # Getting the source point in the network (Peel st & Messounive) id of the corresponding node in the G_ to the id_trc of the road
    source_coords_1 = [(u,v) for u,v,k in G_.edges(data=True) if k['f_ID_TRC']==1260415][0][0]  # downtown at Peel oneway
    net_1 = NetworkPath(G_, source_coords_1, id_hashmap, geo_hashmap)
    net_1.calc_access('link_access_all_dup_p1')

    # second origin point
    # source_coords_2 = [(u, v) for u, v, k in G__.edges(data=True) if k['f_ID_TRC'] == 1460351][0][0]  # North East at Souligny and Pierr
    # net_2 = NetworkPath(G__, source_coords_2, id_hashmap, geo_hashmap)
    # net_2.calc_access('link_access_all_dup_p2')

    # third origin point on Salaberry
    # source_coords_3 = [(u, v) for u, v, k in G__.edges(data=True) if (k['f_ID_TRC'] == 4013148 and  k['TYPE_VOIE']==7)][-1][0]  # Path on Salaberry
    # net_3 = NetworkPath(G__, source_coords_3, id_hashmap, geo_hashmap)
    # net_3.calc_access('link_access_all_dup_p3')

    source_coords_3 = [(u, v) for u, v, k in G__.edges(data=True) if k['f_ID_TRC'] == 4013525 ][0][-1]  # Path on Salaberry
    net_3 = NetworkPath(G__, source_coords_3, id_hashmap, geo_hashmap)
    net_3.calc_access('link_access_all_dup_p3')

    # print("Computing Shortest Path LTS 1...")
    # scenario_name = "lts1"
    # subG_A1 = net_1.subgraphGetter(attr_lts="lts_final", cutoff_lts=1, attr_xlts="xLTS", cutoff_xlts=4)
    # dist_dict, path_dict = nx.single_source_dijkstra(subG_A1, source=source_coords_1, target=None, weight="length")
    # nx.set_node_attributes(G_, dist_dict, scenario_name)
    # # nx.set_node_attributes(G_, path_dict, f"{'r_' + scenario_name}")
    #
    # print("Computing Shortest Path LTS 1 and xLTS 1...")
    # scenario_name = "lts1_x"
    # subG_A2 = net_1.subgraphGetter(attr_lts="lts_final", cutoff_lts=1, attr_xlts="xLTS", cutoff_xlts=1)
    # dist_dict, path_dict = nx.single_source_dijkstra(subG_A2, source=source_coords_1, target=None, weight="length")
    # nx.set_node_attributes(G_, dist_dict, scenario_name)
    # # nx.set_node_attributes(G_, path_dict, f"{'r_' + scenario_name}")
    #
    # print("Computing Shortest Path LTS 2...")
    # scenario_name = "lts2"
    # subG_B1 = net_1.subgraphGetter(attr_lts="lts_final", cutoff_lts=2, attr_xlts="xLTS", cutoff_xlts=4)
    # dist_dict, path_dict = nx.single_source_dijkstra(subG_B1, source=source_coords_1, target=None, weight="length")
    # nx.set_node_attributes(G_, dist_dict, scenario_name)
    # # nx.set_node_attributes(G_, path_dict, f"{'r_' + scenario_name}")
    #
    # print("Computing Shortest Path LTS 2 and xLTS 2...")
    # scenario_name = "lts2_x"
    # subG_B2 = net_1.subgraphGetter(attr_lts="lts_final", cutoff_lts=2, attr_xlts="xLTS", cutoff_xlts=2)
    # dist_dict, path_dict = nx.single_source_dijkstra(subG_B2, source=source_coords_1, target=None, weight="length")
    # nx.set_node_attributes(G_, dist_dict, scenario_name)
    # # nx.set_node_attributes(G_, path_dict, f"{'r_' + scenario_name}")
    #
    # # saving the shortest path values to a dataframe
    # unids, id_trcs, geoms, lts1s, lts1_xs, lts2s, lts2_xs = [], [], [], [], [], [], []
    # for n, attrs in G_.nodes(data=True):
    #     unids.append(n)
    #     id_trcs.append(id_hashmap[n])
    #     geoms.append(geo_hashmap[n])
    #
    #     try:
    #         lts1s.append(attrs['lts1'])
    #     except KeyError:
    #         lts1s.append(999999)
    #     try:
    #         lts1_xs.append(attrs['lts1_x'])
    #     except KeyError:
    #         lts1_xs.append(999999)
    #     try:
    #         lts2s.append(attrs['lts2'])
    #     except KeyError:
    #         lts2s.append(999999)
    #     try:
    #         lts2_xs.append(attrs['lts2_x'])
    #     except KeyError:
    #         lts2_xs.append(999999)
    #
    # access_gdf = geopandas.GeoDataFrame(
    #     {'unid': unids, 'id_trc': id_trcs, 'geometry': geoms, 'lts1': lts1s, 'lts1_x': lts1_xs, 'lts2': lts2s,
    #      'lts2_x': lts2_xs}, crs="EPSG:4326")
    # access_gdf.to_file(
    #     'C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\x_accessiblity\\data\\test\\link_access_all_dup_p1.gpkg')

