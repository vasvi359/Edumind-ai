# Improvement Plan for EduMind AI

This plan outlines several key improvements to enhance the user experience, performance, and robustness of the EduMind AI study companion.

## Proposed Changes

### 1. UI/UX Enhancements
*   **Streaming Responses**: Replace the `typewriter` function with Streamlit's native `st.write_stream` for a more responsive and standard AI chat experience.
*   **Dynamic Thinking Indicators**: Use `st.status` to show what the agents are doing in the background (e.g., "Analyzing query...", "Searching notes...", "Generating summary...").
*   **Tabs for Multi-Agent Outputs**: Instead of only showing a summary, use `st.tabs` to display the "Detailed Answer", "Quick Summary", and "Exam Questions" separately.

### 2. Logic & Agent Improvements
*   **Conversation Memory**: Integrate `st.session_state` history into the LLM prompt so the AI remembers previous questions in the same session.
*   **Agent Orchestration**: Use the `analyzer_agent` to determine the user's intent. If they want a quiz, go straight to `question_generator_agent`. If they want to be tested, use `evaluator_agent`.
*   **Session-Specific Vector Store**: Move the `vectorstore` from a global variable to `st.session_state` to ensure multi-user compatibility and better state management.

### 3. Security & Robustness
*   **Environment Variables**: Move the hardcoded Groq API key to a `.env` file.
*   **Error Handling**: Add robust error handling for file uploads (corrupt files, unsupported formats) and API failures.
*   **Advanced File Loaders**: Use `LangChain` document loaders (`PyPDFLoader`, `Docx2txtLoader`) for better text extraction accuracy.

### 4. File Structure Changes

#### [MODIFY] [app.py](file:///c:/Users/vasvi%20Bali/OneDrive/Desktop/edumind.ai/app.py)
*   Integrate `st.write_stream`.
*   Use `st.session_state` for chat history and vector store.
*   Update UI to use tabs for different agent outputs.
*   Improved voice input handling.

#### [MODIFY] [backend.py](file:///c:/Users/vasvi%20Bali/OneDrive/Desktop/edumind.ai/backend.py)
*   Implement a router logic based on `analyzer_agent`.
*   Pass conversation history to the chain.
*   Return structured data (Answer, Summary, Questions, etc.) to the frontend.

#### [MODIFY] [rag.py](file:///c:/Users/vasvi%20Bali/OneDrive/Desktop/edumind.ai/rag.py)
*   Refactor to return the vector store object instead of using a global variable.
*   Add cleanup methods.

#### [NEW] [.env](file:///c:/Users/vasvi%20Bali/OneDrive/Desktop/edumind.ai/.env)
*   Store `GROQ_API_KEY`.

---

## Verification Plan

### Automated Tests
*   Run the Streamlit app locally and verify file extraction.
*   Test multiple queries to ensure memory is working correctly.
*   Verify that streaming works as expected.

### Manual Verification
*   Check that "Clear Chat" actually clears everything (including session state memory).
*   Test the "Exam Questions" tab to see if it generates relevant content.
*   Verify that the `.env` file is being read correctly.
