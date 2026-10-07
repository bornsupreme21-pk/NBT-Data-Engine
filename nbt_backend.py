import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. Define Stock Universe
universe = {
    'HAL.NS': 'Defence', 
    'BEL.NS': 'Defence',
    'TATAPOWER.NS': 'Energy/EV',
    'KPITTECH.NS': 'Auto Tech',
    'HDFCBANK.NS': 'Banking'
}

macro_scores = {'Defence': 9, 'Energy/EV': 8, 'Auto Tech': 7, 'Banking': 5}
data_frames = []

print("Running NBT Engine...")

for ticker, sector in universe.items():
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5y")
        if hist.empty: continue
            
        life_high = hist['High'].max()
        life_high_date = hist['High'].idxmax().strftime('%Y-%m-%d')
        life_low = hist['Low'].min()
        
        prev_close = hist['Close'].iloc[-1]
        ema_20 = hist['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
        ema_200 = hist['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
        
        if prev_close > ema_200: 
            entry_trigger = round(prev_close * 1.01, 2)
            stop_loss = round(ema_20, 2) 
            risk = entry_trigger - stop_loss
            target = round(entry_trigger + (risk * 2.5), 2) 
            action = "SWING BUY"
        else:
            entry_trigger = "Wait for 200DMA"
            stop_loss = "N/A"
            target = "N/A"
            action = "AVOID"

        data_frames.append([
            ticker.replace('.NS', ''), sector, round(prev_close, 2), 
            round(life_high, 2), life_high_date, round(life_low, 2), 
            macro_scores.get(sector, 5), entry_trigger, target, stop_loss, action
        ])
    except Exception as e:
        print(f"Error on {ticker}: {e}")

# 2. Generate the CSV File
df = pd.DataFrame(data_frames, columns=[
    'Stock', 'Sector', 'Prev_Close', 'Life_High', 'Life_High_Date', 
    'Life_Low', 'Geo_Score', 'Entry_Trigger', 'Target_Price', 'Stop_Loss', 'System_Action'
])
df.to_csv('nbt_backend_data.csv', index=False)
print("CSV successfully generated.")
