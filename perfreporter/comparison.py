from time import time
import datetime
from influxdb import InfluxDBClient

SELECT_DATA_FROM_INFLUX = "SELECT last(tpsRate) as Throughput, min(responseTime) as Min, " \
                                "max(responseTime) as Max, mean(responseTime) as Mean, " \
                                "percentile(responseTime, 50) as pct_50, percentile(responseTime, 75) as pct_75, " \
                                "percentile(responseTime, 90) as pct_90, percentile(responseTime, 95) as pct_95, " \
                                "percentile(responseTime, 99) as pct_99 FROM requestsRaw WHERE " \
                                "\"requestName\"=\'{}\' and buildID=\'{}\'"


class Comparison(object):
    def __init__(self, arguments):
        self.args = arguments

    def write_comparison_data_to_influx(self, test_results):
        comparison = []
        client = InfluxDBClient(self.args["influx_host"], self.args['influx_port'],
                                username=self.args['influx_user'], password=self.args['influx_password'],
                                database=self.args['influx_database'])
        for request in test_results:
            data = client.query(SELECT_DATA_FROM_INFLUX.format(str(request['request_name']), str(request['build_id'])))
            data = list(data.get_points())[0]
            request["throughput"] = data['Throughput']
            request["min"] = data['min']
            request["max"] = data['max']
            request["mean"] = data['mean']
            request["pct50"] = data['pct50']
            request["pct75"] = data['pct75']
            request["pct90"] = data['pct90']
            request["pct95"] = data['pct95']
            request["pct99"] = data['pct99']
            comparison.append(request)

        print("*******************************************")
        for req in comparison:
            print(req)
            print("____________________________________")


        #self.write_to_comparison_db(comparison)
