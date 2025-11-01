#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify
import requests
import warnings
from datetime import datetime
import os

warnings.filterwarnings("ignore")

app = Flask(__name__)

# Get proxy settings from environment variables
PROXY_IP = os.environ.get('PROXY_IP', '')
PROXY_PORT = os.environ.get('PROXY_PORT', '50100')
PROXY_USER = os.environ.get('PROXY_USER', '')
PROXY_PASS = os.environ.get('PROXY_PASS', '')

# Build proxy configuration with embedded credentials
PROXIES = None

if PROXY_IP and PROXY_USER and PROXY_PASS:
    # Embed credentials directly in proxy URL (more reliable for HTTP proxies)
    proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}"
    PROXIES = {
        'http': proxy_url,
        'https': proxy_url
    }
    print(f"✅ Proxy configured: {PROXY_IP}:{PROXY_PORT} with user: {PROXY_USER}")
else:
    print("⚠️ No proxy configured - using direct connection")

# Pokemon Card SKUs
POKEMON_SKUS = {
    'black': '6612728',
    'grey': '6612730',
    'blue': '6612731',
    'white': '6612732'
}

def check_stock_for_sku(sku, zip_code):
    """Check stock availability for a single SKU with retry logic"""
    data = {
        "zipCode": zip_code,
        "showOnShelf": True,
        "lookupInStoreQuantity": False,
        "xboxAllAccess": False,
        "consolidated": False,
        "showOnlyOnShelf": False,
        "showInStore": False,
        "pickupTypes": ["UPS_ACCESS_POINT", "FEDEX_HAL"],
        "onlyBestBuyLocations": True,
        "items": [{
            "sku": sku,
            "condition": None,
            "quantity": 1,
            "itemSeqNumber": "1",
            "reservationToken": None,
            "selectedServices": [],
            "requiredAccessories": [],
            "isTradeIn": False,
            "isLeased": False
        }]
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Origin': 'https://www.bestbuy.com'
    }
    
    try:
        url = 'https://www.bestbuy.com/productfulfillment/c/api/2.0/storeAvailability'
        
        # Make request with or without proxy
        if PROXIES:
            response = requests.post(
                url, 
                json=data, 
                headers=headers, 
                proxies=PROXIES,
                timeout=60,
                verify=False
            )
        else:
            response = requests.post(
                url, 
                json=data, 
                headers=headers, 
                timeout=30
            )
        
        response.raise_for_status()
        
        response_data = response.json()
        
        if not response_data or 'ispu' not in response_data:
            return {'pickup_stores': [], 'ship_stores': []}
        
        # Build location lookup
        locations = {loc['id']: loc for loc in response_data['ispu']['locations']}
        
        pickup_stores = []
        ship_to_location_stores = []
        
        for item in response_data['ispu']['items']:
            for location_data in item['locations']:
                location_id = location_data['locationId']
                store_info = locations.get(location_id)
                
                if not store_info:
                    continue
                
                availability = location_data.get('availability', {})
                fulfillment_type = availability.get('fulfillmentType')
                
                if fulfillment_type == "PICKUP":
                    qty = availability.get('availablePickupQuantity', 0)
                    if qty > 0:
                        pickup_stores.append({
                            'name': store_info['name'],
                            'city': store_info['city'],
                            'state': store_info['state'],
                            'address': store_info.get('address', 'N/A'),
                            'distance': store_info.get('distance', 'N/A'),
                            'quantity': qty,
                            'fulfillment': 'pickup',
                            'available_date': availability.get('minDate', 'Today')
                        })
                
                elif fulfillment_type == "SHIP_TO_LOCATION":
                    ship_to_location_stores.append({
                        'name': store_info['name'],
                        'city': store_info['city'],
                        'state': store_info['state'],
                        'address': store_info.get('address', 'N/A'),
                        'distance': store_info.get('distance', 'N/A'),
                        'fulfillment': 'ship_to_store',
                        'service_level': availability.get('serviceLevel', 'Unknown'),
                        'min_date': availability.get('minDate'),
                        'max_date': availability.get('maxDate')
                    })
        
        return {
            'pickup_stores': pickup_stores,
            'ship_stores': ship_to_location_stores
        }
        
    except Exception as e:
        print(f"Error checking SKU {sku}: {e}")
        return {'pickup_stores': [], 'ship_stores': [], 'error': str(e)}

@app.route('/')
def index():
    """Homepage with search form"""
    return render_template('index.html', skus=POKEMON_SKUS)

@app.route('/check_stock', methods=['POST'])
def check_stock():
    """API endpoint to check stock"""
    try:
        zip_code = request.form.get('zip_code', '').strip()
        selected_colors = request.form.getlist('colors')
        
        if not zip_code:
            return jsonify({'error': 'Please enter a zip code'}), 400
        
        if not selected_colors:
            return jsonify({'error': 'Please select at least one color'}), 400
        
        results = {}
        
        # If "all" is selected, check all SKUs
        if 'all' in selected_colors:
            selected_colors = list(POKEMON_SKUS.keys())
        
        for color in selected_colors:
            if color in POKEMON_SKUS:
                sku = POKEMON_SKUS[color]
                results[color] = check_stock_for_sku(sku, zip_code)
                results[color]['sku'] = sku
        
        return jsonify({
            'success': True,
            'zip_code': zip_code,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

