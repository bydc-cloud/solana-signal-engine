"""Graduation multi-class predictive model."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from .types import EnrichedCandidate, ModelOutput, ScoringResult

logger = logging.getLogger(__name__)

MODEL_STATE_PATH = Path(__file__).parent / "model_state.json"


@dataclass
class CalibrationState:
    temperature: float = 1.0
    prior_shift: float = 0.0


class GraduationModel:
    def __init__(self) -> None:
        self.calibration = CalibrationState()
        self.base_priors = (0.70, 0.25, 0.05)
        self._load_state()

    def _load_state(self) -> None:
        if MODEL_STATE_PATH.exists():
            try:
                data = json.loads(MODEL_STATE_PATH.read_text())
                self.calibration = CalibrationState(**data.get("calibration", {}))
                priors = data.get("priors")
                if isinstance(priors, list) and len(priors) == 3:
                    self.base_priors = tuple(priors)  # type: ignore
            except Exception as exc:
                logger.debug("Failed to load model state: %s", exc)

    def _save_state(self) -> None:
        try:
            MODEL_STATE_PATH.write_text(json.dumps({
                "calibration": self.calibration.__dict__,
                "priors": list(self.base_priors),
            }))
        except Exception as exc:
            logger.debug("Failed to persist model state: %s", exc)

    def predict(self, candidate: EnrichedCandidate, scoring: ScoringResult) -> ModelOutput:
        gs = scoring.gs
        risk_penalty = 0.0
        if not candidate.gates.get("sellability_sim", False):
            risk_penalty += 0.2
        if candidate.risk.get("creator_blocklisted"):
            risk_penalty += 0.3

        mega_chance = max(0.0, min(0.6, (gs - 82) / 25))
        winner_chance = max(0.05, min(0.75, (gs - 68) / 30 + 0.25))
        loser_chance = 1.0 - winner_chance - mega_chance
        if loser_chance < 0:
            mega_chance = max(0.0, mega_chance + loser_chance)
            loser_chance = max(0.01, 1.0 - winner_chance - mega_chance)

        loser_chance = max(0.01, loser_chance + risk_penalty)
        total = loser_chance + winner_chance + mega_chance
        if total <= 0:
            loser_chance, winner_chance, mega_chance = self.base_priors
            total = sum(self.base_priors)
        loser_chance /= total
        winner_chance /= total
        mega_chance /= total

        calibrated = self._apply_calibration((loser_chance, winner_chance, mega_chance))
        return ModelOutput(*calibrated)

    def _apply_calibration(self, probs: Iterable[float]) -> List[float]:
        temperature = max(0.25, self.calibration.temperature)
        scaled = [p ** (1 / temperature) for p in probs]
        total = sum(scaled)
        if total == 0:
            return list(self.base_priors)
        scaled = [p / total for p in scaled]
        shift = self.calibration.prior_shift
        scaled[1] = max(0.0, min(1.0, scaled[1] + shift))
        remainder = 1.0 - scaled[1]
        if remainder <= 0:
            return [0.99, 0.01, 0.0]
        ratio = remainder / (scaled[0] + scaled[2]) if scaled[0] + scaled[2] else 0.5
        scaled[0] = remainder * ratio
        scaled[2] = remainder * (1 - ratio)
        return scaled

    def calibrate(self, errors: List[float]) -> None:
        if not errors:
            return
        avg_error = sum(abs(e) for e in errors) / len(errors)
        self.calibration.temperature = min(2.0, max(0.5, 1 + avg_error))
        self._save_state()

    def train_stub(self, dataset: List[Dict[str, float]]) -> None:
        if not dataset:
            return
        winners = sum(1 for row in dataset if row.get("label") == 1)
        megas = sum(1 for row in dataset if row.get("label") == 2)
        losers = len(dataset) - winners - megas
        total = max(1, len(dataset))
        self.base_priors = (losers / total, winners / total, megas / total)
        self._save_state()


grad_model = GraduationModel()
