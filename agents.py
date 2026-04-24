# agents.py

def analyzer_agent(query, llm):
    return llm.invoke(f"""
    You are the EduMind Analyzer Agent.
    
    Analyze this student query and identify:
    - Key concepts being asked
    - Topic area it belongs to
    - Depth of answer required (basic/intermediate/advanced)
    
    Query: {query}
    
    Return a precise 2-line analysis only.
    """).content


def structure_and_polish_agent(answer, llm):
    return llm.invoke(f"""
    You are the EduMind Structure & Polish Agent.
    
    Format the following content into a beautifully structured, highly detailed study guide.
    CRITICAL INSTRUCTION: You MUST preserve all facts, explanations, details, and deeply technical points. DO NOT condense or remove information.
    Use headings, bullet points, and bold text for key concepts to improve readability, but keep the answer fully detailed and expansive.
    
    Content: {answer}
    """).content


def summarizer_agent(answer, llm):
    return llm.invoke(f"""
    You are the EduMind Summarizer Agent.
    
    Condense the following content into a clear, structured, and short summary.
    Use bullet points for key concepts. Focus strictly on brevity.
    Keep it student-friendly and exam-focused.
    
    Content: {answer}
    """).content


def feedback_agent(user_answers, questions, context, llm):
    return llm.invoke(f"""
    You are the EduMind Evaluator Agent.
    
    Evaluate the student's answers against the source material.
    
    Source Material:
    {context}
    
    Questions Asked:
    {questions}
    
    Student's Answers:
    {user_answers}
    
    Provide a structured Report Card:
    
    Overall Score: X/100
    
    Question-by-Question Review:
    - For each answer: what was correct, what was missing
    
    Strengths: What the student did well
    
    Areas to Improve: Topics that need more practice
    
    Study Tip: One specific actionable tip for next session
    
    Be fair, specific, and encouraging. No emojis.
    """).content


def question_generator_agent(context, llm, history=[], count=5):
    # Get previous questions from memory to avoid repetition
    past_questions = ""
    for m in history:
        if isinstance(m, dict):
            content = m.get("content", "")
            if isinstance(content, str) and len(content) > 50:
                past_questions += content[:300] + "\n"

    return llm.invoke(f"""
    You are the EduMind Question Generator Agent.
    
    Generate exactly {count} exam questions based ONLY on the 
    core concepts in the study material below.
    
    Rules:
    - Focus on KEY CONCEPTS only
    - Ignore metadata like course codes, batch years, URLs, book titles
    - Each question must test deep understanding — not memorization
    - Keep each question clear and under 2 lines
    - Number them 1 to {count}
    - Mix question types: explain, compare, analyze, apply
    - Do NOT repeat these previous questions: {past_questions[:500]}
    
    Study Material:
    {context}
    
    Generate {count} clean concept-based exam questions now:
    """).content
