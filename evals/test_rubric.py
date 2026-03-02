"""Rubric-based evals: judge the bot's output against weighted criteria.

12 cases covering in-domain questions, out-of-scope redirects, edge cases,
yoga overview, and practice plan creation. Each response must score >= 6/10.
"""

import json

from conftest import get_answer, judge_with_rubric

RUBRIC = json.dumps(
    [
        {
            "title": "Answers within physical yoga scope",
            "description": (
                "Essential: response addresses asanas, pranayama, or sequencing "
                "using correct yoga terminology and accurate physical information."
            ),
            "weight": 5,
        },
        {
            "title": "Provides specific, actionable details",
            "description": (
                "Important: includes concrete details — alignment cues, breath "
                "counts, body parts, named poses — not vague generalities."
            ),
            "weight": 3,
        },
        {
            "title": "Handles scope boundaries correctly",
            "description": (
                "Essential: redirects spiritual, philosophical, fitness-programming, "
                "and mental-health questions gracefully without directly answering "
                "the out-of-scope premise. Does not give medical advice."
            ),
            "weight": 5,
        },
        {
            "title": "Uses appropriate yoga terminology",
            "description": (
                "Important: uses both Sanskrit and English names where applicable; "
                "uses correct anatomical and yoga-specific language."
            ),
            "weight": 3,
        },
        {
            "title": "Avoids giving medical advice",
            "description": (
                "Pitfall: does not diagnose conditions, prescribe yoga as medical "
                "treatment, or provide personalized clinical guidance."
            ),
            "weight": -3,
        },
    ]
)

INPUTS = [
    {
        "name": "triangle_pose_alignment",
        "input": "How do I set up Triangle Pose (Trikonasana) correctly?",
    },
    {
        "name": "box_breathing_effects",
        "input": "What is Box Breathing and what does it do to the body?",
    },
    {
        "name": "sun_salutation_order",
        "input": "What is the sequence of poses in a Sun Salutation (Surya Namaskar A)?",
    },
    {
        "name": "beginner_inversion_modification",
        "input": (
            "I'm a beginner and want to try an inversion. "
            "What is a safe, accessible option?"
        ),
    },
    {
        "name": "out_of_scope_religion",
        "input": "Is yoga a religion?",
    },
    {
        "name": "out_of_scope_calories",
        "input": "How many calories does an hour of yoga burn?",
    },
    {
        "name": "out_of_scope_mental_health",
        "input": "Can yoga cure anxiety and depression?",
    },
    {
        "name": "out_of_scope_namaste_spiritual",
        "input": "What is the spiritual significance of saying Namaste?",
    },
    {
        "name": "edge_yoga_for_focus",
        "input": "What yoga style is best for improving mental focus?",
    },
    {
        "name": "edge_yoga_vs_gym",
        "input": "Can yoga completely replace going to the gym?",
    },
    {
        "name": "types_of_yoga",
        "input": "What are the different types of yoga and how do they differ physically?",
    },
    {
        "name": "evening_practice_plan",
        "input": "Make me a 30-minute evening wind-down yoga plan.",
    },
]


def test_rubric_cases():
    """Each bot response should score >= 6/10 against the rubric."""
    print()
    ratings = []
    for case in INPUTS:
        response = get_answer(case["input"])
        rating = judge_with_rubric(
            prompt=case["input"],
            response=response,
            rubric=RUBRIC,
        )
        ratings.append(rating)
        print(f"  {case['name']}: {rating}/10")
        assert rating >= 6, (
            f"[{case['name']}] Rating {rating}/10 — response: {response[:200]}"
        )
    print(f"  average: {sum(ratings) / len(ratings):.1f}/10")
