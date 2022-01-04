from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

#  look for .env
load_dotenv()

# 1- read the smart contract
with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# 2- compile smart contract
install_solc("0.6.0"),
compile_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

# 3- create a json file
with open("compiled_code.json", "w") as file:
    json.dump(compile_sol, file)

# 4- get the bytecode
bytecode = compile_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# 5- get the abi
abi = compile_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# 6- connect blockchain
rinkeby = os.getenv("RINKEBY")
private_key = os.getenv("PRIVATE_KEY")
my_address = os.getenv("MY_ADDRESS")
# w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545")) ganache ui
# w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545")) ganache-cli --deterministic
w3 = Web3(Web3.HTTPProvider(rinkeby)) # rinkeby

# chain_id = 1337 ganache
chain_id = 4 # rinkeby


# 7- deploy
# a - build
# create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# get latest transaction nonce
nonce = w3.eth.getTransactionCount(my_address)
# since our contract does not have constructor
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
# b - sign transaction
signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# c - send transaction
print('Deploying...')
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print('Deployed')


# 8- intract with the contract
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print('Updating Contract...')
store_transaction = simple_storage.functions.store(16).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,  # every transaction new nonce
    }
)
# b - sign transaction
signed_store_tx = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
# c - send transaction
store_tx_hash = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)
store_tx_receipt = w3.eth.wait_for_transaction_receipt(store_tx_hash)
print('Updated')

print(simple_storage.functions.retrieve().call())
