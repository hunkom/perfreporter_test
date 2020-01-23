import csv
import re
from os import path


FIELDNAMES = 'timeStamp', 'response_time', 'request_name', "status_code", "responseMessage", "threadName", "dataType",\
             "success", "failureMessage", "bytes", "sentBytes", "grpThreads", "allThreads", "URL", "Latency",\
             "IdleTime", "Connect"


class JTLParser(object):

    def parse_jtl(self):
        log_file = "/tmp/reports/jmeter.jtl"
        unparsed_counter = 0
        requests = {}
        if not path.exists(log_file):
            return requests
        start_timestamp, end_timestamp = float('inf'), 0
        with open(log_file, 'r+', encoding="utf-8") as tsv:
            entries = csv.DictReader(tsv, delimiter=",", fieldnames=FIELDNAMES, restval="not_found")

            for entry in entries:

                try:
                    if entry['request_name'] != 'label':
                        if re.search(r'-\d+$', entry['request_name']):
                                continue
                        if start_timestamp > int(entry['timeStamp']):
                            start_timestamp = int(entry['timeStamp']) - int(entry['response_time'])
                        if end_timestamp < int(entry['timeStamp']):
                            end_timestamp = int(entry['timeStamp'])
                        if entry['request_name'] not in requests:
                            data = {'request_name': entry['request_name'],
                                    'response_time': [int(entry['response_time'])]}
                            if entry['success'] == 'true':
                                data['OK'], data['KO'] = 1, 0
                            else:
                                data['OK'], data['KO'] = 0, 1
                            requests[entry['request_name']] = data
                        else:
                            requests[entry['request_name']]['response_time'].append(int(entry['response_time']))
                            if entry['success'] == 'true':
                                requests[entry['request_name']]['OK'] += 1
                            else:
                                requests[entry['request_name']]['KO'] += 1
                except Exception as e:
                    print(e)
                    unparsed_counter += 1
                    pass

        if unparsed_counter > 0:
            print("Unparsed errors: %d" % unparsed_counter)
        duration = int((end_timestamp - start_timestamp)/1000)
        print(duration)
        throughput = self.calculate_throughput(requests, duration)
        print(throughput)
        return requests

    def calculate_throughput(self, requests, duration):
        count = 0
        for req in requests:
            count += requests[req]['OK']
        return round(float(count/duration), 2)
