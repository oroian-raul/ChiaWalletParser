from datetime import datetime
import traceback

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS
from data_exporter import DataExporter


class InfluxExporter(DataExporter):
    def __init__(self, database_address: str, bucket: str, org: str, token: str):
        self.db_client = InfluxDBClient(url=database_address, token=token, retries=0)
        self.write_api = self.db_client.write_api(write_options=ASYNCHRONOUS)
        self.bucket = bucket
        self.org = org

    def write(self, data):
        try:
            self.write_api.write(self.bucket, self.org, data)
        except:
            print(traceback.format_exc())

    def export_farm_summary(self, data: DataExporter.FarmSummary):
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

    def export_harvesters_summary(self, data: [DataExporter.HarvesterSummary]):
        points = []
        for item in data:
            points.append(Point("harvester_summary")
                          .tag("user_name", item.user_name)
                          .tag("ip", item.ip)
                          .tag("name", item.name)
                          .field("plots_count", item.plots_count)
                          .field("plots_size", item.plots_size))

        self.write(points)

    def export_wallet_summary(self, data: [DataExporter.WalletSummary]):
        points = []
        for item in data:
            points.append(Point("wallet_summary")
                .tag("user_name", item.user_name)
                .tag("balances_fingerprint", item.balances_fingerprint)
                .tag("wallet_id", item.wallet_id)
                .tag("wallet_type", item.wallet_type)
                .field("total_balance", item.total_balance)
                .field("pending_total_balance", item.pending_total_balance)
                .field("balances_fingerprint", item.balances_fingerprint)
                .field("spendable", item.spendable)
                .time(datetime.utcnow(), WritePrecision.NS))

        self.write(points)
