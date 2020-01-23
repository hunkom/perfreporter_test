import csv
import re


FIELDNAMES = 'timeStamp', 'response_time', 'request_name', "status_code", "responseMessage", "threadName", "dataType",\
             "success", "failureMessage", "bytes", "sentBytes", "grpThreads", "allThreads", "URL", "Latency",\
             "IdleTime", "Connect"


class JTLParser(object):

    @staticmethod
    def parse_jtl():
        path = "/tmp/reports/jmeter.xml"
        unparsed_counter = 0
        requests = {}
        start_timestamp, end_timestamp = int(float('inf')), 0
        with open(path, 'r+', encoding="utf-8") as tsv:
            entries = csv.DictReader(tsv, delimiter=",", fieldnames=FIELDNAMES, restval="not_found")

            for entry in entries:

                try:
                    if entry['request_name'] != 'label':
                        if re.search(r'-\d+$', entry['request_name']):
                                continue
                        if start_timestamp > int(entry['timeStamp']):
                            start_timestamp = int(entry['timeStamp'])
                        if end_timestamp < int(entry['timeStamp']):
                            end_timestamp = int(entry['timeStamp'])
                        if entry['request_name'] not in requests:
                            data = {'request_name': entry['request_name'],
                                    'response_time': [entry['response_time']],
                                    'count': 1}
                            requests[entry['request_name']] = data
                        else:
                            requests[entry['request_name']]['response_time'].append(entry['response_time'])
                            requests[entry['request_name']]['count'] += 1
                except Exception as e:
                    print(e)
                    unparsed_counter += 1
                    pass

        if unparsed_counter > 0:
            print("Unparsed errors: %d" % unparsed_counter)
        duration = end_timestamp - start_timestamp
        print(duration)
        print(duration/1000)
        return requests
