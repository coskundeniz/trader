from queue import Queue
from threading import Thread

from config import logger


class Executor:

    def __init__(self):

        self.order_queue = Queue()
        self._executor_thread = Thread(target=self.execute, daemon=True)
        self._executor_thread.start()

    def add_to_execution_queue(self, order):
        """Add order to the queue

        :type order: MarketOrder
        :param order: Order to add to the execution queue
        """

        logger.info(f"Adding order[{order}] to queue...")
        self.order_queue.put(order)

    def execute(self):
        """Get next order from the queue and execute"""

        while True:
            order = self.order_queue.get()
            logger.info(f"Executing order[{order}]...")
            order.execute_order()
            self.order_queue.task_done()


order_executor = Executor()