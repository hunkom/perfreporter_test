from junit_xml import TestSuite, TestCase


class JUnit_reporter(object):

    @staticmethod
    def process_report(requests, thresholds):
        functional_test_cases, threshold_test_cases = [], []
        test_suites = []
        for req in requests:
            if requests[req]['KO'] != 0:
                functional_test_cases.append(TestCase(name=requests[req]['request_name'], stdout="PASSED: "+str(requests[req]['OK'])+". FAILED: " + str(requests[req]['KO']),
                                           stderr="FAILED: " + str(requests[req]['KO']), elapsed_sec=requests[req]['KO']))
                functional_test_cases[-1].add_failure_info("Request failed "+str(requests[req]['KO']) + " times")
            else:
                functional_test_cases.append(
                    TestCase(name=requests[req]['request_name'], stdout="PASSED: " + str(requests[req]['OK']),
                             stderr="FAILED: " + str(requests[req]['KO']), elapsed_sec=requests[req]['KO']))

        test_suites.append(TestSuite("Functional errors ", functional_test_cases))

        for th in thresholds:
            threshold_test_cases.append(TestCase(name="Threshold for "+th['scope']+", target - "+th['target'],
                                                 stdout="Value: "+str(th['value'])+". Threshold value: "+str(th['threshold'])))
            if th['status'] == 'FAILED':
                threshold_test_cases[-1].add_failure_info(th['target']+" for " + th['scope'] + " exceeded threshold of "
                                                          + str(th['threshold']) + " " + th['metric'] + ". Test result - "
                                                          + str(th['value']) + " " + th['metric'])

        test_suites.append(TestSuite("Thresholds ", threshold_test_cases))
        with open("/tmp/reports/jmeter.xml", 'w') as f:
            TestSuite.to_file(f, test_suites, prettyprint=True)
