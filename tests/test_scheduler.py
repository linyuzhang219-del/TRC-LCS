from trc_lcs.config import TRCLCSConfig
from trc_lcs.scoring import CandidateScheduler
from trc_lcs.types import LoopCandidate


def candidate(score: float, redundancy: float = 0.0) -> LoopCandidate:
    return LoopCandidate(cur_id=40, hist_id=1, source="visual", total_score=score, redundancy=redundancy)


def test_scheduler_respects_budget():
    cfg = TRCLCSConfig(budget=2, high_score_threshold=0.5)
    scheduler = CandidateScheduler(cfg)
    selected = scheduler.schedule([candidate(0.9), candidate(0.8), candidate(0.7)], uncertainty=0.0)
    assert len(selected) == 2


def test_scheduler_suppresses_redundant_candidate():
    cfg = TRCLCSConfig(redundancy_threshold=0.8)
    scheduler = CandidateScheduler(cfg)
    c = candidate(0.9, redundancy=0.9)
    assert scheduler.schedule([c], uncertainty=0.0) == []
    assert c.schedule == "suppressed"
