#!/bin/bash

# ==========================================
# Target File: seer/forecast/price_predict.py
# ==========================================


DOMAIN='stock'
START_DATE="2025-01-06"
END_DATE="2026-04-05"

tickers=(
    "COHR" "CVNA" "ASTS" "HOOD" "RKLB" "APP" "CPNG" "DKNG"
    "DUOL" "RBLX" "S" "SOFI" "U" "CELH" "CRSP" "DDOG"
    "ELF" "MRVL" "PLTR" "SE" "SYM" "TOST" "VRT" "AFRM"
    "ALAB" "CAVA" "COIN" "RDDT" "SNOW" "CEG" "MSTR" "NET"
    "ONON" "ZS" "JOBY" "PATH" "VKTX" "MDB" "RIVN" "SMCI"
)

MODELS=( 'claude-opus-4p6'   'claude-sonnet-4p6'   )   
MODELS=( 'gemini'   'gemini-flash-3p1' )

# MODELS=( 'gemini')
# MODELS=( 'gemini-flash-3p1' )
# MODELS=( 'claude-opus-4p6' )
# MODELS=( 'claude-sonnet-4p6'  )

WINDOW_PAIRS=( "3 3" "3 6" ) 
WORKERS=15
# WORKERS=1
ALPHAS=( 'base3c' 'abl'  )
for RE in 'v0' 'v1' 'v2' ;do
 for MODEL in "${MODELS[@]}"; do
  for WAY in  "3way"  "5way" ; do
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
                
                python -m seer.forecast.forecast_loho_search \
                    -t "$CURRENT_TICKER" \
                    -s "$START_DATE" \
                    -e "$END_DATE" \
                    -w "$WORKERS" \
                    -a "$ALPHA" \
                    -b "$BACKWINDOW" \
                    -p "$HORIZON" \
                    -m "$MODEL" \
                    -y "$WAY" \
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