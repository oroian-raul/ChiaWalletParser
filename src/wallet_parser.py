import socket
from subprocess import check_output
from time import sleep

from data_exporter import DataExporter


class WalletParser:

    def __init__(self, parser_user: str,
                 dry_run: bool,
                 sleep_interval: int,
                 harvesters_name_mapping: dict,
                 data_exporter: DataExporter):
        self.data_exporter = data_exporter
        self.parser_user = parser_user
        self.harvesters_name_mapping = harvesters_name_mapping
        self.dry_run = dry_run
        self.sleep_interval = sleep_interval

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
        self.local_ip_address = s.getsockname()[0]

        self.start()

    @staticmethod
    def run_command(command: str):
        output = None

        try:
            output = check_output(command, shell=True).decode()
        except Exception as e:
            print(str(e))

        return output.splitlines()

    def export_wallet_info(self):
        def get_info_value(info: str):
            value_index_start = info.find(":")
            if value_index_start == -1:
                return None

            value_index_start += 2

            value_index_end = info.find(" ", value_index_start)
            if value_index_end == -1:
                value_index_end = len(info)
            return info[value_index_start: value_index_end]

        def get_harvester_plots_info(info: str):
            plots_count = int(info[3:info[3:].find(" ")+3])
            plots_size = float(get_info_value(info))
            return plots_count, plots_size

        def get_info_time_to_win(info: str):
            return None

        farm_summary = DataExporter.FarmSummary
        farm_summary.user_name = self.parser_user
        harvesters_summary = []
        res = self.run_command("C:\\Users\Administrator\\AppData\\Local\\chia-blockchain\\app-1.2.5\\resources\\app.asar.unpacked\\daemon\\chia.exe farm summary")

        index = 0
        while index < len(res):
            item = res[index]
            if "User transaction fees" in item:
                farm_summary.user_transaction_fees = float(get_info_value(item))
            elif "Total chia farmed" in item:
                farm_summary.total_chia_farmed = float(get_info_value(item))
            elif "Block rewards" in item:
                farm_summary.block_rewords = float(get_info_value(item))
            elif "Last height farmed" in item:
                farm_summary.last_farmed_height = int(get_info_value(item))
            elif "Plot count for all harvesters" in item:
                farm_summary.plots_count = int(get_info_value(item))
            elif "Total size of plots" in item:
                farm_summary.plots_size = float(get_info_value(item))
            elif "Estimated network space" in item:
                farm_summary.estimated_network_space = float(get_info_value(item))
            elif "Expected time to win" in item:
                farm_summary.expected_time_to_win = get_info_time_to_win(item)
            elif "Local Harvester" in item or "Remote Harvester" in item:
                user_name = self.parser_user
                ip = get_info_value(item)

                # Local Harvester
                if ip is None:
                    ip = self.local_ip_address

                name = self.harvesters_name_mapping.get(ip, "None")
                index += 1
                plot_info = get_harvester_plots_info(res[index])
                harvesters_summary.append(DataExporter.HarvesterSummary(
                    user_name=user_name,
                    ip=ip,
                    name=name,
                    plots_count=plot_info[0],
                    plots_size=plot_info[1]
                ))
            index += 1

        print(farm_summary)
        self.data_exporter.export_farm_summary(farm_summary)

        print(harvesters_summary)
        self.data_exporter.export_harvesters_summary(harvesters_summary)

    def start(self):
        while True:
            self.export_wallet_info()
            sleep(self.sleep_interval)
