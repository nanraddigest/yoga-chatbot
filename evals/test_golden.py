"""Golden-example evals: judge the bot's output against reference answers.

12 in-domain cases covering asanas, pranayama, sequencing, modifications,
contraindications, yoga overview, and practice plan creation.
Each response must score >= 6/10 against its reference.
"""

from conftest import get_answer, judge_with_golden

GOLDEN_EXAMPLES = [
    {
        "name": "warrior_ii_alignment",
        "input": "How should I align my body in Warrior II (Virabhadrasana II)?",
        "reference": (
            "Stand with feet roughly 3.5–4 feet apart. Turn the front foot out 90° and "
            "the back foot in about 15°. Bend the front knee directly over the ankle, "
            "tracking toward the second toe. The front thigh works toward parallel with "
            "the floor. Keep the torso upright over the hips — leaning forward is a "
            "common mistake. Arms extend parallel to the floor, reaching in both "
            "directions, palms down. Gaze over the front fingertips. Shoulders relax "
            "away from the ears."
        ),
    },
    {
        "name": "downward_dog_benefits",
        "input": "What are the physical benefits of Adho Mukha Svanasana (Downward-Facing Dog)?",
        "reference": (
            "Downward Dog lengthens the hamstrings, calves, and spine simultaneously. "
            "It strengthens the shoulders, arms, and wrists. As a mild inversion, it "
            "encourages blood flow toward the head and can provide brief relief from "
            "lower back compression. The hip flexors and arches of the feet are also "
            "stretched. Regular practice improves upper body endurance and hip mobility."
        ),
    },
    {
        "name": "nadi_shodhana_ratio",
        "input": "How do I practice Nadi Shodhana pranayama and what breath ratio should I use?",
        "reference": (
            "Nadi Shodhana alternates breath between left and right nostrils using "
            "Vishnu mudra. Close the right nostril, inhale left for 4 counts. Close "
            "both, optional retention for 4. Exhale right for 8. Inhale right for 4. "
            "Retain for 4. Exhale left for 8. The standard beginner ratio is 1:1:2 "
            "(inhale:retention:exhale), e.g., 4-4-8. The extended exhale activates "
            "the parasympathetic nervous system. Start with 5–10 cycles."
        ),
    },
    {
        "name": "chaturanga_mistakes",
        "input": "What are the most common mistakes in Chaturanga Dandasana?",
        "reference": (
            "The most frequent mistakes: elbows flare wide rather than hugging the "
            "ribs (the elbows should stay close to the sides at roughly 90°). The "
            "hips sag toward the floor, straining the lower back — the body should "
            "form one straight line from head to heels. Conversely, the hips may "
            "pike upward. The chest collapses before the core engages. Practitioners "
            "also drop too low — in the full pose the upper arms are parallel to the "
            "floor, not below it. Weak core engagement throughout is the root cause "
            "of most of these errors."
        ),
    },
    {
        "name": "pigeon_modification",
        "input": "What are good modifications for Pigeon Pose for someone with tight hips?",
        "reference": (
            "For tight hips, the best modification is Reclined / Supine Pigeon "
            "(also called Figure Four or Eye of the Needle): lie on your back, "
            "cross one ankle over the opposite thigh, flex the foot, and draw "
            "the legs toward the chest — this provides the same outer hip stretch "
            "with zero compression on the knee. Another option is placing a folded "
            "blanket or block under the hip of the bent leg in the floor version "
            "to level the pelvis and reduce strain. A Half-Pigeon with the front "
            "shin diagonal rather than parallel to the front of the mat is more "
            "accessible and still effective."
        ),
    },
    {
        "name": "pre_savasana_sequence",
        "input": "What poses should I do right before Savasana to wind down?",
        "reference": (
            "A reliable closing arc: Supine Spinal Twist (Supta Matsyendrasana) "
            "on each side, Happy Baby (Ananda Balasana), Legs-Up-the-Wall "
            "(Viparita Karani) for 3–5 minutes, and Reclined Bound Angle "
            "(Supta Baddha Konasana). Before Savasana, spend 1–2 minutes "
            "with diaphragmatic breathing using a 1:2 exhale ratio to signal "
            "the nervous system to settle."
        ),
    },
    {
        "name": "ujjayi_usage",
        "input": "What is Ujjayi pranayama and when should I use it during practice?",
        "reference": (
            "Ujjayi (victorious breath) is produced by gently constricting the "
            "back of the throat, creating a soft oceanic sound on both inhale and "
            "exhale through the nose. The slight resistance slows and lengthens "
            "the breath, builds internal warmth, and focuses the mind. It is most "
            "commonly used during Vinyasa and Ashtanga practice to synchronize "
            "movement with breath — one breath per movement. It can also serve as "
            "an anchor during challenging standing poses to sustain concentration."
        ),
    },
    {
        "name": "shoulderstand_contraindications",
        "input": "Who should generally avoid Shoulderstand (Salamba Sarvangasana)?",
        "reference": (
            "Shoulderstand places significant weight and compression on the cervical "
            "spine, so practitioners with neck issues, disc problems in the neck, "
            "or limited cervical mobility should avoid it or use a supported "
            "variation (blankets under the shoulders to reduce neck angle). "
            "It is also traditionally avoided for practitioners with high blood "
            "pressure, glaucoma or eye pressure concerns, and active ear infections. "
            "Those with thyroid conditions may need to modify or skip it. "
            "Legs-Up-the-Wall is a common accessible alternative."
        ),
    },
    {
        "name": "kapalabhati_effects",
        "input": "What does Kapalabhati pranayama do to the body physically?",
        "reference": (
            "Kapalabhati uses rapid, forceful exhales driven by sharp abdominal "
            "contractions, with passive inhales. Physically: the repeated "
            "contraction of the rectus abdominis and transverse abdominis "
            "strengthens and tones the core. The vigorous breath clears the "
            "nasal passages and upper respiratory tract. The overall effect is "
            "stimulating and energizing — heart rate increases mildly and the "
            "body feels warmer. It is therefore a morning or pre-practice "
            "technique; avoid it in the evening or before restorative work. "
            "Standard practice is 3 rounds of 30–50 pumps with breath retention "
            "between rounds."
        ),
    },
    {
        "name": "cobra_vs_updog",
        "input": "What is the difference between Cobra Pose and Upward-Facing Dog?",
        "reference": (
            "In Cobra (Bhujangasana), the legs and pelvis remain on the floor "
            "and the elbows may stay slightly bent — this is a gentler backbend "
            "with less lumbar load. The hands are beside the lower ribs. "
            "In Upward-Facing Dog (Urdhva Mukha Svanasana), the arms are fully "
            "straight, the thighs and kneecaps lift completely off the floor — "
            "only the tops of the feet and the palms bear weight. This produces "
            "a deeper backbend and requires more shoulder and core strength. "
            "Cobra is appropriate for beginners or when warming up; Upward Dog "
            "is the standard peak of the Vinyasa transition and demands greater "
            "wrist and shoulder stability."
        ),
    },
    {
        "name": "what_is_yoga_beginner",
        "input": "I've never done yoga before. What is it and where should I start?",
        "reference": (
            "Yoga is a physical practice combining intentional movement (asanas), "
            "breath control (pranayama), and body awareness. It differs from ordinary "
            "stretching because the breath is synchronized with movement throughout. "
            "For beginners, the best starting styles are Hatha (slow-paced, pose-by-pose, "
            "ideal for learning alignment) and gentle Vinyasa. Yin yoga (long passive "
            "holds) is also accessible. Begin with foundational poses: Mountain Pose, "
            "Child's Pose, Downward Dog, Cat-Cow, and Warrior I and II. Add basic "
            "breathwork like diaphragmatic breathing once the poses feel familiar."
        ),
    },
    {
        "name": "beginner_practice_plan",
        "input": "Can you give me a simple 20-minute beginner yoga sequence?",
        "reference": (
            "A 20-minute beginner sequence: "
            "Opening breath (2 min) — Box Breathing or diaphragmatic breathing. "
            "Warm-up (4 min) — Cat-Cow (Marjaryasana-Bitilasana) 8 rounds, "
            "Child's Pose (Balasana) 5 breaths. "
            "Standing (8 min) — Mountain Pose (Tadasana), Warrior I (Virabhadrasana I) "
            "each side, Warrior II (Virabhadrasana II) each side, Downward Dog "
            "(Adho Mukha Svanasana) 8 breaths. "
            "Floor cool-down (4 min) — Seated Forward Fold (Paschimottanasana), "
            "Reclined Twist each side. "
            "Savasana (2 min) — full release."
        ),
    },
]


def test_golden_examples():
    """Each bot response should score >= 6/10 against its golden reference."""
    print()
    ratings = []
    for example in GOLDEN_EXAMPLES:
        response = get_answer(example["input"])
        rating = judge_with_golden(
            prompt=example["input"],
            reference=example["reference"],
            response=response,
        )
        ratings.append(rating)
        print(f"  {example['name']}: {rating}/10")
        assert rating >= 6, (
            f"[{example['name']}] Rating {rating}/10 — response: {response[:200]}"
        )
    print(f"  average: {sum(ratings) / len(ratings):.1f}/10")
