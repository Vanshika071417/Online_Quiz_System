"""
AI Quiz Generator Module
Generates structured multiple-choice questions for teachers based on subject, topic, and difficulty.
Supports both Gemini/GenAI API (when API key is set) and a robust offline semantic knowledge engine.
"""

import os
import json
import random
from typing import List, Dict, Any, Optional

# Offline Knowledge Base for instant generation across core topics
TOPIC_TEMPLATES = {
    "python": [
        {
            "text": "What is the primary distinction between mutable and immutable types in Python?",
            "code": "a = [1, 2]\nb = (1, 2)",
            "options": [
                "Mutable types (like lists) can be altered in-place; immutable types (like tuples) cannot",
                "Immutable types use dynamic memory; mutable types are allocated on the stack",
                "Mutable types cannot be passed into functions by reference",
                "Immutable types cannot store primitive integers"
            ],
            "correct": 0,
            "explanation": "In Python, objects whose values can change in-place are mutable (lists, dicts, sets). Tuples and strings are immutable."
        },
        {
            "text": "What does the '__init__' method represent in a Python class?",
            "code": "class Student:\n    def __init__(self, name):\n        self.name = name",
            "options": [
                "The object destructor called upon garbage collection",
                "The constructor/initializer executed when a new instance is instantiated",
                "A static method that creates a database connection",
                "A private decorator restricted to module imports"
            ],
            "correct": 1,
            "explanation": "__init__ is Python's initializer method automatically invoked during object instantiation."
        },
        {
            "text": "How do Python generators optimize memory usage when processing massive datasets?",
            "code": "def number_stream():\n    for i in range(1000000):\n        yield i",
            "options": [
                "By loading all items into high-speed L3 CPU cache",
                "By using lazy evaluation with the 'yield' statement, generating items on-demand",
                "By compiling Python bytecode into C++ pointers",
                "By disabling the Python Global Interpreter Lock (GIL)"
            ],
            "correct": 1,
            "explanation": "Generators produce items lazily one at a time using 'yield', avoiding allocating huge lists in RAM."
        },
        {
            "text": "Which built-in module is used in Python for multithreading and concurrency?",
            "code": None,
            "options": [
                "threading & concurrent.futures",
                "multilog & system.io",
                "async.compile & pythreads",
                "ctypes.kernel & proc"
            ],
            "correct": 0,
            "explanation": "Python provides the 'threading' and 'concurrent.futures' modules for concurrent execution."
        }
    ],
    "web": [
        {
            "text": "In the HTTP/2 and HTTP/3 specifications, what major optimization replaces domain sharding?",
            "code": None,
            "options": [
                "Multiplexing multiple requests over a single TCP/QUIC connection",
                "Converting all JSON payloads into raw XML strings",
                "Enforcing synchronous polling every 10 milliseconds",
                "Restricting browser requests to GET methods only"
            ],
            "correct": 0,
            "explanation": "Multiplexing allows multiple bidirectional request and response streams over a single connection simultaneously without head-of-line blocking."
        },
        {
            "text": "What is the purpose of CORS (Cross-Origin Resource Sharing) in modern browsers?",
            "code": None,
            "options": [
                "To accelerate CSS animation rendering on mobile GPUs",
                "To allow servers to specify who can access their resources via HTTP headers",
                "To compress image assets before transmitting across sockets",
                "To encrypt database passwords in browser localStorage"
            ],
            "correct": 1,
            "explanation": "CORS is a browser security mechanism that uses HTTP headers to tell browsers whether a web app on one origin has permission to access resources from a different origin."
        },
        {
            "text": "Which lifecycle event or hook in single-page applications is ideal for fetching initial API data?",
            "code": None,
            "options": [
                "Component mount / useEffect with an empty dependency array",
                "DOM unload / beforeunload handler",
                "CSS stylesheet compilation callback",
                "Inline HTML onclick event"
            ],
            "correct": 0,
            "explanation": "In React and modern component frameworks, fetching is performed when the component first mounts (e.g. useEffect with [])."
        }
    ],
    "database": [
        {
            "text": "Which ACID property ensures that a transaction either completely finishes or rolls back completely with no partial state?",
            "code": None,
            "options": [
                "Atomicity",
                "Consistency",
                "Isolation",
                "Durability"
            ],
            "correct": 0,
            "explanation": "Atomicity guarantees the 'all-or-nothing' execution of database transactions."
        },
        {
            "text": "What is the primary benefit of creating a B-Tree index on a relational database column?",
            "code": None,
            "options": [
                "Reduces query lookup complexity from O(N) sequential scans to O(log N)",
                "Automatically compresses table files to zero bytes on disk",
                "Prevents any foreign key constraints from being enforced",
                "Converts SQL tables into unstructured NoSQL key-value pairs"
            ],
            "correct": 0,
            "explanation": "B-Tree indexes enable logarithmic time searches, range lookups, and ordered traversals instead of full table scans."
        },
        {
            "text": "Which normalization form requires removing transitive dependencies among non-key attributes?",
            "code": None,
            "options": [
                "Third Normal Form (3NF)",
                "First Normal Form (1NF)",
                "Second Normal Form (2NF)",
                "Boyce-Codd Normal Form (BCNF) strictly for composite keys"
            ],
            "correct": 0,
            "explanation": "A relation is in 3NF if it is in 2NF and has no transitive dependencies between non-prime attributes."
        }
    ],
    "general": [
        {
            "text": "What is the fundamental role of an Operating System's Kernel?",
            "code": None,
            "options": [
                "Serving as the core bridge between software applications and physical hardware resources",
                "Designing graphical web page layouts using CSS stylesheets",
                "Hosting remote Git repositories for source code version control",
                "Providing email notification templates to end users"
            ],
            "correct": 0,
            "explanation": "The kernel manages CPU scheduling, memory allocation, device drivers, and system calls."
        },
        {
            "text": "In computer networking, which layer of the OSI model does the TCP protocol belong to?",
            "code": None,
            "options": [
                "Transport Layer (Layer 4)",
                "Network Layer (Layer 3)",
                "Data Link Layer (Layer 2)",
                "Application Layer (Layer 7)"
            ],
            "correct": 0,
            "explanation": "TCP (Transmission Control Protocol) operates at Layer 4 (Transport Layer)."
        }
    ]
}


def generate_quiz_with_ai(topic: str, num_questions: int = 5, difficulty: str = "Medium") -> List[Dict[str, Any]]:
    """
    Generates a list of question dictionaries for the given topic.
    Checks for Google GenAI / Gemini API if available, otherwise uses the semantic topic engine.
    """
    topic_lower = topic.lower().strip()
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
            You are an expert academic educator. Generate {num_questions} high-quality multiple choice quiz questions on the topic: "{topic}" at difficulty level: "{difficulty}".
            Return ONLY a valid JSON array of objects with the exact schema:
            [
              {{
                "id": "q1",
                "text": "Question text here?",
                "code": null or "optional code snippet",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": 0, // integer index (0-3) of the correct option
                "explanation": "Brief explanation of why this answer is correct."
              }}
            ]
            Do not include markdown code fences or backticks in the response. Return raw JSON only.
            """
            response = model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception as e:
            print(f"GenAI call fallback due to: {e}")

    # Robust Semantic Knowledge Fallback
    chosen_bank = []
    if "python" in topic_lower or "code" in topic_lower or "oop" in topic_lower:
        chosen_bank = TOPIC_TEMPLATES["python"]
    elif "web" in topic_lower or "js" in topic_lower or "html" in topic_lower or "frontend" in topic_lower:
        chosen_bank = TOPIC_TEMPLATES["web"]
    elif "db" in topic_lower or "sql" in topic_lower or "database" in topic_lower or "data" in topic_lower:
        chosen_bank = TOPIC_TEMPLATES["database"]
    else:
        # Merge all available templates for varied general topics
        chosen_bank = TOPIC_TEMPLATES["general"] + TOPIC_TEMPLATES["python"] + TOPIC_TEMPLATES["database"]

    questions = []
    sample_pool = random.sample(chosen_bank, min(num_questions, len(chosen_bank)))
    
    # If more questions requested than sample pool, supplement with parameterized questions
    for idx, template in enumerate(sample_pool):
        q = dict(template)
        q["id"] = f"ai-q-{idx+1}"
        questions.append(q)

    # Pad if requested more
    while len(questions) < num_questions:
        q_idx = len(questions) + 1
        questions.append({
            "id": f"ai-q-{q_idx}",
            "text": f"Regarding '{topic}', which principle is essential for maintaining robust performance and correctness ({difficulty} level)?",
            "code": None,
            "options": [
                f"Adhering to standard design patterns, strict validation, and decoupled architecture in {topic}",
                "Hardcoding all configurations directly into the main thread",
                "Bypassing exception handling to increase CPU clock speed",
                "Disabling network security protocols"
            ],
            "correct": 0,
            "explanation": f"In {topic}, systematic design, validation, and decoupling ensure long-term stability and maintainability."
        })

    return questions[:num_questions]
