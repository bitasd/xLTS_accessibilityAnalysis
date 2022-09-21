import geopandas
import pandas


def crossing_lookup(relation: dict, xlts_gdf: geopandas.GeoDataFrame):
    """

    create a dataframe with the rankings and links of the junction (junc_df in the below function)
    :param relation:
    :param xlts_gdf:
    :return:
    """
    fid, tid = relation['f_ID_TRC'], relation['t_ID_TRC']
    # print("fid, tid: ", fid, tid)
    crossing_row = xlts_gdf.loc[((xlts_gdf['f_ID_TRC_1']==fid) | (xlts_gdf['f_ID_TRC_2']==fid)) &
                             ((xlts_gdf['t_ID_TRC_1']==tid) | (xlts_gdf['t_ID_TRC_2']==tid)) ]
    # Through crossing
    if not crossing_row.empty:
        # print(crossing_row)
        jid = crossing_row.head(1)['Junction_i'].item()
        jdf = xlts_gdf[xlts_gdf['Junction_i'] == jid]
        return crossing_row, jid, jdf


    elif crossing_row.empty:
        # Left turn
        f_row = xlts_gdf.loc[(xlts_gdf['f_ID_TRC_1']==fid) | (xlts_gdf['f_ID_TRC_2']==fid)]
        t_row = xlts_gdf.loc[(xlts_gdf['t_ID_TRC_1'] == tid) | (xlts_gdf['t_ID_TRC_2'] == tid)]
        f_j = list(set(f_row['Junction_i'].tolist()))
        t_j = list(set(t_row['Junction_i'].tolist()))
        if f_j and t_j:
            # print("prob a left turn: ", fid, tid)
            mutual_j = [i for i in f_j if i in t_j]
            if mutual_j:
                jid = mutual_j[0]
                # print("found a left turn at: ", jid, fid, tid)
                jdf = xlts_gdf[xlts_gdf['Junction_i'] == jid]
                return f_row, jid, jdf
            else:
                # not finding that relation in the X layer
                return pandas.DataFrame(), -9999, pandas.DataFrame()
        else:
            # not finding that relation in the X layer
            return pandas.DataFrame(), -9999, pandas.DataFrame()


def assign_bearing_in_junc( jdf: pandas.DataFrame, id_trc: int)-> int:
    """
    takes the segment id_trc of a segment at an intersection and returns the pre-calculated bearing from the xLTS file (only street network)
    :param jdf: df of simple crossings at an intersection
    :param id_trc:
    :return: rank
    """
    rank = jdf.loc[(jdf['f_ID_TRC_1'] == id_trc) | (jdf['f_ID_TRC_2'] == id_trc)]['from_cc'][:1].item()

    #TODO: handle if no rank found
    return rank


def calculate_xlts(f_cc_rank: int, t_cc_rank: int, junc_df: pandas.DataFrame) -> int:
    """
    calculate the xlts for compound movements
    :param junc_df: all the simple crossings from a particular junction produced by crossing_lookup func
    :return: movement lts
    """

    num_legs = len(junc_df)
    num_leg_bein_crossed = ((t_cc_rank - f_cc_rank) % num_legs) - 1

    # if num_leg_bein_crossed in [0, -1]: # right turn and dual carriageway in the same leg
    #     return 0
    if num_leg_bein_crossed == -1:  #  dual carriageway in the same leg
        # the xLTS of the (from before leg to after leg)
        # print("same leg", junc_df)
        before_cc_rank = (f_cc_rank - 1 ) % num_legs
        after_cc_rank = (f_cc_rank + 1) % num_legs

        before_cc_rank = before_cc_rank if before_cc_rank != 0 else num_legs
        after_cc_rank = after_cc_rank if after_cc_rank != 0 else num_legs
        # print("before leg and after leg", before_cc_rank, after_cc_rank)

        xlts = junc_df.loc[(junc_df['from_cc'] == before_cc_rank) & (junc_df['to_cc'] == after_cc_rank)]['xlts'].item()
        return xlts
        # return 0
    if num_leg_bein_crossed == 0:  # right turn
        return 0

    elif num_leg_bein_crossed == 1:
        xlts = junc_df.loc[(junc_df['from_cc'] == f_cc_rank) & (junc_df['to_cc'] == t_cc_rank)]['xlts'].item()
        return xlts

    elif num_leg_bein_crossed >= 2:
        xlts_max = 0
        for i in range(1, num_leg_bein_crossed + 1):
            cross_cc = (f_cc_rank + i) % num_legs
            cross_cc = cross_cc if cross_cc != 0 else num_legs
            xlts = junc_df.loc[junc_df['cross_cc'] == cross_cc]['xlts'].item()
            xlts_max = max(xlts_max, xlts)
        return xlts_max

    else:
        return -9999  #TODO: check if happens at all