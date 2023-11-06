#!/bin/bash

DISTRIBUTION="gamma"
PARAMETERS="9 0.5"

# 90th percentile:
# https://www.wolframalpha.com/input?i=gamma+%289%2C+0.5%29+distribution
WATERMARK_DELAY="5.40"
WATERMARK_SPEED="100"

INPUT_RATE="10000"
DURATION="100"

python3 main.py \
    --distribution $DISTRIBUTION \
    --parameters $PARAMETERS \
    --watermark_delay $WATERMARK_DELAY \
    --watermark_speed $WATERMARK_SPEED \
    --input_rate $INPUT_RATE \
    --duration $DURATION
