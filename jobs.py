import time
import random
from datetime import datetime
from typing import Dict, Optional

from db.schemas.event_schemas import ContractInfoModel
from eth.event_interfaces import EventContractInterface, EventDeployer


class EventDeployerJobs:

    def __init__(self, job_configs, provider_handler, mongo_handler):
        self.job_configs = job_configs
        self.provider_handler = provider_handler
        self.mongo_handler = mongo_handler

    def job_runner(self, run_indefinitely=True):
        while run_indefinitely:
            try:
                for job in self.job_configs:
                    if job["job_type"] == "betting_event_6h":
                        self.deploy_event_job(job_config=job,
                                              provider_handler=self.provider_handler,
                                              mongo_handler=self.mongo_handler)
                    elif job["job_type"] == "betting_event_12h":
                        pass
                    elif job["job_type"] == "betting_event_24h":
                        pass
                    else:
                        raise Exception("Invalid job type")
                print("Job runner sleeping for 2 hrs...")
                time.sleep(86400 / 12)
            except Exception as e:
                print(e)
                run_indefinitely = False

        return

    @classmethod
    def deploy_event_job(cls, job_config, provider_handler, mongo_handler):
        for asset in job_config["params"].keys():
            try:
                params = job_config['params'][asset]
                completed_to_be_updated_event_records = mongo_handler.find(
                    collection=params["collection_name"],
                    query={"is_event_over": False,
                           "event_close": {"$lt": datetime.now().timestamp()},
                           "asset_symbol": asset
                           }
                )
                print(
                    f"Found {len(list(completed_to_be_updated_event_records.clone()))} {asset} {params['collection_name']} "
                    f"completed events to be updated... "
                )
                for event_info in completed_to_be_updated_event_records:
                    event_status = cls.check_contract_status(provider_handler=provider_handler,
                                                             contract_address=event_info["contract_address"],
                                                             contract_abi=event_info["contract_abi"],
                                                             collection_name=params["collection_name"])
                    if event_status["is_event_over"]:
                        current_contract_address = event_status["contract_address"]
                        record_updated = cls.update_event_record(mongo_handler=mongo_handler,
                                                                 collection_name=params["collection_name"],
                                                                 current_contract_address=current_contract_address,
                                                                 current_contract_info=event_status)

                        if record_updated:
                            deployed_contract_interface = cls.deploy_events(provider_handler=provider_handler,
                                                                            mongo_handler=mongo_handler,
                                                                            asset_symbol=asset,
                                                                            collection_name=params[
                                                                                "collection_name"])
                            if deployed_contract_interface is not None:
                                contract_info = deployed_contract_interface.get_event_contract_info()
                                contract_info_record_data = ContractInfoModel(**contract_info)

                                contracts_response = mongo_handler.insert(collection=params["collection_name"],
                                                                          document=contract_info_record_data.dict())
                                if contracts_response.acknowledged:
                                    print("Event {} {} contract record created".format(params["collection_name"],
                                                                                       asset))
                            else:
                                raise Exception("Failed to establish event contract interface")
                        else:
                            raise Exception("Failed to update event record")

                ongoing_event_records = mongo_handler.find(
                    collection=params["collection_name"],
                    query={"is_event_over": False,
                           "event_close": {"$gt": datetime.now().timestamp()},
                           "asset_symbol": asset
                           }
                )

                if len(list(ongoing_event_records.clone())) == 0:
                    print("No {} {} events ongoing...".format(params["collection_name"], asset))
                    print("Deploying new contract...")
                    deployed_contract_interface = cls.deploy_events(provider_handler=provider_handler,
                                                                    mongo_handler=mongo_handler,
                                                                    asset_symbol=asset,
                                                                    collection_name=params["collection_name"])
                    if deployed_contract_interface is not None:
                        contract_info = deployed_contract_interface.get_event_contract_info()
                        contract_info_record_data = ContractInfoModel(**contract_info)

                        contracts_response = mongo_handler.insert(collection=params["collection_name"],
                                                                  document=contract_info_record_data.dict())

                        if contracts_response.acknowledged:
                            print(f"Event {asset} {params['collection_name']} record created")
                    else:
                        raise Exception(f"Failed to deploy {params['collection_name']} contract")

            except Exception as e:
                print(f"An error occurred while processing betting events: {str(e)}")
                return

    @classmethod
    def deploy_event(cls, provider_handler, mongo_handler, asset_symbol: str, hr_duration) -> Optional[EventDeployer]:
        event_deployer = EventDeployer(provider=provider_handler, hr_duration=hr_duration)
        price_mark = None
        if asset_symbol == "BTC":
            mongo_response = mongo_handler.find_one_sorted(collection='btc_live_price',
                                                           query=[("timestamp", -1)])
            btc_latest_price = mongo_response['price']
            price_mark = btc_latest_price + btc_latest_price * random.uniform(-0.07, 0.07)
        elif asset_symbol == "ETH":
            mongo_response = mongo_handler.find_one_sorted(collection='eth_live_price',
                                                           query=[("timestamp", -1)])
            eth_latest_price = mongo_response['price']
            price_mark = eth_latest_price + eth_latest_price * random.uniform(-0.07, 0.07)

        deploy_response = None
        if price_mark is not None:
            deploy_response = event_deployer.deploy_event_contract(price_mark=price_mark,
                                                                   asset_symbol=asset_symbol)

        if deploy_response is not None:
            return event_deployer
        else:
            return None

    @classmethod
    def deploy_events(cls, provider_handler, mongo_handler,
                      asset_symbol: str, collection_name: str) -> Optional[EventContractInterface]:
        asset_symbol = asset_symbol.upper()
        event_deployer = None

        if collection_name == "event_contracts_6h":
            event_deployer = cls.deploy_event(provider_handler=provider_handler,
                                              mongo_handler=mongo_handler, asset_symbol=asset_symbol, hr_duration=6)

        if collection_name == "event_contracts_12h":
            event_deployer = cls.deploy_event(provider_handler=provider_handler,
                                              mongo_handler=mongo_handler, asset_symbol=asset_symbol, hr_duration=12)

        if collection_name == "event_contracts_24h":
            event_deployer = cls.deploy_event(provider_handler=provider_handler,
                                              mongo_handler=mongo_handler, asset_symbol=asset_symbol, hr_duration=24)

        if event_deployer is not None:
            event_interface = EventContractInterface(provider=provider_handler,
                                                     contract_address=event_deployer.get_contract_address(),
                                                     contract_abi=event_deployer.get_contract_abi())
            return event_interface
        else:
            return None

    @classmethod
    def check_contract_status(cls, provider_handler, contract_address, contract_abi, collection_name) -> Optional[Dict]:
        contract_interface = EventContractInterface(provider=provider_handler,
                                                    contract_address=contract_address,
                                                    contract_abi=contract_abi)
        current_contract_info = contract_interface.get_event_contract_info()
        asset_symbol = current_contract_info['asset_symbol']

        if current_contract_info:
            print(f"Checked event {collection_name} {asset_symbol} status")
        else:
            print(f"Unable to check event {collection_name} {asset_symbol} status")
            raise Exception("Event status check failed")

        return current_contract_info

    @classmethod
    def update_event_record(cls, mongo_handler, collection_name, current_contract_address, current_contract_info):
        update_record = ContractInfoModel(**current_contract_info)
        update_result = mongo_handler.update(collection=collection_name,
                                             query={"contract_address": current_contract_address},
                                             document={"$set": update_record.dict()})

        asset_symbol = current_contract_info['asset_symbol']
        if update_result.acknowledged:
            print(f"Event {collection_name} {asset_symbol} record updated")
        else:
            print(f"Event {collection_name} {asset_symbol} record update failed")
            raise Exception("Event record update failed")

        return update_result.acknowledged
