import time
import random
from threading import Thread

SYMBOLS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

# Shared latest prices (simple in-memory store)
PRICES = {s: 0.0 for s in SYMBOLS}

def get_price(symbol):
    return PRICES.get(symbol.upper())


class PriceSimulator:
    def __init__(self, socketio, namespace='/prices'):
        self.socketio = socketio
        self.namespace = namespace
        self.prices = {s: random.uniform(100, 500) for s in SYMBOLS}
        for s, p in self.prices.items():
            PRICES[s] = p
        self.running = False

    def start(self):
        if self.running:
            return
        self.running = True
        thread = Thread(target=self._run, daemon=True)
        thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            for sym in SYMBOLS:
                # Simulate a small random walk
                change = random.uniform(-0.5, 0.5)
                self.prices[sym] = max(0.01, round(self.prices[sym] + change, 2))
                PRICES[sym] = self.prices[sym]
                payload = {
                    'symbol': sym,
                    'price': self.prices[sym],
                    'timestamp': int(time.time())
                }
                # Emit price update
                try:
                    if self.socketio:
                        self.socketio.emit('price_update', payload, namespace=self.namespace)
                except Exception:
                    pass
            # Sleep a bit between ticks
            time.sleep(1)
