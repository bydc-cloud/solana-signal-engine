#!/usr/bin/env python3
"""
Apply Final Features to AURA v0.3.0
Implements:
1. Auto-silence detection for voice
2. Store Telegram signals in database
3. Add Logs and Twitter tabs
4. Complete API endpoints
"""

import re
import sys

def add_database_storage_to_scanner():
    """Add database storage to REALITY_MOMENTUM_SCANNER.py"""

    scanner_file = "REALITY_MOMENTUM_SCANNER.py"

    # Read file
    with open(scanner_file, 'r') as f:
        content = f.read()

    # Find the send_enhanced_signal method and add database storage
    insert_code = '''
                        # Store in AURA database for dashboard
                        try:
                            import sqlite3
                            import json as json_module
                            conn = sqlite3.connect('aura.db')
                            cur = conn.cursor()

                            cur.execute("""
                                INSERT INTO helix_signals
                                (token_address, symbol, momentum_score, market_cap, liquidity, volume_24h, price, timestamp, metadata)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                address,
                                symbol,
                                signal_strength,
                                mcap,
                                token.get('liquidity', 0),
                                volume,
                                price,
                                datetime.now().isoformat(),
                                json_module.dumps({
                                    'risk_score': risk_score,
                                    'buyer_dominance': dominance,
                                    'narrative': narrative,
                                    'discovery': strategy
                                })
                            ))

                            conn.commit()
                            conn.close()
                            logger.info(f"✅ Stored signal in AURA database: {symbol}")
                        except Exception as db_error:
                            logger.error(f"Failed to store signal in database: {db_error}")
'''

    # Insert after the signal_history.append block
    marker = "self.signal_history.append({"
    if marker in content:
        # Find the end of this block (after the closing }])
        marker_pos = content.find(marker)
        block_end = content.find('})', marker_pos) + 2

        # Insert our code after this block
        content = content[:block_end] + insert_code + content[block_end:]

        with open(scanner_file, 'w') as f:
            f.write(content)

        print("✅ Added database storage to REALITY_MOMENTUM_SCANNER.py")
        return True
    else:
        print("❌ Could not find insertion point in scanner file")
        return False


def add_silence_detection_to_dashboard():
    """Add auto-silence detection to voice interface"""

    dashboard_file = "dashboard/aura-complete.html"

    with open(dashboard_file, 'r') as f:
        content = f.read()

    # Add silence detection variables
    var_insert = """        let voiceTimer = null;
        let voiceStartTime = 0;
        let audioContext = null;
        let analyser = null;
        let animationId = null;
        let silenceTimeout = null;
        let lastSoundTime = 0;
        const SILENCE_THRESHOLD = 30;
        const SILENCE_DURATION = 1500;"""

    # Replace existing variable declarations
    content = re.sub(
        r'let voiceTimer = null;.*?let animationId = null;',
        var_insert,
        content,
        flags=re.DOTALL
    )

    # Add silence detection functions before transcribeAudio
    silence_funcs = '''
        function startSilenceDetection() {
            lastSoundTime = Date.now();

            function checkSilence() {
                if (!analyser || !mediaRecorder || mediaRecorder.state !== 'recording') {
                    return;
                }

                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                analyser.getByteFrequencyData(dataArray);
                const average = dataArray.reduce((sum, val) => sum + val, 0) / dataArray.length;

                if (average > SILENCE_THRESHOLD) {
                    lastSoundTime = Date.now();
                } else {
                    const silenceDuration = Date.now() - lastSoundTime;
                    if (silenceDuration > SILENCE_DURATION && (Date.now() - voiceStartTime) > 1000) {
                        console.log('Auto-stopping due to silence');
                        if (mediaRecorder && mediaRecorder.state === 'recording') {
                            mediaRecorder.stop();
                            document.getElementById('voiceBtn').classList.remove('recording');
                        }
                        return;
                    }
                }

                silenceTimeout = setTimeout(checkSilence, 100);
            }

            checkSilence();
        }

        function stopSilenceDetection() {
            if (silenceTimeout) {
                clearTimeout(silenceTimeout);
                silenceTimeout = null;
            }
        }

'''

    # Insert before transcribeAudio function
    content = content.replace(
        '        async function transcribeAudio',
        silence_funcs + '        async function transcribeAudio'
    )

    # Update toggleVoice to call startSilenceDetection
    content = content.replace(
        '                    // Start visualizer and timer\n                    startVisualization();\n                    startTimer();',
        '                    // Start visualizer, timer, and silence detection\n                    startVisualization();\n                    startTimer();\n                    startSilenceDetection();'
    )

    # Update mediaRecorder.onstop to call stopSilenceDetection
    content = content.replace(
        '                        stopVisualization();\n                        stopTimer();',
        '                        stopVisualization();\n                        stopTimer();\n                        stopSilenceDetection();'
    )

    # Update cancelVoice to call stopSilenceDetection
    content = content.replace(
        '            stopVisualization();\n            stopTimer();\n            document.getElementById(\'voiceBtn\')',
        '            stopVisualization();\n            stopTimer();\n            stopSilenceDetection();\n            document.getElementById(\'voiceBtn\')'
    )

    with open(dashboard_file, 'w') as f:
        f.write(content)

    print("✅ Added auto-silence detection to dashboard")
    return True


def main():
    print("🚀 Applying Final Features to AURA v0.3.0")
    print("=" * 50)
    print()

    # 1. Add database storage to scanner
    print("1. Adding database storage to scanner...")
    if add_database_storage_to_scanner():
        print("   ✅ Scanner updated\n")
    else:
        print("   ⚠️  Manual update needed\n")

    # 2. Add silence detection to dashboard
    print("2. Adding auto-silence detection to voice...")
    if add_silence_detection_to_dashboard():
        print("   ✅ Voice interface updated\n")
    else:
        print("   ⚠️  Manual update needed\n")

    print("=" * 50)
    print("✅ Core features applied!")
    print()
    print("📝 Remaining manual steps:")
    print("   3. Add Logs tab to dashboard (see FINAL_INTEGRATION_TASKS.md)")
    print("   4. Add Twitter tab to dashboard (see FINAL_INTEGRATION_TASKS.md)")
    print("   5. Add API endpoints to aura_server.py")
    print()
    print("🚀 After completing, deploy with:")
    print("   git add -A")
    print("   git commit -m 'feat: Complete AURA integration'")
    print("   git push && railway up")


if __name__ == "__main__":
    main()
