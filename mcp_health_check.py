#!/usr/bin/env python3
"""
MCP Health Check & Capability Cache
Tests all MCP servers and stores results in database
"""
import asyncio
import aiohttp
import time
import json
from typing import Dict, List
from datetime import datetime

# MCP endpoints to test
MCP_SERVERS = {
    "telegram": "https://signal-railway-deployment-production.up.railway.app/mcp/telegram",
    "database": "https://signal-railway-deployment-production.up.railway.app/mcp/database",
    "coingecko": "https://signal-railway-deployment-production.up.railway.app/mcp/coingecko",
    "firecrawl": "https://signal-railway-deployment-production.up.railway.app/mcp/firecrawl",
    "helius": "https://signal-railway-deployment-production.up.railway.app/mcp/helius",
    "birdeye": "https://signal-railway-deployment-production.up.railway.app/mcp/birdeye",
    "defillama": "https://signal-railway-deployment-production.up.railway.app/mcp/defillama",
    "viz": "https://signal-railway-deployment-production.up.railway.app/mcp/viz",
    "config": "https://signal-railway-deployment-production.up.railway.app/mcp/config",
    "deploy": "https://signal-railway-deployment-production.up.railway.app/mcp/deploy",
}

# Local MCPs (via npx)
LOCAL_MCPS = {
    "memory": "npx -y @modelcontextprotocol/server-memory",
    "context7": "npx -y @context7/mcp-server",
    "puppeteer": "npx -y @modelcontextprotocol/server-puppeteer",
    "sequential-thinking": "npx -y @modelcontextprotocol/server-sequential-thinking",
    "repo": "npx -y @modelcontextprotocol/server-github",
}


async def check_mcp_health(name: str, url: str, session: aiohttp.ClientSession) -> Dict:
    """
    Check health of a single MCP server
    Returns: {name, url, reachable, tool_count, p50_latency, p95_latency, error}
    """
    latencies = []
    tool_count = 0
    reachable = False
    error = None

    try:
        # Perform 10 health checks to get latency distribution
        for _ in range(10):
            start = time.time()

            try:
                async with session.get(f"{url}/mcp/tools", timeout=5) as resp:
                    latency = (time.time() - start) * 1000  # ms
                    latencies.append(latency)

                    if resp.status == 200:
                        reachable = True
                        data = await resp.json()
                        tool_count = len(data.get("tools", []))
                    else:
                        error = f"HTTP {resp.status}"

            except asyncio.TimeoutError:
                error = "Timeout (5s)"
                break
            except aiohttp.ClientError as e:
                error = f"Connection error: {e}"
                break

        # Calculate percentiles
        if latencies:
            latencies.sort()
            p50 = latencies[len(latencies) // 2]
            p95 = latencies[int(len(latencies) * 0.95)]
        else:
            p50 = 0
            p95 = 0

    except Exception as e:
        error = str(e)

    return {
        "name": name,
        "url": url,
        "reachable": "yes" if reachable else "no",
        "tool_count": tool_count,
        "p50_latency_ms": round(p50, 2) if latencies else 0,
        "p95_latency_ms": round(p95, 2) if latencies else 0,
        "error": error,
        "checked_at": datetime.now().isoformat(),
    }


async def check_local_mcp(name: str, command: str) -> Dict:
    """
    Check health of local MCP (npx-based)
    Returns: {name, command, reachable, error}
    """
    try:
        # Try to run the command with --version or --help
        proc = await asyncio.create_subprocess_shell(
            f"{command} --version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)

        reachable = proc.returncode == 0 or b"version" in stdout.lower() or b"help" in stdout.lower()
        error = None if reachable else f"Exit code {proc.returncode}"

    except asyncio.TimeoutError:
        reachable = False
        error = "Timeout (10s)"
    except Exception as e:
        reachable = False
        error = str(e)

    return {
        "name": name,
        "command": command,
        "reachable": "yes" if reachable else "no",
        "tool_count": "N/A (local)",
        "p50_latency_ms": "N/A",
        "p95_latency_ms": "N/A",
        "error": error,
        "checked_at": datetime.now().isoformat(),
    }


async def run_health_checks() -> List[Dict]:
    """Run health checks on all MCPs"""
    results = []

    # Check HTTP-based MCPs
    async with aiohttp.ClientSession() as session:
        tasks = [check_mcp_health(name, url, session) for name, url in MCP_SERVERS.items()]
        http_results = await asyncio.gather(*tasks)
        results.extend(http_results)

    # Check local MCPs
    local_tasks = [check_local_mcp(name, cmd) for name, cmd in LOCAL_MCPS.items()]
    local_results = await asyncio.gather(*local_tasks)
    results.extend(local_results)

    return results


def print_health_table(results: List[Dict]):
    """Print health check results as a table"""
    print("\n╔═══════════════════════════════════════════════════════════════════════════════════════╗")
    print("║                           MCP HEALTH CHECK RESULTS                                    ║")
    print("╠═══════════════════════════════════════════════════════════════════════════════════════╣")
    print("║ Name             │ Reachable │ Tools │ P50 Latency │ P95 Latency │ Error              ║")
    print("╠══════════════════╪═══════════╪═══════╪═════════════╪═════════════╪═══════════════════║")

    for result in results:
        name = result["name"][:15].ljust(15)
        reachable = result["reachable"].center(9)
        tools = str(result["tool_count"]).center(5)
        p50 = f"{result['p50_latency_ms']}ms".rjust(11) if isinstance(result['p50_latency_ms'], (int, float)) else str(result['p50_latency_ms']).center(11)
        p95 = f"{result['p95_latency_ms']}ms".rjust(11) if isinstance(result['p95_latency_ms'], (int, float)) else str(result['p95_latency_ms']).center(11)
        error = (result["error"] or "OK")[:17].ljust(17)

        print(f"║ {name} │ {reachable} │ {tools} │ {p50} │ {p95} │ {error} ║")

    print("╚═══════════════════════════════════════════════════════════════════════════════════════╝")


def save_to_database(results: List[Dict]):
    """Save health check results to database"""
    try:
        from aura.database import db

        # Store as JSON in configs table under path="mcp/health"
        health_summary = {
            "checked_at": datetime.now().isoformat(),
            "total_mcps": len(results),
            "reachable_count": sum(1 for r in results if r["reachable"] == "yes"),
            "unreachable_count": sum(1 for r in results if r["reachable"] == "no"),
            "servers": results,
        }

        db.set_config("mcp_health", json.dumps(health_summary))

        print(f"\n✅ Health check results saved to database at configs/mcp/health")
        print(f"   Reachable: {health_summary['reachable_count']}/{health_summary['total_mcps']}")

    except Exception as e:
        print(f"\n⚠️  Could not save to database: {e}")


def print_fix_commands(results: List[Dict]):
    """Print curl commands to debug unreachable MCPs"""
    unreachable = [r for r in results if r["reachable"] == "no" and "url" in r]

    if unreachable:
        print("\n╔═══════════════════════════════════════════════════════════════════════════════════════╗")
        print("║                           UNREACHABLE MCPs - DEBUG COMMANDS                          ║")
        print("╚═══════════════════════════════════════════════════════════════════════════════════════╝\n")

        for r in unreachable:
            print(f"# {r['name'].upper()} - {r['error']}")
            print(f"curl -v {r['url']}/mcp/tools\n")

        print("\nCommon fixes:")
        print("  - DNS: Check if URL is accessible")
        print("  - Token: Verify API keys in environment variables")
        print("  - CORS/SSE: Ensure server supports Server-Sent Events")
        print("  - Deployment: Check if Railway service is running\n")


async def main():
    """Main entry point"""
    print("🔧 Starting MCP Health Check...")
    print("⏳ Testing all MCP servers (this may take 30-60 seconds)...\n")

    results = await run_health_checks()

    print_health_table(results)
    save_to_database(results)
    print_fix_commands(results)


if __name__ == "__main__":
    asyncio.run(main())
