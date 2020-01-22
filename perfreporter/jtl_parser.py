import csv


FIELDNAMES = 'timeStamp', 'response_time', 'request_name', "status_code", "responseMessage", "threadName", "dataType",\
             "success", "failureMessage", "bytes", "sentBytes", "grpThreads", "allThreads", "URL", "Latency",\
             "IdleTime", "Connect"


class JTLParser(object):

    @staticmethod
    def parse_jtl():
        path = "/tmp/reports/jmeter.xml"
        unparsed_counter = 0
        requests = []
        with open(path, 'r+', encoding="utf-8") as tsv:
            for entry in csv.DictReader(tsv, delimiter=",", fieldnames=FIELDNAMES, restval="not_found"):
                try:
                    data = {'request_name': entry['request_name'],
                            'response_time': entry['response_time'],
                            'status': entry['success'],
                            'failureMessage': entry['failureMessage']}
                    requests.append(data)
                except Exception as e:
                    print(e)
                    unparsed_counter += 1
                    pass

        if unparsed_counter > 0:
            print("Unparsed errors: %d" % unparsed_counter)
        return requests
