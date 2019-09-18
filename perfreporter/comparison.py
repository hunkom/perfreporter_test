import csv
from time import time
import datetime
from influxdb import InfluxDBClient


class Comparison(object):
    def __init__(self, arguments):
        self.args = arguments

    def write_comparison_data_to_influx(self, test_results):
        comparison = []
        client = InfluxDBClient(self.args["influx_host"], self.args['influx_port'],
                                username=self.args['influx_user'], password=self.args['influx_password'],
                                database=self.args['influx_db'])
        for request in test_results:
            data = client.query("SELECT last(tpsRate) as Throughput, min(responseTime) as Min, "
                                "max(responseTime) as Max, mean(responseTime) as Mean, "
                                "percentile(responseTime, 50) as pct_50, percentile(responseTime, 75) as pct_75, "
                                "percentile(responseTime, 90) as pct_90, percentile(responseTime, 95) as pct_95, "
                                "percentile(responseTime, 99) as pct_99 FROM requestsRaw WHERE "
                                "\"requestName\"=\'" + str(request['request_name']) + "\' and build_id=\'"
                                + str(request['build_id']) + "\'")
            data = list(data.get_points())
            print("**************************************")
            print(request['request_name'])
            print(data)


        #self.write_to_comparison_db(comparison)
