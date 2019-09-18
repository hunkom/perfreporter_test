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
        self.client = InfluxDBClient(self.args["influx_host"], self.args['influx_port'],
                                     username=self.args['influx_user'], password=self.args['influx_password'])

    def write_comparison_data_to_influx(self, test_results):
        comparison = []
        try:
            self.client.switch_database(self.args['influx_database'])
            for request in test_results:
                data = self.client.query(SELECT_DATA_FROM_INFLUX.format(str(request['request_name']),
                                                                        str(request['build_id'])))
                data = list(data.get_points())[0]
                request["throughput"] = round(float(data['Throughput']), 3)
                request["min"] = round(float(data['Min']), 2)
                request["max"] = round(float(data['Max']), 2)
                request["mean"] = round(float(data['Mean']), 2)
                request["pct50"] = int(data['pct_50'])
                request["pct75"] = int(data['pct_75'])
                request["pct90"] = int(data['pct_90'])
                request["pct95"] = int(data['pct_95'])
                request["pct99"] = int(data['pct_99'])
                comparison.append(request)
        except Exception as e:
            print(e)

        self.send_to_influx(comparison)

    def send_to_influx(self, comparison):
        points = []
        timestamp = time()
        for req in comparison:
            influx_record = {
                "measurement": "api_comparison",
                "tags": {
                    "simulation": req['simulation'],
                    "users": req['users'],
                    "test_type": req['test_type'],
                    "build_id": req['build_id'],
                    "request_name": req['request_name'],
                    "method": req['method'],
                    "duration": req['duration'],
                },
                "time": datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "throughput": req['throughput'],
                    "total": req['total'],
                    "ok": req['OK'],
                    "ko": req['KO'],
                    "1xx": req['1xx'],
                    "2xx": req['2xx'],
                    "3xx": req['3xx'],
                    "4xx": req['4xx'],
                    "5xx": req['5xx'],
                    "NaN": req['NaN'],
                    "min": req['min'],
                    "max": req['max'],
                    "mean": req['mean'],
                    "pct50": req['pct50'],
                    "pct75": req['pct75'],
                    "pct90": req['pct90'],
                    "pct95": req['pct95'],
                    "pct99": req['pct99']
                }
            }
            points.append(influx_record)
        try:
            self.client.switch_database(self.args['influx_comparison_database'])
            self.client.write_points(points)
            self.client.close()
        except Exception as e:
            print(e)
