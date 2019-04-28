from __future__ import print_function

import logging
import threading
import time
import Queue
import numpy as np
from MqttPublish import MqttPublish
from Query import QueryStruct

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )


class LargeProducer(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):

        super(LargeProducer, self).__init__()
        self.target = target
        self.name = name
        self.large_queue = Queue.Queue()

    def run(self):

        # print("I am  here in large producer ")
        while True:
            if not self.large_queue.full():

                item = QueryStruct(1, "edgeid")
                self.large_queue.put(item)
                logging.debug('Putting item : ' + str(self.large_queue.qsize()) + ' items in large queue')
                time.sleep(10)

            else:
                logging.debug("queue is full ")
                time.sleep(10)

    @property
    def get_element_from_queue(self):
        """

        :return: return an object if exists else return None
        """

        # check for queue not being empty
        if not self.large_queue.empty():
            item = self.large_queue.get()
            return item

        return None


class MediumProducer(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):

        super(MediumProducer, self).__init__()
        self.target = target
        self.name = name
        self.medium_queue = Queue.Queue()

    def run(self):

        # print("I am  here in medium producer ")
        while True:
            if not self.medium_queue.full():
                item = QueryStruct(2, "edgeid")
                self.medium_queue.put(item)
                logging.debug('Putting ' + ' : ' + str(self.medium_queue.qsize()) + ' items in medium queue')
                time.sleep(5)
                # break
            else:
                logging.debug("queue is full ")
                time.sleep(5)

    @property
    def get_element_from_queue(self):
        """

        :return: return an object if exists else return None
        """

        # check for queue not being empty
        if not self.medium_queue.empty():
            item = self.medium_queue.get()
            return item

        return None


class SmallProducer(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):

        super(SmallProducer, self).__init__()
        self.target = target
        self.name = name
        self.small_queue = Queue.Queue()

    def run(self):

        # print("I am  here in small producer ")
        while True:
            if not self.small_queue.full():
                item = QueryStruct(3, "edgeid")
                self.small_queue.put(item)
                logging.debug('Putting item : ' + str(self.small_queue.qsize()) + ' items in small queue')
                time.sleep(0.01)
                # break
            else:
                logging.debug("queue is full ")
                time.sleep(1)

    @property
    def get_element_from_queue(self):
        """

        :return: return a object if exists else return None
        """

        # check for queue not being empty
        if not self.small_queue.empty():
            item = self.small_queue.get()
            return item

        return None
