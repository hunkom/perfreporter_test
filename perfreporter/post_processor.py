from perfreporter.data_manager import DataManager
from perfreporter.reporter import Reporter
import requests
import re
import zipfile
import json


class PostProcessor:

    def __init__(self, config_file=None):
        self.config_file = config_file

    def post_processing(self, args, aggregated_errors):
        data_manager = DataManager(args)
        if self.config_file:
            with open("/tmp/config.yaml", "w") as f:
                f.write(self.config_file)
        reporter = Reporter()
        rp_service, jira_service = reporter.parse_config_file(args)
        reporter.report_errors(aggregated_errors, rp_service, jira_service)
        if args['influx_host']:
            data_manager.write_comparison_data_to_influx()
            performance_degradation_rate, compare_with_baseline = data_manager.compare_with_baseline()
            missed_threshold_rate, compare_with_thresholds = data_manager.compare_with_thresholds()
            reporter.report_performance_degradation(performance_degradation_rate, compare_with_baseline, rp_service,
                                                    jira_service)
            reporter.report_missed_thresholds(missed_threshold_rate, compare_with_thresholds, rp_service, jira_service)

    def distributed_mode_post_processing(self, galloper_url, results_bucket, build_id):
        errors = []
        args = {}
        r = requests.get(f'{galloper_url}/artifacts?q={results_bucket}')
        pattern = '<a href="/artifacts/{}/({}.+?)"'.format(results_bucket, build_id)
        files = re.findall(pattern, r.text)
        for file in files:
            downloaded_file = requests.get(f'{galloper_url}/artifacts/{results_bucket}/{file}')
            zip_file_object = zipfile.ZipFile(downloaded_file, 'r')
            errors.append(json.loads(zip_file_object.open("aggregated_errors.json")))
            if not args:
                args = json.loads(json.loads(zip_file_object.open("args.json")))

        print("******************************************************************")
        print(args)
        print(errors)
        print("******************************************************************")
        aggregated_errors = self.aggregate_errors(errors)
        print(aggregated_errors)
        print("******************************************************************")
        self.post_processing(args, aggregated_errors)

    @staticmethod
    def aggregate_errors(test_errors):
        aggregated_errors = {}
        for errors in test_errors:
            for err in errors:
                if err not in aggregated_errors:
                    aggregated_errors[err] = errors[err]
                else:
                    aggregated_errors[err]['Error count'] = int(aggregated_errors[err]['Error count']) \
                                                            + int(errors[err]['Error count'])

        return aggregated_errors
