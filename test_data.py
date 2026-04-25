"""Test data for testing all possible PR scenarios."""

TEST_PR_CASES = [
    {
        "name": "improvements_only",
        "data": {
            "repo": "test-repo",
            "branch": "feat/new-feature",
            "title": "feat: Add new user authentication system",
            "description": "### PR Description\n\n## Summary\nThis PR adds OAuth2 authentication support for users to log in with Google and GitHub accounts.\n\n## Changes Made\n- Added OAuth2 integration with Google and GitHub\n- Updated user session management\n- Added login/logout endpoints\n- Updated UI with new login buttons",
            "commits": [
                "Add OAuth2 configuration",
                "Implement Google OAuth flow",
                "Implement GitHub OAuth flow",
                "Update session management",
                "Add login/logout endpoints",
                "Update UI with login buttons"
            ],
            "pr_number": 1
        }
    },
    {
        "name": "bug_fixes_only",
        "data": {
            "repo": "test-repo",
            "branch": "fix/crash-bug",
            "title": "fix: Fix crash when processing empty data",
            "description": "### PR Description\n\n## Summary\nThis PR fixes a crash that occurred when the system received empty data payloads.\n\n## Changes Made\n- Added null check before processing data\n- Added error handling for empty arrays\n- Added unit tests for edge cases",
            "commits": [
                "Add null check for data processing",
                "Add error handling for empty arrays",
                "Add unit tests for edge cases"
            ],
            "pr_number": 2
        }
    },
    {
        "name": "mixed_categories",
        "data": {
            "repo": "test-repo",
            "branch": "feature/update",
            "title": "feat: Update API and fix bugs",
            "description": "### PR Description\n\n## Summary\nThis PR updates the API to version 2.0 and fixes several bugs in the data processing pipeline.\n\n## Changes Made\n- Updated API endpoints to v2\n- Fixed memory leak in data processing\n- Added rate limiting\n- Improved error messages",
            "commits": [
                "Update API to v2",
                "Fix memory leak",
                "Add rate limiting",
                "Improve error messages"
            ],
            "pr_number": 3
        }
    },
    {
        "name": "wip_only",
        "data": {
            "repo": "test-repo",
            "branch": "wip/new-dashboard",
            "title": "wip: Implement new admin dashboard",
            "description": "### PR Description\n\n## Summary\nWork in progress on the new admin dashboard.\n\n## Changes Made\n- Started dashboard layout\n- Added user management section\n- TODO: Add analytics section\n- TODO: Add settings page",
            "commits": [
                "Start dashboard layout",
                "Add user management section"
            ],
            "pr_number": 4
        }
    },
    {
        "name": "known_issues",
        "data": {
            "repo": "test-repo",
            "branch": "release/v1.0",
            "title": "release: Version 1.0 with known issues",
            "description": "### PR Description\n\n## Summary\nFirst stable release with some known issues documented.\n\n## Known Issues\n- Safari browser has rendering issues with dark mode\n- Mobile view needs optimization\n- Performance degradation with large datasets",
            "commits": [
                "Prepare v1.0 release",
                "Document known issues"
            ],
            "pr_number": 5
        }
    },
    {
        "name": "empty_description",
        "data": {
            "repo": "test-repo",
            "branch": "fix/quick-fix",
            "title": "fix: Quick fix for typo",
            "description": "",
            "commits": [
                "Fix typo in error message"
            ],
            "pr_number": 6
        }
    },
    {
        "name": "long_description",
        "data": {
            "repo": "test-repo",
            "branch": "feature/complex",
            "title": "feat: Complex feature with extensive documentation",
            "description": "### PR Description\n\n## Summary\nThis is a complex feature that requires extensive documentation.\n\n## Background\nThe system needed to handle complex data transformations with multiple edge cases. This PR implements a new pipeline that processes data in stages.\n\n## Technical Details\n\n### Stage 1: Data Ingestion\n- Validates input data schema\n- Handles missing fields gracefully\n- Converts data types as needed\n\n### Stage 2: Transformation\n- Applies business logic rules\n- Handles conditional transformations\n- Maintains data integrity\n\n### Stage 3: Output Generation\n- Formats output according to specifications\n- Validates output schema\n- Handles large datasets efficiently\n\n## Performance\n- Processing time reduced by 40%\n- Memory usage optimized\n- Added caching for repeated operations\n\n## Testing\n- Added 50+ unit tests\n- Integration tests for all stages\n- Performance benchmarks",
            "commits": [
                "Implement data ingestion stage",
                "Implement transformation stage",
                "Implement output generation stage",
                "Add comprehensive tests",
                "Optimize performance"
            ],
            "pr_number": 7
        }
    },
    {
        "name": "all_categories",
        "data": {
            "repo": "test-repo",
            "branch": "feature/comprehensive",
            "title": "feat: Comprehensive update with improvements, fixes, and known issues",
            "description": "### PR Description\n\n## Summary\nMajor update with multiple categories of changes.\n\n## Improvements\n- Faster data processing\n- Better error messages\n- Improved UI responsiveness\n\n## Bug Fixes\n- Fixed crash on empty input\n- Fixed memory leak\n- Fixed race condition\n\n## Work in Progress\n- Dashboard redesign (partial)\n- Analytics integration (in progress)\n\n## Known Issues\n- Safari rendering issues\n- Mobile view needs work",
            "commits": [
                "Improve data processing speed",
                "Fix crash on empty input",
                "Start dashboard redesign"
            ],
            "pr_number": 8
        }
    }
]
