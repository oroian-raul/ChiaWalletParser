from collections import namedtuple


class DataExporter:
    FarmSummary = namedtuple("FarmSummary",
                             ["user_name", "total_chia_farmed", "user_transaction_fees", "block_rewords",
                              "last_farmed_height", "estimated_network_space", "expected_time_to_win",
                              "plots_count", "plots_size"])

    HarvesterSummary = namedtuple("HarvesterSummary", ["user_name", "ip", "name", "plots_count", "plots_size"])

    WalletSummary = namedtuple("WalletSummary", ["user_name", "wallet_id", "wallet_type", "total_balance",
                                                 "pending_total_balance", "spendable",
                                                 "balances_fingerprint"])

    def __init__(self, database_address: str, bucket: str, org: str, token: str):
        raise NotImplementedError('Not implemented')

    def export_farm_summary(self, data: FarmSummary):
        raise NotImplementedError('Not implemented')

    def export_harvesters_summary(self, data: [HarvesterSummary]):
        raise NotImplementedError('Not implemented')

    def export_wallet_summary(self, data: [WalletSummary]):
        raise NotImplementedError('Not implemented')
