#!/bin/bash
# Verification script for CODEX fixes
# Run this after deploying to production

echo "🔍 CODEX Fix Verification Checklist"
echo "===================================="
echo ""

# Check 1: Micro-cap sweep logs
echo "✓ Check 1: Micro-cap sweep re-enabled"
echo "  Looking for sweep logs..."
if grep -q "Micro cap sweep" momentum_scanner.log 2>/dev/null; then
    echo "  ✅ Sweep logs found"
    grep "Micro cap sweep:" momentum_scanner.log | tail -3
else
    echo "  ⏳ No sweep logs yet (may need 1 cycle with <25 filtered tokens)"
fi
echo ""

# Check 2: Guard stats tracking
echo "✓ Check 2: Guard stats tracking"
echo "  Looking for guard rejection stats..."
if grep -q "guards ->" momentum_scanner.log 2>/dev/null; then
    echo "  ✅ Guard stats found"
    grep "guards ->" momentum_scanner.log | tail -3
else
    echo "  ⏳ No guard stats yet (wait for first scan cycle)"
fi
echo ""

# Check 3: Relaxed gating triggers
echo "✓ Check 3: Relaxed Birdeye gating"
echo "  Looking for relaxed gating triggers..."
RELAXED_COUNT=$(grep -c "Allowing signal with stale Helius but strong Birdeye" momentum_scanner.log 2>/dev/null || echo "0")
echo "  Relaxed signals: $RELAXED_COUNT"
if [ "$RELAXED_COUNT" -gt 0 ]; then
    echo "  ✅ Relaxed gating active"
    grep "Allowing signal with stale Helius" momentum_scanner.log | tail -2
else
    echo "  ℹ️  No relaxed signals yet (requires high momentum + stale Helius)"
fi
echo ""

# Check 4: API metrics endpoint
echo "✓ Check 4: API metrics exposure"
echo "  Testing /status endpoint..."
STATUS=$(curl -s http://localhost:8000/status 2>/dev/null || echo '{"error":"API not running"}')
if echo "$STATUS" | grep -q "scanner_metrics"; then
    echo "  ✅ /status includes scanner_metrics"
    echo "$STATUS" | python3 -m json.tool 2>/dev/null | grep -A 8 "scanner_metrics"
else
    echo "  ⏳ API server not running or metrics not available"
fi
echo ""

echo "  Testing /scanner/metrics endpoint..."
METRICS=$(curl -s http://localhost:8000/scanner/metrics 2>/dev/null || echo '{"error":"API not running"}')
if echo "$METRICS" | grep -q "cycles"; then
    echo "  ✅ /scanner/metrics endpoint working"
    echo "$METRICS" | python3 -m json.tool 2>/dev/null
else
    echo "  ⏳ API server not running or endpoint not available"
fi
echo ""

# Check 5: Candidate count per cycle
echo "✓ Check 5: Candidate count per cycle"
echo "  Checking recent scan cycles..."
if grep -q "Scan complete:" momentum_scanner.log 2>/dev/null; then
    echo "  Recent cycles:"
    grep "Scan complete:" momentum_scanner.log | tail -3 | while read -r line; do
        PROCESSED=$(echo "$line" | grep -oP '\d+(?= processed)' || echo "?")
        echo "    Processed: $PROCESSED tokens"
    done
    echo "  ✅ Target: ≥40 tokens per cycle"
else
    echo "  ⏳ No scan cycles completed yet"
fi
echo ""

echo "===================================="
echo "📊 Summary:"
echo "  - Re-run this script after 1-2 scan cycles"
echo "  - Expected: 40-60 candidates/cycle, guard stats visible"
echo "  - Monitor for 24h to assess relaxed gating impact"
echo ""
