import json
from perfreporter.comparison import Comparison


class DistributedModePostProcessor:

    def __init__(self, args, aggregated_errors, errors, comparison_data):
        self.aggregated_errors = aggregated_errors
        self.errors = errors
        self.comparison_data = comparison_data
        self.args = args

    def post_processing(self):
        influx_comparison = Comparison(self.args)
        influx_comparison.write_comparison_data_to_influx(self.comparison_data)
