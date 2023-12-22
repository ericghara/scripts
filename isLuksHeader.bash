#!/bin/bash

# Define the size constraints in bytes
MIN_SIZE=$((2 * 1024 * 1024))  # 2MB
MAX_SIZE=$((64 * 1024 * 1024)) # 64MB

# Directory to search in
SEARCH_DIR=$1

# Find files within the size range and check for LUKS header
find "$SEARCH_DIR" -type f -size +${MIN_SIZE}c -size -${MAX_SIZE}c -exec sh -c '
  for file do
    if cryptsetup isLuks "$file" > /dev/null 2>&1; then
      echo "Header: $file"
    fi
  done
' sh {} +
