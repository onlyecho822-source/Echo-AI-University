#!/usr/bin/env python3
"""
Scavenger Intelligence System
"Digital Trash Collectors with Molecule Sorters"

Collects discarded knowledge from public sources:
- Failed experiments
- Abandoned repositories
- Edge case bugs
- Obscure forum posts
- "Didn't work" papers

Extracts signal from noise using molecule sorting algorithms.
"""

import json
import hashlib
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class KnowledgeArtifact:
    """A piece of extracted knowledge from digital trash"""
    artifact_id: str
    source_type: str  # "paper", "github", "forum", "blog", "issue"
    source_url: str
    title: str
    content: str
    extracted_insights: List[str]
    failure_patterns: List[str]
    edge_cases: List[str]
    confidence: float
    relevance_score: float
    collected_at: str
    tags: List[str]


class DigitalTrashCollector:
    """
    Collects "trash" (discarded/failed knowledge) from public sources.
    Operates anonymously to avoid revealing Echo's intelligence gathering.
    """
    
    def __init__(self, collection_path: Path):
        self.collection_path = collection_path
        self.collection_path.mkdir(parents=True, exist_ok=True)
        
        # Anonymous user agents (rotate to avoid detection)
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        self.current_ua_index = 0
    
    def _get_headers(self) -> Dict[str, str]:
        """Get anonymous headers for requests"""
        ua = self.user_agents[self.current_ua_index]
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        
        return {
            "User-Agent": ua,
            "Accept": "text/html,application/json",
            "Accept-Language": "en-US,en;q=0.9"
        }
    
    def collect_arxiv_failures(self, keywords: List[str], days_back: int = 7) -> List[Dict]:
        """
        Collect papers from arXiv that mention failures, limitations, or negative results.
        These are goldmines—most papers hide failures, those that don't are honest.
        """
        artifacts = []
        
        # Search for papers with failure-related keywords
        failure_terms = [
            "did not work",
            "failed to",
            "limitations",
            "negative results",
            "unsuccessful",
            "challenges",
            "difficulties"
        ]
        
        for keyword in keywords:
            for failure_term in failure_terms:
                query = f"{keyword} AND {failure_term}"
                
                # arXiv API search (public, no auth needed)
                url = f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results=10"
                
                try:
                    response = requests.get(url, headers=self._get_headers(), timeout=10)
                    
                    if response.status_code == 200:
                        # Parse XML response (simplified)
                        # In production, use proper XML parsing
                        if "entry" in response.text:
                            artifact = {
                                "source_type": "arxiv_paper",
                                "query": query,
                                "raw_response": response.text[:500],  # Truncate
                                "collected_at": datetime.utcnow().isoformat()
                            }
                            artifacts.append(artifact)
                
                except Exception as e:
                    print(f"Error collecting from arXiv: {e}")
        
        return artifacts
    
    def collect_github_abandoned_repos(self, topic: str) -> List[Dict]:
        """
        Collect abandoned GitHub repositories (last commit > 2 years ago).
        These contain failed experiments and lessons learned.
        """
        artifacts = []
        
        # GitHub API (public, no auth for basic search)
        url = f"https://api.github.com/search/repositories?q={topic}+archived:true&sort=updated&order=asc"
        
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for repo in data.get("items", [])[:10]:  # Limit to 10
                    artifact = {
                        "source_type": "github_abandoned",
                        "repo_name": repo.get("full_name"),
                        "description": repo.get("description"),
                        "last_updated": repo.get("updated_at"),
                        "stars": repo.get("stargazers_count"),
                        "url": repo.get("html_url"),
                        "collected_at": datetime.utcnow().isoformat()
                    }
                    artifacts.append(artifact)
        
        except Exception as e:
            print(f"Error collecting from GitHub: {e}")
        
        return artifacts
    
    def collect_stackoverflow_edge_cases(self, tag: str) -> List[Dict]:
        """
        Collect Stack Overflow questions with no accepted answer.
        These represent unsolved problems and edge cases.
        """
        artifacts = []
        
        # Stack Exchange API (public, no auth needed)
        url = f"https://api.stackexchange.com/2.3/questions/no-answers?order=desc&sort=votes&tagged={tag}&site=stackoverflow"
        
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for question in data.get("items", [])[:10]:
                    artifact = {
                        "source_type": "stackoverflow_unsolved",
                        "question_id": question.get("question_id"),
                        "title": question.get("title"),
                        "tags": question.get("tags"),
                        "score": question.get("score"),
                        "url": question.get("link"),
                        "collected_at": datetime.utcnow().isoformat()
                    }
                    artifacts.append(artifact)
        
        except Exception as e:
            print(f"Error collecting from Stack Overflow: {e}")
        
        return artifacts
    
    def collect_reddit_war_stories(self, subreddit: str = "MachineLearning") -> List[Dict]:
        """
        Collect Reddit posts about failures, disasters, and lessons learned.
        Practitioners are honest about failures in informal settings.
        """
        artifacts = []
        
        # Reddit API (public JSON endpoint, no auth)
        url = f"https://www.reddit.com/r/{subreddit}/search.json?q=failed+OR+disaster+OR+mistake&restrict_sr=1&limit=10"
        
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for post in data.get("data", {}).get("children", []):
                    post_data = post.get("data", {})
                    artifact = {
                        "source_type": "reddit_war_story",
                        "title": post_data.get("title"),
                        "author": post_data.get("author"),
                        "score": post_data.get("score"),
                        "num_comments": post_data.get("num_comments"),
                        "url": f"https://reddit.com{post_data.get('permalink')}",
                        "collected_at": datetime.utcnow().isoformat()
                    }
                    artifacts.append(artifact)
        
        except Exception as e:
            print(f"Error collecting from Reddit: {e}")
        
        return artifacts
    
    def collect_all(self, domains: List[str]) -> List[Dict]:
        """
        Run all collection methods for given domains.
        """
        all_artifacts = []
        
        for domain in domains:
            print(f"Collecting digital trash for domain: {domain}")
            
            # Collect from multiple sources
            all_artifacts.extend(self.collect_arxiv_failures([domain]))
            all_artifacts.extend(self.collect_github_abandoned_repos(domain))
            all_artifacts.extend(self.collect_stackoverflow_edge_cases(domain))
        
        # Also collect general war stories
        all_artifacts.extend(self.collect_reddit_war_stories())
        
        return all_artifacts


class MoleculeSorter:
    """
    Sorts collected "trash" to extract valuable molecules of knowledge.
    Separates signal from noise using pattern recognition.
    """
    
    def __init__(self):
        # Patterns that indicate valuable knowledge
        self.valuable_patterns = [
            # Failure patterns
            r"did not work because",
            r"failed due to",
            r"limitation of",
            r"edge case",
            r"unexpected behavior",
            
            # Insight patterns
            r"learned that",
            r"discovered that",
            r"turns out",
            r"actually",
            
            # Caution patterns
            r"be careful",
            r"watch out for",
            r"gotcha",
            r"pitfall"
        ]
    
    def sort_artifact(self, artifact: Dict) -> Optional[KnowledgeArtifact]:
        """
        Sort a single artifact to extract valuable knowledge.
        Returns None if artifact contains no valuable signal.
        """
        # Calculate relevance score
        relevance = self._calculate_relevance(artifact)
        
        if relevance < 0.3:  # Threshold for "trash"
            return None
        
        # Extract insights
        insights = self._extract_insights(artifact)
        failure_patterns = self._extract_failure_patterns(artifact)
        edge_cases = self._extract_edge_cases(artifact)
        
        # Generate artifact ID
        content_str = json.dumps(artifact, sort_keys=True)
        artifact_id = hashlib.sha256(content_str.encode()).hexdigest()[:16]
        
        # Create knowledge artifact
        knowledge = KnowledgeArtifact(
            artifact_id=artifact_id,
            source_type=artifact.get("source_type", "unknown"),
            source_url=artifact.get("url", ""),
            title=artifact.get("title", "Untitled"),
            content=str(artifact),
            extracted_insights=insights,
            failure_patterns=failure_patterns,
            edge_cases=edge_cases,
            confidence=self._calculate_confidence(artifact),
            relevance_score=relevance,
            collected_at=artifact.get("collected_at", datetime.utcnow().isoformat()),
            tags=self._extract_tags(artifact)
        )
        
        return knowledge
    
    def _calculate_relevance(self, artifact: Dict) -> float:
        """
        Calculate relevance score (0.0-1.0) based on:
        - Source credibility
        - Content quality indicators
        - Community engagement
        """
        score = 0.5  # Base score
        
        # Source type weighting
        source_weights = {
            "arxiv_paper": 0.9,
            "github_abandoned": 0.7,
            "stackoverflow_unsolved": 0.8,
            "reddit_war_story": 0.6
        }
        source_type = artifact.get("source_type", "unknown")
        score *= source_weights.get(source_type, 0.5)
        
        # Engagement indicators
        if "score" in artifact and artifact["score"] > 10:
            score += 0.2
        
        if "stars" in artifact and artifact["stars"] > 50:
            score += 0.2
        
        return min(score, 1.0)
    
    def _extract_insights(self, artifact: Dict) -> List[str]:
        """Extract actionable insights from artifact"""
        insights = []
        
        # Simple pattern matching (in production, use NLP)
        content = str(artifact).lower()
        
        if "learned" in content or "discovered" in content:
            insights.append("Contains learning experience")
        
        if "solution" in content or "workaround" in content:
            insights.append("Contains solution or workaround")
        
        return insights
    
    def _extract_failure_patterns(self, artifact: Dict) -> List[str]:
        """Extract failure patterns from artifact"""
        patterns = []
        
        content = str(artifact).lower()
        
        if "failed" in content or "did not work" in content:
            patterns.append("Documented failure")
        
        if "limitation" in content:
            patterns.append("Known limitation")
        
        return patterns
    
    def _extract_edge_cases(self, artifact: Dict) -> List[str]:
        """Extract edge cases from artifact"""
        edge_cases = []
        
        content = str(artifact).lower()
        
        if "edge case" in content or "corner case" in content:
            edge_cases.append("Explicit edge case mention")
        
        if "unexpected" in content or "surprising" in content:
            edge_cases.append("Unexpected behavior documented")
        
        return edge_cases
    
    def _calculate_confidence(self, artifact: Dict) -> float:
        """Calculate confidence in extracted knowledge"""
        confidence = 0.5
        
        # Higher confidence for academic sources
        if artifact.get("source_type") == "arxiv_paper":
            confidence += 0.3
        
        # Higher confidence for well-documented issues
        if artifact.get("num_comments", 0) > 5:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _extract_tags(self, artifact: Dict) -> List[str]:
        """Extract relevant tags from artifact"""
        tags = [artifact.get("source_type", "unknown")]
        
        # Add domain tags if present
        if "tags" in artifact:
            tags.extend(artifact["tags"][:5])  # Limit to 5 tags
        
        return tags
    
    def sort_batch(self, artifacts: List[Dict]) -> List[KnowledgeArtifact]:
        """Sort a batch of artifacts"""
        sorted_artifacts = []
        
        for artifact in artifacts:
            knowledge = self.sort_artifact(artifact)
            if knowledge:
                sorted_artifacts.append(knowledge)
        
        # Sort by relevance
        sorted_artifacts.sort(key=lambda k: k.relevance_score, reverse=True)
        
        return sorted_artifacts


class ScavengerIntelligenceSystem:
    """
    Complete intelligence gathering system.
    Collects digital trash, sorts molecules, feeds into Phoenix Cycle.
    """
    
    def __init__(self, collection_path: Path, memory_path: Path):
        self.collector = DigitalTrashCollector(collection_path)
        self.sorter = MoleculeSorter()
        self.memory_path = memory_path
        self.memory_path.mkdir(parents=True, exist_ok=True)
    
    def gather_intelligence(self, domains: List[str]) -> Dict[str, Any]:
        """
        Main intelligence gathering pipeline:
        1. Collect digital trash
        2. Sort molecules
        3. Store valuable knowledge
        4. Generate intelligence report
        """
        print(f"[Scavenger] Gathering intelligence for domains: {domains}")
        
        # Step 1: Collect
        raw_artifacts = self.collector.collect_all(domains)
        print(f"[Scavenger] Collected {len(raw_artifacts)} raw artifacts")
        
        # Step 2: Sort
        knowledge_artifacts = self.sorter.sort_batch(raw_artifacts)
        print(f"[Scavenger] Sorted to {len(knowledge_artifacts)} valuable artifacts")
        
        # Step 3: Store
        for artifact in knowledge_artifacts:
            self._store_artifact(artifact)
        
        # Step 4: Generate report
        report = self._generate_intelligence_report(knowledge_artifacts)
        
        return report
    
    def _store_artifact(self, artifact: KnowledgeArtifact):
        """Store artifact to memory"""
        file_path = self.memory_path / f"{artifact.artifact_id}.json"
        
        with open(file_path, 'w') as f:
            json.dump(asdict(artifact), f, indent=2)
    
    def _generate_intelligence_report(self, artifacts: List[KnowledgeArtifact]) -> Dict[str, Any]:
        """Generate intelligence report from artifacts"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_artifacts": len(artifacts),
            "by_source": {},
            "top_insights": [],
            "failure_patterns": [],
            "edge_cases": [],
            "avg_confidence": 0.0,
            "avg_relevance": 0.0
        }
        
        if not artifacts:
            return report
        
        # Count by source
        for artifact in artifacts:
            source = artifact.source_type
            report["by_source"][source] = report["by_source"].get(source, 0) + 1
        
        # Top insights (highest relevance)
        top_artifacts = sorted(artifacts, key=lambda a: a.relevance_score, reverse=True)[:5]
        report["top_insights"] = [
            {
                "title": a.title,
                "source": a.source_type,
                "relevance": a.relevance_score,
                "url": a.source_url
            }
            for a in top_artifacts
        ]
        
        # Aggregate failure patterns
        all_failures = []
        for artifact in artifacts:
            all_failures.extend(artifact.failure_patterns)
        report["failure_patterns"] = list(set(all_failures))
        
        # Aggregate edge cases
        all_edge_cases = []
        for artifact in artifacts:
            all_edge_cases.extend(artifact.edge_cases)
        report["edge_cases"] = list(set(all_edge_cases))
        
        # Averages
        report["avg_confidence"] = sum(a.confidence for a in artifacts) / len(artifacts)
        report["avg_relevance"] = sum(a.relevance_score for a in artifacts) / len(artifacts)
        
        return report


# Example usage
def main():
    collection_path = Path("/home/ubuntu/Echo-AI-University/intelligence/raw")
    memory_path = Path("/home/ubuntu/Echo-AI-University/intelligence/knowledge")
    
    system = ScavengerIntelligenceSystem(collection_path, memory_path)
    
    # Gather intelligence on AI training domains
    domains = [
        "reinforcement learning",
        "agent training",
        "chaos engineering",
        "fault injection"
    ]
    
    report = system.gather_intelligence(domains)
    
    print("\n=== INTELLIGENCE REPORT ===")
    print(f"Total Artifacts: {report['total_artifacts']}")
    print(f"Average Confidence: {report['avg_confidence']:.2f}")
    print(f"Average Relevance: {report['avg_relevance']:.2f}")
    print(f"\nBy Source:")
    for source, count in report['by_source'].items():
        print(f"  {source}: {count}")
    print(f"\nTop Insights:")
    for insight in report['top_insights']:
        print(f"  - {insight['title']} ({insight['source']}, relevance: {insight['relevance']:.2f})")


if __name__ == "__main__":
    main()
