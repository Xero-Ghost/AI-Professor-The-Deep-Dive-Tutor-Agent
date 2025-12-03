import os
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# --- 1. CONFIGURATION ---
print("\n" + "=" * 50)
print("🤖 AI PROFESSOR (Gemini 2.0 - Full Page Read)")
print("=" * 50)

api_key = input("1. Enter Google Gemini API Key: ").strip()
if not api_key: exit("Error: API Key is required.")

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=0.3
    )
except Exception as e:
    exit(f"Error initializing Gemini: {e}")


# --- 2. SEARCH TOOLS ---

def intelligent_search(topic: str, preferred_sources: list[str]):
    print(f"\n🔎 Searching for '{topic}'...")

    with DDGS() as ddgs:
        try:
            # STRATEGY 1: Priority Keyword Search
            if preferred_sources:
                for source in preferred_sources:
                    query = f"{topic} {source}"
                    print(f"   👉 Checking source: {source}...")

                    results = list(ddgs.text(query, region='wt-wt', max_results=1))

                    if results:
                        url = results[0].get('href')
                        if url and (source.lower() in url.lower() or "wiki" in url.lower()):
                            print(f"   ✅ MATCH: {url}")
                            return url

            # STRATEGY 2: General Fallback
            print("   ⚠️ No preferred source match. Searching open web...")
            results = list(ddgs.text(topic, region='wt-wt', max_results=1))

            if results and results[0].get('href'):
                print(f"   ℹ️ Best Result: {results[0]['href']}")
                return results[0]['href']

            return None

        except Exception as e:
            print(f"   [Search Logic Error]: {e}")
            return None


def fetch_content(url: str):
    print(f"📖 Reading FULL content: {url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        # Increased timeout to 20s to allow loading large pages
        resp = requests.get(url, headers=headers, timeout=20)

        if resp.status_code != 200: return None

        soup = BeautifulSoup(resp.content, 'html.parser')

        # Remove junk
        for tag in soup(["header", "footer", "nav", "aside", "form", "iframe", "script", "style", "button"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # UNRESTRICTED: Returns the entire page text
        return "\n".join(lines)
    except:
        return None


# --- 3. MCQ ENGINE ---

def run_mcq_test(topic: str, context: str):
    print("\n" + "=" * 50)
    print(f"📝 QUIZ: {topic.upper()}")
    print("=" * 50)

    score = 0
    total_q = 3

    for i in range(1, total_q + 1):
        # We limit context here just for speed of generating questions,
        # but the teacher part uses the full text.
        prompt = f"""
        Context: {context[:10000]} 
        Task: Create 1 Multiple Choice Question about {topic}.

        STRICT FORMAT:
        QUESTION: [Text]
        A) [Option]
        B) [Option]
        C) [Option]
        D) [Option]
        ANSWER: [Letter Only]
        EXPLANATION: [Reason]
        """

        try:
            response = llm.invoke([HumanMessage(content=prompt)]).content

            parts = response.split("ANSWER:")
            q_text = parts[0].strip()
            rest = parts[1].split("EXPLANATION:")
            ans_letter = rest[0].strip().upper()[0]
            explanation = rest[1].strip()

            print(f"\n[Q{i}] {q_text}")

            while True:
                user_ans = input("\n👉 Answer (A/B/C/D): ").strip().upper()
                if user_ans in ['A', 'B', 'C', 'D']: break

            if user_ans == ans_letter:
                print("✅ CORRECT!")
                score += 1
            else:
                print(f"❌ WRONG. Correct: {ans_letter}")
            print(f"💡 {explanation}")

        except:
            print("Error generating question. Next...")
            continue

    print(f"\n📢 SCORE: {score}/{total_q}")


# --- 4. MAIN LOOP ---

def run_session():
    print("\n--- NEW SESSION ---")
    topic_in = input("2. Topic: ").strip()
    if not topic_in: topic_in = "India"

    print("3. Preferred Source (e.g., wikipedia, geeksforgeeks) [Enter for default]:")
    source_in = input("   > ").strip()

    if source_in:
        sources = [s.strip() for s in source_in.split(",")]
    else:
        sources = []

    # EXECUTION
    url = intelligent_search(topic_in, sources)
    if not url:
        print("❌ Search failed completely.")
        return

    content = fetch_content(url)
    if not content:
        print("❌ Content scrape failed.")
        return

    # TEACHING
    print("\n🤖 Professor: Reading full page and synthesizing...")

    # UNRESTRICTED PROMPT
    teach_prompt = f"""
    You are an expert Professor. 
    SOURCE: {url}
    CONTENT: {content}

    Task: Teach the topic '{topic_in}' using ONLY the content provided above.

    STYLE INSTRUCTIONS:
    1. **Narrative Flow:** Write in smooth, engaging PARAGRAPHS (like a well-written article or ChatGPT response).
    2. **Avoid Lists:** Do NOT use bullet points unless listing specific code syntax or distinct features. 
    3. **Structure:**
       - Start with a comprehensive **Introduction/Definition**.
       - Move into the **Core Concepts/History** (explain the 'Why' and 'How').
       - If it is a coding topic, provide the **Code Example** in a block, then explain the code in a paragraph below it.
    4. **Tone:** Professional, clear, and explanatory.
    """

    try:
        response = llm.invoke([HumanMessage(content=teach_prompt)])
        print("\n" + "=" * 60)
        print(f"🎓 LESSON: {topic_in.upper()}")
        print(f"🔗 Reference: {url}")
        print("=" * 60)
        print(response.content)
    except Exception as e:
        print(f"❌ Error generating lesson (Page might be too huge even for Gemini): {e}")

    # MENU
    while True:
        print("\n" + "-" * 40)
        cmd = input("Command [Test / Next / Quit / Question]: ").strip().lower()

        if cmd == "quit":
            break
        elif "next" in cmd:
            run_session()
            break
        elif "test" in cmd:
            run_mcq_test(topic_in, content)
        else:
            # We use a larger context window for Q&A now
            qa_prompt = f"Context: {content[:20000]}\nUser Question: {cmd}\nAnswer (in a paragraph):"
            resp = llm.invoke([HumanMessage(content=qa_prompt)])
            print(f"\n🤖 Answer: {resp.content}")


if __name__ == "__main__":
    run_session()