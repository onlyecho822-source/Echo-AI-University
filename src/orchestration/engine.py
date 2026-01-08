#!/usr/bin/env python3
"""
Echo Universe - Orchestration Engine with Coherence Lock
The binding substrate that transforms independent components into a self-evolving system.

This engine implements the sense() → plan() → act() control loop with coherence monitoring.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import subprocess

class CoherenceLock:
    """
    Measures semantic convergence and detects drift.
    Prevents the system from diverging into chaos.
    """
    
    def __init__(self, ledger_path: Path):
        self.ledger_path = ledger_path
        self.coherence_threshold = 0.7
        
    def calculate_coherence_index(self) -> float:
        """
        Calculate system coherence based on:
        - Contradiction density (lower is better)
        - Resolution half-life (faster is better)
        - Performance variance (lower is better)
        """
        # Read ledger
        if not self.ledger_path.exists():
            return 1.0  # Perfect coherence if no data yet
        
        with open(self.ledger_path, 'r') as f:
            entries = [json.loads(line) for line in f]
        
        if len(entries) == 0:
            return 1.0
        
        # Calculate metrics
        contradiction_density = self._calculate_contradiction_density(entries)
        resolution_speed = self._calculate_resolution_speed(entries)
        performance_variance = self._calculate_performance_variance(entries)
        
        # Weighted coherence index
        coherence = (
            (1 - contradiction_density) * 0.4 +
            resolution_speed * 0.3 +
            (1 - performance_variance) * 0.3
        )
        
        return coherence
    
    def _calculate_contradiction_density(self, entries: List[Dict]) -> float:
        """Measure rate of contradictions per 100 events"""
        total = len(entries)
        contradictions = sum(1 for e in entries if e.get('event_type') == 'contradiction')
        return min(contradictions / max(total, 1), 1.0)
    
    def _calculate_resolution_speed(self, entries: List[Dict]) -> float:
        """Measure how quickly contradictions are resolved"""
        # Simplified: assume faster is better
        # In real implementation, track time from contradiction to resolution
        return 0.8  # Placeholder
    
    def _calculate_performance_variance(self, entries: List[Dict]) -> float:
        """Measure variance in agent performance"""
        scores = [e.get('overall_score', 0) for e in entries if 'overall_score' in e]
        if len(scores) < 2:
            return 0.0
        
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        return min(variance, 1.0)
    
    def is_coherent(self) -> bool:
        """Check if system is above coherence threshold"""
        return self.calculate_coherence_index() >= self.coherence_threshold


class OrchestrationEngine:
    """
    The control loop that binds all Echo components into a self-evolving system.
    """
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.ledger_path = base_path / "ledger" / "training_log.jsonl"
        self.reports_path = base_path / "reports"
        self.coherence_lock = CoherenceLock(self.ledger_path)
        
    def sense(self) -> Dict[str, Any]:
        """
        Read system state from Constitutional Ledger and file system.
        Returns current state snapshot.
        """
        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "coherence_index": self.coherence_lock.calculate_coherence_index(),
            "agents": self._get_agent_status(),
            "training_queue": self._get_training_queue(),
            "pending_credentials": self._get_pending_credentials()
        }
        
        return state
    
    def _get_agent_status(self) -> List[Dict]:
        """Read agent status from reports"""
        agents = []
        
        if not self.reports_path.exists():
            return agents
        
        for report_file in self.reports_path.glob("*_entry_exam_report.json"):
            with open(report_file, 'r') as f:
                report = json.load(f)
                agents.append({
                    "name": report["agent_name"],
                    "id": report["agent_id"],
                    "score": report["overall_score"],
                    "credential": report["credential_earned"],
                    "exam_date": report["exam_date"]
                })
        
        return agents
    
    def _get_training_queue(self) -> List[str]:
        """Determine which agents need training"""
        agents = self._get_agent_status()
        
        # Agents with score < 1.0 need retraining
        return [a["name"] for a in agents if a["score"] < 1.0]
    
    def _get_pending_credentials(self) -> List[str]:
        """Determine which agents need credential upgrades"""
        agents = self._get_agent_status()
        
        # Agents with "cadet" credential can advance to "specialist"
        return [a["name"] for a in agents if a["credential"] == "cadet"]
    
    def plan(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decide next action based on current state.
        Returns decision object.
        """
        decision = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "none",
            "target": None,
            "rationale": ""
        }
        
        # Priority 1: Check coherence
        if not self.coherence_lock.is_coherent():
            decision["action"] = "restore_coherence"
            decision["rationale"] = f"Coherence index {state['coherence_index']:.2f} below threshold"
            return decision
        
        # Priority 2: Train agents in queue
        if state["training_queue"]:
            decision["action"] = "train_agent"
            decision["target"] = state["training_queue"][0]
            decision["rationale"] = f"Agent {decision['target']} needs retraining"
            return decision
        
        # Priority 3: Upgrade credentials
        if state["pending_credentials"]:
            decision["action"] = "upgrade_credential"
            decision["target"] = state["pending_credentials"][0]
            decision["rationale"] = f"Agent {decision['target']} ready for credential upgrade"
            return decision
        
        # Priority 4: Monitor (no action needed)
        decision["action"] = "monitor"
        decision["rationale"] = "System stable, monitoring for changes"
        
        return decision
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the decided action.
        Returns execution result.
        """
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": decision["action"],
            "target": decision["target"],
            "success": False,
            "details": ""
        }
        
        if decision["action"] == "restore_coherence":
            result["success"] = self._restore_coherence()
            result["details"] = "Triggered coherence restoration procedures"
        
        elif decision["action"] == "train_agent":
            result["success"] = self._train_agent(decision["target"])
            result["details"] = f"Initiated training for {decision['target']}"
        
        elif decision["action"] == "upgrade_credential":
            result["success"] = self._upgrade_credential(decision["target"])
            result["details"] = f"Upgraded credential for {decision['target']}"
        
        elif decision["action"] == "monitor":
            result["success"] = True
            result["details"] = "System monitoring active"
        
        # Log to ledger
        self._log_action(decision, result)
        
        return result
    
    def _restore_coherence(self) -> bool:
        """Restore system coherence"""
        # In real implementation: trigger evolution cycle, rebuild teams, etc.
        print("  [ACTION] Restoring coherence...")
        return True
    
    def _train_agent(self, agent_name: str) -> bool:
        """Train an agent"""
        print(f"  [ACTION] Training agent: {agent_name}")
        # In real implementation: run chaos training scenarios
        return True
    
    def _upgrade_credential(self, agent_name: str) -> bool:
        """Upgrade agent credential"""
        print(f"  [ACTION] Upgrading credential for: {agent_name}")
        # In real implementation: run next stage of training, issue new credential
        return True
    
    def _log_action(self, decision: Dict, result: Dict):
        """Log action to Constitutional Ledger"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "orchestration_action",
            "decision": decision,
            "result": result
        }
        
        with open(self.ledger_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def run_cycle(self):
        """Run one complete sense → plan → act cycle"""
        print(f"\n{'='*60}")
        print(f"ORCHESTRATION CYCLE - {datetime.utcnow().isoformat()}")
        print(f"{'='*60}")
        
        # Sense
        print("\n[SENSE] Reading system state...")
        state = self.sense()
        print(f"  Coherence Index: {state['coherence_index']:.2f}")
        print(f"  Active Agents: {len(state['agents'])}")
        print(f"  Training Queue: {len(state['training_queue'])}")
        print(f"  Pending Credentials: {len(state['pending_credentials'])}")
        
        # Plan
        print("\n[PLAN] Deciding next action...")
        decision = self.plan(state)
        print(f"  Action: {decision['action']}")
        print(f"  Target: {decision['target']}")
        print(f"  Rationale: {decision['rationale']}")
        
        # Act
        print("\n[ACT] Executing action...")
        result = self.act(decision)
        print(f"  Success: {result['success']}")
        print(f"  Details: {result['details']}")
        
        print(f"\n{'='*60}\n")
        
        return result
    
    def run_continuous(self, interval_seconds: int = 900):
        """Run orchestration engine continuously"""
        print(f"Starting Orchestration Engine (interval: {interval_seconds}s)")
        
        while True:
            try:
                self.run_cycle()
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                print("\nOrchestration Engine stopped by user")
                break
            except Exception as e:
                print(f"\nError in orchestration cycle: {e}")
                time.sleep(interval_seconds)


def main():
    base_path = Path(__file__).parent.parent.parent
    engine = OrchestrationEngine(base_path)
    
    # Run one cycle for testing
    engine.run_cycle()
    
    # Uncomment to run continuously:
    # engine.run_continuous(interval_seconds=900)  # 15 minutes


if __name__ == "__main__":
    main()
