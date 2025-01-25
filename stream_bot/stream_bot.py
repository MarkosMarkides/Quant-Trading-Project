from queue import Queue
import threading
from stream_bot.candle_worker import CandleWorker
from stream_bot.price_processor import PriceProcessor
from stream_bot.trade_settings_collection import tradeSettingsCollection
from stream_bot.trade_worker import TradeWorker
from stream_example.stream_prices import PriceStreamer


def run_bot():
    """
    PriceStreamer(producer): Fetches prices → Updates shared_prices → Signals updates.
	PriceProcessor(consumer): Waits for updates → Processes prices → Adds candlesticks to candle_queue.
	CandleWorker(consumer for PriceProcessor): Consumes candlesticks → Applies logic → Adds trade signals to trade_work_queue.
	TradeWorker(consumer for PriceProcessor): Consumes trade signals → Executes trades.
    """ 
    tradeSettingsCollection.load_trade_settings()
    tradeSettingsCollection.print_collection()

    shared_prices = {}
    shared_prices_events = {}
    shared_prices_lock = threading.Lock()

    candle_queue = Queue()
    trade_work_queue = Queue()

    for p in tradeSettingsCollection.pair_list():
        shared_prices_events[p] = threading.Event()
        shared_prices[p] = {}
        
    threads = []
    
    # If daemon = True, the thread will stop running when the main program finishes, even if it’s still processing work.
    # Non-daemon threads must complete their tasks before the program exits.

    price_stream_t = PriceStreamer(shared_prices, shared_prices_lock, shared_prices_events)
    price_stream_t.daemon = True 
    threads.append(price_stream_t)
    price_stream_t.start()

    # The start() method launches a new thread, running the code defined in the thread’s run method.
    # The run() method would not create a new thread, it would just executes the run() method in the current thread

    trade_work_t = TradeWorker(trade_work_queue)
    trade_work_t.daemon = True 
    threads.append(trade_work_t)
    trade_work_t.start()

    # For every pair create, configue and start a PriceProcessor thread

    for p in tradeSettingsCollection.pair_list():
        processing_t = PriceProcessor(shared_prices, shared_prices_lock, shared_prices_events, candle_queue,
                                      f"PriceProcessor_{p}", p, tradeSettingsCollection.granularity)
        processing_t.daemon = True
        threads.append(processing_t)
        processing_t.start()

    # For every pair create, configure and start a CandleWorker thread

    for p in tradeSettingsCollection.pair_list():
        candle_t = CandleWorker(tradeSettingsCollection.get_trade_settings(p), candle_queue, 
                                trade_work_queue, tradeSettingsCollection.granularity)
        candle_t.daemon = True
        threads.append(candle_t)
        candle_t.start()

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
#