cat > run.sh << 'EOF'
#!/bin/bash

python3 /app/person_detector.py \
  --camera "${CAMERA_ENTITY}" \
  --confidence "${CONFIDENCE_THRESHOLD}" \
  --interval "${SCAN_INTERVAL}" \
  --ei-api-key "${EDGE_IMPULSE_API_KEY}"
EOF

# Make it executable
chmod +x run.sh