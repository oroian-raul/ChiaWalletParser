import socket
from subprocess import check_output
from time import sleep

from data_exporter import DataExporter


class WalletParser:

    def __init__(self, parser_user: str,
                 dry_run: bool,
                 sleep_interval: int,
                 harvesters_name_mapping: dict,
                 path_to_chia,
                 data_exporter: DataExporter):
        self.data_exporter = data_exporter
        self.parser_user = parser_user
        self.harvesters_name_mapping = harvesters_name_mapping
        self.dry_run = dry_run
        self.sleep_interval = sleep_interval
        self.path_to_chia = path_to_chia

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

    @staticmethod
    def get_info_value(info: str):
        value_index_start = info.find(":")
        if value_index_start == -1:
            return None

        value_index_start += 2

        value_index_end = info.find(" ", value_index_start)
        if value_index_end == -1:
            value_index_end = len(info)
        return info[value_index_start: value_index_end]

    def export_farm_info(self):
        def get_harvester_plots_info(info: str):
            plots_count = int(info[3:info[3:].find(" ") + 3])
            plots_size = float(self.get_info_value(info))
            return plots_count, plots_size

        def get_info_time_to_win(info: str):
            multiplier_type_values = {"day": 1,
                                      "days": 1,
                                      "week": 7,
                                      "weeks": 7,
                                      "month": 31,
                                      "months": 31,
                                      "year": 365,
                                      "years": 365,
                                      }
            value_str = info[info.find(":") + 2:]
            value_items = [item for item in value_str.split() if item != "and"]
            index = 0
            value = 0
            while index < len(value_items):
                multiplier = int(value_items[index])
                index += 1
                multiplier_type = value_items[index]
                value += multiplier * multiplier_type_values[multiplier_type]
                index += 1

            return value

        harvesters_summary = []
        res = self.run_command(f"{self.path_to_chia}\\chia.exe farm summary")

        index = 0
        while index < len(res):
            item = res[index]
            if "User transaction fees" in item:
                user_transaction_fees = float(self.get_info_value(item))
            elif "Total chia farmed" in item:
                total_chia_farmed = float(self.get_info_value(item))
            elif "Block rewards" in item:
                block_rewords = float(self.get_info_value(item))
            elif "Last height farmed" in item:
                last_farmed_height = int(self.get_info_value(item))
            elif "Plot count for all harvesters" in item:
                plots_count = int(self.get_info_value(item))
            elif "Total size of plots" in item:
                plots_size = float(self.get_info_value(item))
            elif "Estimated network space" in item:
                estimated_network_space = float(self.get_info_value(item))
            elif "Expected time to win" in item:
                expected_time_to_win = get_info_time_to_win(item)
            elif "Local Harvester" in item or "Remote Harvester" in item:
                ip = self.get_info_value(item)

                # Local Harvester
                if ip is None:
                    ip = self.local_ip_address

                name = self.harvesters_name_mapping.get(ip, "None")
                index += 1
                plot_info = get_harvester_plots_info(res[index])
                harvesters_summary.append(DataExporter.HarvesterSummary(
                    user_name=self.parser_user,
                    ip=ip,
                    name=name,
                    plots_count=plot_info[0],
                    plots_size=plot_info[1]
                ))
            index += 1

        farm_summary = DataExporter.FarmSummary(
            user_name=self.parser_user,
            user_transaction_fees=user_transaction_fees,
            expected_time_to_win=expected_time_to_win,
            estimated_network_space=estimated_network_space,
            plots_size=plots_size,
            plots_count=plots_count,
            last_farmed_height=last_farmed_height,
            total_chia_farmed=total_chia_farmed,
            block_rewords=block_rewords
        )

        print(farm_summary)
        self.data_exporter.export_farm_summary(farm_summary)

        print(harvesters_summary)
        self.data_exporter.export_harvesters_summary(harvesters_summary)

    def export_wallet_info(self):
        def get_wallet_id_info(info):
            wallet_id_index_start = info.find("ID") + 3
            wallet_id = info[wallet_id_index_start: info.find(" ", wallet_id_index_start)]

            wallet_type_index_start = info.find("type") + 5
            wallet_type = info[wallet_type_index_start: info.find(" ", wallet_type_index_start)]

            return wallet_id, wallet_type

        res = self.run_command(f"{self.path_to_chia}\\chia.exe wallet show")

        balances_fingerprint = None
        wallets_info = []
        index = 0
        while index < len(res):
            item = res[index]
            if "Balances, fingerprint" in item:
                balances_fingerprint = self.get_info_value(item)
            elif "Wallet ID" in item:
                wallet_id, wallet_type = get_wallet_id_info(item)
                index += 1
                item = res[index]
                total_balance = float(self.get_info_value(item))

                index += 1
                item = res[index]
                pending_total_balance = float(self.get_info_value(item))

                index += 1
                item = res[index]
                spendable = float(self.get_info_value(item))

                wallets_info.append(DataExporter.WalletSummary(
                    user_name=self.parser_user,
                    balances_fingerprint=balances_fingerprint,
                    wallet_id=wallet_id,
                    wallet_type=wallet_type,
                    total_balance=total_balance,
                    pending_total_balance=pending_total_balance,
                    spendable=spendable
                ))
            index += 1

        print(wallets_info)
        self.data_exporter.export_wallet_summary(wallets_info)

    def start(self):
        while True:
            self.export_farm_info()
            self.export_wallet_info()
            sleep(self.sleep_interval)
