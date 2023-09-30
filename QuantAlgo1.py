import numpy as np
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
        self.TradeBank( )
        self.Generate_Trade_Signal( )


    def TradeBank( self ) :
        self.df_Trades = pd.DataFrame(
            columns = [ PlaceOrder.EntryDate , PlaceOrder.EntryTime , PlaceOrder.Qty , PlaceOrder.EntryPrice ,
                        PlaceOrder.Status , PlaceOrder.Ltp
                , PlaceOrder.PnL , PlaceOrder.ExitPrice , PlaceOrder.ExitTime , PlaceOrder.ExitDate ]
        )

    def reverse_dataframe( self ) :
        self.df_Ohlc.sort_index( ascending = True )

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
            self.EntryTrade( df_feed.sort_index( ascending = False ) , trading_date )

            # df_feed.head()
            # print( len( df_feed ) )

            # df_feed = self.df_Ohlc.where( self.df_Ohlc[fd.OHLCV.time].astype(datetime).data() ==  trading_date)

    def Add_trades_to_TradeBank( self , df_today ) :

        concat_df = pd.concat( [ self.df_Trades , df_today ] )

        return concat_df

    def EntryTrade( self , df , trddate ) :
        # print(len( df))
        # convert to List
        # quotes_list = [
        #     Quote( d , o , h , l , c , v )
        #     for d , o , h , l , c , v
        #     in zip( df[ fd.OHLCV.time] , df[ fd.OHLCV.into] , df[ fd.OHLCV.inth ] , df[ fd.OHLCV.intl ] , df[ fd.OHLCV.intc ] , df[ fd.OHLCV.v ] )
        # ]

        df_exchange = pd.DataFrame( data = None , columns = self.df_Trades.columns , index = self.df_Trades.index )

        quotes_list = [ ]
        m_open = 0
        m_close = 0
        m_high = 0
        m_low = 0

        flag_open = True

        for id , bar in df.iterrows( ) :
            # quotes_list.insert(bar[fd.OHLCV.time],bar[fd.OHLCV.into],bar[fd.OHLCV.inth],bar[fd.OHLCV.intl],bar[fd.OHLCV.intc],bar[fd.OHLCV.v])

            open = bar[ fd.OHLCV.into ]
            high = bar[ fd.OHLCV.inth ]
            low = bar[ fd.OHLCV.intl ]
            close = bar[ fd.OHLCV.intc ]
            Ltp = bar[ fd.OHLCV.intc ]

            if flag_open == True :
                print( "First Tick Update" )
                m_open = open
                m_high = high
                m_low = low
                m_close = close
                flag_open = False

            if m_low > low :
                m_low = low

            if m_high < high :
                m_high = high

            m_close = Ltp

            q = Quote( bar[ fd.OHLCV.time ] , bar[ fd.OHLCV.into ] , bar[ fd.OHLCV.inth ] , bar[ fd.OHLCV.intl ] ,
                       bar[ fd.OHLCV.intc ] , bar[ fd.OHLCV.v ]
                       )
            quotes_list.append( q )

            results = indicators.get_sma( quotes_list , 50 , CandlePart.CLOSE )

            final_res = results[ -1 ].sma
            mess = " TradeDate : "+str( trddate )+" Time"+str( bar[ fd.OHLCV.time ] )+" Open :"+str( open
                                                                                                     )+" High :"+str(
                high
                )+" Low :"+str( low )+" Close :"+str( close )+" "
            # print( mess+str( results[ -1 ].sma ) )

            """Entry Condition """
            """ if Closing Price  > SMA -> Trigger Trades"""

            body_length = np.absolute( m_open-m_close )

            if final_res is not None :

                ohlc4 = (open+high+low+close) / 4
                m_ohlc = (m_open+m_high+m_low+m_close) / 4

                if final_res > Ltp and Ltp > m_open and body_length > 30 and Ltp > ohlc4 and Ltp > m_ohlc :
                    _trddate = trddate

                    _entrytime = bar[ fd.OHLCV.time ].time( )
                    print( _entrytime )

                    df_exchange.loc[ len( df_exchange ) ] = [ _trddate , _entrytime , 1 , Ltp , TradeStatus.Open , Ltp ,
                                                              0 , -1 , -1 , -1 ]

        # print("Trade Bank :",self.df_Trades )

        print( self.Add_trades_to_TradeBank( df_exchange ) )
