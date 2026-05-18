#!/bin/bash

rm seer/logs/*

DOMAIN='stock'
START_DATE="2025-10-01"
END_DATE="2026-02-01"

# START_DATE="2026-02-01"
# END_DATE="2026-05-01"

TICKERS=(
    'META' 'AAPL' 'NVDA' 'MSFT' 'GOOGL'  'AMZN' 'TSLA'
    'AMD' 'INTC' 'TSM' 'AVGO' 'QCOM' 
    'NFLX' 'DIS' 'ADBE' 'CRM' 'ORCL'
    'JPM' 'BAC' 'V' 'MA' 
    'WMT' 'COST' 'KO' 'PEP' 'PG'
    'JNJ' 'PFE' 'LLY'  'UNH' 
)

MODELS=(   'gemini' 'gemini-flash-3p1' 'claude-opus-4p6'   'claude-sonnet-4p6')

# w/  Evnts 41.46
# w/o Evnts 34.22

MODELS=('gemini-flash-3p1') 
WINDOW_PAIRS=( "14 1" ) 
# WORKERS=18
WORKERS=1

ALPHAS=( 'seer-r1' )
for MODEL in "${MODELS[@]}"; do
#  for RE in 'v0' 'v1' 'v2' ;do
 for RE in 'v0' ; do
#   for WAY in "3way" "5way" ; do
  for WAY in "3way"; do
    for PAIR in "${WINDOW_PAIRS[@]}"; do
        
        read -r BACKWINDOW HORIZON <<< "$PAIR"
        
        echo ""
        echo "========================================================"
        echo "🚀 STARTING BATCH | MODEL: $MODEL | BACKWINDOW: $BACKWINDOW | HORIZON: $HORIZON"
        echo "========================================================"
        
        for ALPHA in "${ALPHAS[@]}"; do
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
                    "$@"
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

