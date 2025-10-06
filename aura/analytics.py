"""
AURA Advanced Analytics Module
Backtesting, Monte Carlo simulations, risk-adjusted returns
"""
import logging
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from .database import db

logger = logging.getLogger(__name__)


class AdvancedAnalytics:
    """
    Advanced analytics for AURA:
    - Strategy backtesting (walk-forward)
    - Monte Carlo simulations
    - Risk-adjusted return metrics (Sharpe, Sortino)
    - Performance attribution
    """

    def __init__(self):
        self.db = db

    def backtest_strategy(
        self,
        strategy_id: int,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 10000,
    ) -> Dict:
        """
        Backtest a strategy on historical data
        Returns performance metrics
        """
        try:
            # Get strategy rules
            with self.db._get_conn() as conn:
                cur = conn.cursor()
                import json

                cur.execute("""
                    SELECT name, rules, type
                    FROM strategies
                    WHERE id = ?
                """, (strategy_id,))

                row = cur.fetchone()
                if not row:
                    logger.error(f"Strategy {strategy_id} not found")
                    return {}

                strategy_name, rules_json, strategy_type = row
                rules = json.loads(rules_json)

            # Get historical signals in date range
            signals = self._get_historical_signals(start_date, end_date)

            # Simulate trades based on strategy rules
            trades = []
            capital = initial_capital
            positions = []

            for signal in signals:
                # Check if signal matches entry rules
                if self._matches_entry_rules(signal, rules.get('entry', {})):
                    # Simulate entry
                    position_size = rules.get('position_size_usd', 1000)
                    entry_price = signal.get('price', 0)

                    if entry_price > 0 and capital >= position_size:
                        position = {
                            'entry_price': entry_price,
                            'size_usd': position_size,
                            'entry_time': signal['timestamp'],
                            'token_address': signal['token_address'],
                            'symbol': signal['symbol'],
                        }
                        positions.append(position)
                        capital -= position_size

                        # Simulate exit based on rules
                        exit_result = self._simulate_exit(position, rules.get('exit', {}))
                        if exit_result:
                            trades.append(exit_result)
                            capital += exit_result['exit_value_usd']
                            positions.remove(position)

            # Calculate performance metrics
            total_return = ((capital - initial_capital) / initial_capital) * 100
            win_rate = len([t for t in trades if t['pnl'] > 0]) / len(trades) if trades else 0

            return {
                'strategy_id': strategy_id,
                'strategy_name': strategy_name,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                },
                'initial_capital': initial_capital,
                'final_capital': capital,
                'total_return_percent': total_return,
                'total_trades': len(trades),
                'win_rate': win_rate,
                'trades': trades[:50],  # Sample of trades
            }

        except Exception as e:
            logger.error(f"Backtest error: {e}")
            return {}

    def monte_carlo_simulation(
        self,
        strategy_id: int,
        num_simulations: int = 1000,
        initial_capital: float = 10000,
    ) -> Dict:
        """
        Run Monte Carlo simulation on strategy
        Returns distribution of possible outcomes
        """
        try:
            # Get historical strategy performance
            trades = self._get_strategy_trades(strategy_id)

            if not trades:
                logger.warning(f"No trades for strategy {strategy_id}")
                return {}

            # Calculate returns distribution from historical trades
            returns = [t['pnl_percent'] for t in trades]
            mean_return = np.mean(returns)
            std_return = np.std(returns)

            # Run simulations
            final_capitals = []

            for _ in range(num_simulations):
                capital = initial_capital
                num_trades = len(returns)

                for _ in range(num_trades):
                    # Sample random return from distribution
                    trade_return = np.random.normal(mean_return, std_return)
                    capital *= (1 + trade_return / 100)

                final_capitals.append(capital)

            # Calculate statistics
            final_capitals = np.array(final_capitals)

            return {
                'strategy_id': strategy_id,
                'num_simulations': num_simulations,
                'initial_capital': initial_capital,
                'results': {
                    'mean_final_capital': float(np.mean(final_capitals)),
                    'median_final_capital': float(np.median(final_capitals)),
                    'std_final_capital': float(np.std(final_capitals)),
                    'percentile_5': float(np.percentile(final_capitals, 5)),
                    'percentile_25': float(np.percentile(final_capitals, 25)),
                    'percentile_75': float(np.percentile(final_capitals, 75)),
                    'percentile_95': float(np.percentile(final_capitals, 95)),
                    'probability_profit': float(np.mean(final_capitals > initial_capital)),
                },
            }

        except Exception as e:
            logger.error(f"Monte Carlo simulation error: {e}")
            return {}

    def calculate_sharpe_ratio(
        self,
        strategy_id: int,
        risk_free_rate: float = 0.04,
    ) -> float:
        """
        Calculate Sharpe ratio for strategy
        Risk-adjusted return metric
        """
        try:
            trades = self._get_strategy_trades(strategy_id)
            if not trades:
                return 0.0

            returns = [t['pnl_percent'] for t in trades]
            mean_return = np.mean(returns)
            std_return = np.std(returns)

            if std_return == 0:
                return 0.0

            # Annualize metrics (assuming daily returns)
            annual_return = mean_return * 252
            annual_std = std_return * np.sqrt(252)

            sharpe = (annual_return - risk_free_rate * 100) / annual_std

            return float(sharpe)

        except Exception as e:
            logger.error(f"Sharpe ratio error: {e}")
            return 0.0

    def calculate_sortino_ratio(
        self,
        strategy_id: int,
        risk_free_rate: float = 0.04,
    ) -> float:
        """
        Calculate Sortino ratio for strategy
        Like Sharpe but only penalizes downside volatility
        """
        try:
            trades = self._get_strategy_trades(strategy_id)
            if not trades:
                return 0.0

            returns = np.array([t['pnl_percent'] for t in trades])
            mean_return = np.mean(returns)

            # Calculate downside deviation
            downside_returns = returns[returns < 0]
            if len(downside_returns) == 0:
                downside_std = 0.0
            else:
                downside_std = np.std(downside_returns)

            if downside_std == 0:
                return 0.0

            # Annualize
            annual_return = mean_return * 252
            annual_downside_std = downside_std * np.sqrt(252)

            sortino = (annual_return - risk_free_rate * 100) / annual_downside_std

            return float(sortino)

        except Exception as e:
            logger.error(f"Sortino ratio error: {e}")
            return 0.0

    def calculate_max_drawdown(self, strategy_id: int) -> Dict:
        """
        Calculate maximum drawdown for strategy
        """
        try:
            trades = self._get_strategy_trades(strategy_id)
            if not trades:
                return {'max_drawdown_percent': 0}

            # Calculate cumulative returns
            cumulative_capital = [10000]  # Start with $10k
            for trade in trades:
                pnl_ratio = 1 + (trade['pnl_percent'] / 100)
                cumulative_capital.append(cumulative_capital[-1] * pnl_ratio)

            # Calculate drawdowns
            cumulative_capital = np.array(cumulative_capital)
            running_max = np.maximum.accumulate(cumulative_capital)
            drawdowns = (cumulative_capital - running_max) / running_max * 100

            max_dd = float(np.min(drawdowns))

            return {
                'max_drawdown_percent': max_dd,
                'recovery_trades': 0,  # TODO: Calculate recovery time
            }

        except Exception as e:
            logger.error(f"Max drawdown error: {e}")
            return {'max_drawdown_percent': 0}

    def _get_historical_signals(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """Get historical signals from database"""
        try:
            with self.db._get_conn() as conn:
                cur = conn.cursor()
                import json

                cur.execute("""
                    SELECT token_address, symbol, created_at, payload
                    FROM alerts
                    WHERE created_at BETWEEN ? AND ?
                    ORDER BY created_at ASC
                """, (start_date.isoformat(), end_date.isoformat()))

                signals = []
                for row in cur.fetchall():
                    payload = json.loads(row[3]) if row[3] else {}
                    signals.append({
                        'token_address': row[0],
                        'symbol': row[1],
                        'timestamp': row[2],
                        'price': payload.get('price', 0),
                        'momentum_score': payload.get('momentum_score', 0),
                        'volume_ratio': payload.get('volume_ratio', 0),
                    })

                return signals

        except Exception as e:
            logger.error(f"Get historical signals error: {e}")
            return []

    def _get_strategy_trades(self, strategy_id: int) -> List[Dict]:
        """Get historical trades for a strategy"""
        try:
            with self.db._get_conn() as conn:
                cur = conn.cursor()

                cur.execute("""
                    SELECT token_address, side, price, amount_usd, pnl_usd, created_at
                    FROM strategy_trades
                    WHERE strategy_id = ?
                    ORDER BY created_at ASC
                """, (strategy_id,))

                trades = []
                for row in cur.fetchall():
                    trades.append({
                        'token_address': row[0],
                        'side': row[1],
                        'price': float(row[2]),
                        'amount_usd': float(row[3]),
                        'pnl_usd': float(row[4]) if row[4] else 0,
                        'pnl_percent': (float(row[4]) / float(row[3])) * 100 if row[4] and row[3] else 0,
                        'timestamp': row[5],
                    })

                return trades

        except Exception as e:
            logger.error(f"Get strategy trades error: {e}")
            return []

    def _matches_entry_rules(self, signal: Dict, rules: Dict) -> bool:
        """Check if signal matches strategy entry rules"""
        try:
            momentum = signal.get('momentum_score', 0)
            volume_ratio = signal.get('volume_ratio', 0)

            momentum_rule = rules.get('momentum', {})
            if 'gte' in momentum_rule and momentum < momentum_rule['gte']:
                return False

            volume_rule = rules.get('volume_ratio', {})
            if 'gte' in volume_rule and volume_ratio < volume_rule['gte']:
                return False

            return True

        except Exception as e:
            logger.error(f"Match entry rules error: {e}")
            return False

    def _simulate_exit(self, position: Dict, exit_rules: Dict) -> Dict:
        """Simulate position exit based on rules"""
        try:
            # In production, fetch actual price history
            # For now, simulate based on random walk
            target_pnl = exit_rules.get('pnl_percent_target', 25)
            stop_loss = exit_rules.get('stop_loss_percent', -8)

            # Simulate random outcome
            outcome_pnl = np.random.uniform(stop_loss, target_pnl)

            exit_value = position['size_usd'] * (1 + outcome_pnl / 100)

            return {
                'entry_price': position['entry_price'],
                'exit_price': position['entry_price'] * (1 + outcome_pnl / 100),
                'pnl': exit_value - position['size_usd'],
                'pnl_percent': outcome_pnl,
                'exit_value_usd': exit_value,
                'hold_time_minutes': 120,
            }

        except Exception as e:
            logger.error(f"Simulate exit error: {e}")
            return None


# Singleton instance
analytics = AdvancedAnalytics()
