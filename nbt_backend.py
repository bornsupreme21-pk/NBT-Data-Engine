import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 1. Define your Universe & Sector/Macro Geo-political Rules
# Positive scores = Government tailwinds, defense indigenization, infrastructure push.
# Negative scores = Regulatory headwinds, global supply chain issues.
universe = {
    'HAL.NS': 'Defence', 
    'BEL.NS': 'Defence',
    'TATAPOWER.NS': 'Energy/EV',
    'KPITTECH.NS': 'Auto Tech',
    'HDFCBANK.NS': 'Banking',
    'IRFC.NS': 'Railways'
}

macro_scores = {
    'Defence': 9,       # High govt focus, export push
    'Energy/EV': 8,     # Green energy subsidies
    'Auto Tech': 7,
    'Railways': 8,      # Capex expansion
    'Banking': 5,       # Stable, GDP proxy
}

data_frames = []

print("🚀 Starting NBT Engine 2.0 Backend...")

for ticker, sector in universe.items():
    try:
        # Fetch 5 years of historical data
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5y")
        
        if hist.empty:
            continue
            
        # 2. Calculate Lifetime Highs & Lows with Dates
        life_high = hist['High'].max()
        life_high_date = hist['High'].idxmax().strftime('%Y-%m-%d')
        life_low = hist['Low'].min()
        life_low_date = hist['Low'].idxmin().strftime('%Y-%m-%d')
        
        # 52 Week Highs & Lows
        hist_1y = hist.tail(252)
        high_52w = hist_1y['High'].max()
        low_52w = hist_1y['Low'].min()
        
        # 3. Calculate 3-5 Year Momentum & Technicals
        prev_close = hist['Close'].iloc[-1]
        ema_20 = hist['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
        ema_200 = hist['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
        
        # 4. ALGORITHMIC STATIC GOAL POSTS (RESEARCH-BASED)
        # Entry: Requires stock to show strength above 20 EMA, wait for a 1% confirmation breakout above prev close
        if prev_close > ema_200: 
            entry_trigger = round(prev_close * 1.01, 2)
            stop_loss = round(ema_20, 2) # SL is the 20 EMA at EOD. It will NOT shift intraday.
            risk = entry_trigger - stop_loss
            target = round(entry_trigger + (risk * 2.5), 2) # 1:2.5 Risk Reward
            action = "SWING BUY"
        else:
            entry_trigger = "Wait for 200DMA"
            stop_loss = "N/A"
            target = "N/A"
            action = "AVOID"

        # 5. Geopolitics & Fundamental Placeholder Score (Out of 100)
        # In a full system, you merge fundamental API data here. 
        # Here we calculate score based on Trend + Macro
        trend_score = 40 if prev_close > ema_200 else 10
        macro_weight = macro_scores.get(sector, 5) * 5 # Scale to 50
        total_score = trend_score + macro_weight

        data_frames.append({
            'Stock': ticker.replace('.NS', ''),
            'Sector': sector,
            'Prev_Close': round(prev_close, 2),
            'Life_High': round(life_high, 2),
            'Life_High_Date': life_high_date,
            'Life_Low': round(life_low, 2),
            'Life_Low_Date': life_low_date,
            '52W_High': round(high_52w, 2),
            '52W_Low': round(low_52w, 2),
            'Macro_Score': macro_scores.get(sector, 5),
            'NBT_Score': total_score,
            'Entry_Trigger': entry_trigger,
            'Target_Price': target,
            'Stop_Loss': stop_loss,
            'System_Action': action
        })
    except Exception as e:
        print(f"Error processing {ticker}: {e}")

# Compile Master Data
master_df = pd.DataFrame(data_frames)

# Export to CSV (This CSV is what Google Sheets will read)
master_df.to_csv('nbt_backend_data.csv', index=False)
print("✅ NBT Data Fusion Complete. Target Goalposts LOCKED.")
