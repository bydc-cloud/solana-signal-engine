"""
AURA WebSocket Manager
Real-time updates for dashboard
"""
import logging
import json
import asyncio
from typing import Set, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections for real-time dashboard updates
    Broadcasts:
    - New signals
    - Portfolio updates
    - Watchlist changes
    - Strategy executions
    - System metrics
    """

    def __init__(self):
        self.active_connections: Set = set()
        self.broadcast_queue: asyncio.Queue = asyncio.Queue()

    async def connect(self, websocket):
        """Register new WebSocket connection"""
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket):
        """Unregister WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict):
        """
        Broadcast message to all connected clients
        """
        if not self.active_connections:
            return

        message_json = json.dumps(message)
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.add(connection)

        # Remove disconnected clients
        for conn in disconnected:
            await self.disconnect(conn)

    async def broadcast_signal(self, signal: Dict):
        """Broadcast new signal to all clients"""
        await self.broadcast({
            'type': 'signal',
            'data': signal,
            'timestamp': datetime.now().isoformat(),
        })

    async def broadcast_portfolio_update(self, portfolio: Dict):
        """Broadcast portfolio update"""
        await self.broadcast({
            'type': 'portfolio_update',
            'data': portfolio,
            'timestamp': datetime.now().isoformat(),
        })

    async def broadcast_watchlist_update(self, watchlist: Dict):
        """Broadcast watchlist change"""
        await self.broadcast({
            'type': 'watchlist_update',
            'data': watchlist,
            'timestamp': datetime.now().isoformat(),
        })

    async def broadcast_strategy_execution(self, execution: Dict):
        """Broadcast strategy execution"""
        await self.broadcast({
            'type': 'strategy_execution',
            'data': execution,
            'timestamp': datetime.now().isoformat(),
        })

    async def broadcast_alert(self, alert: Dict):
        """Broadcast system alert"""
        await self.broadcast({
            'type': 'alert',
            'data': alert,
            'timestamp': datetime.now().isoformat(),
        })

    async def broadcast_metrics(self, metrics: Dict):
        """Broadcast system metrics"""
        await self.broadcast({
            'type': 'metrics',
            'data': metrics,
            'timestamp': datetime.now().isoformat(),
        })

    async def heartbeat(self):
        """
        Send periodic heartbeat to keep connections alive
        """
        while True:
            try:
                await asyncio.sleep(30)  # Every 30 seconds

                if self.active_connections:
                    await self.broadcast({
                        'type': 'heartbeat',
                        'timestamp': datetime.now().isoformat(),
                        'connections': len(self.active_connections),
                    })

            except Exception as e:
                logger.error(f"Heartbeat error: {e}")


# Singleton instance
websocket_manager = WebSocketManager()
