import asyncio
import unittest

from graduation.config import grad_cfg, grad_state
from graduation.gates import evaluate_gates
from graduation.scoring import compute_graduation_score
from graduation.sizing import compute_sizing
from graduation.types import EnrichedCandidate, GraduationCandidateSeed, ModelOutput


class GraduationPipelineTest(unittest.TestCase):
    def build_candidate(self, gs: float = 80.0) -> EnrichedCandidate:
        seed = GraduationCandidateSeed(address="TestToken", symbol="TEST")
        market = {
            "market_cap": 50_000,
            "liquidity": 25_000,
            "vol_15m_usd": 5_000,
            "buy_ratio_15m": 0.65,
            "pumpfun_curve_pct": 90,
        }
        risk = {
            "sellability_sim_ok": True,
            "mint_revoked": True,
            "freeze_revoked": True,
            "lp_locked_bool": True,
            "lock_days": 45,
            "locker_rep_score": 0.8,
            "sniper_pct": 0.1,
            "top10_pct": 0.3,
            "creator_blocklisted": False,
            "creator_flagged_rugs": 0,
            "holder_velocity": 0.5,
        }
        analytics = {
            "buy_volume": 3000,
            "sell_volume": 2000,
            "whales_inflow": 250,
        }
        candidate = EnrichedCandidate(seed=seed, market=market, onchain={}, risk=risk, analytics=analytics)
        scoring = compute_graduation_score(candidate)
        if gs:
            scoring.gs = gs
        candidate.scoring_inputs = scoring.subscores
        return candidate

    def test_gates_pass(self):
        candidate = self.build_candidate()
        result = evaluate_gates(candidate)
        self.assertTrue(result.passed)

    def test_sizing_zero_when_ev_negative(self):
        decision = asyncio.run(compute_sizing(ModelOutput(1.0, 0.0, 0.0), open_exposure=0.0, open_positions=0))
        self.assertEqual(decision.size_fraction, 0.0)

    def test_scoring_threshold_enforced(self):
        candidate = self.build_candidate(gs=60)
        scoring = compute_graduation_score(candidate)
        self.assertLess(scoring.gs, 72)


if __name__ == "__main__":
    unittest.main()
