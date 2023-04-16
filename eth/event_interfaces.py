import json
import datetime
from typing import List, Optional, Dict
import os
from web3 import Web3
from retrying import retry
from solcx import compile_files, compile_source, install_solc, set_solc_version, compile_solc

from .provider.provider import Provider

install_solc(version='latest')


class EventDeployer:
    def __init__(self, provider: Provider, hr_duration=6):
        self.provider = provider

        if hr_duration == 6:
            self.contract_source_path = os.path.join(os.path.dirname(__file__), "contracts/OverUnderSixHour.sol")
            self.event_contract_name = ":OverUnderSixHour"
        elif hr_duration == 12:
            self.contract_source_path = os.path.join(os.path.dirname(__file__), "contracts/OverUnderTwelveHour.sol")
            self.event_contract_name = ":OverUnderTwelveHour"
        elif hr_duration == 24:
            self.contract_source_path = os.path.join(os.path.dirname(__file__), "contracts/OverUnderTwentyFourHour.sol")
            self.event_contract_name = ":OverUnderTwentyFourHour"

        self.w3_contract_handle = None
        self.contract_address = None
        self.contract_abi = None
        self.deploy_status = False

    def deploy_event_contract(self, price_mark, asset_symbol="BTC"):
        """
        :param asset_symbol:
        :param price_mark:
        :param contract_source_path:
        :param contract_modifiers:
        :return:
        """
        constructor_args = {
            "_priceMark": Web3.to_wei(price_mark, 'ether'),
            "_assetSymbol": asset_symbol.upper()
        }

        compiled_contract_info = self.compile_contract(contract_source_path=self.contract_source_path)
        compiled_abi = compiled_contract_info["compiled_abi"]
        compiled_bytecode = compiled_contract_info["compiled_bytecode"]

        txn_receipt_json = self.create_and_send_deploy_txn(compiled_abi=compiled_abi,
                                                           compiled_bytecode=compiled_bytecode,
                                                           constructor_args=constructor_args)

        if txn_receipt_json['status'] == 0:
            raise Exception('Transaction failed')
        else:
            self.contract_address = txn_receipt_json['contractAddress']
            self.contract_abi = compiled_abi
            self.deploy_status = True

        return txn_receipt_json

    def compile_contract(self, contract_source_path) -> Optional[Dict]:
        """
        Compile solidity contract and modify based on contract_modifiers
        :param contract_source_path:
        :param contract_modifiers:
        :return:
        """
        contract_id = None
        compiled_sol = compile_files(source_files=contract_source_path, output_values=['abi', 'bin'])

        for key in compiled_sol.keys():
            if self.event_contract_name in key:
                contract_id = key

        if contract_id is None:
            raise Exception("Contract ID not found")

        contract_interface = compiled_sol[contract_id]
        compiled_bytecode = contract_interface['bin']
        compiled_abi = contract_interface['abi']

        return {"compiled_bytecode": compiled_bytecode, "compiled_abi": compiled_abi}

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def create_and_send_deploy_txn(self, compiled_abi, compiled_bytecode, constructor_args) -> Optional[Dict]:
        """
        Create and send txn to deploy contract to ETHEREUM network
        :param compiled_abi: compliled json interface for contract
        :param compiled_bytecode: compiled bytecode for contract
        :param constructor_args: arguments for contract constructor
        :return:
        """
        contract = self.provider.w3.eth.contract(abi=compiled_abi, bytecode=compiled_bytecode)

        txn = {"from": self.provider.get_wallet_address(), "nonce": self.provider.get_nonce()}
        constructor = contract.constructor(**constructor_args).build_transaction(txn)

        signed_txn = self.provider.w3.eth.account.sign_transaction(constructor,
                                                                   private_key=self.provider.get_wallet_private_key())
        send_txn = self.provider.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = self.provider.w3.eth.wait_for_transaction_receipt(send_txn)

        return txn_receipt

    def get_contract_address(self):
        return self.contract_address

    def get_contract_abi(self):
        return self.contract_abi

    def is_contract_deployed(self):
        return self.deploy_status


class EventContractInterface:
    def __init__(self, provider: Provider, contract_address, contract_abi):
        self.provider = provider
        self.w3_contract_handle = self.provider.w3.eth.contract(address=contract_address, abi=contract_abi)
        if self.w3_contract_handle is None:
            raise Exception("Contract not found")
        else:
            self.contract_name = self.w3_contract_handle.functions.getContractName().call()
            self.contract_address = self.w3_contract_handle.address
            self.contract_abi = self.w3_contract_handle.abi
            self.price_mark = Web3.from_wei(self.w3_contract_handle.functions.getPriceMark().call(), 'ether')
            self.asset_symbol = self.w3_contract_handle.functions.getAssetSymbol().call()
            self.betting_close = self.w3_contract_handle.functions.getBettingClose().call()
            self.event_close = self.w3_contract_handle.functions.getEventClose().call()

            self.contract_balance = Web3.from_wei(self.w3_contract_handle.functions.getContractBalance().call(),
                                                  'ether')
            self.over_betters_balance = Web3.from_wei(self.w3_contract_handle.functions.getOverBettersBalance().call(),
                                                      'ether')
            self.under_betters_balance = Web3.from_wei(
                self.w3_contract_handle.functions.getUnderBettersBalance().call(), 'ether'
            )
            self.over_betting_payout_modifier = self.w3_contract_handle.functions.getOverBettingPayoutModifier().call()
            self.under_betting_payout_modifier = self.w3_contract_handle.functions.getUnderBettingPayoutModifier().call()
            self.over_betters_addresses = self.w3_contract_handle.functions.getOverBettersAddresses().call()
            self.under_betters_addresses = self.w3_contract_handle.functions.getUnderBettersAddresses().call()
            self.is_event_over = self.w3_contract_handle.functions.isEventOver().call()

    def get_event_contract_info(self) -> Optional[Dict]:

        contract_info = {
            "contract_name": self.contract_name,
            "contract_address": self.contract_address,
            "contract_abi": self.contract_abi,
            "price_mark": self.price_mark,
            "asset_symbol": self.asset_symbol,
            "betting_close": self.betting_close,
            "event_close": self.event_close,
            "contract_balance": self.contract_balance,
            "over_betters_balance": self.over_betters_balance,
            "under_betters_balance": self.under_betters_balance,
            "over_betting_payout_modifier": self.over_betting_payout_modifier,
            "under_betting_payout_modifier": self.under_betting_payout_modifier,
            "over_betters_addresses": self.over_betters_addresses,
            "under_betters_addresses": self.under_betters_addresses,
            "is_event_over": self.is_event_over
        }

        return contract_info
