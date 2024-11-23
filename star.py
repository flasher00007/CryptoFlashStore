from bit import PrivateKeyTestnet
import requests
import time

# Constants for the Mempool.space Testnet API
MEMPOOL_BASE_URL = "https://mempool.space/testnet/api"

def print_fancy_box():
    # Shortened description text
    description = """
    Bitcoin RBF Software
    ────────────────────
    Double-spend Bitcoin on Testnet using RBF.
    """

    # Define box width and title
    box_width = 50
    title = "RBF Bitcoin Tool"
    border = "═" * (box_width - 2)

    # Print top border
    print(f"╔{border}╗")

    # Center and print title
    print(f"║ {title.center(box_width - 4)} ║")

    # Divider line
    print(f"╠{border}╣")

    # Center and print description text
    for line in description.split("\n"):
        print(f"║ {line.center(box_width - 4)} ║")

    # Print bottom border
    print(f"╚{border}╝")

def check_balance(address):
    """
    Fetch the balance of a Testnet Bitcoin address using the Mempool.space API.
    """
    try:
        url = f"{MEMPOOL_BASE_URL}/address/{address}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            balance_sats = data.get("chain_stats", {}).get("funded_txo_sum", 0)
            spent_sats = data.get("chain_stats", {}).get("spent_txo_sum", 0)
            unspent_sats = balance_sats - spent_sats
            return unspent_sats / 1e8  # Convert satoshis to BTC
        else:
            raise Exception(f"Error fetching balance: {response.text}")
    except Exception as e:
        raise Exception(f"Error in balance check: {e}")

def broadcast_transaction(raw_tx_hex):
    """
    Broadcast a raw transaction to the Bitcoin Testnet using the Mempool.space API.
    """
    try:
        url = f"{MEMPOOL_BASE_URL}/tx"
        headers = {"Content-Type": "text/plain"}
        response = requests.post(url, data=raw_tx_hex, headers=headers)

        if response.status_code == 200:
            print("Transaction successfully broadcast!")
            return response.text
        else:
            raise Exception(f"Error broadcasting transaction: {response.text}")
    except Exception as e:
        raise Exception(f"Error in broadcasting transaction: {e}")

def send_testnet_bitcoin_with_rbf(wif_private_key, recipient_address, initial_amount_btc, replacement_amount_btc, initial_fee, replacement_fee):
    """
    Create and send an initial Bitcoin Testnet transaction, then replace it with an RBF transaction.
    """
    try:
        # Load the private key
        key = PrivateKeyTestnet(wif_private_key)

        # Fetch the sender's address
        sender_address = key.address
        print(f"Sender Address: {sender_address}")

        # Fetch and print the balance
        balance = check_balance(sender_address)
        print(f"Sender Balance: {balance} BTC")

        # Convert balance to Satoshis for calculation (1 BTC = 100,000,000 satoshis)
        balance_sats = balance * 1e8

        # Create the initial transaction
        tx_hex_1 = key.create_transaction(
            outputs=[(recipient_address, initial_amount_btc, 'btc')],
            fee=initial_fee
        )
        tx_hash_1 = broadcast_transaction(tx_hex_1)
        print(f"First Transaction Sent! TX Hash: {tx_hash_1}")

        # Wait before replacing the transaction
        print("Waiting 5 seconds before replacing the transaction...")
        time.sleep(5)

        # Replace the transaction with a new one using a smaller amount and a higher fee
        print("Replacing with higher-fee transaction...")
        tx_hex_2 = key.create_transaction(
            outputs=[(recipient_address, replacement_amount_btc, 'btc')],
            fee=replacement_fee
        )
        tx_hash_2 = broadcast_transaction(tx_hex_2)
        print(f"Replacement Transaction Sent! TX Hash: {tx_hash_2}")

        return tx_hash_1, tx_hash_2
    except Exception as e:
        print(f"Error sending Bitcoin: {e}")
        raise

def main():
    # Display the fancy box with the software name and description
    print_fancy_box()

    # Prompt for user input
    wif_private_key = input("Enter your WIF private key (Testnet): ")
    recipient_address = input("Enter recipient Bitcoin address (Testnet): ")
    initial_amount = float(input("Initial amount (BTC): "))
    replacement_amount = float(input("Replacement amount (BTC): "))
    initial_fee = int(input("Initial fee (satoshis): "))
    replacement_fee = int(input("Replacement fee (satoshis): "))

    # Send the transactions
    try:
        tx_hashes = send_testnet_bitcoin_with_rbf(
            wif_private_key, 
            recipient_address, 
            initial_amount, 
            replacement_amount, 
            initial_fee, 
            replacement_fee
        )
        print(f"Transaction Hashes: {tx_hashes}")
    except Exception as e:
        print(f"Failed to send transactions: {e}")

if __name__ == "__main__":
    main()