"""
Enhanced GitHub Analysis Service.
Performs deep analysis of GitHub profiles to assess:
- Contribution authenticity (who actually wrote the code)
- Code origin (organic vs AI-generated vs copied)
- Project classification (personal vs class vs fork)
- Activity patterns and consistency
"""
import httpx
import logging
import re
from typing import Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
import uuid

from ..config import settings

logger = logging.getLogger("pathway.github_analysis")


# ==================== DATA CLASSES ====================

@dataclass
class CommitAnalysis:
    """Analysis of commits for a specific user in a repo."""
    user_commits: int = 0
    total_commits: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    first_commit_date: Optional[str] = None
    last_commit_date: Optional[str] = None
    avg_files_per_commit: float = 0.0
    max_files_in_commit: int = 0
    commit_messages: list[str] = field(default_factory=list)


@dataclass
class CollaboratorInfo:
    """Information about collaborators on a repo."""
    username: str
    commits: int
    lines_added: int
    is_primary: bool = False


@dataclass
class CodeOriginSignals:
    """Signals indicating code origin/authenticity."""
    # AI Generation Signals
    bulk_initial_commit: bool = False      # Many files in first commit
    perfect_structure: bool = False        # Too-perfect file organization
    generic_commit_messages: bool = False  # "Initial commit", "Update", etc.
    no_iterative_fixes: bool = False       # No bug fixes or iterations
    verbose_comments: bool = False         # Overly explanatory comments

    # Template Signals
    has_template_files: bool = False       # TEMPLATE.md, boilerplate markers
    common_starter_structure: bool = False # create-react-app, etc.

    # Plagiarism Signals
    suspicious_timeline: bool = False      # Too fast development
    mismatched_skill_level: bool = False   # Simple readme, complex code

    def get_origin_classification(self) -> tuple[str, float]:
        """Return (classification, confidence) based on signals."""
        ai_signals = sum([
            self.bulk_initial_commit,
            self.perfect_structure,
            self.generic_commit_messages,
            self.no_iterative_fixes,
        ])

        if ai_signals >= 3:
            return ("ai_heavy", 0.8)
        elif ai_signals >= 2:
            return ("ai_assisted", 0.6)
        elif self.has_template_files or self.common_starter_structure:
            return ("template", 0.7)
        else:
            return ("organic", 0.7 + (0.1 * (4 - ai_signals)))


@dataclass
class ProjectClassification:
    """Classification of project type."""
    project_type: str = "unknown"  # personal, class, hackathon, tutorial, fork, organization
    confidence: float = 0.5
    indicators: list[str] = field(default_factory=list)


@dataclass
class RepoAnalysis:
    """Complete analysis of a single repository."""
    repo_name: str
    repo_url: str
    is_fork: bool = False
    is_private: bool = False

    # Classification
    project_type: str = "unknown"
    code_origin: str = "organic"
    classification_confidence: float = 0.5

    # Contribution stats
    user_commits: int = 0
    total_commits: int = 0
    contribution_ratio: float = 0.0
    lines_added: int = 0
    lines_removed: int = 0

    # Collaborators
    collaborators: list[str] = field(default_factory=list)
    user_is_primary_author: bool = True

    # Languages
    languages: dict[str, int] = field(default_factory=dict)
    primary_language: Optional[str] = None

    # Timeline
    first_commit_date: Optional[str] = None
    last_commit_date: Optional[str] = None
    development_span_days: int = 0
    commit_frequency: str = "unknown"  # sporadic, regular, burst

    # Quality indicators
    has_readme: bool = False
    readme_quality: str = "none"  # none, minimal, good, excellent
    has_tests: bool = False
    has_ci: bool = False

    # Signals for review
    signals: dict = field(default_factory=dict)

    # Score contribution
    originality_score: float = 0.0
    depth_score: float = 0.0
    activity_score: float = 0.0


@dataclass
class GitHubProfileAnalysis:
    """Complete analysis of a user's GitHub profile."""
    username: str

    # Overall scores (0-100)
    overall_score: float = 0.0
    originality_score: float = 0.0
    activity_score: float = 0.0
    depth_score: float = 0.0
    collaboration_score: float = 0.0

    # Aggregates
    total_repos_analyzed: int = 0
    total_commits_by_user: int = 0
    total_lines_added: int = 0
    total_lines_removed: int = 0
    total_prs_opened: int = 0

    # Patterns
    avg_commits_per_week: float = 0.0
    active_months_last_year: int = 0

    # Languages
    primary_languages: list[dict] = field(default_factory=list)

    # Classification counts
    personal_projects_count: int = 0
    class_projects_count: int = 0
    fork_contributions_count: int = 0

    # Code origin
    organic_code_ratio: float = 0.0
    ai_assisted_repos: int = 0

    # Quality
    has_tests: bool = False
    has_ci_cd: bool = False
    has_documentation: bool = False

    # Flags
    flags: list[dict] = field(default_factory=list)
    requires_review: bool = False

    # Detailed analyses
    repo_analyses: list[dict] = field(default_factory=list)


# ==================== DETECTION PATTERNS ====================

# Patterns indicating class projects
CLASS_PROJECT_PATTERNS = [
    r'assignment', r'homework', r'hw[0-9]', r'lab[0-9]', r'project[0-9]',
    r'cs[0-9]{2,3}', r'cse[0-9]{2,3}', r'eecs[0-9]{2,3}', r'cis[0-9]{2,3}',
    r'cmsc[0-9]{2,3}', r'comp[0-9]{2,3}', r'cpsc[0-9]{2,3}',
    r'midterm', r'final[-_]project', r'course[-_]project',
]

# Patterns indicating tutorials/learning projects
TUTORIAL_PATTERNS = [
    r'tutorial', r'learn[-_]', r'practice', r'example',
    r'todo[-_]?mvc', r'hello[-_]?world', r'getting[-_]started',
    r'my[-_]first', r'sample[-_]', r'demo[-_]',
]

# Files indicating template usage
TEMPLATE_INDICATORS = [
    'TEMPLATE.md', '.template', 'boilerplate',
    'create-react-app', 'vue-cli', 'angular-cli',
    'cookiecutter', 'yeoman',
]

# Generic commit messages (often AI-generated or low-effort)
GENERIC_COMMIT_PATTERNS = [
    r'^initial commit$', r'^first commit$', r'^init$',
    r'^update$', r'^fix$', r'^update readme$',
    r'^add files$', r'^add code$', r'^changes$',
    r'^wip$', r'^work in progress$', r'^minor changes$',
]


class GitHubAnalysisService:
    """
    Service for deep GitHub profile analysis.
    Computes derived metrics without storing raw code.
    """

    API_BASE_URL = "https://api.github.com"

    def __init__(self):
        pass

    async def analyze_profile(
        self,
        access_token: str,
        username: str,
        include_private: bool = True,
        max_repos: int = 20,
    ) -> GitHubProfileAnalysis:
        """
        Perform comprehensive analysis of a GitHub profile.

        Args:
            access_token: OAuth token for API access
            username: GitHub username
            include_private: Whether to analyze private repos (with permission)
            max_repos: Maximum repos to analyze (for rate limiting)

        Returns:
            GitHubProfileAnalysis with all computed metrics
        """
        logger.info(f"Starting GitHub analysis for {username}")

        analysis = GitHubProfileAnalysis(username=username)

        try:
            # Get repos
            repos = await self._get_user_repos(access_token, max_repos, include_private)
            analysis.total_repos_analyzed = len(repos)

            # Analyze each repo
            repo_analyses = []
            for repo in repos:
                try:
                    repo_analysis = await self._analyze_repo(access_token, username, repo)
                    repo_analyses.append(repo_analysis)
                except Exception as e:
                    logger.warning(f"Failed to analyze repo {repo['name']}: {e}")
                    continue

            # Aggregate results
            analysis = self._aggregate_analyses(analysis, repo_analyses)

            # Compute final scores
            analysis = self._compute_final_scores(analysis)

            # Check for red flags
            analysis = self._check_flags(analysis, repo_analyses)

            # Store repo analyses
            analysis.repo_analyses = [asdict(r) for r in repo_analyses]

            logger.info(f"Completed GitHub analysis for {username}: score={analysis.overall_score}")

        except Exception as e:
            logger.error(f"GitHub analysis failed for {username}: {e}")
            analysis.flags.append({
                "type": "analysis_error",
                "detail": str(e)
            })

        return analysis

    async def _get_user_repos(
        self,
        access_token: str,
        limit: int,
        include_private: bool
    ) -> list[dict]:
        """Fetch user's repositories."""
        async with httpx.AsyncClient() as client:
            params = {
                "sort": "updated",
                "direction": "desc",
                "per_page": min(limit, 100),
            }
            if not include_private:
                params["visibility"] = "public"

            response = await client.get(
                f"{self.API_BASE_URL}/user/repos",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
                params=params,
            )

            if response.status_code != 200:
                logger.error(f"Failed to fetch repos: {response.text}")
                return []

            return response.json()

    async def _analyze_repo(
        self,
        access_token: str,
        username: str,
        repo: dict
    ) -> RepoAnalysis:
        """Analyze a single repository in depth."""
        analysis = RepoAnalysis(
            repo_name=repo["name"],
            repo_url=repo["html_url"],
            is_fork=repo.get("fork", False),
            is_private=repo.get("private", False),
        )

        full_name = repo["full_name"]

        async with httpx.AsyncClient() as client:
            # Get commit analysis
            commit_analysis = await self._analyze_commits(
                client, access_token, full_name, username
            )
            analysis.user_commits = commit_analysis.user_commits
            analysis.total_commits = commit_analysis.total_commits
            analysis.lines_added = commit_analysis.lines_added
            analysis.lines_removed = commit_analysis.lines_removed
            analysis.first_commit_date = commit_analysis.first_commit_date
            analysis.last_commit_date = commit_analysis.last_commit_date

            if commit_analysis.total_commits > 0:
                analysis.contribution_ratio = commit_analysis.user_commits / commit_analysis.total_commits

            # Get collaborators
            collaborators = await self._get_collaborators(
                client, access_token, full_name, username
            )
            analysis.collaborators = [c.username for c in collaborators if c.username != username]
            analysis.user_is_primary_author = all(
                c.commits <= commit_analysis.user_commits for c in collaborators
            )

            # Get languages
            analysis.languages = await self._get_languages(client, access_token, full_name)
            if analysis.languages:
                analysis.primary_language = max(analysis.languages, key=analysis.languages.get)

            # Check for quality indicators
            analysis.has_readme = await self._check_readme(client, access_token, full_name)
            analysis.has_tests = await self._check_tests(client, access_token, full_name)
            analysis.has_ci = await self._check_ci(client, access_token, full_name)

            # Compute timeline
            if analysis.first_commit_date and analysis.last_commit_date:
                try:
                    first = datetime.fromisoformat(analysis.first_commit_date.replace('Z', '+00:00'))
                    last = datetime.fromisoformat(analysis.last_commit_date.replace('Z', '+00:00'))
                    analysis.development_span_days = (last - first).days
                except:
                    pass

            # Classify project type
            classification = self._classify_project(repo, commit_analysis)
            analysis.project_type = classification.project_type
            analysis.classification_confidence = classification.confidence

            # Detect code origin
            origin_signals = self._detect_code_origin(repo, commit_analysis)
            origin, confidence = origin_signals.get_origin_classification()
            analysis.code_origin = origin
            analysis.signals = {
                "class_indicators": classification.indicators,
                "ai_indicators": self._get_ai_indicators(origin_signals),
            }

            # Compute component scores
            analysis.originality_score = self._compute_originality_score(analysis)
            analysis.depth_score = self._compute_depth_score(analysis, commit_analysis)
            analysis.activity_score = self._compute_activity_score(analysis)

        return analysis

    async def _analyze_commits(
        self,
        client: httpx.AsyncClient,
        access_token: str,
        full_name: str,
        username: str,
    ) -> CommitAnalysis:
        """Analyze commits in a repository."""
        analysis = CommitAnalysis()

        try:
            # Get commit list
            response = await client.get(
                f"{self.API_BASE_URL}/repos/{full_name}/commits",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
                params={"per_page": 100},
            )

            if response.status_code != 200:
                return analysis

            commits = response.json()
            analysis.total_commits = len(commits)

            if not commits:
                return analysis

            # Track user's commits
            user_commits = []
            for commit in commits:
                author = commit.get("author") or {}
                committer = commit.get("committer") or {}

                # Check if this is the user's commit
                if (author.get("login", "").lower() == username.lower() or
                    committer.get("login", "").lower() == username.lower()):
                    user_commits.append(commit)

                    # Store commit message for analysis
                    message = commit.get("commit", {}).get("message", "")
                    analysis.commit_messages.append(message)

            analysis.user_commits = len(user_commits)

            # Get first and last commit dates
            if commits:
                analysis.last_commit_date = commits[0].get("commit", {}).get("committer", {}).get("date")
                analysis.first_commit_date = commits[-1].get("commit", {}).get("committer", {}).get("date")

            # Analyze a sample of commits for line changes
            sample_commits = user_commits[:10]  # Limit API calls
            total_files = 0
            max_files = 0

            for commit in sample_commits:
                sha = commit.get("sha")
                if not sha:
                    continue

                try:
                    commit_response = await client.get(
                        f"{self.API_BASE_URL}/repos/{full_name}/commits/{sha}",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Accept": "application/vnd.github+json",
                        },
                    )

                    if commit_response.status_code == 200:
                        commit_data = commit_response.json()
                        stats = commit_data.get("stats", {})
                        analysis.lines_added += stats.get("additions", 0)
                        analysis.lines_removed += stats.get("deletions", 0)

                        files = commit_data.get("files", [])
                        num_files = len(files)
                        total_files += num_files
                        max_files = max(max_files, num_files)
                except:
                    pass

            if sample_commits:
                analysis.avg_files_per_commit = total_files / len(sample_commits)
            analysis.max_files_in_commit = max_files

        except Exception as e:
            logger.warning(f"Commit analysis failed for {full_name}: {e}")

        return analysis

    async def _get_collaborators(
        self,
        client: httpx.AsyncClient,
        access_token: str,
        full_name: str,
        username: str,
    ) -> list[CollaboratorInfo]:
        """Get contributor statistics for a repo."""
        collaborators = []

        try:
            response = await client.get(
                f"{self.API_BASE_URL}/repos/{full_name}/contributors",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
                params={"per_page": 10},
            )

            if response.status_code == 200:
                contributors = response.json()

                max_commits = 0
                for contrib in contributors:
                    commits = contrib.get("contributions", 0)
                    max_commits = max(max_commits, commits)

                for contrib in contributors:
                    login = contrib.get("login", "")
                    commits = contrib.get("contributions", 0)
                    collaborators.append(CollaboratorInfo(
                        username=login,
                        commits=commits,
                        lines_added=0,  # Would need per-contributor stats
                        is_primary=(commits == max_commits),
                    ))

        except Exception as e:
            logger.warning(f"Failed to get collaborators for {full_name}: {e}")

        return collaborators

    async def _get_languages(
        self,
        client: httpx.AsyncClient,
        access_token: str,
        full_name: str,
    ) -> dict[str, int]:
        """Get language breakdown for a repo."""
        try:
            response = await client.get(
                f"{self.API_BASE_URL}/repos/{full_name}/languages",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )

            if response.status_code == 200:
                return response.json()
        except:
            pass

        return {}

    async def _check_readme(
        self,
        client: httpx.AsyncClient,
        access_token: str,
        full_name: str,
    ) -> bool:
        """Check if repo has a README."""
        try:
            response = await client.get(
                f"{self.API_BASE_URL}/repos/{full_name}/readme",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            return response.status_code == 200
        except:
            return False

    async def _check_tests(
        self,
        client: httpx.AsyncClient,
        access_token: str,
        full_name: str,
    ) -> bool:
        """Check if repo has test files."""
        try:
            # Check for common test directories/files
            response = await client.get(
                f"{self.API_BASE_URL}/repos/{full_name}/contents",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )

            if response.status_code == 200:
                contents = response.json()
                for item in contents:
                    name = item.get("name", "").lower()
                    if name in ["test", "tests", "__tests__", "spec", "specs"]:
                        return True
                    if name.startswith("test_") or name.endswith("_test.py"):
                        return True
        except:
            pass

        return False

    async def _check_ci(
        self,
        client: httpx.AsyncClient,
        access_token: str,
        full_name: str,
    ) -> bool:
        """Check if repo has CI/CD configuration."""
        try:
            response = await client.get(
                f"{self.API_BASE_URL}/repos/{full_name}/contents",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )

            if response.status_code == 200:
                contents = response.json()
                for item in contents:
                    name = item.get("name", "").lower()
                    if name in [".github", ".circleci", ".travis.yml", "jenkinsfile"]:
                        return True
        except:
            pass

        return False

    def _classify_project(
        self,
        repo: dict,
        commit_analysis: CommitAnalysis,
    ) -> ProjectClassification:
        """Classify the type of project."""
        name = repo.get("name", "").lower()
        description = (repo.get("description") or "").lower()
        topics = [t.lower() for t in repo.get("topics", [])]
        is_fork = repo.get("fork", False)

        indicators = []
        project_type = "unknown"
        confidence = 0.5

        # Check for fork
        if is_fork:
            return ProjectClassification(
                project_type="fork",
                confidence=0.95,
                indicators=["Repository is a fork"]
            )

        # Check for class project
        for pattern in CLASS_PROJECT_PATTERNS:
            if re.search(pattern, name) or re.search(pattern, description):
                indicators.append(f"Name/description matches pattern: {pattern}")
                project_type = "class"
                confidence = 0.8

        # Check for tutorial
        for pattern in TUTORIAL_PATTERNS:
            if re.search(pattern, name) or re.search(pattern, description):
                indicators.append(f"Appears to be tutorial: {pattern}")
                project_type = "tutorial"
                confidence = 0.7

        # Check topics
        if "homework" in topics or "assignment" in topics or "coursework" in topics:
            indicators.append("Has class-related topics")
            project_type = "class"
            confidence = 0.85

        if "hackathon" in topics:
            indicators.append("Has hackathon topic")
            project_type = "hackathon"
            confidence = 0.9

        # If no indicators found, likely personal
        if project_type == "unknown" and commit_analysis.user_commits > 5:
            project_type = "personal"
            confidence = 0.6
            indicators.append("No class/tutorial indicators, multiple commits")

        return ProjectClassification(
            project_type=project_type,
            confidence=confidence,
            indicators=indicators,
        )

    def _detect_code_origin(
        self,
        repo: dict,
        commit_analysis: CommitAnalysis,
    ) -> CodeOriginSignals:
        """Detect signals about code origin (AI-generated, template, etc.)."""
        signals = CodeOriginSignals()

        # Check for bulk initial commit
        if commit_analysis.max_files_in_commit > 30:
            signals.bulk_initial_commit = True

        # Check for generic commit messages
        generic_count = 0
        for msg in commit_analysis.commit_messages:
            msg_lower = msg.lower().strip()
            for pattern in GENERIC_COMMIT_PATTERNS:
                if re.match(pattern, msg_lower):
                    generic_count += 1
                    break

        if len(commit_analysis.commit_messages) > 0:
            if generic_count / len(commit_analysis.commit_messages) > 0.5:
                signals.generic_commit_messages = True

        # Check for no iterative development
        if commit_analysis.user_commits <= 3 and commit_analysis.lines_added > 1000:
            signals.no_iterative_fixes = True

        # Check for template usage (in repo name or description)
        name = repo.get("name", "").lower()
        description = (repo.get("description") or "").lower()

        for indicator in TEMPLATE_INDICATORS:
            if indicator.lower() in name or indicator.lower() in description:
                signals.has_template_files = True
                break

        # Check for suspicious timeline
        if commit_analysis.development_span_days == 0 and commit_analysis.lines_added > 500:
            signals.suspicious_timeline = True

        return signals

    def _get_ai_indicators(self, signals: CodeOriginSignals) -> list[str]:
        """Convert signals to human-readable indicators."""
        indicators = []
        if signals.bulk_initial_commit:
            indicators.append("Large number of files in single commit")
        if signals.generic_commit_messages:
            indicators.append("Mostly generic commit messages")
        if signals.no_iterative_fixes:
            indicators.append("No iterative development pattern")
        if signals.has_template_files:
            indicators.append("Based on template/boilerplate")
        if signals.suspicious_timeline:
            indicators.append("Suspiciously fast development")
        return indicators

    def _compute_originality_score(self, analysis: RepoAnalysis) -> float:
        """Compute originality score for a repo (0-10)."""
        score = 5.0  # Base score

        # Penalize forks
        if analysis.is_fork:
            score -= 2.0

        # Penalize class projects slightly
        if analysis.project_type == "class":
            score -= 1.0
        elif analysis.project_type == "tutorial":
            score -= 2.0

        # Reward being primary author
        if analysis.user_is_primary_author and analysis.contribution_ratio > 0.7:
            score += 2.0
        elif analysis.contribution_ratio > 0.5:
            score += 1.0

        # Penalize AI-generated signals
        if analysis.code_origin == "ai_heavy":
            score -= 2.0
        elif analysis.code_origin == "ai_assisted":
            score -= 1.0
        elif analysis.code_origin == "template":
            score -= 0.5

        return max(0.0, min(10.0, score))

    def _compute_depth_score(
        self,
        analysis: RepoAnalysis,
        commit_analysis: CommitAnalysis,
    ) -> float:
        """Compute depth/complexity score for a repo (0-10)."""
        score = 3.0  # Base score

        # Reward substantial code contribution
        if analysis.lines_added > 2000:
            score += 2.0
        elif analysis.lines_added > 500:
            score += 1.0

        # Reward multiple languages
        if len(analysis.languages) >= 3:
            score += 1.0
        elif len(analysis.languages) >= 2:
            score += 0.5

        # Reward tests and CI
        if analysis.has_tests:
            score += 1.5
        if analysis.has_ci:
            score += 1.0

        # Reward documentation
        if analysis.has_readme:
            score += 0.5

        # Reward sustained development
        if analysis.development_span_days > 30:
            score += 1.0
        elif analysis.development_span_days > 7:
            score += 0.5

        return max(0.0, min(10.0, score))

    def _compute_activity_score(self, analysis: RepoAnalysis) -> float:
        """Compute activity score for a repo (0-10)."""
        score = 3.0  # Base score

        # Reward commit count
        if analysis.user_commits > 50:
            score += 3.0
        elif analysis.user_commits > 20:
            score += 2.0
        elif analysis.user_commits > 10:
            score += 1.0

        # Reward recent activity
        if analysis.last_commit_date:
            try:
                last = datetime.fromisoformat(analysis.last_commit_date.replace('Z', '+00:00'))
                days_ago = (datetime.now(last.tzinfo) - last).days
                if days_ago < 30:
                    score += 2.0
                elif days_ago < 90:
                    score += 1.0
                elif days_ago > 365:
                    score -= 1.0
            except:
                pass

        # Reward sustained development
        if analysis.development_span_days > 60:
            score += 1.0

        return max(0.0, min(10.0, score))

    def _aggregate_analyses(
        self,
        profile: GitHubProfileAnalysis,
        repo_analyses: list[RepoAnalysis],
    ) -> GitHubProfileAnalysis:
        """Aggregate individual repo analyses into profile analysis."""
        if not repo_analyses:
            return profile

        # Sum up metrics
        total_originality = 0.0
        total_depth = 0.0
        total_activity = 0.0

        for repo in repo_analyses:
            profile.total_commits_by_user += repo.user_commits
            profile.total_lines_added += repo.lines_added
            profile.total_lines_removed += repo.lines_removed

            # Count project types
            if repo.project_type == "personal":
                profile.personal_projects_count += 1
            elif repo.project_type == "class":
                profile.class_projects_count += 1
            elif repo.project_type == "fork":
                profile.fork_contributions_count += 1

            # Count code origin
            if repo.code_origin in ["ai_assisted", "ai_heavy"]:
                profile.ai_assisted_repos += 1

            # Quality flags
            if repo.has_tests:
                profile.has_tests = True
            if repo.has_ci:
                profile.has_ci_cd = True
            if repo.has_readme:
                profile.has_documentation = True

            # Accumulate scores
            total_originality += repo.originality_score
            total_depth += repo.depth_score
            total_activity += repo.activity_score

        # Compute averages
        n = len(repo_analyses)
        profile.originality_score = (total_originality / n) * 10  # Scale to 0-100
        profile.depth_score = (total_depth / n) * 10
        profile.activity_score = (total_activity / n) * 10

        # Compute organic code ratio
        organic_repos = sum(1 for r in repo_analyses if r.code_origin == "organic")
        profile.organic_code_ratio = organic_repos / n if n > 0 else 0.0

        # Aggregate languages
        all_languages: dict[str, int] = {}
        for repo in repo_analyses:
            for lang, bytes_count in repo.languages.items():
                all_languages[lang] = all_languages.get(lang, 0) + bytes_count

        # Convert to proficiency levels
        if all_languages:
            total_bytes = sum(all_languages.values())
            profile.primary_languages = [
                {
                    "language": lang,
                    "bytes": count,
                    "percentage": round(count / total_bytes * 100, 1),
                    "proficiency": self._bytes_to_proficiency(count),
                }
                for lang, count in sorted(all_languages.items(), key=lambda x: -x[1])[:6]
            ]

        return profile

    def _bytes_to_proficiency(self, bytes_count: int) -> str:
        """Convert bytes of code to proficiency level."""
        if bytes_count > 50000:
            return "advanced"
        elif bytes_count > 10000:
            return "intermediate"
        elif bytes_count > 2000:
            return "beginner"
        else:
            return "exposure"

    def _compute_final_scores(
        self,
        profile: GitHubProfileAnalysis,
    ) -> GitHubProfileAnalysis:
        """Compute final weighted scores."""
        # Weights for overall score
        ORIGINALITY_WEIGHT = 0.35
        DEPTH_WEIGHT = 0.30
        ACTIVITY_WEIGHT = 0.25
        COLLABORATION_WEIGHT = 0.10

        # Compute collaboration score (basic for now)
        if profile.fork_contributions_count > 0 or profile.total_prs_opened > 0:
            profile.collaboration_score = 60.0
        else:
            profile.collaboration_score = 30.0

        # Compute overall
        profile.overall_score = (
            profile.originality_score * ORIGINALITY_WEIGHT +
            profile.depth_score * DEPTH_WEIGHT +
            profile.activity_score * ACTIVITY_WEIGHT +
            profile.collaboration_score * COLLABORATION_WEIGHT
        )

        return profile

    def _check_flags(
        self,
        profile: GitHubProfileAnalysis,
        repo_analyses: list[RepoAnalysis],
    ) -> GitHubProfileAnalysis:
        """Check for red flags that require human review."""
        flags = []

        # Flag if too many AI-assisted repos
        if profile.ai_assisted_repos > len(repo_analyses) * 0.5:
            flags.append({
                "type": "high_ai_ratio",
                "detail": f"{profile.ai_assisted_repos} of {len(repo_analyses)} repos show AI generation signals",
            })

        # Flag if only class projects
        if profile.class_projects_count == len(repo_analyses) and len(repo_analyses) > 0:
            flags.append({
                "type": "only_class_projects",
                "detail": "All analyzed repos appear to be class assignments",
            })

        # Flag if very low commit count
        if profile.total_commits_by_user < 10 and len(repo_analyses) > 3:
            flags.append({
                "type": "low_commits",
                "detail": f"Only {profile.total_commits_by_user} commits across {len(repo_analyses)} repos",
            })

        # Flag suspicious repos
        for repo in repo_analyses:
            if repo.code_origin == "ai_heavy":
                flags.append({
                    "type": "ai_heavy_repo",
                    "repo": repo.repo_name,
                    "detail": "Repo shows strong AI generation signals",
                })

        profile.flags = flags
        profile.requires_review = len(flags) > 0

        return profile


    # ==================== ENHANCED ANALYSIS METHODS ====================

    async def analyze_pull_requests(
        self,
        client: httpx.AsyncClient,
        access_token: str,
        username: str,
        max_repos: int = 10,
    ) -> dict:
        """
        Analyze PR activity including reviews given and received.
        Shows collaboration and code review quality.
        """
        pr_analysis = {
            "prs_opened": 0,
            "prs_merged": 0,
            "prs_reviewed": 0,
            "review_comments_given": 0,
            "review_quality_samples": [],
            "avg_pr_size": 0,
            "repos_contributed_to": [],
        }

        try:
            # Get PRs created by user
            response = await client.get(
                f"{self.API_BASE_URL}/search/issues",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
                params={
                    "q": f"author:{username} type:pr",
                    "per_page": 50,
                    "sort": "updated",
                },
            )

            if response.status_code == 200:
                data = response.json()
                pr_analysis["prs_opened"] = data.get("total_count", 0)

                # Analyze sample PRs
                for pr in data.get("items", [])[:10]:
                    if pr.get("pull_request", {}).get("merged_at"):
                        pr_analysis["prs_merged"] += 1

            # Get reviews given by user
            response = await client.get(
                f"{self.API_BASE_URL}/search/issues",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
                params={
                    "q": f"reviewed-by:{username} type:pr",
                    "per_page": 50,
                },
            )

            if response.status_code == 200:
                data = response.json()
                pr_analysis["prs_reviewed"] = data.get("total_count", 0)

        except Exception as e:
            logger.warning(f"PR analysis failed for {username}: {e}")

        return pr_analysis

    async def analyze_code_quality_samples(
        self,
        client: httpx.AsyncClient,
        access_token: str,
        full_name: str,
        primary_language: str,
    ) -> list[dict]:
        """
        Sample code files to analyze quality patterns.
        Does NOT store actual code - only derived metrics.
        """
        quality_samples = []

        try:
            # Get file tree
            response = await client.get(
                f"{self.API_BASE_URL}/repos/{full_name}/git/trees/HEAD",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
                params={"recursive": "1"},
            )

            if response.status_code != 200:
                return quality_samples

            tree = response.json().get("tree", [])

            # Find source files (limit to 5 samples)
            source_extensions = {
                "Python": [".py"],
                "JavaScript": [".js", ".jsx"],
                "TypeScript": [".ts", ".tsx"],
                "Java": [".java"],
                "Go": [".go"],
                "Rust": [".rs"],
                "C++": [".cpp", ".cc", ".hpp"],
            }

            extensions = source_extensions.get(primary_language, [".py", ".js"])
            source_files = [
                f for f in tree
                if f["type"] == "blob" and any(f["path"].endswith(ext) for ext in extensions)
                and not any(skip in f["path"].lower() for skip in ["test", "spec", "mock", "node_modules", "vendor"])
            ][:5]

            for file_info in source_files:
                try:
                    # Get file content
                    file_response = await client.get(
                        f"{self.API_BASE_URL}/repos/{full_name}/contents/{file_info['path']}",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Accept": "application/vnd.github.raw",
                        },
                    )

                    if file_response.status_code == 200:
                        content = file_response.text
                        # Analyze code quality (metrics only, not storing code)
                        quality = self._analyze_code_content(content, primary_language)
                        quality["file_path"] = file_info["path"]
                        quality_samples.append(quality)

                except Exception as e:
                    logger.debug(f"Failed to analyze file {file_info['path']}: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Code quality analysis failed for {full_name}: {e}")

        return quality_samples

    def _analyze_code_content(self, content: str, language: str) -> dict:
        """
        Analyze code content for quality signals.
        Returns metrics only - does NOT store the code.
        """
        lines = content.split('\n')
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = 0

        # Count comments based on language
        if language in ["Python"]:
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        elif language in ["JavaScript", "TypeScript", "Java", "Go", "Rust", "C++"]:
            comment_lines = sum(1 for line in lines if line.strip().startswith('//'))

        code_lines = total_lines - blank_lines - comment_lines

        # Quality indicators
        quality = {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_ratio": round(comment_lines / max(code_lines, 1), 3),
            "blank_ratio": round(blank_lines / max(total_lines, 1), 3),
            "avg_line_length": round(sum(len(line) for line in lines) / max(total_lines, 1), 1),
            "max_line_length": max(len(line) for line in lines) if lines else 0,
            "quality_indicators": [],
        }

        # Detect quality patterns
        content_lower = content.lower()

        # Error handling
        if any(kw in content_lower for kw in ['try:', 'except:', 'catch', 'error', 'exception']):
            quality["quality_indicators"].append("has_error_handling")

        # Logging
        if any(kw in content_lower for kw in ['logging', 'logger', 'console.log', 'print(']):
            quality["quality_indicators"].append("has_logging")

        # Type hints (Python/TypeScript)
        if language == "Python" and ('->' in content or ': ' in content):
            quality["quality_indicators"].append("has_type_hints")
        elif language == "TypeScript":
            quality["quality_indicators"].append("has_types")

        # Docstrings/documentation
        if '"""' in content or "'''" in content or '/**' in content:
            quality["quality_indicators"].append("has_docstrings")

        # Constants/configuration
        if any(kw in content for kw in ['CONST', 'CONFIG', 'SETTINGS', 'ENV']):
            quality["quality_indicators"].append("uses_constants")

        # Design patterns
        if any(kw in content_lower for kw in ['factory', 'singleton', 'observer', 'strategy', 'decorator']):
            quality["quality_indicators"].append("uses_design_patterns")

        # Long functions (potential smell)
        if quality["max_line_length"] > 120:
            quality["quality_indicators"].append("has_long_lines")

        return quality

    async def analyze_skill_evolution(
        self,
        client: httpx.AsyncClient,
        access_token: str,
        username: str,
        repo_analyses: list,
    ) -> dict:
        """
        Analyze how skills have evolved over time.
        Tracks language adoption and complexity growth.
        """
        evolution = {
            "languages_by_year": {},
            "complexity_trend": "stable",
            "activity_trend": "stable",
            "years_active": 0,
            "skill_progression": [],
            "notable_growth_periods": [],
        }

        try:
            # Get user's contribution history
            response = await client.get(
                f"{self.API_BASE_URL}/users/{username}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )

            if response.status_code == 200:
                user_data = response.json()
                created_at = user_data.get("created_at")
                if created_at:
                    try:
                        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        evolution["years_active"] = (datetime.now(created.tzinfo) - created).days // 365
                    except:
                        pass

            # Analyze repos by creation date to track language evolution
            repos_by_year = {}
            for repo in repo_analyses:
                if repo.first_commit_date:
                    try:
                        year = datetime.fromisoformat(
                            repo.first_commit_date.replace('Z', '+00:00')
                        ).year
                        if year not in repos_by_year:
                            repos_by_year[year] = {"repos": [], "languages": {}, "complexity_avg": 0}
                        repos_by_year[year]["repos"].append(repo)

                        # Track languages
                        for lang, bytes_count in repo.languages.items():
                            if lang not in repos_by_year[year]["languages"]:
                                repos_by_year[year]["languages"][lang] = 0
                            repos_by_year[year]["languages"][lang] += bytes_count
                    except:
                        pass

            # Calculate complexity trend
            if repos_by_year:
                yearly_complexity = []
                for year in sorted(repos_by_year.keys()):
                    repos = repos_by_year[year]["repos"]
                    avg_depth = sum(r.depth_score for r in repos) / len(repos) if repos else 0
                    yearly_complexity.append((year, avg_depth))
                    evolution["languages_by_year"][str(year)] = repos_by_year[year]["languages"]

                # Determine trend
                if len(yearly_complexity) >= 2:
                    first_half = sum(c[1] for c in yearly_complexity[:len(yearly_complexity)//2])
                    second_half = sum(c[1] for c in yearly_complexity[len(yearly_complexity)//2:])

                    if second_half > first_half * 1.2:
                        evolution["complexity_trend"] = "increasing"
                    elif second_half < first_half * 0.8:
                        evolution["complexity_trend"] = "decreasing"

            # Track new language adoption
            all_languages = set()
            for year in sorted(repos_by_year.keys()):
                year_languages = set(repos_by_year[year]["languages"].keys())
                new_languages = year_languages - all_languages
                if new_languages and year != min(repos_by_year.keys()):
                    evolution["skill_progression"].append({
                        "year": year,
                        "new_languages": list(new_languages),
                    })
                all_languages.update(year_languages)

        except Exception as e:
            logger.warning(f"Skill evolution analysis failed for {username}: {e}")

        return evolution

    async def get_contribution_calendar(
        self,
        client: httpx.AsyncClient,
        access_token: str,
        username: str,
    ) -> dict:
        """
        Analyze contribution patterns from events.
        """
        calendar = {
            "total_contributions_year": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "peak_day": None,
            "consistency_score": 0,
            "active_days_last_year": 0,
        }

        try:
            # Get recent events
            response = await client.get(
                f"{self.API_BASE_URL}/users/{username}/events",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
                params={"per_page": 100},
            )

            if response.status_code == 200:
                events = response.json()

                # Count contributions by day
                from collections import defaultdict
                daily_counts = defaultdict(int)

                for event in events:
                    event_type = event.get("type", "")
                    if event_type in ["PushEvent", "PullRequestEvent", "IssuesEvent", "CreateEvent"]:
                        created_at = event.get("created_at", "")
                        if created_at:
                            try:
                                date_str = created_at[:10]  # YYYY-MM-DD
                                daily_counts[date_str] += 1
                            except:
                                pass

                calendar["active_days_last_year"] = len(daily_counts)
                calendar["total_contributions_year"] = sum(daily_counts.values())

                if daily_counts:
                    calendar["peak_day"] = max(daily_counts, key=daily_counts.get)

                # Calculate consistency (active days / total days in range)
                if daily_counts:
                    dates = sorted(daily_counts.keys())
                    if len(dates) >= 2:
                        try:
                            first = datetime.strptime(dates[0], "%Y-%m-%d")
                            last = datetime.strptime(dates[-1], "%Y-%m-%d")
                            total_days = (last - first).days + 1
                            calendar["consistency_score"] = round(
                                len(daily_counts) / max(total_days, 1) * 100, 1
                            )
                        except:
                            pass

        except Exception as e:
            logger.warning(f"Contribution calendar analysis failed: {e}")

        return calendar

    async def enhanced_analyze_profile(
        self,
        access_token: str,
        username: str,
        include_private: bool = True,
        max_repos: int = 20,
        deep_analysis: bool = True,
    ) -> GitHubProfileAnalysis:
        """
        Enhanced profile analysis with PR reviews, code quality, and skill evolution.
        """
        # Start with base analysis
        analysis = await self.analyze_profile(
            access_token, username, include_private, max_repos
        )

        if not deep_analysis:
            return analysis

        try:
            async with httpx.AsyncClient() as client:
                # Add PR analysis
                pr_data = await self.analyze_pull_requests(
                    client, access_token, username
                )
                analysis.total_prs_opened = pr_data.get("prs_opened", 0)

                # Update collaboration score based on PRs
                if pr_data["prs_reviewed"] > 5:
                    analysis.collaboration_score = min(100, analysis.collaboration_score + 20)
                if pr_data["prs_merged"] > 10:
                    analysis.collaboration_score = min(100, analysis.collaboration_score + 10)

                # Add contribution calendar
                calendar = await self.get_contribution_calendar(
                    client, access_token, username
                )

                # Update activity score based on consistency
                if calendar["consistency_score"] > 30:
                    analysis.activity_score = min(100, analysis.activity_score + 10)

                analysis.active_months_last_year = calendar["active_days_last_year"] // 30

                # Recalculate overall with enhanced data
                analysis = self._compute_final_scores(analysis)

        except Exception as e:
            logger.warning(f"Enhanced analysis failed for {username}: {e}")

        return analysis


# Singleton instance
github_analysis_service = GitHubAnalysisService()
