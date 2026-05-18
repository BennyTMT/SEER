#!/bin/bash

# 清理日志（只需在最开始执行一次）
rm -f seer/logs/*

# 保存从外部传给此脚本的额外参数，防止被函数内的 $@ 覆盖
EXTRA_ARGS=("$@")

DOMAIN='stock'
NAME='stock-baseline'

START_DATE="2026-02-01"
END_DATE="2026-05-01"

MODELS=('gemini-flash-3p1') 
WINDOW_PAIRS=( "14 1" ) 

WORKERS=1

# ALPHAS=( 'seer-r2' )
    
ALPHAS=( r1-12k  r1-5k  r2-12k  r2-5k )
TECH=('META' 'AAPL' 'MSFT' 'GOOGL' 'AMZN' 'TSLA' 'NFLX' 'DIS' 'ADBE' 'CRM' 'ORCL')
SEMI=('NVDA' 'AMD' 'INTC' 'TSM' 'AVGO' 'QCOM')
FIN=('JPM' 'BAC' 'V' 'MA')
CONSUMER=('WMT' 'COST' 'KO' 'PEP' 'PG')
HEALTH=('JNJ' 'PFE' 'LLY' 'UNH')
    
run_domain_thread() {
    local DOMAIN_NAME=$1
    shift
    local TICKERS=("$@") 
    
    echo "========================================================"
    echo "🚀 STARTING THREAD | DOMAIN: $DOMAIN_NAME | TICKERS: ${TICKERS[*]}"
    echo "========================================================"

    for MODEL in "${MODELS[@]}"; do
        for RE in 'eval' ; do
            for WAY in "3way"; do
                for PAIR in "${WINDOW_PAIRS[@]}"; do
                    read -r BACKWINDOW HORIZON <<< "$PAIR"
                    
                    for ALPHA in "${ALPHAS[@]}"; do
                        for CURRENT_TICKER in "${TICKERS[@]}"; do
                            
                            echo "[$DOMAIN_NAME] 📈 Running: $CURRENT_TICKER | Alpha: $ALPHA ($START_DATE to $END_DATE)"
                            
                            python -m seer.forecast.forecast_w_memory \
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
                                -n "$NAME"\
                                -d "$DOMAIN" \
                                "${EXTRA_ARGS[@]}" # 传递外部参数
                                
                            if [ $? -eq 0 ]; then
                                echo "✅ [$DOMAIN_NAME] [$CURRENT_TICKER | $MODEL | w=${BACKWINDOW},h=${HORIZON}] Done."
                            else
                                echo "❌ [$DOMAIN_NAME] [$CURRENT_TICKER | $MODEL | w=${BACKWINDOW},h=${HORIZON}] Failed."
                            fi
                            
                        done
                    done 
                done 
            done 
        done 
    done
    echo "🏁 THREAD FOR [$DOMAIN_NAME] COMPLETED!"
}

# 3. 启动 5 个后台进程 (核心：最后的 & 符号)
run_domain_thread "TECH" "${TECH[@]}" &
run_domain_thread "SEMI" "${SEMI[@]}" &
run_domain_thread "FIN" "${FIN[@]}" &
run_domain_thread "CONSUMER" "${CONSUMER[@]}" &
run_domain_thread "HEALTH" "${HEALTH[@]}" &

# 4. 阻塞等待所有后台进程完成
wait

echo ""
echo "🎉 All 5 parallel domain threads and grid search predictions completed!"