#!/bin/bash
# Ensure unbuffered output
export PYTHONUNBUFFERED=1

# Start Gunicorn with 1 worker and longer timeout
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 600

