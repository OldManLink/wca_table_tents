#!/bin/bash

ROUND="$1"

CSV=$(python3 fetch_wca_live_seeds.py "$ROUND") || exit $?

echo "Creating table tents from $CSV"
python3 make_table_tents.py "$CSV"

