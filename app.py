#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify
import requests
import warnings
from datetime import datetime
import time

warnings.filterwarnings("ignore")

app = Flask(__name__)

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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Origin': 'https://www.bestbuy.com',
        'Referer': 'https://www.bestbuy.com/',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    
    url = 'https://www.bestbuy.com/productfulfillment/c/api/2.0/storeAvailability'
    
    # Retry logic: try up to 3 times with increasing timeouts
    max_retries = 3
    timeouts = [45, 60, 90]  # Increased timeouts
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} for SKU {sku}...")
            response = requests.post(
                url, 
                json=data, 
                headers=headers, 
                timeout=timeouts[attempt],
                verify=False
            )
            response.raise_for_status()
            
            response_data = response.json()
            
            # Success! Process the data
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
            
            # Successfully retrieved data, return it
            return {
                'pickup_stores': pickup_stores,
                'ship_stores': ship_to_location_stores
            }
            
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            # Network issues - retry
            print(f"Timeout/Connection error on attempt {attempt + 1} for SKU {sku}: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            else:
                # Final attempt failed
                return {
                    'pickup_stores': [], 
                    'ship_stores': [], 
                    'error': f'Best Buy API timeout after {max_retries} attempts. Try again in a moment.'
                }
        except Exception as e:
            # Other errors
            print(f"Error checking SKU {sku}: {e}")
            return {'pickup_stores': [], 'ship_stores': [], 'error': str(e)}
    
    # Should never reach here, but just in case
    return {'pickup_stores': [], 'ship_stores': [], 'error': 'Unexpected error'}

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
        
        for i, color in enumerate(selected_colors):
            if color in POKEMON_SKUS:
                sku = POKEMON_SKUS[color]
                
                # Add small delay between requests to avoid rate limiting (except first request)
                if i > 0:
                    time.sleep(1)
                
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

