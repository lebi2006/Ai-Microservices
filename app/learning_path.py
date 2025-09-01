# app/learning_path.py
import json
import re
import traceback
from typing import List, Dict

from langchain_community.chat_models import ChatOllama
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

_RESOURCE_CATALOG = [
    {"topic": "Python Basics", "tags": ["python", "basics"], "desc": "Variables, control flow, functions", "link": "https://docs.python.org/3/tutorial/"},
    {"topic": "NumPy", "tags": ["numpy", "python", "data"], "desc": "Numerical arrays and operations", "link": "https://numpy.org/doc/stable/"},
    {"topic": "Pandas", "tags": ["pandas", "data", "dataframe"], "desc": "Data manipulation with DataFrame", "link": "https://pandas.pydata.org/"},
    {"topic": "Matplotlib", "tags": ["visualization", "matplotlib"], "desc": "Basic plotting", "link": "https://matplotlib.org/stable/tutorials/introductory/pyplot.html"},
    {"topic": "Seaborn", "tags": ["visualization", "seaborn"], "desc": "Statistical visualizations", "link": "https://seaborn.pydata.org/"},
    {"topic": "Exploratory Data Analysis", "tags": ["eda", "statistics"], "desc": "EDA fundamentals", "link": "https://www.kaggle.com/learn/data-analysis"},
    {"topic": "Statistics for Data Science", "tags": ["statistics"], "desc": "Descriptive & inferential statistics", "link": "https://online.stat.psu.edu/statprogram/"},
    {"topic": "Scikit-learn", "tags": ["ml", "scikit-learn"], "desc": "Classic ML algorithms and tools", "link": "https://scikit-learn.org/stable/"},
    {"topic": "Feature Engineering", "tags": ["feature", "ml"], "desc": "Feature construction and selection", "link": ""},
    {"topic": "Model Evaluation", "tags": ["evaluation", "ml"], "desc": "Metrics, cross-validation", "link": ""},
    {"topic": "Project Work", "tags": ["project", "capstone"], "desc": "Real-world dataset project", "link": "https://www.kaggle.com/"},
    {"topic": "SQL Basics", "tags": ["sql", "data"], "desc": "Intro to SQL queries", "link": "https://www.w3schools.com/sql/"},
]


def _retrieve_resources(goal: str, background: str, top_k: int = 8) -> List[Dict]:
    """
    Very small retrieval: score catalog entries by tag/keyword overlap with goal/background.
    Returns top_k matching resources (fall back to first N if nothing matches).
    """
    text = f"{goal} {background or ''}".lower()
    tokens = set(re.findall(r"[a-zA-Z0-9]+", text))
    scored = []
    for item in _RESOURCE_CATALOG:
        score = 0
        for t in item.get("tags", []):
            if t.lower() in tokens:
                score += 2
        if any(tok in item.get("topic", "").lower() for tok in tokens):
            score += 1
        if any(tok in item.get("desc", "").lower() for tok in tokens):
            score += 1
        scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [it for s, it in scored if s > 0]
    if not selected:
        selected = [it for _, it in scored[:top_k]]
    return selected[:top_k]


def _try_parse_json_from_text(raw: str):
    """
    Try to extract the first JSON object or array from raw text and parse it.
    """
    import json
    import re

    obj_match = re.search(r"(\{[\s\S]*\})", raw)
    arr_match = re.search(r"(\[[\s\S]*\])", raw)

    candidate = None
    if obj_match:
        candidate = obj_match.group(1)
    elif arr_match:
        candidate = arr_match.group(1)

    if candidate:
        repaired = re.sub(r",\s*([\}\]])", r"\1", candidate)
        try:
            return json.loads(repaired)
        except Exception:
            try:
                return json.loads("{" + repaired + "}")
            except Exception:
                return None
    return None


def generate_learning_path(goal: str, background: str = None, duration_weeks: int = 8, hours_per_week: int = 6) -> dict:
    """
    Retrieval-augmented generation.
    Returns a dict with keys:
      - weeks: list of {week:int, topics:[str], resources:[{title,link?}], practicals:[str]}
      - raw_text: str (LLM full output)
    """
    try:
        resources = _retrieve_resources(goal, background, top_k=10)
        resources_text_lines = []
        for r in resources:
            resources_text_lines.append(f"- {r['topic']}: {r.get('desc','')}" + (f" ({r.get('link')})" if r.get("link") else ""))

        resources_block = "\n".join(resources_text_lines)

        system_msg = SystemMessagePromptTemplate.from_template(
            "You are an expert curriculum designer. Be pragmatic, concise, and realistic."
        )
        human_template = """
        Using the resources below, design a practical {weeks}-week learning plan to achieve the goal: "{goal}".
        Learner background: {background}
        Weekly time budget: ~{hours_per_week} hours/week.

        Resources (use or replace if needed):
        {resources_block}

        MUST OUTPUT strictly valid JSON only (no surrounding text) in this exact schema:

        {{
          "weeks": [
            {{
              "week": 1,
              "topics": ["topic A", "topic B"],
              "resources": [
                {{"title": "Resource title", "type": "article|video|course", "link": "optional URL"}}
              ],
              "practicals": ["short practical task or project suggestion"]
            }}
            // ... week objects up to {weeks}
          ]
        }}

        Keep topics actionable and realistic. Prefer free, high-quality resources. If you cannot fill all weeks, fill as many as you can.
        """
        human_msg = HumanMessagePromptTemplate.from_template(human_template)

        prompt = ChatPromptTemplate.from_messages([system_msg, human_msg])
        formatted = prompt.format_prompt(
            goal=goal,
            background=background or "unspecified",
            weeks=duration_weeks,
            hours_per_week=hours_per_week,
            resources_block=resources_block
        )

        chat = ChatOllama(model="mistral", temperature=0.2)
        response = chat.invoke(formatted.to_messages())
        raw_text = (response.content or "").strip()

        print("\n=== RAW LLM OUTPUT ===\n")
        print(raw_text)
        print("\n=== END RAW LLM OUTPUT ===\n")

        parsed = _try_parse_json_from_text(raw_text)
        weeks = []
        if parsed:
            if isinstance(parsed, dict) and "weeks" in parsed and isinstance(parsed["weeks"], list):
                for w in parsed["weeks"]:
                    week_no = w.get("week") if isinstance(w.get("week"), int) else None
                    topics = w.get("topics") if isinstance(w.get("topics"), list) else []
                    resources_list = w.get("resources") if isinstance(w.get("resources"), list) else []
                    practicals = w.get("practicals") if isinstance(w.get("practicals"), list) else []
                    weeks.append({
                        "week": week_no if week_no else len(weeks) + 1,
                        "topics": [str(t) for t in topics],
                        "resources": resources_list,
                        "practicals": practicals
                    })
            elif isinstance(parsed, list):
                for idx, w in enumerate(parsed):
                    if isinstance(w, dict):
                        topics = w.get("topics") if isinstance(w.get("topics"), list) else []
                        weeks.append({
                            "week": w.get("week", idx + 1),
                            "topics": [str(t) for t in topics],
                            "resources": w.get("resources", []),
                            "practicals": w.get("practicals", [])
                        })
        else:
            blocks = re.split(r"(?:\n){1,}\s*Week\s*(\d+)\s*:\s*", raw_text, flags=re.IGNORECASE)
            if len(blocks) >= 3:
                it = iter(blocks[1:])
                for weeknum, content in zip(it, it):
                    num = None
                    try:
                        num = int(weeknum)
                    except:
                        num = len(weeks) + 1
                    topics = [ln.lstrip("-• ").strip() for ln in content.splitlines() if ln.strip().startswith(("-", "•"))]
                    if not topics:
                        topics = [ln.strip() for ln in content.splitlines() if ln.strip()][:3]
                    weeks.append({"week": num, "topics": topics, "resources": [], "practicals": []})
        return {"weeks": weeks, "raw_text": raw_text}

    except Exception as e:
        print("\n=== ERROR ===")
        print(e)
        print(traceback.format_exc())
        print("=== END ERROR ===\n")
        return {"weeks": [], "raw_text": f"Error generating plan: {e}"}
