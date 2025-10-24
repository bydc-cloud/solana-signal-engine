# AURA Voice Controller - Deployment Checklist

## Pre-Deployment Verification

### 1. Local Environment Check

- [ ] **Files exist:**
  ```bash
  ls -la voice_controller.py
  ls -la test_voice_controller.py
  ls -la dashboard/aura-jarvis-v3.html
  ```

- [ ] **Dependencies installed:**
  ```bash
  python3 -c "import anthropic; print('✓ Anthropic:', anthropic.__version__)"
  python3 -c "import fastapi; print('✓ FastAPI installed')"
  python3 -c "import aiohttp; print('✓ Aiohttp installed')"
  ```

- [ ] **Database exists:**
  ```bash
  ls -la aura.db
  sqlite3 aura.db "SELECT COUNT(*) FROM live_whale_wallets;"
  sqlite3 aura.db "SELECT COUNT(*) FROM whale_stats;"
  ```

### 2. Configuration Check

- [ ] **API Keys in .env:**
  ```bash
  grep -q "ANTHROPIC_API_KEY=" .env && echo "✓ Anthropic key found" || echo "✗ Missing!"
  grep -q "OPENAI_API_KEY=" .env && echo "✓ OpenAI key found" || echo "✗ Missing!"
  grep -q "ELEVENLABS_API_KEY=" .env && echo "✓ ElevenLabs key found" || echo "✗ Missing!"
  grep -q "HELIUS_API_KEY=" .env && echo "✓ Helius key found" || echo "✗ Missing!"
  ```

- [ ] **Requirements up to date:**
  ```bash
  grep -q "anthropic" requirements.txt && echo "✓ Anthropic in requirements"
  ```

### 3. Functionality Testing

- [ ] **Test voice controller:**
  ```bash
  python3 test_voice_controller.py
  ```
  Expected: All tests pass without errors

- [ ] **Test server locally:**
  ```bash
  # Terminal 1:
  python3 aura_server.py

  # Terminal 2:
  curl -X POST http://localhost:8000/api/aura/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "Show system status"}'
  ```
  Expected: JSON response with system status

- [ ] **Test dashboard:**
  - Open: http://localhost:8000/jarvis
  - Click "System Status" button
  - Verify rich cards display
  - Try voice input if available

### 4. Code Review

- [ ] **No syntax errors:**
  ```bash
  python3 -m py_compile voice_controller.py
  python3 -m py_compile aura_server.py
  ```

- [ ] **No import errors:**
  ```bash
  python3 -c "from voice_controller import voice_controller; print('✓ Import successful')"
  ```

- [ ] **Database queries work:**
  ```bash
  python3 -c "
  from voice_controller import voice_controller
  import asyncio
  async def test():
      result = await voice_controller._get_system_status()
      print('✓ Database query successful:', result)
  asyncio.run(test())
  "
  ```

## Local Deployment

### Step-by-Step:

1. **Set API Keys:**
   ```bash
   # Edit .env file
   nano .env

   # Add:
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

2. **Start Server:**
   ```bash
   python3 aura_server.py
   ```

3. **Verify Endpoints:**
   ```bash
   # Health check
   curl http://localhost:8000/health

   # Chat endpoint
   curl -X POST http://localhost:8000/api/aura/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "Hello"}'
   ```

4. **Test Voice Interface:**
   - Open: http://localhost:8000/jarvis
   - Click "Top Whales" button
   - Verify response shows wallet cards
   - Try other quick commands

5. **Monitor Logs:**
   ```bash
   tail -f momentum_scanner.log
   ```

## Railway Deployment

### Pre-Deployment:

- [ ] **Git status clean:**
  ```bash
  git status
  ```
  Ensure all changes are committed

- [ ] **Files in Git:**
  ```bash
  git ls-files | grep voice_controller.py
  git ls-files | grep "dashboard/aura-jarvis-v3.html"
  ```

- [ ] **No secrets in code:**
  ```bash
  grep -r "sk-ant-" voice_controller.py || echo "✓ No hardcoded keys"
  grep -r "sk-" aura_server.py | grep -v "os.getenv" || echo "✓ No hardcoded keys"
  ```

### Railway Configuration:

1. **Environment Variables:**

   Set in Railway dashboard:
   ```
   ANTHROPIC_API_KEY=sk-ant-api-03-...
   OPENAI_API_KEY=sk-proj-...
   ELEVENLABS_API_KEY=...
   HELIUS_API_KEY=...
   ```

2. **Verify Requirements:**
   ```bash
   cat requirements.txt
   ```
   Should include:
   ```
   anthropic>=0.39.0
   fastapi>=0.116.0
   uvicorn>=0.32.0
   python-multipart>=0.0.6
   aiohttp>=3.8.0
   python-dotenv>=1.0.0
   ```

3. **Build Settings:**
   - Build Command: (default)
   - Start Command: `python3 aura_server.py` or `uvicorn aura_server:app --host 0.0.0.0 --port $PORT`

### Deployment Steps:

1. **Commit Changes:**
   ```bash
   git add voice_controller.py
   git add aura_server.py
   git add dashboard/aura-jarvis-v3.html
   git add test_voice_controller.py
   git add *.md
   git commit -m "Add master voice controller with Claude function calling

   - Implement voice_controller.py with 9 tools
   - Update chat endpoint with tool support
   - Enhance dashboard with quick commands
   - Add rich result formatting
   - Complete documentation"
   ```

2. **Push to GitHub:**
   ```bash
   git push origin main
   ```

3. **Deploy on Railway:**
   - Railway auto-detects changes
   - Build starts automatically
   - Monitor build logs

4. **Verify Deployment:**
   ```bash
   # Replace with your Railway URL
   RAILWAY_URL="https://your-app.up.railway.app"

   # Health check
   curl $RAILWAY_URL/health

   # Chat endpoint
   curl -X POST $RAILWAY_URL/api/aura/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "Show system status"}'

   # Dashboard
   open $RAILWAY_URL/jarvis
   ```

5. **Monitor Logs:**
   - View logs in Railway dashboard
   - Check for errors
   - Verify tool execution

## Post-Deployment Testing

### Test Suite:

1. **System Status:**
   ```bash
   curl -X POST $RAILWAY_URL/api/aura/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the system status?"}'
   ```
   Expected: Status with wallet/signal counts

2. **Whale Wallets:**
   ```bash
   curl -X POST $RAILWAY_URL/api/aura/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "Show me the top 3 whale wallets"}'
   ```
   Expected: List of 3 wallets with stats

3. **Signals:**
   ```bash
   curl -X POST $RAILWAY_URL/api/aura/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What signals came in today?"}'
   ```
   Expected: Recent signals list

4. **Dashboard:**
   - Open: $RAILWAY_URL/jarvis
   - Click each quick command button
   - Verify results display correctly
   - Test voice input (if supported)

### Load Testing:

```bash
# Test 10 concurrent requests
for i in {1..10}; do
  curl -X POST $RAILWAY_URL/api/aura/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "Show system status"}' &
done
wait
```

## Rollback Plan

If deployment fails:

1. **Revert Git Commit:**
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Railway Redeploy:**
   - Railway auto-deploys previous version
   - Or manually trigger redeploy

3. **Restore .env:**
   - Ensure environment variables unchanged

## Monitoring

### Health Checks:

```bash
# Every 5 minutes
watch -n 300 "curl -s $RAILWAY_URL/health | jq"
```

### Log Monitoring:

```bash
# Check for errors
railway logs --tail 100 | grep -i "error"

# Check tool execution
railway logs --tail 100 | grep "Executing tool"
```

### Performance Metrics:

- Response times should be < 5 seconds
- Tool execution should complete successfully
- No Python import errors
- Database connections stable

## Success Criteria

- [ ] ✅ Server starts without errors
- [ ] ✅ /api/aura/chat endpoint responds
- [ ] ✅ Voice controller imports successfully
- [ ] ✅ Tools execute and return data
- [ ] ✅ Dashboard loads and displays results
- [ ] ✅ Quick commands work instantly
- [ ] ✅ Rich formatting displays correctly
- [ ] ✅ No breaking changes to existing features
- [ ] ✅ Voice transcription works (if API key set)
- [ ] ✅ Text-to-speech works (if API key set)

## Troubleshooting

### "ModuleNotFoundError: anthropic"
**Solution:**
```bash
# Add to requirements.txt if missing
echo "anthropic>=0.39.0" >> requirements.txt
git add requirements.txt
git commit -m "Add anthropic to requirements"
git push
```

### "ANTHROPIC_API_KEY not set"
**Solution:**
- Check Railway environment variables
- Verify key format: `sk-ant-api-03-...`
- Restart Railway service

### "Database error"
**Solution:**
- Verify aura.db exists
- Check table schemas
- Run initialization if needed:
  ```bash
  curl -X POST $RAILWAY_URL/api/aura/init
  ```

### "Tool execution failed"
**Solution:**
- Check logs for specific error
- Verify database queries
- Test locally first

### Dashboard not loading
**Solution:**
- Check static file mounting
- Verify HTML file path
- Check browser console for errors

## Maintenance

### Weekly:
- [ ] Check Railway logs for errors
- [ ] Monitor API usage (Anthropic, OpenAI, ElevenLabs)
- [ ] Verify database size < 1GB
- [ ] Test all quick commands

### Monthly:
- [ ] Update dependencies
- [ ] Review and optimize slow queries
- [ ] Check API rate limits
- [ ] Backup database

### As Needed:
- [ ] Add new tools based on user requests
- [ ] Improve system prompts
- [ ] Optimize response times
- [ ] Add more quick commands

## Documentation

All documentation files:
- `VOICE_CONTROLLER_SETUP.md` - Complete setup guide
- `VOICE_CONTROLLER_SUMMARY.md` - Technical implementation details
- `VOICE_COMMANDS_REFERENCE.md` - User command reference
- `DEPLOYMENT_CHECKLIST.md` - This file

## Final Verification

Before marking deployment complete:

```bash
# 1. Server healthy
curl $RAILWAY_URL/health | jq '.status'
# Should return: "healthy"

# 2. Voice controller working
curl -X POST $RAILWAY_URL/api/aura/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Show system status"}' | jq '.success'
# Should return: true

# 3. Tools executing
curl -X POST $RAILWAY_URL/api/aura/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Show top 3 whales"}' | jq '.tool_results | length'
# Should return: 1

# 4. Dashboard accessible
curl -I $RAILWAY_URL/jarvis | grep "200 OK"
# Should return: HTTP/1.1 200 OK
```

---

## Status: READY FOR DEPLOYMENT ✓

All components built and tested locally. Ready to deploy to Railway.

**Next Steps:**
1. Add `ANTHROPIC_API_KEY` to `.env` for local testing
2. Set environment variables in Railway
3. Push code to GitHub
4. Monitor Railway deployment
5. Test on production URL
