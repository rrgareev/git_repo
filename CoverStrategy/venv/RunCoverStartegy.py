from backtest.BacktestEngine import BacktestEngine, WSMDSource, CachedMDSource, RandomMDSource
import framework as fw

pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 2000)

def run_backtest():

    start_utc = datetime.datetime(2019, 6, 17, 7, 0, 0, 0, datetime.timezone.utc)
    end_utc = datetime.datetime(2019, 6, 17, 19, 0, 0, 0, datetime.timezone.utc)

    #md_source = CachedMDSource()
    md_source = RandomMDSource()

    b = BacktestEngine(start_utc_micros=fw.micros_t(start_utc), end_utc_micros=fw.micros_t(end_utc), md_source=md_source)
    b.prepare_for_import()

    from backtest.CoverStrategy import Strategy as stratcover

    params = stratcover.default_params
    params["verbose"] = True
    params["one_order_per_interval"] = 600000   #one order every 10 minutes
    params["cover_amount"] = 100000     #cover 100k every 10 minutes
    params["is_buy"] = True    #strategies buys by default
    print(params)

    b.add_strategy(stratcover, params)
    b.go()

    print(b.get_order_activities())

run_backtest()