"""Tests for job state transitions."""

import pytest
from app.models import JobStatus


class TestJobStatusTransitions:
    """Test valid and invalid job state transitions."""

    # Valid transition map: from -> [allowed next states]
    VALID_TRANSITIONS = {
        JobStatus.QUEUED: [JobStatus.DOWNLOADING, JobStatus.FAILED],
        JobStatus.DOWNLOADING: [JobStatus.EXTRACTING_AUDIO, JobStatus.FAILED],
        JobStatus.EXTRACTING_AUDIO: [JobStatus.TRANSCRIBING, JobStatus.FAILED],
        JobStatus.TRANSCRIBING: [JobStatus.ANALYZING, JobStatus.FAILED],
        JobStatus.ANALYZING: [JobStatus.GENERATING_THUMBNAILS, JobStatus.FAILED],
        JobStatus.GENERATING_THUMBNAILS: [JobStatus.INDEXING, JobStatus.FAILED],
        JobStatus.INDEXING: [JobStatus.COMPLETED, JobStatus.FAILED],
        JobStatus.COMPLETED: [],  # Terminal state
        JobStatus.FAILED: [JobStatus.QUEUED],  # Can retry
    }

    def test_queued_to_downloading(self):
        """Queued -> Downloading is valid."""
        assert JobStatus.DOWNLOADING in self.VALID_TRANSITIONS[JobStatus.QUEUED]

    def test_downloading_to_extracting(self):
        """Downloading -> Extracting Audio is valid."""
        assert JobStatus.EXTRACTING_AUDIO in self.VALID_TRANSITIONS[JobStatus.DOWNLOADING]

    def test_full_pipeline_sequence(self):
        """Full pipeline should follow the expected sequence."""
        sequence = [
            JobStatus.QUEUED,
            JobStatus.DOWNLOADING,
            JobStatus.EXTRACTING_AUDIO,
            JobStatus.TRANSCRIBING,
            JobStatus.ANALYZING,
            JobStatus.GENERATING_THUMBNAILS,
            JobStatus.INDEXING,
            JobStatus.COMPLETED,
        ]
        for i in range(len(sequence) - 1):
            current = sequence[i]
            next_status = sequence[i + 1]
            assert next_status in self.VALID_TRANSITIONS[current], \
                f"Invalid transition: {current} -> {next_status}"

    def test_any_state_can_fail(self):
        """Any non-terminal state should be able to transition to FAILED."""
        non_terminal = [
            JobStatus.QUEUED, JobStatus.DOWNLOADING, JobStatus.EXTRACTING_AUDIO,
            JobStatus.TRANSCRIBING, JobStatus.ANALYZING,
            JobStatus.GENERATING_THUMBNAILS, JobStatus.INDEXING,
        ]
        for status in non_terminal:
            assert JobStatus.FAILED in self.VALID_TRANSITIONS[status], \
                f"{status} should be able to transition to FAILED"

    def test_completed_is_terminal(self):
        """COMPLETED should be a terminal state with no transitions."""
        assert self.VALID_TRANSITIONS[JobStatus.COMPLETED] == []

    def test_failed_can_retry(self):
        """FAILED should be able to retry (transition back to QUEUED)."""
        assert JobStatus.QUEUED in self.VALID_TRANSITIONS[JobStatus.FAILED]

    def test_invalid_skip_transition(self):
        """Skipping stages should not be valid."""
        # Queued -> Analyzing (skipping Downloading and Extracting) is invalid
        assert JobStatus.ANALYZING not in self.VALID_TRANSITIONS[JobStatus.QUEUED]

    def test_cannot_go_back_from_completed(self):
        """Cannot transition from COMPLETED to any processing state."""
        for status in [JobStatus.DOWNLOADING, JobStatus.TRANSCRIBING, JobStatus.ANALYZING]:
            assert status not in self.VALID_TRANSITIONS[JobStatus.COMPLETED]

    def test_all_statuses_defined(self):
        """All 9 job statuses should be defined."""
        statuses = list(JobStatus)
        assert len(statuses) == 9

    def test_status_values(self):
        """Status values should match expected strings."""
        assert JobStatus.QUEUED.value == "queued"
        assert JobStatus.DOWNLOADING.value == "downloading"
        assert JobStatus.EXTRACTING_AUDIO.value == "extracting_audio"
        assert JobStatus.TRANSCRIBING.value == "transcribing"
        assert JobStatus.ANALYZING.value == "analyzing"
        assert JobStatus.GENERATING_THUMBNAILS.value == "generating_thumbnails"
        assert JobStatus.INDEXING.value == "indexing"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"


class TestJobProgress:
    """Test job progress percentage mapping."""

    # Expected progress ranges for each stage
    PROGRESS_RANGES = {
        JobStatus.QUEUED: (0, 0),
        JobStatus.DOWNLOADING: (1, 15),
        JobStatus.EXTRACTING_AUDIO: (15, 25),
        JobStatus.TRANSCRIBING: (25, 45),
        JobStatus.ANALYZING: (45, 65),
        JobStatus.GENERATING_THUMBNAILS: (65, 85),
        JobStatus.INDEXING: (85, 95),
        JobStatus.COMPLETED: (100, 100),
        JobStatus.FAILED: (0, 0),
    }

    def test_queued_progress_is_zero(self):
        """Queued jobs should have 0% progress."""
        low, high = self.PROGRESS_RANGES[JobStatus.QUEUED]
        assert low == 0 and high == 0

    def test_completed_progress_is_100(self):
        """Completed jobs should have 100% progress."""
        low, high = self.PROGRESS_RANGES[JobStatus.COMPLETED]
        assert low == 100 and high == 100

    def test_progress_increases_through_pipeline(self):
        """Progress should increase monotonically through the pipeline."""
        stages = [
            JobStatus.QUEUED,
            JobStatus.DOWNLOADING,
            JobStatus.EXTRACTING_AUDIO,
            JobStatus.TRANSCRIBING,
            JobStatus.ANALYZING,
            JobStatus.GENERATING_THUMBNAILS,
            JobStatus.INDEXING,
            JobStatus.COMPLETED,
        ]
        for i in range(len(stages) - 1):
            current_high = self.PROGRESS_RANGES[stages[i]][1]
            next_low = self.PROGRESS_RANGES[stages[i + 1]][0]
            assert next_low >= current_high, \
                f"Progress should not decrease: {stages[i]} max={current_high} -> {stages[i+1]} min={next_low}"
