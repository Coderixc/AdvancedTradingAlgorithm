import QuantAlgo1 as Q

if __name__ == '__main__' :
    print ( "starting.." )
    run1 = Q.IndexAnalysis ( )
    run1.Run_StrategyAnalysis ( print_tocsv = True )
    run1.Summary ( )

"""YAHOO FINANCE """

# import Analysis_Index as IA
#
# if __name__ == '__main__' :
#     My_analysis_stocks = "^NSEI"
#     Aq = IA.Analysis_Index( My_analysis_stocks )
