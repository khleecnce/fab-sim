#!/bin/bash
# 폰에서 FabSim 열기 — 더블클릭하면 QR이 뜬다. 폰 카메라로 찍어 접속.
#
#   같은 Wi-Fi     : 이 스크립트 그대로 (가장 빠르고 데이터가 밖으로 안 나감)
#   밖에서(LTE 등) : 터미널에서  tools/mobile.py --tunnel
#
# 종료: tools/mobile.py --stop
cd "$(dirname "$0")" || exit 1
.venv/bin/python tools/mobile.py "$@"
echo ""
read -r -p "창을 닫으려면 Enter (서버는 계속 돕니다) " _
