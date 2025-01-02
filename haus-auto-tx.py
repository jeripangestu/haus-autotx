import random
import time
import os
import requests
from web3 import Web3
from dotenv import load_dotenv

# Prompt user to input the private key
private_key_input = input("Enter your private key: ").strip()

# File .env path
env_file_path = ".env"

# Update or create .env file with the new private key
if os.path.exists(env_file_path):
    with open(env_file_path, "r") as file:
        lines = file.readlines()
    
    with open(env_file_path, "w") as file:
        for line in lines:
            if line.startswith("PRIVATE_KEY="):
                file.write(f"PRIVATE_KEY={private_key_input}\n")
            else:
                file.write(line)
else:
    # Create .env if it doesn't exist
    with open(env_file_path, "w") as file:
        file.write(f"PRIVATE_KEY={private_key_input}\n")

print("✅ Private key updated in .env file.")

# Load environment variables
load_dotenv()

# User Configurations (Replace with your own or use .env)
PRIVATE_KEY = os.getenv('PRIVATE_KEY')  # Add your private key to .env
SENDER_ADDRESS = input("Enter your wallet address: ").strip()
RECIPIENT_ADDRESS = input("Enter the recipient wallet address: ").strip()
MIN_AMOUNT = float(input("Enter minimum transfer amount: ").strip())
MAX_AMOUNT = float(input("Enter maximum transfer amount: ").strip())
LOOP_COUNT = int(input("Enter the number of transactions to loop: ").strip())

# Sleep time settings
MIN_SLEEP_TIME = int(input("Enter the minimum sleep time (seconds): ").strip())
MAX_SLEEP_TIME = int(input("Enter the maximum sleep time (seconds): ").strip())

# Haust Testnet Configuration
RPC_URL = "https://rpc-test.haust.network"
CHAIN_ID = 1570754601
CURRENCY_SYMBOL = "HAUST"
EXPLORER_URL = "https://explorer-test.haust.network"

# Connect to Blockchain
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Verify Connection
if web3.is_connected():
    print(f"✅ Connected to Haust Testnet ({RPC_URL})")
else:
    raise ConnectionError("❌ Failed to connect to Haust Testnet!")

# Derive sender address from private key if not input directly
if not SENDER_ADDRESS:
    SENDER_ADDRESS = web3.eth.account.from_key(PRIVATE_KEY).address
print(f"🔑 Wallet Address: {SENDER_ADDRESS}")

# Function to fetch balance from the API
def get_balance_from_explorer(address):
    try:
        url = f"https://explorer-test.haust.network/api/v2/addresses/{address}/coin-balance-history-by-day"
        response = requests.get(url)
        response.raise_for_status()  # Check for successful response

        # Parse the response JSON
        data = response.json()
        
        # Extract the balance value
        balance_wei = int(data['items'][0]['value'])
        
        # Convert Wei to HAUST
        balance_haust = balance_wei / 1e18
        
        print(f"🔍 Current Balance for {address}: {balance_haust:.7f} HAUST")
        return balance_haust
    except Exception as e:
        print(f"❌ Failed to fetch balance: {e}")
        return None

# Function to send a transaction
def send_transaction(sender, recipient, amount, private_key):
    try:
        nonce = web3.eth.get_transaction_count(sender)
        gas_price = web3.eth.gas_price

        tx = {
            'nonce': nonce,
            'to': recipient,
            'value': web3.to_wei(amount, 'ether'),
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': CHAIN_ID,
        }

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"✅ Transaction sent! Tx Hash: {tx_hash.hex()}")
        print(f"🔗 Explorer: {EXPLORER_URL}/tx/{tx_hash.hex()}")
        return tx_hash.hex()

    except Exception as e:
        print(f"❌ Transaction failed: {e}")
        return None

# Main Loop for Transactions
def main():
    for i in range(LOOP_COUNT):
        amount = random.uniform(MIN_AMOUNT, MAX_AMOUNT)
        print(f"\n🔄 Loop {i + 1}/{LOOP_COUNT}")
        print(f"💸 Sending {amount:.6f} {CURRENCY_SYMBOL} to {RECIPIENT_ADDRESS}")
        
        tx_hash = send_transaction(SENDER_ADDRESS, RECIPIENT_ADDRESS, amount, PRIVATE_KEY)
        
        if tx_hash:
            print(f"✅ Transaction Successful: {tx_hash}")
            # Fetch the latest balance after the transaction
            get_balance_from_explorer(SENDER_ADDRESS)
        else:
            print("❌ Transaction Failed, stopping further execution.")
            break

        # Random sleep time between MIN_SLEEP_TIME and MAX_SLEEP_TIME
        sleep_time = random.randint(MIN_SLEEP_TIME, MAX_SLEEP_TIME)
        print(f"⏳ Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)

# Entry Point
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Script terminated by user.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
