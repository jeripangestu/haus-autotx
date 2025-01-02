import random
import time
from web3 import Web3
from dotenv import load_dotenv
import os
from threading import Thread
from rich.console import Console
from rich.table import Table
from rich import box

# Load environment variables
load_dotenv()

# Initialize console for better output
console = Console()

# User Configurations
with open(".env", "r") as file:
    PRIVATE_KEYS = [line.strip() for line in file if line.strip()]  # Read all private keys line by line

if not PRIVATE_KEYS:
    raise ValueError("No private keys found in .env file!")

MIN_AMOUNT = float(input("Enter minimum transfer amount: ").strip())
MAX_AMOUNT = float(input("Enter maximum transfer amount: ").strip())

# Haust Testnet Configuration
RPC_URL = "https://rpc-test.haust.network"
CHAIN_ID = 1570754601
CURRENCY_SYMBOL = "HAUST"

# Connect to Blockchain
web3 = Web3(Web3.HTTPProvider(RPC_URL))
if not web3.is_connected():
    console.print("[bold red]❌ Failed to connect to Haust Testnet![/bold red]")
    raise ConnectionError("Failed to connect to Haust Testnet!")

console.print(f"[bold green]✅ Connected to Haust Testnet ({RPC_URL})[/bold green]")

# Get addresses from private keys
def get_addresses_from_private_keys(keys):
    addresses = []
    for key in keys:
        address = web3.eth.account.from_key(key).address
        addresses.append(address)
    return addresses

# Add addresses to address.txt
private_key_addresses = get_addresses_from_private_keys(PRIVATE_KEYS)
with open("address.txt", "a+") as file:
    file.seek(0)
    existing_addresses = {line.strip() for line in file if line.strip()}
    for address in private_key_addresses:
        if address not in existing_addresses:
            file.write(address + "\n")

# Load recipient addresses
with open("address.txt", "r") as file:
    recipient_addresses = [line.strip() for line in file if line.strip()]
if not recipient_addresses:
    raise ValueError("No recipient addresses found in address.txt.")

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

        console.print(f"[bold green]✅ Transaction Successful![/bold green] [blue]Tx Hash:[/blue] {tx_hash.hex()}")
        return tx_hash.hex()

    except Exception as e:
        console.print(f"[bold red]❌ Transaction failed:[/bold red] {e}")
        return None

def process_transactions_for_key(private_key, recipient_addresses):
    sender_address = web3.eth.account.from_key(private_key).address
    console.print(f"\n[bold cyan]🔑 Starting transactions for Private Key:[/bold cyan] {sender_address}")

    for recipient_address in recipient_addresses:
        amount = random.uniform(MIN_AMOUNT, MAX_AMOUNT)
        console.print(f"[yellow]💸 Sending {amount:.6f} {CURRENCY_SYMBOL} from {sender_address} to {recipient_address}[/yellow]")

        tx_hash = send_transaction(sender_address, recipient_address, amount, private_key)
        time.sleep(random.randint(12, 25))

# Main Loop for Multithreading
def main():
    while True:  # Infinite loop to repeat the process
        threads = []
        table = Table(title="Transaction Summary", box=box.DOUBLE_EDGE)
        table.add_column("Private Key", style="cyan", justify="center")
        table.add_column("Recipient Address", style="magenta", justify="center")
        table.add_column("Amount", style="green", justify="center")
        table.add_column("Status", style="bold")

        for private_key in PRIVATE_KEYS:
            thread = Thread(target=process_transactions_for_key, args=(private_key, recipient_addresses))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        console.print("[bold magenta]🔄 All private keys processed. Restarting the loop...[/bold magenta]")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print("[bold red]\n🛑 Script terminated by user.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Unexpected Error:[/bold red] {e}")
