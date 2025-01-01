from web3 import Web3
import sys
import random

def get_sender_address_from_private_key(web3, private_key):
    """Retrieve the address associated with the private key."""
    account = web3.eth.account.from_key(private_key)
    return account.address

def main():
    try:
        # Input private key
        private_key = input("Enter your private key: ").strip()
        
        # Input RPC URL
        rpc_url = input("Enter RPC URL: ").strip()
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Validate connection
        if not web3.is_connected():
            print("Failed to connect to the blockchain. Check your RPC URL.")
            sys.exit(1)
        
        # Retrieve sender address
        sender_address = get_sender_address_from_private_key(web3, private_key)
        print(f"Sender Address: {sender_address}")
        
        # Input recipient address
        recipient_address = input("Enter recipient address: ").strip()
        
        # Input minimum and maximum transaction amounts
        min_transaction = float(input("Enter minimum transaction amount (e.g., 0.00001): "))
        max_transaction = float(input("Enter maximum transaction amount (e.g., 0.0002): "))
        
        # Input number of transactions
        num_transactions = int(input("Enter the number of transactions to perform: "))
        
        # Get the chain ID (required for EIP-155 compliance)
        chain_id = web3.eth.chain_id
        
        # Initialize base gas price
        base_gas_price = web3.eth.gas_price
        
        for i in range(num_transactions):
            # Generate a random transaction amount within the range
            transaction_amount = round(random.uniform(min_transaction, max_transaction), 8)
            
            # Get the current nonce
            nonce = web3.eth.get_transaction_count(sender_address)
            
            # Increment gas price slightly for each subsequent transaction
            gas_price = base_gas_price + (i * web3.to_wei(0.0000001, 'ether'))  # Increase gas price incrementally
            
            # Prepare the transaction
            tx = {
                'nonce': nonce,
                'to': recipient_address,
                'value': web3.to_wei(transaction_amount, 'ether'),
                'gas': 49000,
                'gasPrice': gas_price,
                'chainId': chain_id  # Include the chain ID for EIP-155
            }
            
            # Sign the transaction
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            
            # Send the transaction
            tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Display transaction details
            print(f"Transaction {i + 1}/{num_transactions} sent!")
            print(f"Amount: {transaction_amount} ETH, Gas Price: {web3.from_wei(gas_price, 'gwei')} Gwei, Hash: {web3.to_hex(tx_hash)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
