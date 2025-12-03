# 🤖 AI Professor Agent (Gemini 2.0)</br>

## 🏆 Problem Statement</br>
In the age of AI, students face two problems:</br>
1.  **Shallow Summaries:** Standard chatbots give brief, surface-level answers without deep technical context.</br>
2.  **Information Overload:** Searching Google leads to ad-heavy websites and SEO spam.</br>

## 💡 Solution</br>
The **AI Professor** is an autonomous agent that acts as a strict academic tutor. It does not hallucinate; it reads.</br>
1.  **Intelligent Search:** It searches for trusted documentation (e.g., *GeeksForGeeks*, *Wikipedia*) based on user priority.</br>
2.  **Deep Reading:** It uses a custom scraper to read **100% of the webpage text** (unrestricted context window).</br>
3.  **Narrative Teaching:** It synthesizes the raw data into a structured lecture (Definition -> Concepts -> Code).</br>
4.  **Active Recall:** It generates interactive **MCQ Quizzes** based strictly on the material read.</br>

## ⚙️ Architecture</br>
-   **Model:** `Gemini 2.0 Flash` (For massive context handling).</br>
-   **Search:** `DuckDuckGo (ddgs)` with Region-Unlocking (`wt-wt`).</br>
-   **Tools:** Custom Python Scraper (`BeautifulSoup`) & MCQ Engine.</br>

## 🚀 How to Run</br>
1.  Clone the repository.</br>
2.  Install dependencies:</br>
    ```bash</br>
    pip install -r requirements.txt </br>
    ```</br>
3.  Run the agent:</br>
    ```bash</br>
    python main.py </br>
    ```</br>
4.  Enter your Google API Key when prompted. </br>
