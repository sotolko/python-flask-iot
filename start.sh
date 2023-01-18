#!/bin/bash
trap 'kill $(jobs -p)' EXIT
echo $$
python main.py &
python backend.py &
wait