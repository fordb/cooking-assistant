"""
Results tracking and display for recipe evaluations.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from statistics import mean, stdev
from evaluations.evaluator import RecipeEvaluation
from src.config import get_logger

logger = get_logger(__name__)


class EvaluationResults:
    """Manages evaluation results storage and analysis."""
    
    def __init__(self, results_file: str = "evaluation_results.json"):
        self.results_file = results_file
        self.results_dir = "evaluations/results"
        os.makedirs(self.results_dir, exist_ok=True)
        self.results_path = os.path.join(self.results_dir, results_file)
    
    def save_results(self, evaluations: List[RecipeEvaluation], metadata: Dict[str, Any] = None) -> str:
        """Save evaluation results to JSON file with timestamp."""
        timestamp = datetime.now().isoformat()
        
        # Convert evaluations to serializable format
        serializable_results = []
        for eval_result in evaluations:
            result_data = {
                "test_case": eval_result.test_case,
                "template_type": eval_result.template_type,
                "recipe": eval_result.recipe.model_dump() if eval_result.recipe else None,
                "scores": [
                    {
                        "metric": score.metric,
                        "score": score.score,
                        "reasoning": score.reasoning
                    }
                    for score in eval_result.scores
                ],
                "performance_metrics": eval_result.performance_metrics,
                "error": eval_result.error,
                "average_score": eval_result.average_score
            }
            serializable_results.append(result_data)
        
        # Create results record
        results_record = {
            "timestamp": timestamp,
            "metadata": metadata or {},
            "summary": self._generate_summary(evaluations),
            "results": serializable_results
        }
        
        # Load existing results if file exists
        all_results = []
        if os.path.exists(self.results_path):
            try:
                with open(self.results_path, 'r') as f:
                    all_results = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                all_results = []
        
        # Add new results
        all_results.append(results_record)
        
        # Save updated results
        with open(self.results_path, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        return timestamp
    
    def _generate_summary(self, evaluations: List[RecipeEvaluation]) -> Dict[str, Any]:
        """Generate summary statistics from evaluations."""
        successful_evals = [e for e in evaluations if e.recipe is not None]
        failed_evals = [e for e in evaluations if e.recipe is None]
        
        if not successful_evals:
            return {
                "total_cases": len(evaluations),
                "successful": 0,
                "failed": len(failed_evals),
                "success_rate": 0.0
            }
        
        # Calculate score statistics
        all_scores = [eval_result.average_score for eval_result in successful_evals]
        
        # Performance statistics
        generation_times = [e.performance_metrics.get("generation_time", 0) for e in successful_evals]
        total_times = [e.performance_metrics.get("total_time", 0) for e in successful_evals]
        
        # Score breakdown by metric
        metric_scores = {}
        for eval_result in successful_evals:
            for score in eval_result.scores:
                if score.metric not in metric_scores:
                    metric_scores[score.metric] = []
                metric_scores[score.metric].append(score.score)
        
        metric_averages = {
            metric: mean(scores) for metric, scores in metric_scores.items()
        }
        
        return {
            "total_cases": len(evaluations),
            "successful": len(successful_evals),
            "failed": len(failed_evals),
            "success_rate": len(successful_evals) / len(evaluations),
            "overall_average_score": mean(all_scores) if all_scores else 0,
            "score_std_dev": stdev(all_scores) if len(all_scores) > 1 else 0,
            "metric_averages": metric_averages,
            "avg_generation_time": mean(generation_times) if generation_times else 0,
            "avg_total_time": mean(total_times) if total_times else 0,
            "template_type_breakdown": self._template_breakdown(successful_evals)
        }
    
    def _template_breakdown(self, evaluations: List[RecipeEvaluation]) -> Dict[str, Dict[str, float]]:
        """Break down scores by template type."""
        template_scores = {}
        
        for eval_result in evaluations:
            template = eval_result.template_type
            if template not in template_scores:
                template_scores[template] = []
            template_scores[template].append(eval_result.average_score)
        
        return {
            template: {
                "count": len(scores),
                "average": mean(scores),
                "std_dev": stdev(scores) if len(scores) > 1 else 0
            }
            for template, scores in template_scores.items()
        }
    
    def display_results(self, evaluations: List[RecipeEvaluation]):
        """Display evaluation results in a readable format."""
        logger.info(f"Displaying evaluation results for {len(evaluations)} evaluations")
        print("\n🧑‍🍳 Recipe Evaluation Results")
        print("=" * 50)
        
        # Summary statistics
        summary = self._generate_summary(evaluations)
        
        print(f"\n📊 SUMMARY")
        print(f"Total test cases: {summary['total_cases']}")
        print(f"Successful generations: {summary['successful']}")
        print(f"Failed generations: {summary['failed']}")
        print(f"Success rate: {summary['success_rate']:.1%}")
        
        if summary['successful'] > 0:
            print(f"Overall average score: {summary['overall_average_score']:.2f}/5.0")
            print(f"Score standard deviation: {summary['score_std_dev']:.2f}")
            print(f"Average generation time: {summary['avg_generation_time']:.2f}s")
        
        # Metric breakdown
        if summary.get('metric_averages'):
            print(f"\n📈 SCORE BREAKDOWN BY METRIC")
            for metric, avg_score in summary['metric_averages'].items():
                print(f"{metric}: {avg_score:.2f}/5.0")
        
        # Template type breakdown
        if summary.get('template_type_breakdown'):
            print(f"\n🏷️ TEMPLATE TYPE BREAKDOWN")
            for template, stats in summary['template_type_breakdown'].items():
                print(f"{template}: {stats['average']:.2f}/5.0 (n={stats['count']})")
        
        # Detailed results for failed cases
        failed_cases = [e for e in evaluations if e.recipe is None]
        if failed_cases:
            print(f"\n❌ FAILED CASES ({len(failed_cases)})")
            for failed in failed_cases:
                print(f"  • {failed.test_case} [{failed.template_type}]: {failed.error}")
        
        # Show top and bottom performers
        successful_evals = [e for e in evaluations if e.recipe is not None]
        if len(successful_evals) >= 2:
            sorted_evals = sorted(successful_evals, key=lambda x: x.average_score, reverse=True)
            
            print(f"\n🏆 TOP PERFORMERS")
            for eval_result in sorted_evals[:3]:
                print(f"  • {eval_result.test_case} [{eval_result.template_type}]: {eval_result.average_score:.2f}/5.0")
            
            print(f"\n🔄 NEEDS IMPROVEMENT")
            for eval_result in sorted_evals[-3:]:
                print(f"  • {eval_result.test_case} [{eval_result.template_type}]: {eval_result.average_score:.2f}/5.0")
    
    def compare_runs(self, run1_timestamp: str, run2_timestamp: str):
        """Compare results between two evaluation runs."""
        if not os.path.exists(self.results_path):
            print("No results file found.")
            logger.warning(f"Results file not found: {self.results_path}")
            return
        
        with open(self.results_path, 'r') as f:
            all_results = json.load(f)
        
        # Find the specified runs
        run1 = next((r for r in all_results if r['timestamp'] == run1_timestamp), None)
        run2 = next((r for r in all_results if r['timestamp'] == run2_timestamp), None)
        
        if not run1 or not run2:
            print("One or both specified runs not found.")
            return
        
        print(f"\n🔄 COMPARING EVALUATION RUNS")
        print("=" * 50)
        print(f"Run 1: {run1['timestamp'][:19]}")
        print(f"Run 2: {run2['timestamp'][:19]}")
        
        # Compare summaries
        s1, s2 = run1['summary'], run2['summary']
        
        print(f"\n📈 COMPARISON")
        print(f"Success rate: {s1['success_rate']:.1%} → {s2['success_rate']:.1%} ({s2['success_rate'] - s1['success_rate']:+.1%})")
        
        if s1['successful'] > 0 and s2['successful'] > 0:
            score_change = s2['overall_average_score'] - s1['overall_average_score']
            time_change = s2['avg_generation_time'] - s1['avg_generation_time']
            
            print(f"Average score: {s1['overall_average_score']:.2f} → {s2['overall_average_score']:.2f} ({score_change:+.2f})")
            print(f"Generation time: {s1['avg_generation_time']:.2f}s → {s2['avg_generation_time']:.2f}s ({time_change:+.2f}s)")
    
    def list_runs(self):
        """List all available evaluation runs."""
        if not os.path.exists(self.results_path):
            print("No results file found.")
            logger.warning(f"Results file not found: {self.results_path}")
            return
        
        with open(self.results_path, 'r') as f:
            all_results = json.load(f)
        
        print(f"\n📋 EVALUATION RUNS ({len(all_results)} total)")
        print("=" * 50)
        
        for i, run in enumerate(all_results, 1):
            summary = run['summary']
            timestamp = run['timestamp'][:19]  # Remove microseconds
            
            print(f"{i}. {timestamp}")
            print(f"   Cases: {summary['total_cases']} | Success: {summary['success_rate']:.1%} | Avg Score: {summary.get('overall_average_score', 0):.2f}/5.0")