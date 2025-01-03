import os
import asyncio
import random
import requests
from web3 import Web3
import configparser
from colorama import Fore, Style, init

init(autoreset=True)

config = configparser.ConfigParser()
config.read('config.ini')

FAUCET_API_URL = config.get('General', 'FAUCET_API_URL')
PROXY_FILE = config.get('General', 'PROXY_FILE')
PRIVATE_KEY_FILE = config.get('General', 'PRIVATE_KEY_FILE')
RPC_URL = config.get('General', 'RPC_URL')
CHAIN_ID = int(config.get('General', 'CHAIN_ID'))
CURRENCY_SYMBOL = config.get('General', 'CURRENCY_SYMBOL')
MIN_AMOUNT = float(config.get('Transactions', 'MIN_AMOUNT'))
MAX_AMOUNT = float(config.get('Transactions', 'MAX_AMOUNT'))

def load_private_keys(private_key_file=PRIVATE_KEY_FILE):
    try:
        with open(private_key_file, "r") as file:
            private_keys = [line.strip() for line in file if line.strip()]
        if not private_keys:
            raise ValueError(f"No private keys found in {PRIVATE_KEY_FILE} file.")
        return private_keys
    except Exception as e:
        print(f"{Fore.RED}❌ Error loading private keys: {e}")
        exit()

def load_proxies(proxy_file=PROXY_FILE):
    try:
        with open(proxy_file, "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
        if not proxies:
            print(f"{Fore.YELLOW}⚠️ Proxy list is empty. Running without proxies.")
            return [None] 
        return proxies
    except Exception as e:
        print(f"{Fore.RED}❌ Error loading proxies: {e}")
        exit()

def get_wallet_address(private_key):
    account = Web3().eth.account.from_key(private_key)
    return account.address

async def faucet_process(private_key, proxy):
    wallet_address = get_wallet_address(private_key)
    print(f"{Fore.CYAN}🔑 Wallet Address: {wallet_address} | Proxy: {proxy if proxy else 'No Proxy'}")

    payload = {
        "address": wallet_address
    }
    headers = {
        "Content-Type": "application/json"
    }
    proxies_dict = {"http": proxy, "https": proxy} if proxy else None

    try:
        response = requests.post(FAUCET_API_URL, json=payload, headers=headers, proxies=proxies_dict, timeout=10)
        if response.status_code == 200:
            response_data = response.json()
            print(f"{Fore.GREEN}🎉 Faucet Claim Successful! Response: {response_data.get('msg', 'No message')}")
        else:
            response_data = response.json()
            print(f"{Fore.RED}❌ Faucet Claim Failed! Status Code: {response.status_code} | Response: {response_data}")
    except requests.exceptions.ProxyError:
        print(f"{Fore.RED}❌ Proxy failed. Skipping this proxy...")
    except Exception as e:
        print(f"{Fore.RED}❌ Error during faucet request: {e}")

async def auto_tx_process(private_key, min_amount, max_amount, all_wallets):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    sender_address = Web3().eth.account.from_key(private_key).address
    recipient_address = random.choice(all_wallets)  
    amount = random.uniform(min_amount, max_amount)

    try:
        nonce = w3.eth.get_transaction_count(sender_address)
        gas_price = w3.eth.gas_price

        tx = {
            'nonce': nonce,
            'to': recipient_address,
            'value': w3.to_wei(amount, 'ether'),
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': CHAIN_ID,
        }

        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print(f"{Fore.MAGENTA}💸 Send Balance from address: {sender_address} to {recipient_address} | amount: {amount} {CURRENCY_SYMBOL}")
        print(f"{Fore.GREEN}✅ Transaction Successful! Tx Hash: {tx_hash.hex()}\n")
    except Exception as e:
        print(f"{Fore.RED}❌ Transaction failed: {e}")

async def main():
    private_keys = load_private_keys()
    proxies = load_proxies()

    if len(proxies) < len(private_keys):
        proxies = (proxies * (len(private_keys) // len(proxies) + 1))[:len(private_keys)]

    all_wallets = [get_wallet_address(private_key) for private_key in private_keys]

    while True:  
        for private_key, proxy in zip(private_keys, proxies):
            await faucet_process(private_key, proxy)
            await auto_tx_process(private_key, MIN_AMOUNT, MAX_AMOUNT, all_wallets)
            print(f"{Fore.BLUE}🟢 Next Account\n")
        print(f"{Fore.GREEN}🔄 Repeating the process for all accounts...\n")
        await asyncio.sleep(7200)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Script terminated by user.")
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected Error: {e}")