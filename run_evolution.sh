#!/bin/bash
echo "Starting grounded evolution (30 generations)..."

for GEN in {1..30}; do
    echo ""
    echo "=== Generation $GEN ==="
    
    python mutate.py
    python evaluate.py
    python reflect.py
    
    git add population/ reflection.md results.log 2>/dev/null || true
    git commit -m "gen $GEN" 2>/dev/null || true
done

echo ""
echo "Done. Check population/ for best prompts and reflection.md for insights."
