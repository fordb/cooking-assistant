"""
Main evaluation runner script.

Usage:
    python -m evaluations.run_eval                    # Run all test cases
    python -m evaluations.run_eval --category basic   # Run specific category
    python -m evaluations.run_eval --sample 10        # Run random sample
    python -m evaluations.run_eval --list-runs        # List previous runs
    python -m evaluations.run_eval --compare run1 run2 # Compare two runs
"""

import argparse
import random
from evaluations.evaluator import RecipeEvaluator
from evaluations.test_cases import get_test_cases, get_test_case_summary
from evaluations.results import EvaluationResults
from src.common.config import get_logger

logger = get_logger(__name__)


def run_evaluation(category: str = "all", sample_size: int = None, judge_model: str = "gpt-3.5-turbo"):
    """Run recipe evaluation on specified test cases."""
    
    print(f"🧑‍🍳 Starting Recipe Evaluation")
    print("=" * 50)
    
    logger.info(f"Starting recipe evaluation - category: {category}, judge_model: {judge_model}")
    
    # Get test cases
    test_cases = get_test_cases(category)
    
    # Sample if requested
    if sample_size and sample_size < len(test_cases):
        test_cases = random.sample(test_cases, sample_size)
        print(f"Running on random sample of {sample_size} cases")
        logger.info(f"Sampling {sample_size} cases from {len(test_cases)} available")
    
    print(f"Test cases: {len(test_cases)}")
    print(f"Judge model: {judge_model}")
    
    # Initialize evaluator and results tracker
    evaluator = RecipeEvaluator(judge_model=judge_model)
    results_tracker = EvaluationResults()
    
    # Run evaluation
    print(f"\n🔄 Running Evaluations...")
    logger.info(f"Beginning evaluation of {len(test_cases)} test cases")
    evaluations = evaluator.batch_evaluate(test_cases)
    
    # Save and display results
    metadata = {
        "category": category,
        "sample_size": sample_size,
        "judge_model": judge_model,
        "total_test_cases": len(test_cases)
    }
    
    timestamp = results_tracker.save_results(evaluations, metadata)
    results_tracker.display_results(evaluations)
    
    print(f"\n💾 Results saved with timestamp: {timestamp}")
    logger.info(f"Evaluation completed, results saved with timestamp: {timestamp}")
    return evaluations


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Recipe Generation Evaluation")
    
    parser.add_argument("--category", 
                       choices=["all", "basic", "quick", "dietary", "cuisine", "substitution", "edge"],
                       default="all",
                       help="Category of test cases to run")
    
    parser.add_argument("--sample", 
                       type=int,
                       help="Run on random sample of N test cases")
    
    parser.add_argument("--judge-model",
                       default="gpt-3.5-turbo",
                       help="Model to use for LLM-as-a-judge evaluation")
    
    parser.add_argument("--list-runs",
                       action="store_true", 
                       help="List all previous evaluation runs")
    
    parser.add_argument("--compare",
                       nargs=2,
                       metavar=("RUN1", "RUN2"),
                       help="Compare two evaluation runs by timestamp")
    
    parser.add_argument("--summary",
                       action="store_true",
                       help="Show test case summary")
    
    args = parser.parse_args()
    
    results_tracker = EvaluationResults()
    
    if args.list_runs:
        results_tracker.list_runs()
        return
    
    if args.compare:
        results_tracker.compare_runs(args.compare[0], args.compare[1])
        return
    
    if args.summary:
        summary = get_test_case_summary()
        print(f"\n📋 Test Case Summary")
        print("=" * 30)
        for category, count in summary.items():
            print(f"{category.capitalize()}: {count}")
        logger.info(f"Test case summary displayed: {dict(summary)}")
        return
    
    # Run evaluation
    run_evaluation(
        category=args.category,
        sample_size=args.sample,
        judge_model=args.judge_model
    )


if __name__ == "__main__":
    main()