import pandas as pd
from stock_indicators import CandlePart
from stock_indicators import Quote
from stock_indicators import indicators

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


# Trade parameter

class TradeStatus :
    Open = 1
    Close = 0

class IntraCarry :
    Intra = "I"
    Carry = "C"

class PlaceOrder :
    EntryDate = "EntryDate"
    EntryTime = "EntryTime"
    Qty = "Qty"
    EntryPrice = "EntryPrice"
    Status = "Status"
    Ltp = "LTP"
    PnL = "PnL"
    ExitPrice = "ExitPrice"
    ExitTime = "ExitTime"
    ExitDate = "ExitDate"

#  create class to load OHLC data
class IndexAnalysis :

    def __init__( self ) :
        _data = ReadData( )
        self.df_Ohlc = _data.get_data( )

        self.List_Distinct_TradeDate = [ ]

        self.reverse_dataframe( )
        self.get_all_distinct_Trading_data( )
        self.Generate_Trade_Signal( )
        self.TradeBank( self.df_Trades )

    def TradeBank( self , df ) :
        df = pd.DataFrame(
            columns = [ PlaceOrder.EntryDate , PlaceOrder.EntryTime , PlaceOrder.Qty , PlaceOrder.EntryPrice ,
                        PlaceOrder.Status , PlaceOrder.Ltp
                , PlaceOrder.Pnl , PlaceOrder.ExitPrice , PlaceOrder.ExitTime , PlaceOrder.ExitDate
                        ]
        )

    def reverse_dataframe( self ) :
        self.df_Ohlc.sort_index( ascending = False )

    def get_all_distinct_Trading_data( self ) :
        """ Convert  coloumn to datetime"""
        self.df_Ohlc[ fd.OHLCV.time ] = pd.to_datetime( self.df_Ohlc[ fd.OHLCV.time ] )

        self.List_Distinct_TradeDate = self.df_Ohlc[ fd.OHLCV.time ].map( pd.Timestamp.date ).unique( )

        # for _date in self.List_Distinct_TradeDate:
        #     print ("date available:" + str(_date))

    def Generate_Trade_Signal( self ) :
        # for idx ,row in self.df_Ohlc.iterrows():

        # datetime = row[fd.OHLCV.time].astype() strftime("%Y-%m-%d %H:%M:%S")
        # print(row[fd.OHLCV.time] )
        # datetime_str = datetime.datetime.strptime( row[fd.OHLCV.time], '%d-%m-%Y %H:%M:%S' )

        # print(row[fd.OHLCV.time].date())
        # datetime_str = datetime.datetime.strptime( row[fd.OHLCV.time], FinancialData.DateTimeFromat.dd_mm_yyyy__HH_MM_SS )
        # print(datetime_str)

        # for idx ,row in self.df_Ohlc.iterrows():
        #     d= str(row[ fd.OHLCV.time ])[0:10]
        #     # print(d)

        for trading_date in self.List_Distinct_TradeDate :
            """ Get back Data"""
            print( trading_date )
            # mask = pd.to_datetime( self.df_Ohlc[fd.OHLCV.time]).date() == trading_date
            mask = self.df_Ohlc[ fd.OHLCV.time ].astype( str ).str[ 0 :10 ] == str( trading_date )
            # replace('-','')
            df_feed = self.df_Ohlc.loc[ mask ]
            self.EntryTrade( df_feed , trading_date )

            # df_feed.head()
            # print( len( df_feed ) )

            # df_feed = self.df_Ohlc.where( self.df_Ohlc[fd.OHLCV.time].astype(datetime).data() ==  trading_date)

    def EntryTrade( self , df , trddate ) :
        # print(len( df))
        # convert to List
        # quotes_list = [
        #     Quote( d , o , h , l , c , v )
        #     for d , o , h , l , c , v
        #     in zip( df[ fd.OHLCV.time] , df[ fd.OHLCV.into] , df[ fd.OHLCV.inth ] , df[ fd.OHLCV.intl ] , df[ fd.OHLCV.intc ] , df[ fd.OHLCV.v ] )
        # ]

        quotes_list = [ ]

        for id , bar in df.iterrows( ) :
            # quotes_list.insert(bar[fd.OHLCV.time],bar[fd.OHLCV.into],bar[fd.OHLCV.inth],bar[fd.OHLCV.intl],bar[fd.OHLCV.intc],bar[fd.OHLCV.v])

            q = Quote( bar[ fd.OHLCV.time ] , bar[ fd.OHLCV.into ] , bar[ fd.OHLCV.inth ] , bar[ fd.OHLCV.intl ] ,
                       bar[ fd.OHLCV.intc ] , bar[ fd.OHLCV.v ]
                       )
            quotes_list.append( q )
            open = bar[ fd.OHLCV.into ]
            high = bar[ fd.OHLCV.inth ]
            low = bar[ fd.OHLCV.intl ]
            close = bar[ fd.OHLCV.intc ]

            results = indicators.get_sma( quotes_list , 20 , CandlePart.CLOSE )

            final_res = results[ -1 ].sma
            mess = " TradeDate : "+str( trddate )+" Time"+str( bar[ fd.OHLCV.time ] )+" Open :"+str( open
                                                                                                     )+" High :"+str(
                high
                )+" Low :"+str( low )+" Close :"+str( close )+" "
            print( mess+str( results[ -1 ].sma ) )
