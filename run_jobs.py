import multiprocessing
from dotenv import dotenv_values, find_dotenv

from eth.provider.provider import Provider

from db.mongo_interface import MongoInterface

from jobs import EventDeployerJobs

# Load environment variables
config = dotenv_values(dotenv_path=find_dotenv())


def event_deploy_worker():
    try:
        print("Connecting to Alchemy RPC...")
        provider = Provider(provider_url=config['ALCHEMY_SEPOLIA_URL'],
                            wallet_address=config['WALLET_ADDRESS'],
                            wallet_private_key=config['WALLET_PRIVATE_KEY'])
        if not provider.get_is_connected():
            raise Exception("Unable to connect to Alchemy RPC...")
    except Exception as e:
        print(e)
        print("Using Infura RPC instead...")
        try:
            provider = Provider(provider_url=config['INFURA_SEPOLIA_URL'],
                                wallet_address=config['WALLET_ADDRESS'],
                                wallet_private_key=config['WALLET_PRIVATE_KEY'])
            if not provider.get_is_connected():
                raise Exception("Unable to connect to Alchemy RPC...")
        except Exception as e:
            print(e)
            print("Exiting...")
            return

    mongo_handler = MongoInterface(db_name=config['MONGO_DB_NAME'],
                                   connection_url=config['MONGO_DB_CONNECTION_STRING'])
    job_configs = [
        {
            "job_type": "betting_event_6h",
            "params": {
                "BTC": {"collection_name": "event_contracts_6h"},
                "ETH": {"collection_name": "event_contracts_6h"}
            }
        },
        {
            "job_type": "betting_event_test",
            "params": {
                "BTC": {"collection_name": "event_contracts_test"},
                "ETH": {"collection_name": "event_contracts_test"}
            }
        }
    ]

    if config['is_test'].lower() == "true":
        is_test = True
    else:
        is_test = False

    EventDeployerJobs(job_configs=job_configs,
                      provider_handler=provider,
                      mongo_handler=mongo_handler).job_runner(is_test=is_test)

    return


if __name__ == '__main__':

    # process queue
    processes = []

    betting_events_job_process = multiprocessing.Process(target=event_deploy_worker)

    betting_events_job_process.start()

    # wait for all processes to finish
    for process in processes:
        process.join()

    pass
