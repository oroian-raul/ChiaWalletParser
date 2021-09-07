import socket
import time

from data_exporter import DataExporter


class WalletParser:

    def __init__(self, parser_user: str, dry_run: bool, data_exporter: DataExporter):
        self.data_exporter = data_exporter
        self.parser_user = parser_user
        self.dry_run = dry_run
        self.start()

    def export_wallet_info(self):
        pass

    def start(self):
        while True:
            self.export_wallet_info()
