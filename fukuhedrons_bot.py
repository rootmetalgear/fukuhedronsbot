import requests
import time
from datetime import datetime

# Magic Eden API endpoint
ME_API_URL = "https://api-mainnet.magiceden.dev/v2/ordinals/activities"
COLLECTION_NAME = "fukuhedrons"

def get_fukuhedrons_sales():
    headers = {
        "accept": "application/json"
    }
    
    params = {
        "type": "buyNow",
        "limit": 20,
        "collectionName": COLLECTION_NAME
    }
    
    try:
        response = requests.get(ME_API_URL, headers=headers, params=params)
        return response.json()
    except Exception as e:
        print(f"Error fetching sales: {e}")
        return None

def format_sale_info(sale):
    price_btc = sale.get('price', 0) / 100000000
    inscription_id = sale.get('inscriptionId', 'Unknown')
    seller = sale.get('seller', 'Unknown')
    buyer = sale.get('buyer', 'Unknown')
    
    return (f"🚨 New Fukuhedron Sale! 🚨\n"
            f"💰 Price: {price_btc} BTC\n"
            f"🔢 Inscription: {inscription_id}\n"
            f"🤝 Seller: {seller}\n"
            f"👤 Buyer: {buyer}\n"
            f"🔍 View: https://ordinals.com/inscription/{inscription_id}")

def main():
    processed_sales = set()
    print(f"Bot started! Monitoring Fukuhedrons sales...")
    
    while True:
        try:
            sales = get_fukuhedrons_sales()
            
            if sales:
                for sale in sales:
                    sale_id = sale.get('signature')
                    
                    if sale_id and sale_id not in processed_sales:
                        sale_info = format_sale_info(sale)
                        print("\n" + sale_info + "\n")
                        processed_sales.add(sale_id)
            
            if len(processed_sales) > 1000:
                processed_sales.clear()
                
            time.sleep(30)
            
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()