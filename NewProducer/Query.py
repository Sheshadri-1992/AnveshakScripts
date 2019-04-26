import sys
import time
from datetime import datetime
from datetime import timedelta
from enum import Enum


class QueryType(Enum):
    largeview = 1
    mediumview = 2
    smallview = 3


class QueryStruct:

    querytype = QueryType(QueryType.smallview)
    arguments = ""
    prevtime = datetime.now()
    timestamp = time.time()

    def __init__(self, enumtype, args):

        print "creating new object "

        self.querytype = QueryType(enumtype)
        self.arguments = args
        self.prevtime = datetime.now()

        if self.querytype == QueryType.largeview:

            self.timestamp = datetime.now() + timedelta(seconds=10)

        elif self.querytype == QueryType.mediumview:

            self.timestamp = datetime.now() + timedelta(seconds=5)

        else:

            self.timestamp = datetime.now() + timedelta(seconds=1)

    def print_members(self):

        """

        :return:
        """

        ans = (self.timestamp - self.prevtime)
        print self.querytype, " ", self.timestamp, " ", self.arguments, " ", ans.seconds
        return "printed"

# test code
# myObj = Query(2,"hello")
# myObj.print_members()
