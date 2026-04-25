"""Test runner for testing all possible PR scenarios."""

import os
import sys
import logging
import argparse
from datetime import datetime
from test_data import TEST_PR_CASES

# Add current directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import generate_ai_summary, send_to_discord, generate_gemini_summary, generate_groq_summary
from config import AI_MODELS
from github import Github, Auth

# Set up logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

date_prefix = datetime.now().strftime("%Y%m%d")
log_file = os.path.join(log_dir, f"{date_prefix}_test.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="w", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_real_prs(repo_name, limit=10):
    """Fetch real PRs from a GitHub repository."""
    import main as main_module
    gh = Github(auth=Auth.Token(main_module.GITHUB_TOKEN))
    
    try:
        repo = gh.get_repo(repo_name)
        pulls = repo.get_pulls(state="closed")[:limit]
        
        pr_data_list = []
        for pr in pulls:
            commits = [c.commit.message for c in pr.get_commits()]
            pr_data = {
                "repo": repo_name.split('/')[-1],
                "branch": pr.head.ref,
                "title": pr.title,
                "description": pr.body or "No description provided.",
                "commits": commits,
                "pr_number": pr.number
            }
            pr_data_list.append({
                "name": f"PR #{pr.number}: {pr.title[:50]}",
                "data": pr_data
            })
        
        return pr_data_list
    except Exception as e:
        logging.error(f"Failed to fetch PRs from {repo_name}: {e}")
        return []

def run_test_case(test_case, specific_model=None, lang="sv"):
    """Run a single test case."""
    name = test_case["name"]
    data = test_case["data"]
    
    logging.info('\n' + '='*60)
    logging.info(f"Running test case: {name}")
    logging.info('='*60)
    logging.info(f"PR Title: {data['title']}")
    logging.info(f"PR Description: {data['description'][:100]}...")
    logging.info(f"Commits: {len(data['commits'])}")
    logging.info(f"Language: {lang}")
    
    try:
        # Test AI summary generation
        logging.info("Testing AI summary generation...")
        
        if specific_model:
            logging.info(f"Testing specific model: {specific_model} ({AI_MODELS[specific_model]})")
            if specific_model.startswith("gemini"):
                ai_summary = generate_gemini_summary(data, lang, specific_model)
            elif specific_model.startswith("groq"):
                ai_summary = generate_groq_summary(data, lang, specific_model)
            else:
                raise ValueError(f"Unknown model: {specific_model}")
        else:
            ai_summary = generate_ai_summary(data, lang)
        
        ai_data, ai_model = ai_summary
        
        logging.info(f"AI Model used: {ai_model}")
        logging.info("Categories generated:")
        for key, items in ai_data.items():
            if items:
                logging.info(f"  - {key}: {len(items)} items")
                for item in items:
                    logging.info(f"    • {item}")
        
        # Send Discord webhook
        logging.info("Sending Discord webhook...")
        send_to_discord(ai_data, data['repo'], lang, ai_model)
        
        logging.info(f"✅ Test case '{name}' PASSED")
        return True
        
    except Exception as e:
        logging.error(f"❌ Test case '{name}' FAILED: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False

def run_all_tests(specific_model=None, test_cases=None, lang="sv"):
    """Run all test cases."""
    if test_cases is None:
        test_cases = TEST_PR_CASES
    
    logging.info("Starting comprehensive test suite...")
    logging.info(f"Total test cases: {len(test_cases)}")
    logging.info(f"Language: {lang}")
    if specific_model:
        logging.info(f"Testing specific model: {specific_model} ({AI_MODELS[specific_model]})")
    
    results = []
    for test_case in test_cases:
        success = run_test_case(test_case, specific_model, lang)
        results.append((test_case["name"], success))
    
    # Summary
    logging.info('\n' + '='*60)
    logging.info("TEST SUMMARY")
    logging.info('='*60)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logging.info(f"{name}: {status}")
    
    logging.info(f"\nTotal: {len(results)}")
    logging.info(f"Passed: {passed}")
    logging.info(f"Failed: {failed}")
    
    if failed > 0:
        logging.error("Some tests failed!")
        sys.exit(1)
    else:
        logging.info("All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run comprehensive test suite for Discord changelog notifier")
    parser.add_argument("--model", type=str, choices=list(AI_MODELS.keys()), help="Test specific AI model (e.g., groq_1, gemini_2)")
    parser.add_argument("--test-all-models", action="store_true", help="Test all 6 AI models with all test cases")
    parser.add_argument("--repo", type=str, help="Test real PRs from a GitHub repository (e.g., username/repo)")
    parser.add_argument("--limit", type=int, default=10, help="Number of PRs to fetch from repository (default: 10)")
    parser.add_argument("--language", type=str, choices=["sv", "en"], default="sv", help="Output language: sv (Swedish) or en (English), default: sv")
    args = parser.parse_args()
    
    # Determine test cases to use
    test_cases = TEST_PR_CASES
    if args.repo:
        logging.info(f"Fetching real PRs from repository: {args.repo}")
        test_cases = get_real_prs(args.repo, args.limit)
        if not test_cases:
            logging.error("No PRs found or failed to fetch. Exiting.")
            sys.exit(1)
    
    if args.test_all_models:
        logging.info("Testing all 6 AI models...")
        for model in AI_MODELS.keys():
            logging.info(f"\n{'#'*60}")
            logging.info(f"Testing model: {model} ({AI_MODELS[model]})")
            logging.info(f"{'#'*60}")
            run_all_tests(specific_model=model, test_cases=test_cases, lang=args.language)
    else:
        run_all_tests(specific_model=args.model, test_cases=test_cases, lang=args.language)
