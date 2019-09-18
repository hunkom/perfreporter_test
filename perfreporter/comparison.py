import csv
from time import time
import datetime
from influxdb import InfluxDBClient


class Comparison(object):
    def __init__(self, arguments):
        self.args = arguments

    def write_comparison_data_to_influx(self, test_results):
        comparison = dict()
        print("*******************************************")
        for req in test_results:
            print(req)
            print("________________________")
        print("*******************************************")
        #self.write_to_comparison_db(comparison)
