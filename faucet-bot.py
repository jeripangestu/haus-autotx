import os
import requests
import random
from web3 import Web3
from dotenv import load_dotenv
from threading import Thread
from time import sleep

# Load environment variables
load_dotenv()

# Configuration
FAUCET_API_URL = "https://faucet-test.haust.network/api/claim"
PROXY_FILE = "proxylist.txt"

# Load private keys from .env
def load_private_keys(env_file=".env"):
    try:
        with open(env_file, "r") as file:
            private_keys = [line.strip() for line in file if line.strip()]
        if not private_keys:
            raise ValueError("No private keys found in .env file.")
        return private_keys
    except Exception as e:
        print(f"âŒ Error loading private keys: {e}")
        exit()

# Load proxies from file
def load_proxies(file_path):
    try:
        if not os.path.exists(file_path):
            print(f"âš ï¸ Proxy file '{file_path}' not found. Running without proxies.")
            return []
        
        with open(file_path, "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
        
        if not proxies:
            print("âš ï¸ Proxy list is empty. Running without proxies.")
        
        return proxies
    except Exception as e:
        print(f"âŒ Error loading proxies: {e}")
        return []

# Connect to a wallet and extract the address
def get_wallet_address(private_key):
    try:
        account = Web3().eth.account.from_key(private_key)
        return account.address
    except Exception as e:
        print(f"âŒ Failed to derive wallet address: {e}")
        return None

# Make a faucet request with a proxy
def request_faucet(address, proxy=None):
    payload = {
        "address": address
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "FaucetBot/1.0"
    }
    
    proxies = {
        "http": proxy,
        "https": proxy
    } if proxy else None

    try:
        if proxy:
            print(f"ðŸŒ Using proxy: {proxy}")
        else:
            print("ðŸŒ No proxy being used.")

        response = requests.post(
            FAUCET_API_URL, 
            json=payload, 
            headers=headers, 
            proxies=proxies, 
            timeout=10
        )
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"âœ… Faucet Claim Successful! Response: {response_data['msg']}")
            return response_data['msg']
        else:
            print(f"âŒ Faucet Claim Failed! Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
    except requests.exceptions.ProxyError:
        print("âŒ Proxy failed. Skipping this proxy...")
        return None
    except Exception as e:
        print(f"âŒ Error during faucet request: {e}")
        return None

# Threaded faucet process for each PK-proxy pair
def faucet_process(private_key, proxy):
    wallet_address = get_wallet_address(private_key)
    
    if not wallet_address:
        print(f"âŒ Could not derive wallet address for Private Key: {private_key}. Skipping...")
        return
    
    success = False
    while not success:  # Keep looping until success
        print(f"ðŸ”‘ Wallet Address: {wallet_address} | Proxy: {proxy if proxy else 'No Proxy'}")
        tx_hash = request_faucet(wallet_address, proxy)
        
        if tx_hash:
            print(f"ðŸŽ‰ Success! Transaction Hash: {tx_hash}")
            success = True
        else:
            print(f"âŒ Faucet claim failed for Wallet: {wallet_address}. Retrying in 10 seconds...")
            sleep(10)

# Main function
def main():
    while True:  # Infinite loop to repeat the process
        # Load private keys and proxies
        private_keys = load_private_keys()
        proxies = load_proxies(PROXY_FILE)

        if not proxies:
            proxies = [None] * len(private_keys)  # No proxies, use None for each PK

        if len(private_keys) != len(proxies):
            print(f"? Mismatch: {len(private_keys)} private keys and {len(proxies)} proxies.")
            print("Ensure each private key has a corresponding proxy in proxylist.txt.")
            return

        threads = []
        for private_key, proxy in zip(private_keys, proxies):
            thread = Thread(target=faucet_process, args=(private_key, proxy))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        print("? All faucet claims completed. Restarting process in 30 seconds...")
        sleep(30)  # Optional wait time before restarting

# Entry Point
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nðŸ›‘ Script terminated by user.")
    except Exception as e:
        print(f"âŒ Unexpected Error: {e}")
