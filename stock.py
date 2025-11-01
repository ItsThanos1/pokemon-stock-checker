#!/usr/bin/env python3

import requests
import json
import sys
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

def analyze_fulfillment_options(sku, zip_code):
    """Analyze all fulfillment options available for a SKU"""
    print(f"\n🔍 Analyzing ALL fulfillment options for SKU '{sku}' near '{zip_code}'...")
    
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
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        
        response_data = response.json()
        
        if not response_data or 'ispu' not in response_data:
            print("❌ No fulfillment data available")
            return
        
        # Build location lookup
        locations = {loc['id']: loc for loc in response_data['ispu']['locations']}
        
        pickup_stores = []
        ship_to_location_stores = []
        
        print("\n" + "="*80)
        print("📊 DETAILED FULFILLMENT ANALYSIS")
        print("="*80)
        
        for item in response_data['ispu']['items']:
            for location_data in item['locations']:
                location_id = location_data['locationId']
                store_info = locations.get(location_id)
                
                if not store_info:
                    continue
                
                availability = location_data.get('availability', {})
                fulfillment_type = availability.get('fulfillmentType')
                
                print(f"\n🏪 {store_info['name']} ({store_info['city']}, {store_info['state']})")
                print(f"   📋 Fulfillment Type: {fulfillment_type}")
                
                if fulfillment_type == "PICKUP":
                    # In-store pickup available
                    qty = availability.get('availablePickupQuantity', 0)
                    if qty > 0:
                        pickup_stores.append({
                            'name': store_info['name'],
                            'city': store_info['city'],
                            'state': store_info['state'],
                            'quantity': qty,
                            'fulfillment': 'pickup'
                        })
                        
                        qty_display = "High stock" if qty == 9999 else f"{qty} units"
                        print(f"   ✅ PICKUP AVAILABLE: {qty_display}")
                        print(f"   📅 Available: {availability.get('minDate', 'Today')}")
                
                elif fulfillment_type == "SHIP_TO_LOCATION":
                    # Ship to store option
                    ship_to_location_stores.append({
                        'name': store_info['name'],
                        'city': store_info['city'],
                        'state': store_info['state'],
                        'fulfillment': 'ship_to_store',
                        'service_level': availability.get('serviceLevel', 'Unknown'),
                        'min_date': availability.get('minDate'),
                        'max_date': availability.get('maxDate'),
                        'procure_from': availability.get('procureFromLocationId')
                    })
                    
                    print(f"   📦 SHIP TO STORE AVAILABLE")
                    print(f"   📅 Delivery: {availability.get('minDate')} - {availability.get('maxDate')}")
                    print(f"   🚚 Service Level: {availability.get('serviceLevel')}")
                    print(f"   🏭 Ships from: Location {availability.get('procureFromLocationId')}")
                
                # Show all availability fields for debugging
                print(f"   🔍 All availability data:")
                for key, value in availability.items():
                    print(f"      {key}: {value}")
        
        # Summary
        print("\n" + "="*80)
        print("📋 SUMMARY")
        print("="*80)
        
        print(f"\n🛒 PICKUP OPTIONS ({len(pickup_stores)} stores):")
        if pickup_stores:
            for store in pickup_stores:
                qty_display = "High stock" if store['quantity'] == 9999 else f"{store['quantity']} units"
                print(f"   • {store['name']} - {qty_display}")
        else:
            print("   ❌ No pickup available")
        
        print(f"\n📦 SHIP-TO-STORE OPTIONS ({len(ship_to_location_stores)} stores):")
        if ship_to_location_stores:
            for store in ship_to_location_stores:
                print(f"   • {store['name']} - Ships {store['min_date']} ({store['service_level']})")
        else:
            print("   ❌ No ship-to-store available")
        
        print(f"\n💡 WHAT THIS MEANS:")
        if pickup_stores:
            print("   ✅ You can pick up this item immediately at stores with stock")
        if ship_to_location_stores:
            print("   ✅ You can ORDER this item in-store and have it shipped to that store for pickup")
            print("   ℹ️  This is available even when pickup shows 'out of stock'!")
        
        if not pickup_stores and not ship_to_location_stores:
            print("   ❌ No fulfillment options available")
        
        return pickup_stores, ship_to_location_stores
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return [], []

def main():
    print("\n" + "="*80)
    print("🛒 BEST BUY ADVANCED FULFILLMENT ANALYZER")
    print("="*80)
    print("This analyzes ALL ordering options: pickup, ship-to-store, etc.")
    
    try:
        sku = input("\n📦 Product SKU: ").strip()
        if not sku:
            print("❌ Please enter a valid SKU")
            return
        
        zip_code = input("📍 Zip Code: ").strip()
        if not zip_code:
            print("❌ Please enter a valid zip code")
            return
        
        pickup_stores, ship_stores = analyze_fulfillment_options(sku, zip_code)
        
        print(f"\n🎯 CONCLUSION:")
        print(f"   Pickup available at: {len(pickup_stores)} stores")
        print(f"   Ship-to-store available at: {len(ship_stores)} stores")
        
        if ship_stores and not pickup_stores:
            print(f"\n🔥 INSIDER TIP: Even though this item shows 'out of stock' for pickup,")
            print(f"   you can still ORDER it in-store at {len(ship_stores)} locations and have it shipped there!")
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 