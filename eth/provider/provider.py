from web3 import Web3


class Provider:
    def __init__(self, provider_url, wallet_address, wallet_private_key):
        self.provider = Web3.HTTPProvider(endpoint_uri=provider_url)
        self.w3 = Web3(self.provider)
        self.chain_id = self.w3.eth.chain_id
        self.is_connected = self.w3.is_connected()

        self.__wallet_address = wallet_address
        self.__wallet_private_key = wallet_private_key

    def get_chain_id(self):
        return self.chain_id

    def get_nonce(self):
        return self.w3.eth.get_transaction_count(self.__wallet_address)

    def get_is_connected(self):
        return self.is_connected

    def get_w3(self):
        return self.w3

    def get_provider(self):
        return self.provider

    def get_wallet_address(self):
        return self.__wallet_address

    def get_wallet_private_key(self):
        return self.__wallet_private_key
