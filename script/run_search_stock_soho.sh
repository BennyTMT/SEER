#!/bin/bash

# ==========================================
# Target File: seer/forecast/price_predict.py
# ==========================================
# 高流动性

# 2025年 10月  
# For training
# 2026年 2 月  
# For Evaling 
# 2026年 5 月

DOMAIN='stock'
START_DATE="2025-10-01"
END_DATE="2026-02-01"
TICKERS=(
    'META' 'AAPL' 'NVDA' 'MSFT' 'GOOGL' 
    'AMZN' 'TSLA'
    'AMD' 'INTC' 'TSM' 'AVGO' 'QCOM' 
    'NFLX' 'DIS' 'ADBE' 'CRM' 'ORCL'
    'JPM' 'BAC' 'V' 'MA' 
    'WMT' 'COST' 'KO' 'PEP' 'PG'
    'JNJ' 'PFE' 'LLY' 'UNH'
)

MODELS=(   'gemini' 'gemini-flash-3p1' )
# MODELS=( 'claude-opus-4p6'   'claude-sonnet-4p6' )   
WINDOW_PAIRS=(   "14 1"  "14 2"  ) 
WORKERS=18
# WORKERS=1
    
ALPHAS=( 'base'  'abl'   )
for MODEL in "${MODELS[@]}"; do
 for RE in 'v0' 'v1' 'v2' ;do
  for WAY in "3way" "5way" ; do
    for PAIR in "${WINDOW_PAIRS[@]}"; do
        
        # 将 "14 3" 解析为 BACKWINDOW=14 和 HORIZON=3
        read -r BACKWINDOW HORIZON <<< "$PAIR"
        
        echo ""
        echo "========================================================"
        echo "🚀 STARTING BATCH | MODEL: $MODEL | BACKWINDOW: $BACKWINDOW | HORIZON: $HORIZON"
        echo "========================================================"
        
        # 最内层循环：遍历 Alphas
        for ALPHA in "${ALPHAS[@]}"; do

            # 内循环 1：遍历 Tickers
            for CURRENT_TICKER in "${TICKERS[@]}"; do
                
                echo "--------------------------------------------------------"
                echo "📈 Running: $CURRENT_TICKER | Alpha: $ALPHA ($START_DATE to $END_DATE)"
                echo "--------------------------------------------------------"
                
                python -m seer.forecast.forecast_soho_search \
                    -t "$CURRENT_TICKER" \
                    -s "$START_DATE" \
                    -e "$END_DATE" \
                    -w "$WORKERS" \
                    -a "$ALPHA" \
                    -b "$BACKWINDOW" \
                    -p "$HORIZON" \
                    -m "$MODEL" \
                    -y "$WAY" \
                    -r "$RE"\
                    -d "$DOMAIN" \
                    -r "$RE" \
                    "$@"
                    
                # 检查运行状态
                if [ $? -eq 0 ]; then
                    echo "✅ [$CURRENT_TICKER | $MODEL | w=${BACKWINDOW},h=${HORIZON} | a=${ALPHA}] Done."
                else
                    echo "❌ [$CURRENT_TICKER | $MODEL | w=${BACKWINDOW},h=${HORIZON} | a=${ALPHA}] Failed."
                fi
                
            done
            
        done 
        
    done 
  done 
 done 
done

echo ""
echo "🎉 All grid search predictions completed!"

