#!/usr/bin/env python3
"""
Octopus Memory Architecture
Distributed cognition system inspired by octopus intelligence.

Central Brain: Constitutional Ledger (global coordination)
Arms: Global Nexus nodes (regional intelligence)
Arm Memory: Local file-based memory stores
Hive Memory: Shared knowledge across all nodes
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Memory:
    """A single memory unit (knowledge artifact)"""
    memory_id: str
    memory_type: str  # "practice", "failure", "insight", "pattern"
    content: Dict[str, Any]
    created_at: str
    created_by: str  # node_id or agent_id
    confidence: float  # 0.0-1.0
    usage_count: int
    last_accessed: str
    tags: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class ArmMemory:
    """
    Local memory store for a single Global Nexus node (octopus arm).
    Each arm maintains its own memory independent of other arms.
    """
    
    def __init__(self, node_id: str, memory_path: Path):
        self.node_id = node_id
        self.memory_path = memory_path
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # Memory categories
        self.practices_path = self.memory_path / "practices"
        self.failures_path = self.memory_path / "failures"
        self.insights_path = self.memory_path / "insights"
        self.patterns_path = self.memory_path / "patterns"
        
        for path in [self.practices_path, self.failures_path, 
                     self.insights_path, self.patterns_path]:
            path.mkdir(exist_ok=True)
    
    def create_memory(self, memory_type: str, content: Dict[str, Any], 
                     tags: List[str] = None, confidence: float = 1.0) -> Memory:
        """
        Create a new memory and persist to disk.
        """
        # Generate memory ID from content hash
        content_str = json.dumps(content, sort_keys=True)
        memory_id = hashlib.sha256(content_str.encode()).hexdigest()[:16]
        
        memory = Memory(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            created_at=datetime.utcnow().isoformat(),
            created_by=self.node_id,
            confidence=confidence,
            usage_count=0,
            last_accessed=datetime.utcnow().isoformat(),
            tags=tags or []
        )
        
        # Persist to disk
        self._save_memory(memory)
        
        return memory
    
    def _save_memory(self, memory: Memory):
        """Save memory to appropriate category folder"""
        category_path = self._get_category_path(memory.memory_type)
        file_path = category_path / f"{memory.memory_id}.json"
        
        with open(file_path, 'w') as f:
            f.write(memory.to_json())
    
    def _get_category_path(self, memory_type: str) -> Path:
        """Get path for memory category"""
        mapping = {
            "practice": self.practices_path,
            "failure": self.failures_path,
            "insight": self.insights_path,
            "pattern": self.patterns_path
        }
        return mapping.get(memory_type, self.memory_path)
    
    def recall_memory(self, memory_id: str) -> Optional[Memory]:
        """Recall a specific memory by ID"""
        # Search all categories
        for category_path in [self.practices_path, self.failures_path,
                             self.insights_path, self.patterns_path]:
            file_path = category_path / f"{memory_id}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    memory = Memory(**data)
                    
                    # Update usage stats
                    memory.usage_count += 1
                    memory.last_accessed = datetime.utcnow().isoformat()
                    self._save_memory(memory)
                    
                    return memory
        
        return None
    
    def search_memories(self, memory_type: Optional[str] = None, 
                       tags: Optional[List[str]] = None,
                       min_confidence: float = 0.0) -> List[Memory]:
        """Search memories by type, tags, or confidence"""
        results = []
        
        # Determine which categories to search
        if memory_type:
            search_paths = [self._get_category_path(memory_type)]
        else:
            search_paths = [self.practices_path, self.failures_path,
                          self.insights_path, self.patterns_path]
        
        # Search all relevant paths
        for category_path in search_paths:
            for file_path in category_path.glob("*.json"):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    memory = Memory(**data)
                    
                    # Apply filters
                    if memory.confidence < min_confidence:
                        continue
                    
                    if tags and not any(tag in memory.tags for tag in tags):
                        continue
                    
                    results.append(memory)
        
        # Sort by confidence and recency
        results.sort(key=lambda m: (m.confidence, m.last_accessed), reverse=True)
        
        return results
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about arm memory"""
        stats = {
            "node_id": self.node_id,
            "total_memories": 0,
            "by_type": {},
            "avg_confidence": 0.0,
            "most_used": None
        }
        
        all_memories = self.search_memories()
        stats["total_memories"] = len(all_memories)
        
        if all_memories:
            # Count by type
            for memory in all_memories:
                stats["by_type"][memory.memory_type] = \
                    stats["by_type"].get(memory.memory_type, 0) + 1
            
            # Average confidence
            stats["avg_confidence"] = sum(m.confidence for m in all_memories) / len(all_memories)
            
            # Most used
            most_used = max(all_memories, key=lambda m: m.usage_count)
            stats["most_used"] = {
                "memory_id": most_used.memory_id,
                "type": most_used.memory_type,
                "usage_count": most_used.usage_count
            }
        
        return stats


class HiveMemory:
    """
    Shared memory across all Global Nexus nodes (octopus hive mind).
    Coordinates memory sharing and synchronization between arms.
    """
    
    def __init__(self, ledger_path: Path):
        self.ledger_path = ledger_path
        self.arms: Dict[str, ArmMemory] = {}
    
    def register_arm(self, node_id: str, memory_path: Path) -> ArmMemory:
        """Register a new arm (node) with the hive"""
        arm = ArmMemory(node_id, memory_path)
        self.arms[node_id] = arm
        return arm
    
    def share_memory(self, source_node: str, memory: Memory, target_nodes: List[str] = None):
        """
        Share a memory from one arm to others.
        If target_nodes is None, share with all arms.
        """
        if target_nodes is None:
            target_nodes = [node_id for node_id in self.arms.keys() if node_id != source_node]
        
        for target_node in target_nodes:
            if target_node in self.arms:
                target_arm = self.arms[target_node]
                
                # Create copy of memory in target arm
                target_arm.create_memory(
                    memory_type=memory.memory_type,
                    content=memory.content,
                    tags=memory.tags + [f"shared_from_{source_node}"],
                    confidence=memory.confidence * 0.9  # Slight confidence decay for shared memories
                )
        
        # Log to Constitutional Ledger
        self._log_memory_share(source_node, memory, target_nodes)
    
    def _log_memory_share(self, source_node: str, memory: Memory, target_nodes: List[str]):
        """Log memory sharing event to Constitutional Ledger"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "memory_shared",
            "source_node": source_node,
            "memory_id": memory.memory_id,
            "memory_type": memory.memory_type,
            "target_nodes": target_nodes,
            "confidence": memory.confidence
        }
        
        with open(self.ledger_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def collective_recall(self, memory_id: str) -> List[Memory]:
        """
        Query all arms for a specific memory.
        Returns all versions found across the hive.
        """
        results = []
        
        for node_id, arm in self.arms.items():
            memory = arm.recall_memory(memory_id)
            if memory:
                results.append(memory)
        
        return results
    
    def consensus_memory(self, memory_type: str, tags: List[str]) -> Optional[Memory]:
        """
        Find the memory with highest consensus across arms.
        Useful for determining "what the hive believes."
        """
        all_memories = []
        
        for arm in self.arms.values():
            memories = arm.search_memories(memory_type=memory_type, tags=tags)
            all_memories.extend(memories)
        
        if not all_memories:
            return None
        
        # Group by content similarity
        memory_groups = self._group_similar_memories(all_memories)
        
        # Find group with highest total confidence
        best_group = max(memory_groups, key=lambda g: sum(m.confidence for m in g))
        
        # Return highest confidence memory from best group
        return max(best_group, key=lambda m: m.confidence)
    
    def _group_similar_memories(self, memories: List[Memory]) -> List[List[Memory]]:
        """Group memories by content similarity"""
        groups = []
        
        for memory in memories:
            # Find existing group with similar content
            found_group = False
            for group in groups:
                if self._are_similar(memory, group[0]):
                    group.append(memory)
                    found_group = True
                    break
            
            # Create new group if no match
            if not found_group:
                groups.append([memory])
        
        return groups
    
    def _are_similar(self, m1: Memory, m2: Memory) -> bool:
        """Check if two memories are similar (simplified)"""
        # In real implementation, use semantic similarity
        return m1.memory_type == m2.memory_type and \
               len(set(m1.tags) & set(m2.tags)) > 0
    
    def get_hive_stats(self) -> Dict[str, Any]:
        """Get statistics about entire hive memory"""
        stats = {
            "total_arms": len(self.arms),
            "total_memories": 0,
            "memories_by_arm": {},
            "knowledge_diversity": 0.0,
            "most_active_arm": None
        }
        
        for node_id, arm in self.arms.items():
            arm_stats = arm.get_memory_stats()
            stats["memories_by_arm"][node_id] = arm_stats["total_memories"]
            stats["total_memories"] += arm_stats["total_memories"]
        
        if stats["memories_by_arm"]:
            # Most active arm
            stats["most_active_arm"] = max(
                stats["memories_by_arm"].items(),
                key=lambda x: x[1]
            )[0]
            
            # Knowledge diversity (variance in memory counts)
            counts = list(stats["memories_by_arm"].values())
            avg = sum(counts) / len(counts)
            variance = sum((c - avg) ** 2 for c in counts) / len(counts)
            stats["knowledge_diversity"] = 1.0 / (1.0 + variance)  # Normalize
        
        return stats


class PhoenixMemoryEngine:
    """
    Integration of Phoenix Cycle with Octopus Memory Architecture.
    Enables continuous learning through memory creation and evolution.
    """
    
    def __init__(self, hive: HiveMemory):
        self.hive = hive
    
    def capture_successful_practice(self, node_id: str, practice: Dict[str, Any], 
                                   performance: Dict[str, Any]):
        """
        Capture a successful practice as a memory.
        Part of Phoenix Cycle Phase 3 (Reproduction).
        """
        arm = self.hive.arms[node_id]
        
        memory = arm.create_memory(
            memory_type="practice",
            content={
                "practice": practice,
                "performance": performance,
                "fitness_score": performance.get("fitness", 0.0)
            },
            tags=["successful", "phoenix_cycle", practice.get("domain", "general")],
            confidence=performance.get("fitness", 0.0)
        )
        
        # Share with other arms if fitness > 0.8
        if performance.get("fitness", 0.0) > 0.8:
            self.hive.share_memory(node_id, memory)
        
        return memory
    
    def capture_failure_pattern(self, node_id: str, failure: Dict[str, Any]):
        """
        Capture a failure pattern as a memory.
        Used for learning from mistakes.
        """
        arm = self.hive.arms[node_id]
        
        memory = arm.create_memory(
            memory_type="failure",
            content=failure,
            tags=["failure", "learning_opportunity", failure.get("failure_type", "unknown")],
            confidence=1.0  # Failures are facts
        )
        
        # Always share failures (learn from each other's mistakes)
        self.hive.share_memory(node_id, memory)
        
        return memory
    
    def capture_insight(self, node_id: str, insight: str, context: Dict[str, Any]):
        """
        Capture an insight (emergent understanding).
        Part of Phoenix Cycle Phase 4 (Adaptation).
        """
        arm = self.hive.arms[node_id]
        
        memory = arm.create_memory(
            memory_type="insight",
            content={
                "insight": insight,
                "context": context,
                "derived_from": context.get("source_memories", [])
            },
            tags=["insight", "emergent", context.get("domain", "general")],
            confidence=0.7  # Insights are hypotheses
        )
        
        return memory
    
    def detect_pattern(self, node_id: str, pattern: Dict[str, Any]):
        """
        Detect and capture a pattern across multiple memories.
        Enables meta-learning.
        """
        arm = self.hive.arms[node_id]
        
        memory = arm.create_memory(
            memory_type="pattern",
            content=pattern,
            tags=["pattern", "meta_learning", pattern.get("pattern_type", "unknown")],
            confidence=pattern.get("confidence", 0.5)
        )
        
        # Share high-confidence patterns
        if pattern.get("confidence", 0.0) > 0.75:
            self.hive.share_memory(node_id, memory)
        
        return memory


# Example usage
def main():
    # Initialize hive
    ledger_path = Path("/home/ubuntu/Echo-AI-University/ledger/training_log.jsonl")
    hive = HiveMemory(ledger_path)
    
    # Register arms (Global Nexus nodes)
    arm_us = hive.register_arm("node_us", Path("/home/ubuntu/Echo-AI-University/memory/node_us"))
    arm_eu = hive.register_arm("node_eu", Path("/home/ubuntu/Echo-AI-University/memory/node_eu"))
    arm_apac = hive.register_arm("node_apac", Path("/home/ubuntu/Echo-AI-University/memory/node_apac"))
    
    # Initialize Phoenix Memory Engine
    phoenix = PhoenixMemoryEngine(hive)
    
    # Example: Capture successful practice
    practice = {
        "name": "exponential_backoff_retry",
        "description": "Retry failed API calls with exponential backoff",
        "domain": "api_failure_recovery"
    }
    performance = {
        "fitness": 0.92,
        "survival_rate": 0.95,
        "avg_recovery_time": 2.3
    }
    
    memory = phoenix.capture_successful_practice("node_us", practice, performance)
    print(f"Created memory: {memory.memory_id}")
    print(f"Shared with: {len(hive.arms) - 1} other arms")
    
    # Get hive stats
    stats = hive.get_hive_stats()
    print(f"\nHive Stats:")
    print(f"  Total Arms: {stats['total_arms']}")
    print(f"  Total Memories: {stats['total_memories']}")
    print(f"  Knowledge Diversity: {stats['knowledge_diversity']:.2f}")


if __name__ == "__main__":
    main()
