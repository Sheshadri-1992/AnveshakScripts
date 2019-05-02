import time
from datetime import datetime
from datetime import timedelta
from enum import Enum


class QueryType(Enum):
    largeview = 1
    mediumview = 2
    smallview = 3


class QueryStruct:
    # querytype = QueryType(QueryType.smallview)
    # edgeid = ""
    # prevtime = datetime.now()
    # timestamp = time.time()

    def __init__(self, enumtype, args):

        print("creating new object ")

        self.querytype = QueryType(enumtype)
        self.edgeid = args
        self.prevtime = datetime.now()
	self.timestamp = datetime.now()

        if self.querytype == QueryType.largeview:
            self.timestamp = datetime.now() + timedelta(seconds=10)

        elif self.querytype == QueryType.mediumview:
            self.timestamp = datetime.now() + timedelta(seconds=5)

        else:
            self.timestamp = datetime.now() + timedelta(seconds=1)

    def print_members(self):

        """
        A utility function to print all the members of the Query
        :return: nothing
        """

        ans = (self.timestamp - self.prevtime)
        print("here ", self.querytype, " ", self.timestamp, " ", self.edgeid, " ", ans.seconds)
        return "printed"

    def get_edge_id(self):
        """
        Returns the edge id
        :return: the edge id
        """

        return self.edgeid

    def get_timestamp(self):

        return self.timestamp

# test code
# myObj = Query(2,"hello")
# myObj.print_members()
