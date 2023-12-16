import pandas as pd
import yfinance as yf


class Quote :
    mDate = "Date"
    mOpen = "Open"
    mHigh = "High"
    mLow = "Low"
    mClose = "Close"
    mAdjClose = "Adj Close"
    mVolume = "Volume"


class Metrics :

    def __init__( self , date , wick_2_wick_range , body_2_body_range ) :
        self.Date = date
        self.Wick_2_Wick_Range = wick_2_wick_range
        self.Body_2_Body_Range = body_2_body_range


class Metrics2 :
    def __init__( self , year , min_wick , max_wick , min_body , max_body ) :
        self.Year = year
        self.Min_Wick = min_wick
        self.Max_Wick = max_wick
        self.Min_Body = min_body
        self.Max_Body = max_body


class Analysis_Index :

    def __init__( self , TradingSymbol ) :
        print( "Constructor Called" )

        print( "Creating Storage to Store Historical (Financial) Data" )
        self.df_history_data = pd.DataFrame(
            columns = [ Quote.mDate , Quote.mOpen , Quote.mHigh , Quote.mLow , Quote.mClose , Quote.mAdjClose ,
                        Quote.mVolume ]
        )

        print( "Stock Symbol is " , TradingSymbol )

        self.get_history_data( TradingSymbol )
        self.evaluate_Metrics( )
        self.print_All_stats( )

    def get_history_data( self , TradingSymbol ) :
        try :

            """Call Yahoo Finance Function () to get data """
            self.df_history_data = yf.download( TradingSymbol , start = "2002-01-01" , end = "2023-10-01"
                                                ).reset_index( )
            # self.df_history_data = data.DataReader( TradingSymbol , start = "2023-01-01" , end = "2023-10-01" )

            # self.df_history_data  = self.df_history_data.reset_index()
            """ date coloumn is itself index"""

            """ Convert Date to DateTime """
            self.df_history_data[ Quote.mDate ] = pd.to_datetime( self.df_history_data[ Quote.mDate ] )

            _count_rows_in_df = len( self.df_history_data )
            print( "Row(s) present in Fetching(s) Financial Data : " , _count_rows_in_df )

            self.Strat_Analysing( )
        except :
            print( "Error(s) Occur while Downloading.." )

    def Strat_Analysing( self ) :

        if len( self.df_history_data ) == 0 :
            print( "No Data Found" )
            return

        List_processing_year_record = [ ]
        self.list_metrics = [ ]

        for index , bar in self.df_history_data.iterrows( ) :
            # print(bar)

            _get_current_processing_year = bar[ Quote.mDate ].year
            if _get_current_processing_year not in List_processing_year_record :
                List_processing_year_record.append( _get_current_processing_year )
                # print( "Processing Year is  :" , _get_current_processing_year )

            try :
                wick_2_wick = abs( bar[ Quote.mHigh ]-bar[ Quote.mLow ] )
                body_2_body = abs( bar[ Quote.mOpen ]-bar[ Quote.mClose ] )

                """ Creaet object For Metrics """
                O = Metrics( bar[ Quote.mDate ] , wick_2_wick , body_2_body )

                if wick_2_wick > 900 :
                    print( bar[ Quote.mDate ] , wick_2_wick , body_2_body )

                self.list_metrics.append( O )
                # print( " Range  is  ", _get_range)

                # print("Year is :" ,bar.index )

            except :
                print( "Unknown Error(s) Occured" )
                return

    def evaluate_Metrics( self ) :

        min_wick_range = 0
        min_body_range = 0

        max_wick_range = 0
        max_body_range = 0

        processing_year = 0

        metrics = [ ]

        self.List_metrics_return = [ ]

        last_record = len( self.list_metrics )
        scanning_rows = 0
        for metric in self.list_metrics :
            scanning_rows = scanning_rows+1
            if (processing_year != metric.Date.year) :

                """  Save Last(Process) Recod """
                if processing_year != 0 :
                    m = Metrics2( processing_year , min_wick_range , max_wick_range , min_body_range , max_body_range )
                    self.List_metrics_return.append( m )

                processing_year = metric.Date.year

                min_wick_range = metric.Wick_2_Wick_Range
                min_body_range = metric.Body_2_Body_Range

                max_wick_range = metric.Wick_2_Wick_Range
                max_body_range = metric.Body_2_Body_Range

            """ Major Calculation """

            if min_body_range > metric.Body_2_Body_Range :
                min_body_range = metric.Body_2_Body_Range

            if min_wick_range > metric.Wick_2_Wick_Range :
                min_wick_range = metric.Wick_2_Wick_Range

            if max_wick_range < metric.Wick_2_Wick_Range :
                max_wick_range = metric.Wick_2_Wick_Range

            if max_body_range < metric.Body_2_Body_Range :
                max_body_range = metric.Body_2_Body_Range

            """ Record last Result """

            if processing_year not in metrics :  # n- 1 Year
                metrics.append( processing_year )

                # print("MA" ,processing_year )

            if scanning_rows == last_record :  # nth Year
                print( "Last Record is --" )

                m = Metrics2( processing_year , min_wick_range , max_wick_range , min_body_range , max_body_range )
                self.List_metrics_return.append( m )

            # if(metric.Wick_2_Wick_Range)

        # """ print Analysis """
        # print("MIN WICK Range :" , min_wick_range)
        # print( "MIN BODY Range :" , min_body_range )
        #
        # print( "MAX WICK Range :" , max_wick_range )
        # print( "MAX BODY Range :" , max_body_range )
        print( "Task evaluate_Metrics is Completed : Now Start get ALl Statitics Result " )

    def print_All_stats( self ) :
        print( "Processing year ," , "MIN WICK_2_WICK ," , "MAX WICK_2_WICK," ,
               "MIN BODY_2_BODY," , "MAX BODY_2_BODY,"
               )
        for stat in self.List_metrics_return :
            # print("Processing year :" ,stat.Year , "MIN WICK_2_WICK :" , round(stat.Min_Wick,2), "MAX WICK_2_WICK" , round(stat.Max_Wick,2) ,
            #       "MIN BODY_2_BODY : ", round(stat.Min_Body,2) , "MAX BODY_2_BODY :" ,round( stat.Max_Body))

            print( stat.Year , "," , round( stat.Min_Wick , 2 ) , "," , round( stat.Max_Wick , 2 ) , "," ,
                   round( stat.Min_Body , 2 ) , "," , round( stat.Max_Body )
                   )
