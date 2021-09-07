from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS
from data_exporter import DataExporter


class InfluxExporter(DataExporter):
    def __init__(self, database_address: str, bucket: str, org: str, token: str):
        self.db_client = InfluxDBClient(url=database_address, token=token, retries=0)
        self.write_api = self.db_client.write_api(write_options=ASYNCHRONOUS)
        self.bucket = bucket
        self.org = org

    def write(self, point):
        try:
            self.write_api.write(self.bucket, self.org, point)
        except Exception as e:
            print(str(e))

    def write_points(self, points):
        try:
            self.write_api.write_points(self.bucket, self.org, points)
        except Exception as e:
            print(str(e))

    def export_farm_summary(self, data: FarmSummary):
        point = Point("farm_summary") \
            .tag("user_name", data.user_name) \
            .field("total_chia_farmed", data.total_chia_farmed) \
            .field("user_transaction_fees", data.user_transaction_fees) \
            .field("block_rewords", data.block_rewords) \
            .field("last_farmed_height", data.last_farmed_height) \
            .field("estimated_network_space", data.estimated_network_space) \
            .field("expected_time_to_win", data.expected_time_to_win) \
            .field("plots_count", data.plots_count) \
            .field("plots_size", data.plots_size) \
            .time(datetime.utcnow(), WritePrecision.NS)

        self.write(point)

    def export_harvesters_summary(self, data: [HarversterSummary]):
        points = []
        for item in data:
            points.append( Point("harvester") \
                .tag("user_name", data.user_name) \
                .field("ip", data.ip) \
                .field("name", data.name) \
                .field("plots_count", data.plots_count) \
                .field("plots_size", data.plots_size))

        self.write_points(points)
