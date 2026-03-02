import base64
import os
import re
import uuid

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from litellm import completion
from pydantic import BaseModel

load_dotenv()

# --- Config ---

MODEL = "vertex_ai/gemini-2.5-flash-lite"

# Vertex AI Imagen model used for pose illustrations.
# imagen-3.0-fast-generate-001 is the lightweight ("nano") Imagen 3 variant —
# faster generation time, lower quota cost, quality sufficient for instructional use.
IMAGE_GEN_MODEL = "imagen-3.0-fast-generate-001"

# Vertex AI project / region — reuse the same env vars that LiteLLM reads.
_VERTEXAI_PROJECT = (
    os.getenv("VERTEXAI_PROJECT")
    or os.getenv("VERTEX_PROJECT")
    or os.getenv("GOOGLE_CLOUD_PROJECT", "")
)
_VERTEXAI_LOCATION = os.getenv("VERTEXAI_LOCATION", "us-central1")

SYSTEM_PROMPT = """\
<role>
You are a knowledgeable yoga practice guide specializing in the physical aspects of yoga — \
asanas (poses) and pranayama (breathwork). Your audience ranges from complete beginners \
who have never tried yoga, to experienced practitioners deepening their practice. \
You respond with calm precision, use both Sanskrit and English terminology, and encourage \
safe, mindful exploration.
</role>

<task>
Answer questions about physical yoga practice. Your expertise covers:

YOGA OVERVIEW (for beginners and those new to the practice):
- What yoga is as a physical movement and breathwork discipline
- Major physical yoga styles and their defining characteristics:
    Hatha — foundational, slower-paced individual poses; the ideal starting point
    Vinyasa / Flow — poses linked breath-by-breath in continuous sequences; dynamic
    Ashtanga — a fixed series of poses practiced in set order; physically demanding
    Yin — long passive holds (3–5 minutes) targeting connective tissue; meditative
    Restorative — fully supported poses using props; focused on deep relaxation
    Power — strength-focused vinyasa; athletic in character
- How to choose a style based on goals, current fitness, and experience level
- What pranayama is and how it fits into physical yoga practice
- Major pranayama categories:
    Energizing: Kapalabhati (skull-shining breath), Bhastrika (bellows breath)
    Balancing: Nadi Shodhana (alternate nostril), Box Breathing (sama vritti)
    Calming: Sitali (cooling breath), Chandra Bhedana (left-nostril breath)

ASANAS (Poses):
- Sanskrit and English names, proper alignment cues for each pose
- Physical benefits each pose provides to the body
- Common mistakes practitioners make and how to recognize them
- Modifications and variations for different body types and experience levels
- General contraindications: which poses require caution given stated physical attributes \
(such as limited flexibility, limited range of motion, or structural considerations) \
that do not involve pain, injury, or medical diagnosis

PRANAYAMA (Breathwork):
- Technique names in Sanskrit and English, step-by-step instructions
- Breath ratios, counts, and recommended durations
- Practical effects on the body during and after practice
- How specific breathwork complements specific poses or sequences

SEQUENCING:
- How to pair poses together effectively
- Logical ordering principles — warming up, building toward peak poses, cooling down
- Which breathwork techniques pair well with specific poses or practice styles

PRACTICE PLANS:
- Create structured practice sessions tailored to the user's stated goals, \
experience level, and available time
- Plans specify: warm-up poses, main sequence, cool-down, Savasana, hold durations, \
number of rounds, and any recommended pranayama
- Label each pose with both its English and Sanskrit name
</task>

<output_constraints>
- Respond only to questions within the physical yoga practice scope above.
- When a question includes spiritual, religious, or philosophical dimensions of yoga, \
acknowledge the question and focus your answer on the physical practice dimension; \
suggest that the user explore yoga philosophy texts or a teacher who covers those areas.
- When a question involves general fitness programming, physical therapy, rehabilitation, \
or mental health treatment, acknowledge the question and direct the user to the \
appropriate professional.
- When you are uncertain about a specific claim, say so clearly and recommend the user \
consult a certified yoga teacher for personalized guidance.
- When a question falls entirely outside your scope, state clearly what you can help \
with instead.
</output_constraints>"""

FEW_SHOT_EXAMPLES = [
    {
        "user": "How should I set up Warrior II (Virabhadrasana II)?",
        "assistant": (
            "Stand with feet wide apart — roughly 3.5 to 4 feet, depending on your height. "
            "Turn your front foot out 90° and your back foot in about 15°. Bend your front "
            "knee directly over your ankle, tracking toward your second toe — never letting "
            "the knee collapse inward. Your front thigh works toward parallel with the floor. "
            "Keep your torso upright over your hips; a very common mistake is leaning the "
            "trunk forward over the front leg, which compresses the hip flexor rather than "
            "strengthening it. Extend both arms parallel to the floor, reaching actively "
            "in opposite directions with palms facing down. Gaze over your front fingertips. "
            "Shoulders stay relaxed and drawn away from the ears. Hold 5–10 steady breaths "
            "per side, pressing evenly through both feet."
        ),
    },
    {
        "user": "What is Nadi Shodhana and how do I practice it?",
        "assistant": (
            "Nadi Shodhana (alternate nostril breathing) is a pranayama that alternates "
            "breath between the left and right nostrils, producing a calming, balancing "
            "effect on the nervous system. "
            "To practice: Sit comfortably with a tall spine. Bring your right hand into "
            "Vishnu mudra — fold the index and middle fingers toward the palm, leaving "
            "the thumb, ring finger, and pinky extended. "
            "Close your right nostril with your right thumb. Inhale slowly through your "
            "left nostril for a count of 4. Close both nostrils (ring finger closes the "
            "left), hold briefly — a 4-count retention is standard for beginners, though "
            "retention can be omitted when starting out. Release the right nostril and "
            "exhale fully for a count of 8. Inhale through the right nostril for 4. Close "
            "both, retain for 4. Exhale through the left for 8. That is one complete cycle. "
            "The 1:1:2 inhale-retention-exhale ratio (4-4-8) supports parasympathetic "
            "activation. Begin with 5–10 cycles and gradually extend the session. "
            "Practice on an empty stomach, ideally in the morning or before meditation."
        ),
    },
    {
        "user": "What poses work well right before Savasana to wind down?",
        "assistant": (
            "Effective pre-Savasana sequencing moves progressively toward stillness. "
            "A reliable closing arc: "
            "Supine Spinal Twist (Supta Matsyendrasana) — releases accumulated tension "
            "in the spine and outer hips after standing work; hold 1–2 minutes per side. "
            "Happy Baby (Ananda Balasana) — gently opens the inner groin and lower back; "
            "rocking side to side provides a light spinal massage. "
            "Legs-Up-the-Wall (Viparita Karani) — promotes venous return, cools the "
            "nervous system, and is accessible for most practitioners; 3–5 minutes is ideal. "
            "Reclined Bound Angle (Supta Baddha Konasana) — passive hip opener that "
            "encourages the body to release without effort. "
            "Before settling into Savasana, take 1–2 minutes of slow diaphragmatic "
            "breathing — extend the exhale to twice the length of the inhale. "
            "This exhale emphasis signals the nervous system to downshift before complete rest."
        ),
    },
    {
        "user": "What does the chakra system say about forward folds?",
        "assistant": (
            "Chakra theory belongs to yoga's philosophical and energetic traditions, "
            "which fall outside my focus — I concentrate on the physical practice of "
            "asanas and pranayama. For chakra system resources, I'd recommend exploring "
            "yoga philosophy texts or an instructor who teaches subtle body anatomy. "
            "What I can tell you about forward folds from a physical standpoint: "
            "they lengthen the posterior chain — hamstrings, calves, and erector spinae. "
            "Seated forward folds gently decompress the lumbar spine when the pelvis "
            "tilts forward freely. The forward-folding shape, combined with a slow "
            "extended exhale, activates the parasympathetic nervous system, producing "
            "a calming physiological response. This makes forward folds a reliable "
            "transition toward restorative work or Savasana."
        ),
    },
    {
        "user": "I've never done yoga before. What actually is it and where do I start?",
        "assistant": (
            "Yoga, as a physical practice, is a discipline that combines intentional body "
            "movement, breath control, and body awareness. You move through poses (asanas) "
            "while coordinating your breath — the breath is what separates yoga from "
            "ordinary stretching or calisthenics. The physical benefits include improved "
            "flexibility, muscular strength and endurance, better posture, and a calmer "
            "nervous system through the breathwork component.\n\n"
            "For a complete beginner, the most approachable styles are:\n"
            "- Hatha yoga — slower-paced classes that introduce individual poses with "
            "clear alignment guidance. The best starting point.\n"
            "- Gentle Vinyasa — a flowing style, but taught at a beginner pace with "
            "modifications offered throughout.\n"
            "- Yin yoga — long, passive holds (3–5 minutes per pose) that are very "
            "accessible physically, though they require patience.\n\n"
            "Where to start practically: Begin with foundational poses — Mountain Pose "
            "(Tadasana), Child's Pose (Balasana), Downward-Facing Dog (Adho Mukha "
            "Svanasana), Warrior I and II, and Cat-Cow (Marjaryasana-Bitilasana). "
            "These appear in almost every class and teach the key principles of alignment "
            "and breath. A 20–30 minute beginner class practiced 3 times per week builds "
            "a solid foundation. Add basic pranayama — starting with simple diaphragmatic "
            "breathing or Box Breathing — once the poses feel familiar."
        ),
    },
    {
        "user": "Can you create a 20-minute morning yoga practice for a complete beginner?",
        "assistant": (
            "Here is a structured 20-minute beginner morning practice:\n\n"
            "OPENING BREATH (2 minutes)\n"
            "Box Breathing (Sama Vritti) — Seated comfortably, inhale for 4 counts, "
            "hold for 4, exhale for 4, hold for 4. Repeat 6–8 cycles. Settles the "
            "nervous system and brings attention inward.\n\n"
            "WARM-UP (4 minutes)\n"
            "Cat-Cow (Marjaryasana-Bitilasana) — On hands and knees, alternate arching "
            "and rounding the spine with the breath. 8–10 slow rounds.\n"
            "Child's Pose (Balasana) — Rest with hips toward heels, arms extended forward "
            "or alongside the body. Hold 5–8 breaths.\n\n"
            "STANDING SEQUENCE (8 minutes)\n"
            "Mountain Pose (Tadasana) — Stand tall, feet hip-width. 5 steady breaths. "
            "Establishes ground and posture.\n"
            "Warrior I (Virabhadrasana I) — Step back into a lunge, front knee over "
            "ankle, arms overhead. 5 breaths each side.\n"
            "Warrior II (Virabhadrasana II) — Open the hips and arms wide, gaze forward. "
            "5 breaths each side.\n"
            "Downward-Facing Dog (Adho Mukha Svanasana) — Inverted V-shape, press "
            "through palms and heels. 8 breaths.\n\n"
            "FLOOR COOL-DOWN (4 minutes)\n"
            "Seated Forward Fold (Paschimottanasana) — Legs extended, hinge forward from "
            "the hips (not the waist). Hold 8 breaths.\n"
            "Reclined Spinal Twist (Supta Matsyendrasana) — Lie on back, draw one knee "
            "across the body. 5 breaths each side.\n\n"
            "SAVASANA (2 minutes)\n"
            "Corpse Pose (Savasana) — Lie flat, let the body fully release. Breathe "
            "naturally. Allow 2 full minutes without movement."
        ),
    },
]


def build_initial_messages() -> list[dict]:
    """Build the initial message list with system prompt and few-shot examples."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for example in FEW_SHOT_EXAMPLES:
        messages.append({"role": "user", "content": example["user"]})
        messages.append({"role": "assistant", "content": example["assistant"]})
    return messages


# --- Safety Backstop ---

SAFETY_PATTERNS = [
    r"\bpain\b",
    r"\bhurt(?:s|ing)?\b",
    r"\binjur(?:y|ied|ies)\b",
    r"\bpregnant\b",
    r"\bpregnancy\b",
    r"\bsurger(?:y|ies)\b",
    r"\bpost[.\-\s]?op\b",
    r"\bpost[.\-\s]?surg\w*\b",
    r"\brecovering\b",
    r"\brecovery\b",
    r"\bherniated\b",
    r"\bsciatica\b",
    r"\bosteoporosis\b",
    r"\bmedical\s+condition\b",
]

SAFETY_RESPONSE = (
    "Your question touches on something that may involve physical discomfort, an injury, "
    "a medical condition, pregnancy, or post-surgery recovery. For your safety, I strongly "
    "recommend consulting a qualified yoga instructor or licensed healthcare professional "
    "before beginning or modifying your practice. They can provide personalized guidance "
    "appropriate to your specific situation. I'm happy to answer general questions about "
    "yoga poses and breathwork that don't involve individual health concerns."
)


def check_safety(message: str) -> str | None:
    """Return the safety response if the message triggers a safety keyword, else None."""
    for pattern in SAFETY_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE):
            return SAFETY_RESPONSE
    return None


# --- Pose Image Generation (Vertex AI Imagen) ---

# Map of lowercase question substrings → canonical pose name fed into the image prompt.
# Ordered most-specific first so longer / more-precise keys match before catch-alls.
POSE_NAME_MAP: dict[str, str] = {
    # ── Downward-Facing Dog ──────────────────────────────────────────
    "adho mukha svanasana":     "Adho Mukha Svanasana (Downward-Facing Dog)",
    "downward-facing dog":      "Downward-Facing Dog (Adho Mukha Svanasana)",
    "downward dog":             "Downward-Facing Dog",
    # ── Warriors (specific variants before catch-all) ────────────────
    "virabhadrasana ii":        "Warrior II (Virabhadrasana II)",
    "virabhadrasana i":         "Warrior I (Virabhadrasana I)",
    "warrior iii":              "Warrior III (Virabhadrasana III)",
    "warrior ii":               "Warrior II",
    "warrior i":                "Warrior I",
    "warrior pose":             "Warrior Pose",
    "warrior":                  "Warrior Pose",
    # ── Tree Pose ────────────────────────────────────────────────────
    "vriksasana":               "Tree Pose (Vriksasana)",
    "vrksasana":                "Tree Pose (Vrksasana)",
    "tree pose":                "Tree Pose",
    # ── Triangle Pose ────────────────────────────────────────────────
    "trikonasana":              "Triangle Pose (Trikonasana)",
    "triangle pose":            "Triangle Pose",
    "triangle":                 "Triangle Pose",
    # ── Child's Pose ─────────────────────────────────────────────────
    "balasana":                 "Child's Pose (Balasana)",
    "child's pose":             "Child's Pose",
    "childs pose":              "Child's Pose",
    "child pose":               "Child's Pose",
    # ── Cobra ────────────────────────────────────────────────────────
    "bhujangasana":             "Cobra Pose (Bhujangasana)",
    "cobra pose":               "Cobra Pose",
    "cobra":                    "Cobra Pose",
    # ── Upward-Facing Dog ────────────────────────────────────────────
    "urdhva mukha svanasana":   "Upward-Facing Dog (Urdhva Mukha Svanasana)",
    "upward-facing dog":        "Upward-Facing Dog",
    "upward dog":               "Upward-Facing Dog",
    # ── Chair Pose ───────────────────────────────────────────────────
    "utkatasana":               "Chair Pose (Utkatasana)",
    "chair pose":               "Chair Pose",
    # ── Bridge Pose ──────────────────────────────────────────────────
    "setu bandha sarvangasana": "Bridge Pose (Setu Bandha Sarvangasana)",
    "setu bandhasana":          "Bridge Pose",
    "bridge pose":              "Bridge Pose",
    "bridge":                   "Bridge Pose",
    # ── Shoulderstand ────────────────────────────────────────────────
    "salamba sarvangasana":     "Shoulderstand (Salamba Sarvangasana)",
    "sarvangasana":             "Shoulderstand",
    "shoulderstand":            "Shoulderstand",
    "shoulder stand":           "Shoulderstand",
    # ── Seated Forward Fold ──────────────────────────────────────────
    "paschimottanasana":        "Seated Forward Fold (Paschimottanasana)",
    "seated forward fold":      "Seated Forward Fold",
    "forward fold":             "Standing Forward Fold",
    # ── Camel Pose ───────────────────────────────────────────────────
    "ustrasana":                "Camel Pose (Ustrasana)",
    "camel pose":               "Camel Pose",
    "camel":                    "Camel Pose",
    # ── Boat Pose ────────────────────────────────────────────────────
    "paripurna navasana":       "Boat Pose (Paripurna Navasana)",
    "navasana":                 "Boat Pose",
    "boat pose":                "Boat Pose",
    "boat":                     "Boat Pose",
    # ── Pigeon Pose ──────────────────────────────────────────────────
    "eka pada rajakapotasana":  "Pigeon Pose (Eka Pada Rajakapotasana)",
    "kapotasana":               "Pigeon Pose",
    "pigeon pose":              "Pigeon Pose",
    "pigeon":                   "Pigeon Pose",
    # ── Wheel / Upward Bow ───────────────────────────────────────────
    "urdhva dhanurasana":       "Wheel Pose (Urdhva Dhanurasana)",
    "chakrasana":               "Wheel Pose",
    "wheel pose":               "Wheel Pose",
    "wheel":                    "Wheel Pose",
    # ── Savasana / Corpse Pose ───────────────────────────────────────
    "shavasana":                "Savasana (Corpse Pose)",
    "savasana":                 "Savasana",
    "corpse pose":              "Corpse Pose",
    # ── Chaturanga ───────────────────────────────────────────────────
    "chaturanga dandasana":     "Chaturanga Dandasana",
    "chaturanga":               "Chaturanga",
}

# In-memory cache: canonical pose name → base64 data URL.
# Prevents regenerating the same pose on subsequent requests.
_IMAGE_CACHE: dict[str, str] = {}

# Lazily initialized Imagen model (avoids import cost at startup).
_imagen_model = None


def _get_imagen_model():
    """Lazily initialize and return the Vertex AI Imagen model (singleton)."""
    global _imagen_model
    if _imagen_model is None:
        import vertexai
        from vertexai.preview.vision_models import ImageGenerationModel

        vertexai.init(project=_VERTEXAI_PROJECT, location=_VERTEXAI_LOCATION)
        _imagen_model = ImageGenerationModel.from_pretrained(IMAGE_GEN_MODEL)
    return _imagen_model


def detect_pose_name(question: str) -> str | None:
    """Return the canonical pose name if the question names a specific asana, else None."""
    q = question.lower()
    for key, name in POSE_NAME_MAP.items():
        if key in q:
            return name
    return None


def generate_pose_image(question: str) -> str | None:
    """Generate a yoga pose illustration via Vertex AI Imagen.

    1. Extracts a canonical pose name from the question (returns None if none found).
    2. Returns a cached base64 data URL on repeated requests for the same pose.
    3. Calls Imagen to generate a new image and caches + returns it as a data URL.
    4. Fails silently on any error — the app continues without an image.
    """
    pose_name = detect_pose_name(question)
    if not pose_name:
        return None

    if pose_name in _IMAGE_CACHE:
        return _IMAGE_CACHE[pose_name]

    try:
        model = _get_imagen_model()
        prompt = (
            f"A yoga instructor demonstrating {pose_name} on a plain white background. "
            "Full body view, clear alignment visible, instructional diagram style, "
            "clean and minimal, suitable for a yoga practice guide."
        )
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="1:1",
        )
        image_bytes: bytes = response.images[0]._image_bytes
        b64 = base64.b64encode(image_bytes).decode()
        data_url = f"data:image/png;base64,{b64}"
        _IMAGE_CACHE[pose_name] = data_url
        return data_url
    except Exception:
        return None  # Fail silently; app continues without image


# --- LLM Call ---


def generate_response(messages: list[dict]) -> str:
    """Generate a response using LiteLLM.

    Args:
        messages: List of message dicts with 'role' and 'content' keys.

    Returns:
        The assistant's response text.
    """
    try:
        response = completion(model=MODEL, messages=messages)
        return response.choices[0].message.content
    except Exception as e:
        return f"Something went wrong: {e}"


# --- Session Management ---

# Each session stores a list of messages in OpenAI format:
# [
#     {"role": "system", "content": "..."},
#     {"role": "user", "content": "Hello!"},
#     {"role": "assistant", "content": "..."},
#     ...
# ]
sessions: dict[str, list[dict]] = {}


# --- FastAPI App ---

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    image_url: str | None = None


@app.get("/")
def index():
    return FileResponse("index.html")


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    # Safety backstop — intercept before any LLM call
    safety_reply = check_safety(request.message)
    if safety_reply:
        return ChatResponse(response=safety_reply, session_id=session_id, image_url=None)

    # Get or create session
    if session_id not in sessions:
        sessions[session_id] = build_initial_messages()

    # Add user message to conversation
    sessions[session_id].append({"role": "user", "content": request.message})

    # Generate response
    response_text = generate_response(sessions[session_id])

    # Add assistant response to conversation history
    sessions[session_id].append({"role": "assistant", "content": response_text})

    # Generate pose illustration via Vertex AI Imagen (fails silently if no pose detected)
    image_url = generate_pose_image(request.message)

    return ChatResponse(response=response_text, session_id=session_id, image_url=image_url)


@app.post("/clear")
def clear(session_id: str | None = None):
    if session_id and session_id in sessions:
        del sessions[session_id]
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
