#!/bin/bash

DISTRIBUTION="exponential"
PARAMETERS="0.5"

WATERMARK_DELAY="3"
WATERMARK_SPEED=100

INPUT_RATE=10000
DURATION=1000

python3 waterpark.py \
    --distribution $DISTRIBUTION \
    --parameters $PARAMETERS \
    --watermark_delay $WATERMARK_DELAY \
    --watermark_speed $WATERMARK_SPEED \
    --input_rate $INPUT_RATE \
    --duration $DURATION
