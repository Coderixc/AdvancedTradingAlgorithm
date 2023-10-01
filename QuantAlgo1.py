import numpy as np
import pandas as pd
from stock_indicators import CandlePart
from stock_indicators import Quote
from stock_indicators import indicators

import FinancialData as fd
import Report as R


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
    MaxProfit = "MaxProfit"
    MaxLoss = "MaxLoss"
    StopLoss = "StopLoss"
    TargetPoint = "TargetPoint"


class RiskManagement :
    StopLoss = 26
    Targetpoint = 80
    IsAllowed = True


#  create class to load OHLC data
class IndexAnalysis :

    def __init__( self ) :
        _data = ReadData( )
        self.df_Ohlc = _data.get_data( )

        self.List_Distinct_TradeDate = [ ]
        self.df_Trades = pd.DataFrame( )

        self.reverse_dataframe( )
        self.get_all_distinct_Trading_data( )
        self.TradeBank( )
        self.Generate_Trade_Signal( )
    def TradeBank( self ) :
        self.df_Trades = pd.DataFrame(
            columns = [ PlaceOrder.EntryDate , PlaceOrder.EntryTime , PlaceOrder.Qty , PlaceOrder.EntryPrice ,
                        PlaceOrder.Status , PlaceOrder.Ltp
                , PlaceOrder.PnL , PlaceOrder.ExitPrice , PlaceOrder.ExitTime , PlaceOrder.ExitDate ,
                        PlaceOrder.MaxProfit , PlaceOrder.MaxLoss , PlaceOrder.StopLoss , PlaceOrder.TargetPoint ]
        )

    def reverse_dataframe( self ) :
        self.df_Ohlc.sort_index( ascending = True )

    def get_all_distinct_Trading_data( self ) :
        """ Convert  coloumn to datetime"""
        self.df_Ohlc[ fd.OHLCV.time ] = pd.to_datetime( self.df_Ohlc[ fd.OHLCV.time ] )

        self.List_Distinct_TradeDate = self.df_Ohlc[ fd.OHLCV.time ].sort_index( ascending = False ).map(
            pd.Timestamp.date
            ).unique( )

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

        print( "Total Trading Day : " , len( self.List_Distinct_TradeDate ) )
        for trading_date in self.List_Distinct_TradeDate :
            """ Get back Data"""
            print( "Proceeding Back testing for : " , trading_date )
            # mask = pd.to_datetime( self.df_Ohlc[fd.OHLCV.time]).date() == trading_date
            mask = self.df_Ohlc[ fd.OHLCV.time ].astype( str ).str[ 0 :10 ] == str( trading_date )
            # replace('-','')
            df_feed = self.df_Ohlc.loc[ mask ].dropna( )
            self.StartTrading( df_feed.sort_index( ascending = False ) , trading_date )

            # df_feed.head()
            # print( len( df_feed ) )

            # df_feed = self.df_Ohlc.where( self.df_Ohlc[fd.OHLCV.time].astype(datetime).data() ==  trading_date)

        print( "Trade Bank Complted" )
        # print(self.df_Ohlc)

    def Add_trades_to_TradeBank( self , df_today ) :

        self.df_Trades = pd.concat( [ self.df_Trades , df_today ] )
        # for trade in df_today.iterrows():
        # self.df_Trades = pd.concat( [ self.df_Trades , df_today ] , ignore_index=True )

        return self.df_Trades

    def Calculate_Pnl( self , qty , buyprice , Ltp ) :
        _pnl = 0.0
        if qty > 0 :
            _pnl = round( qty * (Ltp-buyprice) , 2 )
        else :
            _pnl = round( -1 * qty * (Ltp-buyprice) , 2 )

        return (_pnl)

    def ExitTrades_update_pnl( self , df_Open_Trades , Ltp: float , currenttime , tradedate ) :

        inttime = int( str( currenttime ) )
        # print("Current Time" , inttime)

        for idx , trd in df_Open_Trades.iterrows( ) :

            if (trd[ PlaceOrder.Status ] == TradeStatus.Close) :
                continue

            _maxprofit = trd[ PlaceOrder.MaxProfit ]
            _maxLoss = trd[ PlaceOrder.MaxLoss ]
            pnl = self.Calculate_Pnl( trd[ PlaceOrder.Qty ] , trd[ PlaceOrder.EntryPrice ] , Ltp )

            if RiskManagement.IsAllowed == True :
                _stoploss = trd[ PlaceOrder.StopLoss ]
                _target = trd[ PlaceOrder.TargetPoint ]
                # exit Trades  If above conditions is followed

                if Ltp <= _stoploss :
                    df_Open_Trades.loc[ idx , PlaceOrder.Status ] = TradeStatus.Close
                    df_Open_Trades.loc[ idx , PlaceOrder.ExitTime ] = currenttime
                    df_Open_Trades.loc[ idx , PlaceOrder.ExitPrice ] = Ltp
                    df_Open_Trades.loc[ idx , PlaceOrder.Ltp ] = Ltp
                    df_Open_Trades.loc[ idx , PlaceOrder.ExitDate ] = tradedate
                    df_Open_Trades.loc[ idx , PlaceOrder.PnL ] = pnl
                elif Ltp >= _target :

                    df_Open_Trades.loc[ idx , PlaceOrder.Status ] = TradeStatus.Close
                    df_Open_Trades.loc[ idx , PlaceOrder.ExitTime ] = currenttime
                    df_Open_Trades.loc[ idx , PlaceOrder.ExitPrice ] = Ltp
                    df_Open_Trades.loc[ idx , PlaceOrder.Ltp ] = Ltp
                    df_Open_Trades.loc[ idx , PlaceOrder.ExitDate ] = tradedate
                    df_Open_Trades.loc[ idx , PlaceOrder.PnL ] = pnl

                # continue
            #     Pass operation to Next Bar

            if inttime > 151500 and trd[ PlaceOrder.Status ] == TradeStatus.Open :
                df_Open_Trades.loc[ idx , PlaceOrder.Status ] = TradeStatus.Close
                df_Open_Trades.loc[ idx , PlaceOrder.ExitTime ] = currenttime
                df_Open_Trades.loc[ idx , PlaceOrder.ExitPrice ] = Ltp
                df_Open_Trades.loc[ idx , PlaceOrder.Ltp ] = Ltp
                df_Open_Trades.loc[ idx , PlaceOrder.ExitDate ] = tradedate
                df_Open_Trades.loc[ idx , PlaceOrder.PnL ] = pnl





            elif trd[ PlaceOrder.Status ] == TradeStatus.Open :
                df_Open_Trades.loc[ idx , PlaceOrder.PnL ] = pnl
                df_Open_Trades.loc[ idx , PlaceOrder.Ltp ] = Ltp

                if _maxprofit < pnl :
                    df_Open_Trades.loc[ idx , PlaceOrder.MaxProfit ] = pnl

                if (_maxLoss > pnl) :
                    df_Open_Trades.loc[ idx , PlaceOrder.MaxLoss ] = pnl

    def StartTrading( self , df , trddate ) :
        # print(len( df))
        # convert to List
        # quotes_list = [
        #     Quote( d , o , h , l , c , v )
        #     for d , o , h , l , c , v
        #     in zip( df[ fd.OHLCV.time] , df[ fd.OHLCV.into] , df[ fd.OHLCV.inth ] , df[ fd.OHLCV.intl ] , df[ fd.OHLCV.intc ] , df[ fd.OHLCV.v ] )
        # ]

        df_exchange = pd.DataFrame( data = None , columns = self.df_Trades.columns )

        quotes_list = [ ]
        m_open = 0
        m_close = 0
        m_high = 0
        m_low = 0

        flag_open = True

        prev_candle_ohlc4 = 0

        for id , bar in df.iterrows( ) :
            # quotes_list.insert(bar[fd.OHLCV.time],bar[fd.OHLCV.into],bar[fd.OHLCV.inth],bar[fd.OHLCV.intl],bar[fd.OHLCV.intc],bar[fd.OHLCV.v])

            open = bar[ fd.OHLCV.into ]
            high = bar[ fd.OHLCV.inth ]
            low = bar[ fd.OHLCV.intl ]
            close = bar[ fd.OHLCV.intc ]
            Ltp = bar[ fd.OHLCV.into ]

            if flag_open == True :
                # print( "First Tick Update" )
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
            _entrytime = bar[ fd.OHLCV.time ].time( )

            currenttime = bar[ fd.OHLCV.time ].time( ).strftime( "%H%M%S" )
            # print(currenttime)

            """ Exit or Update PnL of The Open tardes"""
            self.ExitTrades_update_pnl( df_exchange , Ltp , currenttime , trddate )

            inttime = int( str( currenttime ) )

            if inttime > 152500 :
                continue

            q = Quote( bar[ fd.OHLCV.time ] , bar[ fd.OHLCV.into ] , bar[ fd.OHLCV.inth ] , bar[ fd.OHLCV.intl ] ,
                       bar[ fd.OHLCV.intc ] , bar[ fd.OHLCV.v ]
                       )
            quotes_list.append( q )

            results = indicators.get_sma( quotes_list , 50 , CandlePart.CLOSE )
            results_rsi = indicators.get_rsi( quotes_list , 10 )

            final_res = results[ -1 ].sma
            rsi = results_rsi[ -1 ].rsi

            mess = " TradeDate : "+str( trddate )+" Time"+str( bar[ fd.OHLCV.time ] )+" Open :"+str( open
                                                                                                     )+" High :"+str(
                high
            )+" Low :"+str( low )+" Close :"+str( close )+" "
            # print( mess+str( results[ -1 ].sma ) )

            """Entry Condition """
            """ if Closing Price  > SMA -> Trigger Trades"""

            body_length = np.absolute( m_open-m_close )

            if final_res is not None :

                if (rsi is not None) :

                    m_ohlc = (m_open+m_high+m_low+Ltp) / 4

                    if final_res > Ltp and rsi > 51 and body_length > 30 and Ltp >= m_ohlc and Ltp >= prev_candle_ohlc4 :
                        _trddate = trddate
                        _maxprofit = 0
                        _maxloss = 0
                        _stoplosss = 0
                        _targetpoint = 0
                        # print( "New Trade Entry :" , _entrytime )
                        if RiskManagement.IsAllowed == True :
                            _stoplosss = Ltp-RiskManagement.StopLoss
                            _targetpoint = Ltp+RiskManagement.Targetpoint

                        df_exchange.loc[ len( df_exchange ) ] = [ trddate , _entrytime , 1 , Ltp , TradeStatus.Open ,
                                                                  Ltp ,
                                                                  0 , -1 , -1 , -1 , _maxprofit , _maxloss ,
                                                                  _stoplosss , _targetpoint ]

            prev_candle_ohlc4 = (open+high+low+close) / 4

        # print("Trade Bank :",self.df_Trades )

        self.Add_trades_to_TradeBank( df_exchange )

        # print("Task : Back Testing (BT) completed Sucessfully")

    def Run_StrategyAnalysis( self , print_tocsv = False ) :
        ListTradeExecutedDate = self.df_Trades[ PlaceOrder.EntryDate ].unique( )
        # self.df_Trades.to_csv( "Trades_z" , encoding = 'utf-8' )

        if print_tocsv == True :
            self.df_Report = pd.DataFrame(
                columns = [ R.ReportFile.TradeDate , R.ReportFile.TotalTrades , R.ReportFile.MaxProfit ,
                            R.ReportFile.MaxLoss , R.ReportFile.NoOf_ProfitTrades , R.ReportFile.NoOf_LossTrades ,

                            R.ReportFile.Profit_Loss_Ratio , R.ReportFile.Total_PointGained ,
                            R.ReportFile.Total_Return ,
                            R.ReportFile.Total_Loss_point

                            ]
            )

        for extrades in ListTradeExecutedDate :
            # print(extrades)

            mask = self.df_Trades[ PlaceOrder.EntryDate ] == extrades
            df_record = self.df_Trades.where( mask ).dropna( )

            m_win_trade = 0
            m_loss_trade = 0

            m_profit = 0
            m_loss = 0
            m_total_trade = 0

            m_Max_Gain_point = 0
            m_Max_Loss_Point = 0

            m_max_profit = 0
            m_max_loss = 0

            for idx , trd in df_record.iterrows( ) :
                m_total_trade = m_total_trade+1
                _pnl = trd[ PlaceOrder.PnL ]
                if _pnl >= 0 :
                    m_win_trade = m_win_trade+1
                    m_profit = m_profit+_pnl

                    if m_max_profit < _pnl :
                        m_max_profit = _pnl

                    if m_Max_Gain_point < _pnl :
                        m_Max_Gain_point = _pnl
                else :
                    m_loss_trade = m_loss_trade+1
                    m_loss = m_loss+_pnl

                    if m_Max_Loss_Point > _pnl :
                        m_Max_Loss_Point = _pnl

                    if m_max_loss > _pnl :
                        m_max_loss = _pnl

            print( "****** Post Trade Analysis Metrics **********" )
            print( "Executed trade Analysis :" , extrades )
            print( "Total Trades :" , m_total_trade )

            print( "Max Profit :" , m_max_profit )
            print( "Max Loss :" , m_max_loss )

            print( "Profit/Loss Ratio:" , m_win_trade , "/" , m_loss_trade )
            print( "Total  Point Gained :" , m_profit )
            print( "Total Return:" , m_profit+m_loss , "\n" )
            print( "Loss Point :" , m_loss )
            print( "Max Profit :" , m_Max_Gain_point )
            print( "Max Loss :" , m_Max_Loss_Point )
            print( "\n" )

            #     add records to Report File
            if print_tocsv == True :
                try :
                    PnL_ratio = (m_win_trade / m_loss_trade)

                except :
                    PnL_ratio = m_win_trade
                _total_return = (m_profit+m_loss)
                _record = [ extrades , m_total_trade , m_max_profit , m_max_loss , m_win_trade , m_loss_trade ,
                            PnL_ratio ,
                            m_profit , _total_return , m_loss ]

                self.df_Report.loc[ len( self.df_Report ) ] = _record

        if print_tocsv == True :
            print( "Record & Trades" )
            # print( "Preparing Post Trade Analysis For BT" )
            # print( self.df_Trades.to_string( ) )
            # print( self.df_Report.to_string( ) )
            # df_Report.to_csv("Report_1" , encoding = 'utf-8')
            # self.df_Trades.to_csv("Trades_1" , encoding = 'utf-8')

    def Summary( self ) :

        total_trades = 0
        total_point_earned = 0
        total_point_lost = 0

        total_profit_trade = 0
        total_lost_trade = 0

        total_return = 0
        for idx , report in self.df_Report.iterrows( ) :
            total_profit_trade = total_profit_trade+report[ R.ReportFile.NoOf_ProfitTrades ]
            total_lost_trade = total_lost_trade+report[ R.ReportFile.NoOf_LossTrades ]
            total_trades = total_trades+report[ R.ReportFile.TotalTrades ]

            total_point_earned = total_point_earned+report[ R.ReportFile.Total_PointGained ]
            total_point_lost = total_point_lost+report[ R.ReportFile.Total_Loss_point ]
            total_return = total_return+report[ R.ReportFile.Total_Return ]

        print( "**        Summary of BT Test          **" )
        print( "Total profit Trades" , total_profit_trade )
        print( "Total Loss Trades" , total_lost_trade )
        print( "Total Trades" , total_trades )

        print( "Total point Earned(Point)" , round( total_point_earned , 2 ) )
        print( "Total point Lost(Point)" , round( total_point_lost , 2 ) )
        print( "Total Return(s) Point" , round( total_return , 2 ) )

        try :
            _avg = round( total_return / total_trades , 2 )
        except :
            _avg = 0
        print( "Average PnL of Each Trade(s)" , _avg )

        print( "Probability Of Win Trade" , round( (total_profit_trade / total_trades) * 100 , 2 ) , "%" )
