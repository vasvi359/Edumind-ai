# backend.py

from agents import analyzer_agent, summarizer_agent, feedback_agent, question_generator_agent, structure_and_polish_agent
from rag import retrieve_context


# ============================================
# MEMORY SYSTEM
# Stores conversation context between queries
# ============================================
class EduMindMemory:
    def __init__(self):
        self.current_topic = None        # What topic is being studied
        self.last_questions = None       # Last quiz questions asked
        self.last_context = None         # Last RAG context retrieved
        self.quiz_active = False         # Whether a quiz is in progress
        self.session_history = []        # Last 10 exchanges

    def update(self, topic=None, questions=None, context=None):
        if topic:
            self.current_topic = topic
        if questions:
            self.last_questions = questions
            self.quiz_active = True
        if context:
            self.last_context = context

    def add_to_history(self, role, content):
        self.session_history.append({
            "role": role,
            "content": str(content)[:2000]  # store max 2000 chars per message (prev 500)
        })
        # Keep only last 10 exchanges to manage memory
        if len(self.session_history) > 10:
            self.session_history = self.session_history[-10:]

    def get_recent_history(self, n=4):
        recent = self.session_history[-n:]
        return "\n".join([
            f"{m['role'].upper()}: {m['content']}"
            for m in recent
        ])

    def get_status(self):
        return {
            "topic": self.current_topic,
            "quiz_active": self.quiz_active,
            "history_length": len(self.session_history)
        }


# ============================================
# ORCHESTRATOR
# The brain — decides which agents to call
# based on intent and memory
# ============================================
class EduMindOrchestrator:
    def __init__(self, memory: EduMindMemory):
        self.memory = memory

    def detect_intent(self, query):
        """
        Detects what the student wants to do.
        Returns one of: GENERAL_CHAT, EVALUATE, QUIZ, EXPLAIN, FOLLOWUP, GENERAL
        """
        query_lower = query.lower()

        # General chat — greetings and casual conversation
        if len(query.split()) <= 5 and any(word in query_lower for word in [
            "hi", "hii", "hello", "hey", "thanks", "thank you",
            "ok", "okay", "bye", "good", "great", "nice", "cool",
            "how are you", "who are you", "what are you", "what can you do"
        ]):
            return "GENERAL_CHAT"

        # 1. EVALUATION intent — prioritized over everything else if answers are mentioned
        if any(word in query_lower for word in [
            "my answer", "grade", "evaluate", "score me",
            "check my", "grade my", "here is my answer",
            "my response", "assess", "evaluate those"
        ]):
            return "EVALUATE"

        # 2. FOLLOWUP intent — prioritized to ensure continuity
        if any(word in query_lower for word in [
            "those", "these", "that", "them", "previous", "above",
            "give answers", "answers of", "answer those", "explain those",
            "elaborate", "more about", "continue", "go on", "next",
            "also", "additionally", "furthermore", "what about",
            "what are the answers", "provide answers"
        ]):
            return "FOLLOWUP"

        # 3. QUIZ intent — student wants NEW questions
        if any(word in query_lower for word in [
            "question", "quiz", "exam", "generate questions",
            "important questions", "prepare", "test me", "practice"
        ]):
            return "QUIZ"

        # 4. EXPLAIN intent
        if any(word in query_lower for word in [
            "explain", "what is", "define", "describe",
            "tell me about", "summarize", "overview",
            "how does", "why is", "what are"
        ]):
            return "EXPLAIN"

        return "GENERAL"

    def should_skip_analyzer(self, query, intent):
        """
        Skip analyzer for simple or evaluation queries
        to save tokens and time
        """
        if intent == "EVALUATE":
            return True  # Evaluator doesn't need analysis
        if len(query.split()) < 5:
            return True  # Very short query — skip analysis
        return False

    def should_use_summarizer(self, intent):
        """
        Use summarizer only for explanation and general queries
        """
        return intent in ["EXPLAIN", "GENERAL"]

    def route(self, query, context, llm):
        """
        Main routing function — decides which agents to call
        """
        import re

        intent = self.detect_intent(query)
        agents_used = []

        result = {
            "answer": "",
            "evaluation": "",
            "questions": "",
            "agents_used": [],
            "intent": intent,
            "memory_status": self.memory.get_status()
        }

        # ============================================
        # ROUTE 0 — GENERAL CHAT
        # No agents, no RAG — just friendly conversation
        # ============================================
        if intent == "GENERAL_CHAT":
            answer = llm.invoke(f"""
            You are EduMind AI, a friendly and helpful study assistant.
            Respond naturally and warmly to this message.
            Keep it brief and friendly — 1-2 sentences max.
            Do NOT mention documents, RAG, or study material unless asked.

            Message: {query}
            """).content

            self.memory.add_to_history("user", query)
            self.memory.add_to_history("assistant", answer)

            result["answer"] = answer
            result["intent"] = "GENERAL_CHAT"
            result["agents_used"] = []
            return result

        # ============================================
        # ROUTE 1 — EVALUATE
        # Only Evaluator Agent runs
        # Orchestrator uses memory to find last questions
        # ============================================
        if intent == "EVALUATE":
            agents_used.append("⭐ Evaluator Agent")

            # Use memory to get last quiz questions
            last_questions = self.memory.last_questions
            if not last_questions:
                last_questions = "No previous quiz found in memory."

            evaluation = feedback_agent(
                query,
                last_questions,
                context,
                llm
            )

            # Update memory
            self.memory.quiz_active = False
            self.memory.add_to_history("user", query)
            self.memory.add_to_history("assistant", evaluation)

            result["evaluation"] = evaluation
            result["agents_used"] = agents_used
            return result

        # ============================================
        # ROUTE 2 — QUIZ
        # Analyzer (optional) + Question Generator
        # Orchestrator uses memory topic if available
        # ============================================
        if intent == "QUIZ":

            # Use memory topic if available for better context
            if self.memory.current_topic:
                enriched_context = f"Topic: {self.memory.current_topic}\n\n{context}"
            else:
                enriched_context = context
                self.memory.update(topic=query)

            # Skip analyzer for simple quiz requests
            if not self.should_skip_analyzer(query, intent):
                agents_used.append("🔍 Analyzer Agent")
                analyzer_agent(query, llm)

            # Extract question count from query
            count_match = re.search(r'(\d+)', query)
            count = int(count_match.group(1)) if count_match else 5

            agents_used.append("❓ Question Generator")
            questions = question_generator_agent(
                enriched_context,
                llm,
                history=self.memory.session_history,
                count=count
            )

            # Store in memory for future evaluation
            self.memory.update(
                questions=questions,
                context=enriched_context
            )
            self.memory.add_to_history("user", query)
            self.memory.add_to_history("assistant", questions)

            result["questions"] = questions
            result["agents_used"] = agents_used
            return result

        # ============================================
        # ROUTE 3 — EXPLAIN
        # Analyzer + Summarizer
        # Orchestrator uses conversation history from memory
        # ============================================
        if intent == "EXPLAIN":

            # Analyzer always runs for explanations
            agents_used.append("🔍 Analyzer Agent")
            analyzer_agent(query, llm)

            # Store topic in memory
            self.memory.update(topic=query, context=context)

            # Build prompt using memory history
            memory_history = self.memory.get_recent_history(4)

            answer = llm.invoke(f"""
            You are EduMind AI, a professional study assistant.

            Recent Conversation (from memory):
            {memory_history}

            Source Material:
            {context}

            Student Question: {query}

            Provide a clear, structured answer.
            Use bullet points for key concepts.
            Focus on what will help in exams.
            """).content

            if "summar" in query.lower() or "short" in query.lower():
                agents_used.append("📝 Summarizer Agent")
                final_answer = summarizer_agent(answer, llm)
            else:
                agents_used.append("📝 Structure & Polish Agent")
                final_answer = structure_and_polish_agent(answer, llm)

            self.memory.add_to_history("user", query)
            self.memory.add_to_history("assistant", final_answer)

            result["answer"] = final_answer
            result["agents_used"] = agents_used
            return result

        # ============================================
        # ROUTE 3.5 — FOLLOWUP
        # Student is asking about previous conversation
        # Uses full memory history as primary context
        # ============================================
        if intent == "FOLLOWUP":
            agents_used.append("🔍 Analyzer Agent")

            # Build rich context from memory + RAG
            memory_history = self.memory.get_recent_history(6)
            last_questions = self.memory.last_questions or ""
            last_context = self.memory.last_context or context

            answer = llm.invoke(f"""
            You are EduMind AI, a professional study assistant.

            This is a follow-up question referring to the previous conversation.

            Previous Conversation:
            {memory_history}

            Previous Questions Generated (if any):
            {last_questions}

            Source Material:
            {last_context}

            Follow-up Query: {query}

            Answer this follow-up naturally and completely.
            If the student is asking for answers to previously generated questions,
            provide clear, detailed answers to each of those questions.
            Use the conversation history to understand context.
            """).content
            if "summar" in query.lower() or "short" in query.lower():
                agents_used.append("📝 Summarizer Agent")
                final_answer = summarizer_agent(answer, llm)
            else:
                agents_used.append("📝 Structure & Polish Agent")
                final_answer = structure_and_polish_agent(answer, llm)

            self.memory.add_to_history("user", query)
            self.memory.add_to_history("assistant", final_answer)

            result["answer"] = final_answer
            result["agents_used"] = agents_used
            return result

        # ============================================
        # ROUTE 4 — GENERAL
        # Smart decision based on query complexity
        # ============================================

        # Only run analyzer for complex queries
        if not self.should_skip_analyzer(query, intent):
            agents_used.append("🔍 Analyzer Agent")
            analyzer_agent(query, llm)

        # Use full memory history for context continuity
        memory_history = self.memory.get_recent_history(4)

        answer = llm.invoke(f"""
        You are EduMind AI, a professional study assistant.

        Previous Conversation (use this for context):
        {memory_history}

        Source Material:
        {context}

        Question: {query}

        Answer clearly and concisely.
        If this question refers to anything from the previous conversation, use that context.
        """).content

        # Polisher or Summarizer for longer responses
        if self.should_use_summarizer(intent):
            if "summar" in query.lower() or "short" in query.lower():
                agents_used.append("📝 Summarizer Agent")
                answer = summarizer_agent(answer, llm)
            else:
                agents_used.append("📝 Structure & Polish Agent")
                answer = structure_and_polish_agent(answer, llm)

        self.memory.add_to_history("user", query)
        self.memory.add_to_history("assistant", answer)

        result["answer"] = answer
        result["agents_used"] = agents_used
        return result


# ============================================
# MAIN ENTRY POINT
# Called from app.py
# ============================================
def process_query(query, vectorstore, memory, llm):
    # Check for general chat first — no vectorstore needed
    query_lower = query.lower().strip()
    is_general_chat = len(query.split()) <= 5 and any(word in query_lower for word in [
        "hi", "hii", "hello", "hey", "thanks", "thank you",
        "ok", "okay", "bye", "good", "great", "nice", "cool",
        "how are you", "who are you", "what are you", "what can you do"
    ])

    if is_general_chat:
        orchestrator = EduMindOrchestrator(memory)
        return orchestrator.route(query, "", llm)

    if vectorstore is None:
        return {
            "answer": "Please upload your study notes from the sidebar first to get started!",
            "evaluation": "",
            "questions": "",
            "agents_used": [],
            "intent": "NONE",
            "memory_status": {}
        }

    context = retrieve_context(query, vectorstore)
    orchestrator = EduMindOrchestrator(memory)
    return orchestrator.route(query, context, llm)
