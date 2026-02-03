"""
Tests for AI scoring service.

Tests cover:
- Score bounds validation
- Score conversion (0-100 to 0-10)
- Interview response scoring
- Vertical-specific scoring weights
- Multi-rater simulation
- Profile scoring
- Coding challenge scoring
- Edge cases
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.scoring import (
    ScoringService,
    ScoreResult,
    InterviewSummary,
    clamp_score,
    validate_and_convert_score,
    SCORING_ALGORITHM_VERSION,
)


# ==================== Score Bounds Validation Tests ====================

class TestScoreBoundsValidation:
    """Tests for score clamping and validation functions."""

    def test_clamp_score_within_bounds(self):
        """Test that scores within bounds are unchanged."""
        assert clamp_score(5.0) == 5.0
        assert clamp_score(0.0) == 0.0
        assert clamp_score(10.0) == 10.0
        assert clamp_score(7.5) == 7.5

    def test_clamp_score_below_minimum(self):
        """Test that scores below minimum are clamped."""
        assert clamp_score(-5.0) == 0.0
        assert clamp_score(-100.0) == 0.0
        assert clamp_score(-0.1) == 0.0

    def test_clamp_score_above_maximum(self):
        """Test that scores above maximum are clamped."""
        assert clamp_score(15.0) == 10.0
        assert clamp_score(100.0) == 10.0
        assert clamp_score(10.1) == 10.0

    def test_clamp_score_with_none(self):
        """Test that None returns minimum value."""
        assert clamp_score(None) == 0.0

    def test_clamp_score_with_invalid_type(self):
        """Test that invalid types return minimum value."""
        assert clamp_score("invalid") == 0.0
        assert clamp_score([1, 2, 3]) == 0.0
        assert clamp_score({}) == 0.0

    def test_clamp_score_custom_bounds(self):
        """Test clamping with custom min/max bounds."""
        assert clamp_score(5.0, min_val=0.0, max_val=5.0) == 5.0
        assert clamp_score(10.0, min_val=0.0, max_val=5.0) == 5.0
        assert clamp_score(-1.0, min_val=0.0, max_val=5.0) == 0.0

    def test_validate_and_convert_score_from_100(self):
        """Test conversion from 0-100 to 0-10 scale."""
        assert validate_and_convert_score(100, scale=100) == 10.0
        assert validate_and_convert_score(50, scale=100) == 5.0
        assert validate_and_convert_score(0, scale=100) == 0.0
        assert validate_and_convert_score(75, scale=100) == 7.5

    def test_validate_and_convert_score_already_10_scale(self):
        """Test that 0-10 scale scores are preserved."""
        assert validate_and_convert_score(10, scale=10) == 10.0
        assert validate_and_convert_score(5, scale=10) == 5.0
        assert validate_and_convert_score(0, scale=10) == 0.0

    def test_validate_and_convert_score_out_of_bounds(self):
        """Test that out-of-bounds scores are clamped."""
        assert validate_and_convert_score(150, scale=100) == 10.0
        assert validate_and_convert_score(-50, scale=100) == 0.0

    def test_validate_and_convert_score_with_none(self):
        """Test that None returns 0."""
        assert validate_and_convert_score(None, scale=100) == 0.0

    def test_validate_and_convert_score_with_float(self):
        """Test conversion with float values."""
        result = validate_and_convert_score(77.5, scale=100)
        assert result == 7.75


# ==================== Scoring Service Configuration Tests ====================

class TestScoringServiceConfig:
    """Tests for scoring service configuration."""

    def test_vertical_scoring_config_exists(self):
        """Test that all verticals have scoring config."""
        service = ScoringService()
        expected_verticals = [
            "software_engineering", "data", "product", "design", "finance"
        ]
        for vertical in expected_verticals:
            assert vertical in service.VERTICAL_SCORING_CONFIG
            config = service.VERTICAL_SCORING_CONFIG[vertical]
            assert "weights" in config
            assert "rubric" in config

    def test_vertical_weights_sum_to_one(self):
        """Test that weights for each vertical sum to 1.0."""
        service = ScoringService()
        for vertical, config in service.VERTICAL_SCORING_CONFIG.items():
            weights = config["weights"]
            total = sum(weights.values())
            assert abs(total - 1.0) < 0.01, f"{vertical} weights sum to {total}, expected 1.0"

    def test_default_weights_sum_to_one(self):
        """Test that default weights sum to 1.0."""
        service = ScoringService()
        total = sum(service.SCORING_WEIGHTS.values())
        assert abs(total - 1.0) < 0.01

    def test_get_vertical_config_known_vertical(self):
        """Test getting config for known vertical."""
        service = ScoringService()
        weights, rubric = service._get_vertical_config("software_engineering")
        assert "problem_solving" in weights
        assert weights["problem_solving"] == 0.30  # SWE has higher weight
        assert "SCORING RUBRIC" in rubric

    def test_get_vertical_config_unknown_vertical(self):
        """Test getting config for unknown vertical returns defaults."""
        service = ScoringService()
        weights, rubric = service._get_vertical_config("unknown_vertical")
        assert weights == service.SCORING_WEIGHTS
        assert rubric == ""

    def test_get_vertical_config_legacy_mapping(self):
        """Test that legacy verticals are mapped correctly."""
        service = ScoringService()
        # 'engineering' should map to 'software_engineering'
        weights, _ = service._get_vertical_config("engineering")
        swe_weights, _ = service._get_vertical_config("software_engineering")
        assert weights == swe_weights

        # 'business' should map to 'product'
        weights, _ = service._get_vertical_config("business")
        product_weights, _ = service._get_vertical_config("product")
        assert weights == product_weights


# ==================== Interview Response Scoring Tests ====================

class TestInterviewResponseScoring:
    """Tests for interview response scoring."""

    @pytest.mark.asyncio
    async def test_analyze_response_success(self, mock_llm_response):
        """Test successful response analysis."""
        service = ScoringService()

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_llm_response()

            result = await service.analyze_response(
                question="Tell me about yourself",
                transcript="I am a software engineer with 3 years of experience...",
                job_title="Software Engineer",
                job_requirements=["Python", "Testing"],
                vertical="software_engineering",
            )

            assert isinstance(result, ScoreResult)
            assert 0 <= result.overall <= 10
            assert 0 <= result.communication <= 10
            assert 0 <= result.problem_solving <= 10
            assert result.algorithm_version == SCORING_ALGORITHM_VERSION

    @pytest.mark.asyncio
    async def test_analyze_response_bounds_checking(self, mock_llm_response):
        """Test that out-of-bounds AI scores are clamped."""
        service = ScoringService()

        # Create response with out-of-bounds scores
        def bad_scores_response():
            return {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "scores": {
                                "communication": 150,  # Over 100
                                "problem_solving": -20,  # Negative
                                "domain_knowledge": 100,
                                "motivation": 75,
                                "culture_fit": 80,
                            },
                            "overall_score": 200,  # Over 100
                            "analysis": "Test",
                            "strengths": [],
                            "concerns": [],
                            "highlight_quotes": [],
                        })
                    }
                }]
            }

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = bad_scores_response()

            result = await service.analyze_response(
                question="Test",
                transcript="Test",
                job_title="Test",
                job_requirements=[],
            )

            # All scores should be clamped to 0-10
            assert result.communication == 10.0  # Clamped from 150
            assert result.problem_solving == 0.0  # Clamped from -20
            assert result.domain_knowledge == 10.0
            assert 0 <= result.overall <= 10

    @pytest.mark.asyncio
    async def test_analyze_response_missing_scores(self, mock_llm_response):
        """Test handling of missing score dimensions."""
        service = ScoringService()

        # Create response with missing scores
        def incomplete_response():
            return {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "scores": {
                                "communication": 75,
                                # Missing other dimensions
                            },
                            "analysis": "Test",
                            "strengths": [],
                            "concerns": [],
                        })
                    }
                }]
            }

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = incomplete_response()

            result = await service.analyze_response(
                question="Test",
                transcript="Test",
                job_title="Test",
                job_requirements=[],
            )

            # Missing scores should default to 50 (converted to 5.0)
            assert result.communication == 7.5  # 75 / 10
            assert result.problem_solving == 5.0  # Default 50 / 10


# ==================== Summary Generation Tests ====================

class TestSummaryGeneration:
    """Tests for interview summary generation."""

    @pytest.mark.asyncio
    async def test_generate_summary_success(self):
        """Test successful summary generation."""
        service = ScoringService()

        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "total_score": 75,
                        "summary": "Strong candidate with good communication.",
                        "overall_strengths": ["Communication", "Problem solving"],
                        "overall_concerns": ["Technical depth"],
                        "recommendation": "advance",
                    })
                }
            }]
        }

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await service.generate_summary(
                responses=[
                    {"question": "Q1", "transcript": "A1", "score": 7.5},
                    {"question": "Q2", "transcript": "A2", "score": 8.0},
                ],
                job_title="Software Engineer",
                job_requirements=["Python"],
            )

            assert isinstance(result, InterviewSummary)
            assert result.total_score == 7.5  # 75 / 10
            assert result.recommendation == "advance"

    @pytest.mark.asyncio
    async def test_generate_summary_invalid_recommendation(self):
        """Test that invalid recommendations are normalized."""
        service = ScoringService()

        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "total_score": 60,
                        "summary": "Average candidate.",
                        "overall_strengths": [],
                        "overall_concerns": [],
                        "recommendation": "invalid_recommendation",  # Invalid
                    })
                }
            }]
        }

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await service.generate_summary(
                responses=[],
                job_title="Test",
                job_requirements=[],
            )

            assert result.recommendation == "maybe"  # Defaults to 'maybe'


# ==================== Overall Score Calculation Tests ====================

class TestOverallScoreCalculation:
    """Tests for overall score calculation."""

    def test_calculate_overall_score_empty_responses(self):
        """Test that empty responses return 0."""
        service = ScoringService()
        assert service.calculate_overall_score([]) == 0.0

    def test_calculate_overall_score_single_response(self):
        """Test calculation with a single response."""
        service = ScoringService()
        result = ScoreResult(
            communication=7.0, problem_solving=8.0, domain_knowledge=7.5,
            motivation=8.0, culture_fit=7.5, overall=7.6,
            analysis="", strengths=[], concerns=[], highlight_quotes=[],
        )
        assert service.calculate_overall_score([result]) == 7.6

    def test_calculate_overall_score_multiple_responses(self):
        """Test calculation with multiple responses."""
        service = ScoringService()
        results = [
            ScoreResult(
                communication=7.0, problem_solving=8.0, domain_knowledge=7.5,
                motivation=8.0, culture_fit=7.5, overall=8.0,
                analysis="", strengths=[], concerns=[], highlight_quotes=[],
            ),
            ScoreResult(
                communication=6.0, problem_solving=7.0, domain_knowledge=6.5,
                motivation=7.0, culture_fit=6.5, overall=6.0,
                analysis="", strengths=[], concerns=[], highlight_quotes=[],
            ),
        ]
        # Average of 8.0 and 6.0 = 7.0
        assert service.calculate_overall_score(results) == 7.0


# ==================== Profile Scoring Tests ====================

class TestProfileScoring:
    """Tests for profile scoring."""

    @pytest.mark.asyncio
    async def test_score_profile_with_all_data(self):
        """Test profile scoring with complete data."""
        service = ScoringService()

        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "scores": {
                            "technical_skills": 8.0,
                            "experience_quality": 7.0,
                            "education": 8.5,
                            "github_activity": 7.5,
                            "overall_potential": 7.8,
                        },
                        "profile_score": 7.8,
                        "strengths": ["Strong technical background"],
                        "gaps": ["Limited work experience"],
                        "summary": "Promising candidate.",
                    })
                }
            }]
        }

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await service.score_profile(
                resume_data={"skills": ["Python", "JavaScript"]},
                github_data={"repos": [{"name": "project1"}], "totalContributions": 100},
                education_data={"university": "MIT", "gpa": 3.8},
                vertical="software_engineering",
            )

            assert "profile_score" in result
            assert 0 <= result["profile_score"] <= 10
            assert result["completeness"] > 0

    @pytest.mark.asyncio
    async def test_score_profile_empty_data(self):
        """Test profile scoring with no data."""
        service = ScoringService()

        result = await service.score_profile()

        assert result["profile_score"] is None
        assert result["completeness"] == 0


# ==================== Coding Challenge Scoring Tests ====================

class TestCodingChallengeScoring:
    """Tests for coding challenge scoring."""

    @pytest.mark.asyncio
    async def test_score_coding_response_all_pass(self):
        """Test coding score with all tests passing."""
        service = ScoringService()

        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "scores": {
                            "correctness": 100,
                            "code_quality": 85,
                            "efficiency": 80,
                            "problem_understanding": 90,
                        },
                        "overall_score": 89,
                        "analysis": "Good solution.",
                        "strengths": ["Efficient"],
                        "concerns": [],
                        "time_complexity": "O(n)",
                        "space_complexity": "O(1)",
                    })
                }
            }]
        }

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await service.score_coding_response(
                problem_description="Two Sum problem",
                code="def two_sum(nums, target): pass",
                test_results=[
                    {"name": "test1", "passed": True},
                    {"name": "test2", "passed": True},
                ],
            )

            assert isinstance(result, ScoreResult)
            assert result.problem_solving == 10.0  # Correctness mapped to problem_solving

    @pytest.mark.asyncio
    async def test_score_coding_response_partial_pass(self):
        """Test coding score with partial test passes."""
        service = ScoringService()

        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "scores": {
                            "correctness": 50,
                            "code_quality": 70,
                            "efficiency": 60,
                            "problem_understanding": 65,
                        },
                        "overall_score": 61,
                        "analysis": "Partial solution.",
                        "strengths": [],
                        "concerns": ["Missing edge cases"],
                        "time_complexity": "O(n^2)",
                        "space_complexity": "O(n)",
                    })
                }
            }]
        }

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await service.score_coding_response(
                problem_description="Test problem",
                code="def solution(): pass",
                test_results=[
                    {"name": "test1", "passed": True},
                    {"name": "test2", "passed": False},
                ],
            )

            assert result.problem_solving == 5.0  # 50 / 10


# ==================== Behavioral Signal Extraction Tests ====================

class TestBehavioralSignals:
    """Tests for behavioral signal extraction."""

    def test_extract_filler_words(self):
        """Test filler word detection."""
        service = ScoringService()
        transcript = "Um, so like, I basically, you know, did the thing."
        signals = service.extract_behavioral_signals(transcript)

        assert signals["filler_word_count"] > 0
        assert signals["filler_ratio"] > 0

    def test_extract_star_format(self):
        """Test STAR format detection."""
        service = ScoringService()
        transcript = """
        The situation was that we had a deadline approaching.
        My task was to lead the team.
        I decided to implement a new process.
        The result was a 30% improvement in efficiency.
        """
        signals = service.extract_behavioral_signals(transcript)

        assert signals["star_format"]["has_situation"] == True
        assert signals["star_format"]["has_task"] == True
        assert signals["star_format"]["has_action"] == True
        assert signals["star_format"]["has_result"] == True
        assert signals["star_format"]["completeness"] == 1.0

    def test_extract_confidence_indicators(self):
        """Test confidence indicator detection."""
        service = ScoringService()

        confident = "I definitely know how to solve this. I've done similar work before."
        hedging = "I think maybe I could probably try to do it, I guess."

        confident_signals = service.extract_behavioral_signals(confident)
        hedging_signals = service.extract_behavioral_signals(hedging)

        assert confident_signals["confidence_count"] > hedging_signals["confidence_count"]
        assert hedging_signals["hedging_count"] > confident_signals["hedging_count"]

    def test_extract_quantified_results(self):
        """Test detection of quantified results."""
        service = ScoringService()

        with_numbers = "I improved performance by 50% and reduced costs by $10,000."
        without_numbers = "I improved performance significantly."

        signals_with = service.extract_behavioral_signals(with_numbers)
        signals_without = service.extract_behavioral_signals(without_numbers)

        assert signals_with["has_quantified_results"] == True
        assert signals_without["has_quantified_results"] == False


# ==================== Score Calibration Tests ====================

class TestScoreCalibration:
    """Tests for score calibration."""

    @pytest.mark.asyncio
    async def test_calibrate_score_normal_range(self):
        """Test calibration for normal score range."""
        service = ScoringService()

        result = await service.calibrate_score(
            raw_score=7.5,
            vertical="software_engineering",
            role_type="backend",
        )

        assert "calibrated_score" in result
        assert "hire_probability" in result
        assert "percentile" in result
        assert 0 <= result["calibrated_score"] <= 10

    @pytest.mark.asyncio
    async def test_calibrate_score_out_of_bounds(self):
        """Test calibration clamps out-of-bounds scores."""
        service = ScoringService()

        result = await service.calibrate_score(
            raw_score=15.0,  # Over 10
            vertical="software_engineering",
            role_type="backend",
        )

        assert result["raw_score"] == 10.0
        assert result["calibrated_score"] <= 10.0

    @pytest.mark.asyncio
    async def test_calibrate_score_interpretation(self):
        """Test score interpretation."""
        service = ScoringService()

        high_result = await service.calibrate_score(9.0, "software_engineering", "backend")
        low_result = await service.calibrate_score(3.0, "software_engineering", "backend")

        assert "Exceptional" in high_result["interpretation"] or "Strong" in high_result["interpretation"]
        assert "improvement" in low_result["interpretation"].lower()


# ==================== Multi-Rater Simulation Tests ====================

class TestMultiRaterSimulation:
    """Tests for multi-rater scoring simulation."""

    def test_interviewer_personas_defined(self):
        """Test that all interviewer personas are defined."""
        service = ScoringService()
        assert "technical" in service.INTERVIEWER_PERSONAS
        assert "hiring_manager" in service.INTERVIEWER_PERSONAS
        assert "peer" in service.INTERVIEWER_PERSONAS

    def test_persona_weight_adjustments(self):
        """Test that personas have valid weight adjustments."""
        service = ScoringService()

        for persona_name, config in service.INTERVIEWER_PERSONAS.items():
            assert "weight_adjustments" in config
            # Sum of adjustments should be close to 0 (rebalancing)
            total_adjustment = sum(config["weight_adjustments"].values())
            assert abs(total_adjustment) < 0.5, f"{persona_name} has unbalanced adjustments"


# ==================== Edge Cases Tests ====================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_analyze_response_empty_transcript(self, mock_llm_response):
        """Test analysis with empty transcript."""
        service = ScoringService()

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_llm_response()

            result = await service.analyze_response(
                question="Test",
                transcript="",  # Empty
                job_title="Test",
                job_requirements=[],
            )

            assert isinstance(result, ScoreResult)

    @pytest.mark.asyncio
    async def test_analyze_response_very_long_transcript(self, mock_llm_response):
        """Test analysis with very long transcript."""
        service = ScoringService()

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_llm_response()

            long_transcript = "This is a test. " * 1000  # Very long

            result = await service.analyze_response(
                question="Test",
                transcript=long_transcript,
                job_title="Test",
                job_requirements=[],
            )

            assert isinstance(result, ScoreResult)

    @pytest.mark.asyncio
    async def test_llm_json_parse_error(self):
        """Test handling of malformed LLM response."""
        service = ScoringService()

        bad_response = {
            "choices": [{
                "message": {
                    "content": "This is not valid JSON {"
                }
            }]
        }

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = bad_response

            with pytest.raises(Exception, match="Failed to parse"):
                await service.analyze_response(
                    question="Test",
                    transcript="Test",
                    job_title="Test",
                    job_requirements=[],
                )

    def test_score_result_algorithm_version(self):
        """Test that ScoreResult includes algorithm version."""
        result = ScoreResult(
            communication=7.0, problem_solving=7.0, domain_knowledge=7.0,
            motivation=7.0, culture_fit=7.0, overall=7.0,
            analysis="Test", strengths=[], concerns=[], highlight_quotes=[],
        )
        assert result.algorithm_version == SCORING_ALGORITHM_VERSION
