import pandas as pd

import FinancialData as fd


# new seperate class to load data
class ReadData :

    def __init__( self ) :
        self.path = fd.DataPath.path

        self.df_Ohlc = pd.read_csv( self.path )

    def verify_ohlc_data( self ) :

        # if datafraome is empty
        count_rows = self.df_Ohlc.shape[ 0 ]
        print( "Total rows :" , count_rows )

        # data contain """slice postion """
        self.df_Ohlc[ 'creation_date' ] = pd.to_datetime( self.df_Ohlc[ fd.OHLCV.time ] )
        starting_time = self.df_Ohlc[ 'creation_date' ].min( )
        last_time = self.df_Ohlc[ 'creation_date' ].max( )

        print( "Data : Starting from ->" , starting_time )
        print( "Data: Last Data time ->" , last_time )

        if (count_rows >= 0) :
            return True
        else :
            return False

    def get_data( self ) :
        isvalid = self.verify_ohlc_data( )
        if isvalid :
            return self.df_Ohlc

        else :
            print( "Error in Data file :" , fd.DataPath.path )
            return pd.DataFrame( )


#  create class to load OHLC data
class IndexAnalysis :

    def __init__( self ) :
        _data = ReadData( )
        self.df_Ohlc = _data.get_data( )
