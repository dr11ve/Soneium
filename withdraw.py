from web3 import Web3
import time
import random
from typing import List

# Конфигурация
RPC_URL = "https://rpc.soneium.org"
RECEIVER_ADDRESS = "0x3885b38c9b592742364c8b161095846928bf4411"  # Адрес получателя

# Подключение к сети
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Чтение приватных ключей из файла
def load_private_keys(filename: str = "private.txt") -> List[str]:
    try:
        with open(filename, 'r') as file:
            private_keys = [line.strip() for line in file if line.strip()]
            return private_keys
    except FileNotFoundError:
        print(f"Файл {filename} не найден!")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла: {str(e)}")
        return []

def send_eth(sender_private_key: str, receiver: str, amount: int, nonce: int) -> str:
    """Отправка ETH на указанный адрес"""
    receiver = Web3.to_checksum_address(receiver)
    
    tx = {
        'nonce': nonce,
        'to': receiver,
        'value': amount,
        'gas': 21000,  # Возвращаем стандартный лимит газа для простой отправки
        'gasPrice': w3.eth.gas_price,
        'chainId': w3.eth.chain_id
    }
    
    signed_tx = w3.eth.account.sign_transaction(tx, sender_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.to_hex(tx_hash)

def main():
    # Загрузка приватных ключей
    PRIVATE_KEYS = load_private_keys("private.txt")
    if not PRIVATE_KEYS:
        print("Нет приватных ключей для отправки!")
        return
    
    print(f"Найдено {len(PRIVATE_KEYS)} кошельков отправителей")
    
    # Проверка подключения
    if not w3.is_connected():
        print("Не удалось подключиться к сети!")
        return
    
    print(f"Подключено к сети. Блок: {w3.eth.block_number}")
    
    # Сумма, которую оставляем на кошельке (0.000003 ETH)
    RESERVE_AMOUNT = w3.to_wei(0.000003, 'ether')
    
    # Отправка ETH с каждого кошелька
    for i, private_key in enumerate(PRIVATE_KEYS):
        try:
            # Получение адреса отправителя из приватного ключа
            sender_address = w3.eth.account.from_key(private_key).address
            
            # Проверка баланса отправителя
            balance = w3.eth.get_balance(sender_address)
            if balance <= RESERVE_AMOUNT:
                print(f"Недостаточный баланс на {sender_address}: {w3.from_wei(balance, 'ether')} ETH")
                continue
                
            # Расчет газа
            gas_cost = 21000 * w3.eth.gas_price
            
            # Максимальная сумма для отправки (весь баланс минус резерв и газ)
            eth_amount = balance - gas_cost - RESERVE_AMOUNT
            if eth_amount <= 0:
                print(f"Недостаточно средств для отправки с {sender_address}")
                continue
            
            # Получение nonce для отправителя
            nonce = w3.eth.get_transaction_count(sender_address)
            
            # Отправка ETH
            tx_hash = send_eth(private_key, RECEIVER_ADDRESS, eth_amount, nonce)
            print(f"ETH ({w3.from_wei(eth_amount, 'ether')}) отправлен с {sender_address} на {RECEIVER_ADDRESS}. Tx: {tx_hash}")
            
            # Пауза между транзакциями 6-10 секунд
            time.sleep(random.uniform(6, 10))
            
        except Exception as e:
            print(f"Ошибка при отправке с кошелька {i + 1}: {str(e)}")
            continue

if __name__ == "__main__":
    main()