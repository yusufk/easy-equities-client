#!/usr/bin/env python3
"""Fetch MAX historical data for all portfolio holdings."""
import os, json, csv
from datetime import datetime
from dotenv import load_dotenv
from easy_equities_client.clients import EasyEquitiesClient
from easy_equities_client.instruments.types import Period

HOLDINGS = [
    {"symbol": "SHP", "contract_code": "EQU.ZA.SHP", "name": "Shoprite Holdings Limited"},
    {"symbol": "WBC", "contract_code": "EQU.ZA.WBC", "name": "WeBuyCars Holdings Ltd"},
    {"symbol": "CLS", "contract_code": "EQU.ZA.CLS", "name": "Clicks Group Limited"},
    {"symbol": "AAPL", "contract_code": "EQU.US.AAPL", "name": "Apple Inc"},
    {"symbol": "AMD", "contract_code": "EQU.US.AMD", "name": "Advanced Micro Devices Inc"},
    {"symbol": "MDLZ", "contract_code": "EQU.US.MDLZ", "name": "Mondelez International Inc-A"},
    {"symbol": "HD", "contract_code": "EQU.US.HD", "name": "Home Depot Inc"},
    {"symbol": "GE", "contract_code": "EQU.US.GE", "name": "GE Aerospace"},
    {"symbol": "TM", "contract_code": "EQU.US.TM", "name": "Toyota Motor Corp"},
    {"symbol": "MAR", "contract_code": "EQU.US.MAR", "name": "Marriott International -Cl A"},
    {"symbol": "RACE", "contract_code": "EQU.US.RACE", "name": "Ferrari NV"},
    {"symbol": "HMC", "contract_code": "EQU.US.HMC", "name": "Honda Motor Co Ltd"},
    {"symbol": "COST", "contract_code": "EQU.US.COST", "name": "Costco Wholesale Corp"},
]

def main():
    load_dotenv()
    client = EasyEquitiesClient()
    client.login(os.getenv("EASYEQUITIES_USERNAME"), os.getenv("EASYEQUITIES_PASSWORD"))
    
    output_dir = "/Users/yusuf/Documents/Obsidian/Yusufs Vault/AI brain/data"
    os.makedirs(output_dir, exist_ok=True)
    
    for holding in HOLDINGS:
        try:
            data = client.instruments.historical_prices(holding["contract_code"], Period.MAX)
            if not data or not data.get('success') or 'chartData' not in data:
                continue
                
            chart_data = data['chartData']
            dataset = chart_data.get('Dataset', [])
            if not dataset:
                continue
            
            # Save JSON summary
            summary = {
                "symbol": holding["symbol"],
                "contract_code": holding["contract_code"],
                "name": holding["name"],
                "period": "MAX",
                "current_price": dataset[-1],
                "period_return": chart_data.get('PeriodReturn', 0),
                "daily_change": chart_data.get('DailyChange', 0),
                "data_points": len(dataset),
                "retrieved_at": datetime.now().isoformat()
            }
            
            with open(f"{output_dir}/{holding['symbol']}_MAX.json", 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Save CSV data
            with open(f"{output_dir}/{holding['symbol']}_MAX.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Point', 'Price'])
                for i, price in enumerate(dataset):
                    writer.writerow([i, price])
            
            print(f"✅ {holding['symbol']}: {len(dataset)} points, {chart_data.get('PeriodReturn', 0):.1f}% return")
        except Exception as e:
            print(f"❌ {holding['symbol']}: {e}")

if __name__ == "__main__":
    main()
