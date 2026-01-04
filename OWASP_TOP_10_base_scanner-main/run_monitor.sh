#!/bin/bash

echo "=== Ruqos Security Monitor 시작 ==="

# DISPLAY 환경변수 설정
if [ -z "$DISPLAY" ]; then
    echo "DISPLAY 환경변수가 설정되지 않았습니다."
    echo "자동으로 :0으로 설정합니다..."
    export DISPLAY=:0
fi

echo "현재 DISPLAY: $DISPLAY"

# X11이 실행 중인지 확인
if ! pgrep -x "Xorg" > /dev/null && ! pgrep -x "X" > /dev/null; then
    echo "경고: X11 서버가 실행되지 않는 것 같습니다."
    echo "데스크톱 환경에서 실행하세요."
fi

# GUI 실행
echo "Security Monitor GUI를 시작합니다..."
cd "$(dirname "$0")"
python3 gui/monitor.py

echo "=== 프로그램 종료 ==="