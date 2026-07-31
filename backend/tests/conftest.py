"""Pytest configuration and fixtures for Videology AI backend tests."""

import os
import sys
import pytest
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture
def sample_segments():
    """Sample transcript segments for testing."""
    return [
        {"start": 0.0, "end": 5.0, "text": "Welcome to this tutorial on machine learning."},
        {"start": 5.0, "end": 12.0, "text": "Today we'll cover the basics of neural networks."},
        {"start": 12.0, "end": 20.0, "text": "Neural networks are inspired by the human brain."},
        {"start": 20.0, "end": 30.0, "text": "They consist of layers of interconnected nodes."},
        {"start": 30.0, "end": 45.0, "text": "Each node applies a mathematical function to its inputs."},
        {"start": 45.0, "end": 60.0, "text": "The network learns through a process called backpropagation."},
        {"start": 60.0, "end": 75.0, "text": "Backpropagation adjusts the weights of connections."},
        {"start": 75.0, "end": 90.0, "text": "This allows the network to minimize prediction errors."},
        {"start": 90.0, "end": 105.0, "text": "Let's look at a practical example next."},
        {"start": 105.0, "end": 120.0, "text": "We'll build a simple image classifier using TensorFlow."},
    ]


@pytest.fixture
def sample_analysis_result():
    """Sample GPT-4o analysis result for schema testing."""
    return {
        "summary": "This video provides an introduction to machine learning and neural networks.",
        "executive_summary": "A beginner-friendly tutorial covering neural network fundamentals.",
        "key_points": [
            "Neural networks are inspired by the human brain",
            "They consist of layers of interconnected nodes",
            "Learning happens through backpropagation",
        ],
        "topics": [
            {"topic": "Machine Learning", "relevance_score": 0.95, "mention_count": 5},
            {"topic": "Neural Networks", "relevance_score": 0.90, "mention_count": 8},
            {"topic": "Backpropagation", "relevance_score": 0.85, "mention_count": 3},
        ],
        "chapters": [
            {"chapter_index": 0, "title": "Introduction", "summary": "Welcome and overview", "start_time": 0.0, "end_time": 12.0},
            {"chapter_index": 1, "title": "Neural Network Basics", "summary": "How neural networks work", "start_time": 12.0, "end_time": 45.0},
            {"chapter_index": 2, "title": "Backpropagation", "summary": "Learning process", "start_time": 45.0, "end_time": 90.0},
            {"chapter_index": 3, "title": "Practical Example", "summary": "Building a classifier", "start_time": 90.0, "end_time": 120.0},
        ],
        "key_moments": [
            {"timestamp_seconds": 12.0, "title": "Neural networks explained", "description": "Core concept introduction", "moment_type": "insight", "importance_score": 0.9},
            {"timestamp_seconds": 45.0, "title": "Backpropagation", "description": "Learning mechanism", "moment_type": "insight", "importance_score": 0.85},
        ],
        "entities": [
            {"entity_text": "TensorFlow", "entity_type": "technology", "mention_count": 2},
            {"entity_text": "Neural Networks", "entity_type": "concept", "mention_count": 8},
        ],
        "difficulty_level": "beginner",
        "sentiment": "informative",
        "content_type": "tutorial",
        "target_audience": "Beginners interested in machine learning",
    }


@pytest.fixture
def sample_quiz_result():
    """Sample quiz generation result for schema testing."""
    return {
        "title": "Quiz: Introduction to Machine Learning",
        "questions": [
            {
                "question_index": 0,
                "question_type": "mcq",
                "question_text": "What are neural networks inspired by?",
                "options": ["The human brain", "Computer processors", "Mathematical equations", "DNA sequences"],
                "correct_answer": "The human brain",
                "explanation": "Neural networks are biologically inspired by the structure of the human brain.",
                "difficulty": "easy",
            },
            {
                "question_index": 1,
                "question_type": "true_false",
                "question_text": "Backpropagation is used to adjust the weights of connections in a neural network.",
                "correct_answer": "True",
                "explanation": "Backpropagation is the learning algorithm that adjusts weights to minimize errors.",
                "difficulty": "medium",
            },
            {
                "question_index": 2,
                "question_type": "short_answer",
                "question_text": "What framework is used in the practical example?",
                "correct_answer": "TensorFlow",
                "explanation": "The video demonstrates building an image classifier using TensorFlow.",
                "difficulty": "easy",
            },
        ],
    }


@pytest.fixture
def sample_learning_report():
    """Sample learning report for schema testing."""
    return {
        "learning_outcomes": [
            "You will be able to explain what neural networks are",
            "You will be able to describe the backpropagation process",
        ],
        "key_concepts": [
            {"concept": "Neural Network", "definition": "A computational model inspired by the brain", "timestamp": 12.0},
            {"concept": "Backpropagation", "definition": "Algorithm for adjusting network weights", "timestamp": 45.0},
        ],
        "key_facts": [
            "Neural networks consist of layers of interconnected nodes",
            "Backpropagation minimizes prediction errors",
        ],
        "action_items": [
            "Try building a simple neural network with TensorFlow",
            "Experiment with different network architectures",
        ],
        "misconceptions": [
            {"misconception": "Neural networks think like humans", "correction": "They are mathematical models that mimic brain structure, not consciousness"},
        ],
        "next_topics": ["Deep Learning", "Convolutional Neural Networks", "Natural Language Processing"],
        "prerequisites": ["Basic Python programming", "Understanding of linear algebra"],
    }
