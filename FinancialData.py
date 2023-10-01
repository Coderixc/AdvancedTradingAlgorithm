# Define Data File Header as present in Csv Format """
# time	into	inth	intl		intc	intvwap	intv	v	intoi	oi
class OHLCV:
    time ="time"
    into="into"
    inth="inth"
    intl ="intl"
    intc="intc"
    intvwap="intvwap"
    v="v"
    intoi="intoi"
    oi="oi"

class DateTimeFromat :
    dd_mm_yyyy__HH_MM_SS = "%d-%m-%Y %H:%M:%S"


class DataPath :
    # filename = "NIFTY_22_28_TF_1"
    filename = "NIFTY_20220501"
    path = ".//Data//"+filename+".csv"
