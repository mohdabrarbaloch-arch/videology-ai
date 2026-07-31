"""Tests for AI response schema validation."""

import pytest
import json
from app.models import (
    VideoAnalysisResult,
    LearningReportResult,
    QuizGenerationResult,
    QuizQuestionModel,
    QuestionType,
    Difficulty,
    ThumbnailStyle,
)


class TestAnalysisSchema:
    """Test GPT-4o analysis response schema validation."""

    def test_valid_analysis_result(self, sample_analysis_result):
        """Valid analysis result should pass schema validation."""
        result = VideoAnalysisResult(**sample_analysis_result)
        assert result.summary is not None
        assert len(result.key_points) > 0
        assert len(result.topics) > 0
        assert len(result.chapters) > 0

    def test_missing_required_field(self, sample_analysis_result):
        """Missing required field should raise validation error."""
        del sample_analysis_result["summary"]
        with pytest.raises(Exception):
            VideoAnalysisResult(**sample_analysis_result)

    def test_chapter_timestamps_are_floats(self, sample_analysis_result):
        """Chapter timestamps should be floats."""
        result = VideoAnalysisResult(**sample_analysis_result)
        for chapter in result.chapters:
            assert isinstance(chapter["start_time"], (int, float))

    def test_chapters_are_ordered(self, sample_analysis_result):
        """Chapters should be ordered by chapter_index."""
        result = VideoAnalysisResult(**sample_analysis_result)
        indices = [c["chapter_index"] for c in result.chapters]
        assert indices == sorted(indices)

    def test_difficulty_level_valid(self, sample_analysis_result):
        """Difficulty level should be a valid value."""
        result = VideoAnalysisResult(**sample_analysis_result)
        assert result.difficulty_level in ["beginner", "intermediate", "advanced", "expert"]

    def test_sentiment_valid(self, sample_analysis_result):
        """Sentiment should be a valid value."""
        result = VideoAnalysisResult(**sample_analysis_result)
        assert result.sentiment in ["positive", "neutral", "negative", "mixed", "informative", "inspiring", "critical"]


class TestQuizSchema:
    """Test GPT-4o quiz generation response schema validation."""

    def test_valid_quiz_result(self, sample_quiz_result):
        """Valid quiz result should pass schema validation."""
        result = QuizGenerationResult(**sample_quiz_result)
        assert result.title is not None
        assert len(result.questions) > 0

    def test_mcq_has_options(self, sample_quiz_result):
        """MCQ questions should have options."""
        result = QuizGenerationResult(**sample_quiz_result)
        mcq_questions = [q for q in result.questions if q.question_type == QuestionType.MCQ]
        for q in mcq_questions:
            assert q.options is not None
            assert len(q.options) == 4  # MCQ should have 4 options

    def test_true_false_correct_answer(self, sample_quiz_result):
        """True/False questions should have 'True' or 'False' as answer."""
        result = QuizGenerationResult(**sample_quiz_result)
        tf_questions = [q for q in result.questions if q.question_type == QuestionType.TRUE_FALSE]
        for q in tf_questions:
            assert q.correct_answer in ["True", "False"]

    def test_question_types_valid(self, sample_quiz_result):
        """All question types should be valid enum values."""
        result = QuizGenerationResult(**sample_quiz_result)
        for q in result.questions:
            assert q.question_type in [QuestionType.MCQ, QuestionType.TRUE_FALSE, QuestionType.SHORT_ANSWER]

    def test_difficulty_valid(self, sample_quiz_result):
        """All difficulties should be valid enum values."""
        result = QuizGenerationResult(**sample_quiz_result)
        for q in result.questions:
            assert q.difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def test_questions_have_explanations(self, sample_quiz_result):
        """All questions should have explanations."""
        result = QuizGenerationResult(**sample_quiz_result)
        for q in result.questions:
            assert q.explanation is not None
            assert len(q.explanation) > 0

    def test_question_indices_sequential(self, sample_quiz_result):
        """Question indices should be sequential starting from 0."""
        result = QuizGenerationResult(**sample_quiz_result)
        indices = [q.question_index for q in result.questions]
        assert indices == list(range(len(indices)))


class TestLearningReportSchema:
    """Test GPT-4o learning report response schema validation."""

    def test_valid_learning_report(self, sample_learning_report):
        """Valid learning report should pass schema validation."""
        result = LearningReportResult(**sample_learning_report)
        assert len(result.learning_outcomes) > 0
        assert len(result.key_concepts) > 0
        assert len(result.action_items) > 0

    def test_key_concepts_have_definitions(self, sample_learning_report):
        """Key concepts should have definitions."""
        result = LearningReportResult(**sample_learning_report)
        for concept in result.key_concepts:
            assert "concept" in concept
            assert "definition" in concept
            assert len(concept["definition"]) > 0

    def test_misconceptions_have_corrections(self, sample_learning_report):
        """Misconceptions should have corrections."""
        result = LearningReportResult(**sample_learning_report)
        for m in result.misconceptions:
            assert "misconception" in m
            assert "correction" in m

    def test_next_topics_not_empty(self, sample_learning_report):
        """Next topics should not be empty."""
        result = LearningReportResult(**sample_learning_report)
        assert len(result.next_topics) > 0


class TestThumbnailStyles:
    """Test thumbnail style enum values."""

    def test_all_styles_defined(self):
        """All 6 thumbnail styles should be defined."""
        styles = list(ThumbnailStyle)
        assert len(styles) == 6

    def test_style_values(self):
        """Style values should match expected strings."""
        assert ThumbnailStyle.YOUTUBE_CREATOR.value == "youtube_creator"
        assert ThumbnailStyle.CINEMATIC.value == "cinematic"
        assert ThumbnailStyle.EDUCATIONAL.value == "educational"
        assert ThumbnailStyle.MINIMAL.value == "minimal"
        assert ThumbnailStyle.HIGH_CONTRAST.value == "high_contrast"
        assert ThumbnailStyle.EDITORIAL.value == "editorial"
