from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
import os

# Networks setup
web3_local_rinkeby = Web3(Web3.HTTPProvider('http://127.0.0.1:8888'))
web3_arbitrum_rinkeby = Web3(Web3.HTTPProvider('https://rinkeby.arbitrum.io/rpc'))
acct = web3_arbitrum_rinkeby.eth.account.from_key(os.environ.get('ARBITRUM_PRIVATE_KEY'))
web3_arbitrum_rinkeby.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))
web3_arbitrum_rinkeby.eth.default_account = acct.address

# Arbitrum TheLootBox contract setup
addr_lootbox_arbitrum = os.environ.get("TEST_NET_ARBITRUM_LOOTBOX")
addr_lootbox_arbitrum_abi = os.environ.get("TEST_NET_ARBITRUM_LOOTBOX_ABI")
addr_lootbox_factory_rinkeby = os.environ.get("LOOTBOX_FACTORY_CONTRACT_RINKEBY")
addr_lootbox_factory_rinkeby_abi = os.environ.get("TEST_NET_RINKEBY_LOOTBOX_FACTORY_ABI")
lootbox_contract_arbitrum = web3_arbitrum_rinkeby.eth.contract(address=addr_lootbox_arbitrum, abi=addr_lootbox_arbitrum_abi)
lootbox_contract_rinkeby = web3_local_rinkeby.eth.contract(address=addr_lootbox_factory_rinkeby, abi=addr_lootbox_factory_rinkeby_abi)

# TheLootBox bundle contract setup
addr_lootbox_bundle_arbitrum = os.environ.get("TEST_NET_ARBITRUM_LOOTBOX_BUNDLE_CONTRACT")
addr_lootbox_arbitrum_abi_v2 = os.environ.get("TEST_NET_ARBITRUM_LOOTBOX_ABI_V2")
lootbox_contract_arbitrum_bundle = web3_arbitrum_rinkeby.eth.contract(address=addr_lootbox_bundle_arbitrum, abi=addr_lootbox_arbitrum_abi_v2)

# DAI contract setup
dai_abi = os.environ.get("DAI_ABI")
addr_dai = os.environ.get("DAI_ADDR")
dai_contract_rinkeby = web3_local_rinkeby.eth.contract(address=addr_dai, abi=dai_abi)

# Dev setup
dev = os.environ.get("DEV")
key = os.environ.get('ARBITRUM_PRIVATE_KEY')
gas_price = web3_arbitrum_rinkeby.eth.gasPrice