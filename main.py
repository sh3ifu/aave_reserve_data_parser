import os
import json
import requests
from eth_abi import decode
from dotenv import load_dotenv
from eth_utils import keccak, encode_hex, to_hex, to_bytes

load_dotenv()

INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')
url = f"https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}"

def print_reserve_data(reserve_data):
    print('\nReserveConfigurationMap:\t', reserve_data[0])
    print('liquidityIndex:\t\t\t', reserve_data[1])
    print('variableBorrowIndex:\t\t', reserve_data[2])
    print('currentLiquidityRate:\t\t', reserve_data[3])
    print('currentVariableBorrowRate:\t', reserve_data[4])
    print('currentStableBorrowRate:\t', reserve_data[5])
    print('lastUpdateTimestamp:\t\t', reserve_data[6])
    print('aTokenAddress:\t\t\t', reserve_data[7])
    print('stableDebtTokenAddress:\t\t', reserve_data[8])
    print('variableDebtTokenAddress:\t', reserve_data[9])
    print('interestRateStrategyAddress:\t', reserve_data[10])
    print('id:\t\t\t\t', reserve_data[11])

def get_data(asset_address, block_number):
    # Generate data for eth_call    
    function_selector = encode_hex(keccak(b"getReserveData(address)")[:4])
    data = function_selector + "000000000000000000000000" + asset_address[2:]

    block_number = to_hex(block_number)

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [
            {
                "to": "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",     # aave v2 lendingPool address
                "data": data
            },
            block_number
        ],
        "id": 1
    }

    return requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))

def parse_data(response):
    if response.status_code == 200:
        result = response.json().get("result")    

        # Fields types in ReserveData struct
        types = [
            "uint256", "uint128", "uint128", "uint128", "uint128", "uint128", "uint40",
            "address", "address", "address", "address", "uint8"
        ]

        decoded_data = decode(types, to_bytes(hexstr=result))
        return decoded_data
    else:
        print("Error:", response.status_code, response.text)

def parse_reserve_configuration_map(config_map):
    # Extract fields using bitwise operations
    ltv = config_map & ((1 << 16) - 1)
    liquidation_threshold = (config_map >> 16) & ((1 << 16) - 1)
    liquidation_bonus = (config_map >> 32) & ((1 << 16) - 1)
    decimals = (config_map >> 48) & ((1 << 8) - 1)
    is_active = (config_map >> 56) & 1
    is_frozen = (config_map >> 57) & 1
    borrowing_enabled = (config_map >> 58) & 1
    stable_borrowing_enabled = (config_map >> 59) & 1
    reserve_factor = (config_map >> 64) & ((1 << 16) - 1)

    print('\nltv:\t\t\t\t', ltv)
    print('liquidation_threshold:\t\t', liquidation_threshold)
    print('liquidation_bonus:\t\t', liquidation_bonus)
    print('decimals:\t\t\t', decimals)
    print('is_active:\t\t\t', bool(is_active))
    print('is_frozen:\t\t\t', bool(is_frozen))
    print('borrowing_enabled:\t\t', bool(borrowing_enabled))
    print('stable_borrowing_enabled:\t', bool(stable_borrowing_enabled))
    print('reserve_factor:\t\t\t', reserve_factor)


def main():
    asset_address = input('Asset address: ')
    block_number = int(input('Block number: '))

    response = get_data(asset_address, block_number)
    decoded_data = parse_data(response)
    print_reserve_data(decoded_data)

    parse_reserve_configuration_map(decoded_data[0])


if __name__ == '__main__':
    main()
