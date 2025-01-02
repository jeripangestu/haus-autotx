# faucet-bot.py

import os
import requests
import random
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
FAUCET_API_URL = "https://faucet-test.haust.network/api/claim"
PROXY_FILE = "proxylist.txt"


# Connect to a wallet and extract the address
def get_wallet_address(private_key):
    try:
        account = Web3().eth.account.from_key(private_key)
        return account.address
    except Exception as e:
        print(f"❌ Failed to derive wallet address: {e}")
        return None


# Load proxies from file
def load_proxies(file_path):
    try:
        if not os.path.exists(file_path):
            print(f"⚠️ Proxy file '{file_path}' not found. Running without proxies.")
            return []
        
        with open(file_path, 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
        
        if not proxies:
            print("⚠️ Proxy list is empty. Running without proxies.")
        
        return proxies
    except Exception as e:
        print(f"❌ Error loading proxies: {e}")
        return []


# Select a random proxy
def get_random_proxy(proxies):
    return random.choice(proxies) if proxies else None


# Make a faucet request with or without a proxy
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
            print(f"🌐 Using proxy: {proxy}")
        else:
            print("🌐 No proxy being used.")

        response = requests.post(
            FAUCET_API_URL, 
            json=payload, 
            headers=headers, 
            proxies=proxies, 
            timeout=10
        )
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Faucet Claim Successful! Response: {response_data['msg']}")
            return response_data['msg']
        else:
            print(f"❌ Faucet Claim Failed! Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
    except requests.exceptions.ProxyError:
        print("❌ Proxy failed. Skipping this proxy...")
        return None
    except Exception as e:
        print(f"❌ Error during faucet request: {e}")
        return None


# Main Function
def main():
    if not PRIVATE_KEY:
        print("❌ PRIVATE_KEY is not set in the .env file.")
        return
    
    print("🔑 Extracting wallet address from private key...")
    wallet_address = get_wallet_address(PRIVATE_KEY)
    
    if not wallet_address:
        print("❌ Could not derive wallet address. Exiting...")
        return
    
    print(f"✅ Wallet Address: {wallet_address}")
    
    # Load and validate proxies
    proxies = load_proxies(PROXY_FILE)
    use_proxy = len(proxies) > 0
    
    if use_proxy:
        print(f"✅ Loaded {len(proxies)} proxies. Proxies will be used.")
    else:
        print("⚠️ No proxies loaded. Running without proxies.")
    
    success = False
    attempts = 0
    max_attempts = len(proxies) if use_proxy else 1  # At least one attempt without proxies
    
    while not success and attempts < max_attempts:
        proxy = get_random_proxy(proxies) if use_proxy else None
        if proxy and use_proxy:
            proxies.remove(proxy)  # Remove used proxy
        attempts += 1
        
        print(f"🚀 Attempt {attempts}/{max_attempts}")
        tx_hash = request_faucet(wallet_address, proxy)
        
        if tx_hash:
            print(f"🎉 Success! Transaction Hash: {tx_hash}")
            success = True
        else:
            print("❌ Faucet claim failed. Trying again...\n")
    
    if not success:
        print("❌ All attempts failed. Please check your proxy list or connection.")


# Entry Point
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Script terminated by user.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
