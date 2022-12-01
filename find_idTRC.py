import geopandas
import numpy

streets = geopandas.read_file(
    'C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\x_accessiblity\\data\\downtown_ToAll_2_4326.gpkg')
streets[['lts', 'lts_c', 'lts_negD', 'length', 'slope', 'slope_edit', 'TYPE_VOIE']] = streets[

    ['lts', 'lts_c', 'lts_negD', 'length', 'slope', 'slope_edit', 'TYPE_VOIE']].replace(numpy.nan, 0)

crossings = geopandas.read_file(
        "C:\\Users\\bitas\\folders\\Research\\Montreal\\QGIS_projects\\dec10\\xLTS_edited.gpkg"
    )
streets_only = streets.loc[~(streets['TYPE_VOIE'].isin([5,7]))]

def get_id(tid: int, streets_df: geopandas.GeoDataFrame) -> int:
    tdf =  streets_df.loc[streets_df['ID_TRC_int']==tid].head(1)
    if len(tdf)>0:
        tlts = tdf['lts'].item()
    else:
        tlts = -9999
        print(tid)
    return tlts

crossings[['f_ID_TRC_1', 'f_ID_TRC_2', 't_ID_TRC_1', 't_ID_TRC_2', 'xlts', 'Junction_i', 'from_cc', 'to_cc',
              'cross_cc']] = \
crossings[['f_ID_TRC_1', 'f_ID_TRC_2', 't_ID_TRC_1', 't_ID_TRC_2', 'xlts', 'Junction_i', 'from_cc', 'to_cc',
          'cross_cc']].astype(int)


crossings['DepLTS_1'] = crossings.apply(lambda row: get_id(row['t_ID_TRC_1'], streets_only), axis=1)