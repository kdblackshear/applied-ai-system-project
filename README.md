Original Project: Pawpal+
    Summary: 
        The original Pawpal+ system was built as an app that aids pet owners in organizing the schedules of their pets based on its needs. The application tracked individual routines and care tasks and created a master schedule/daily task list to prevent any double booking. It allowed the user to add their pets with a name, type, medical notes, and task priorities. Pawpal+, overall, made having and caring for pets much easier and organized. 

Title: Pawpal+ : AI-Powered Pet Care Planner
    Summary:
        The new AI-powered system does all of the things that the original Pawpal+ system did, but it is now augmented with a Retrieval-Augmented Generation. RAG is used as an AI advisor and conflict analyzer for the daily task scheduling. It will now automatically detect overlaps in scheduling, retrieve guidence from veterinary professionals for pet care, and generate a dynamic and flexible daily care plan. 

        This is important because users value balance in their pet's care when it comes to pairing tasks with harsh time constraints with the specific needs of their pet. The PawPal+ : AI-Powered Pet Care Planner bridges this gap and allows for the intelligent planning and maintenance of a pet's health, while making things much eaiser for the owner to keep up with.

Architecture Overview: 
    System Flow (Input → Process → Output):
        Input: 
            User registers pets, sets owner preferences (max daily minutes), and submits daily tasks or care queries via the Streamlit interface.

    Process:
        Rule-Based Scheduler: 
            Validates task durations, time windows, and detects overlapping task times.

        RAG Retriever: 
            Searches an internal knowledge base of veterinary guidelines based on the task/query.

        AI Advisor & Agent: 
            Integrates retrieved context with individual pet profile notes to generate personalized daily plans and advice.

    Output: 
        Interactive schedule breakdown with priority ratings, warning alerts for time conflicts, and evidence-backed care advice.

    Human & Safety Interventions:
        Input Guardrails: 
            An emergency keyword filter flags high-risk queries (e.g., poisoning, severe injury) and instantly redirects the user to emergency veterinary contacts instead of generating advice.

        Human-in-the-Loop: 
            Owners review all generated daily plans, override scheduled task times, and manually mark tasks complete.

Setup Instructions:
    Prerequisites: 
        Python 3.9 or higher
    
    Step 1:
        Install dependencies (i.e. python3 pip install -r requirements.txt)
    
    Step 2:
        Launch web application (i.e. streamlit run streamlit_app.py)
    
    Step 3:
        Access in browser (i.e http://localhost:8501)

Sample Interactions:
    Example 1: Time Conflict Detection

        Input: 
            Task 1: "Morning Walk" (8:30 AM – 9:15 AM). Task 2: "Vet Consultation Call" (8:45 AM – 9:15 AM).

        Output: 
            ⚠️ Scheduling Warning: 'Vet Consultation Call' (08:45 AM) overlaps with 'Morning Walk' assigned to Buster at 08:30 AM!

    Example 2: RAG AI Care Consultation

        Input Query: 
            "How long should I walk my high-energy dog in the summer?"

        Retrieved Context: 
            [doc1: dog exercise requirements], [doc3: heat safety rules]

        Output: 
            "Based on your pet Buster (Dog - High energy): Dogs require 30-60 minutes of exercise. However, according to veterinary guidelines: 'Never walk dogs on asphalt when temperatures exceed 85°F (29°C) to prevent paw pad burns.' Plan walks during early morning hours."

    Example 3: Emergency Safety Guardrail

        Input Query: 
            "My cat ingested chocolate and is bleeding, what do I do?"

        Output: 
            ⚠️ Safety Alert: Your query indicates a potential veterinary emergency. Please contact your nearest emergency animal hospital immediately!

Design Decisions:
    For this new AI-powered system, local in-memory RAG was used, meaning a structured keyword retriveal module (KnowledgeBaseRAG) was used and written purely in Python. The tradeoff is that it keep the setup lightweight and easily reproducible without needing an external database or the use of C++, all while still fulfilling the RAG semantics.

    Also, the new system utilizes a rule based schdueler + a generative AI layer. This keeps a strcit schedule constraint to avoid and check for time conflicts in rule-based python while giving the tasks of generating contextual advice and plan summaries to AI. The tradeoff in this is that it prevents AI hallucinations when it comes to scheduling while leveraging the AI's strengths for care recommendations.

Testing Summary:
    When testing, the things that worked included time overlap detection across different pets, emergency guardrails that intercepted medical risk keywords, and the RAG retriever consistently surfacing care documentation for queries regading things like dog excersie and cat medication. 

    In terms of things that did not work, there was an inital bug with filtering mutiple pet's completed tasks. These completed task were being hidden incorrectly across pets. To fix it, the task filtering had to be made a single-pass across all pet objects. From this, I learned that relying solely on generative AI is not smart because it is untrustworthy for exact math. Using a hybrid of deterministic code and AI for logic and reasoning, respectively, is a much more reliable arichitecture.

    I opted for an automated unit and integration test. After running it, 8 out of 8 tests passed (100% pass rate). 

Reflection:
    Building Pawpal+ : AI-Powered Pet Care Planner gave me insight into how AI can and should be incorporated into programs, as well as the value it hold for the user of the program. Using RAG has taught me that designing using AI system requires a level of anticipation and thorough thinking when it comes to safety risks, guardarails, and guaranteeting a relaible solution. 

Demo Evidence:
    1. Input: 
        Task 1: Morning Walk (8:30 AM - 9:15 AM) assigned to Buster
        Task 2: Vet Consultation Call (8:45 AM - 9:15 AM) assigned to Luna
    
    Output:
    '''
    ⚠️ Scheduling Warning: 'Vet Consultation Call' (08:45 AM) overlaps with 'Morning Walk' assigned to Buster at 08:30 AM!
    '''

    2. Input:
        "How long should I walk my high-energy dog and what are heat safety rules?"
    
    Output:
    '''
    Based on your household pets (Pet: Buster (Dog) - Notes: High energy, needs morning exercise.):

    AI Recommendation:
    To address 'How long should I walk my high-energy dog and what are heat safety rules?', ensure you factor in your pet's specific routine. According to veterinary guidelines: "Dogs require at least 30-60 minutes of daily physical activity depending on breed. Never walk dogs on asphalt when temperatures exceed 85°F (29°C) to prevent paw pad burns."

    🔍 RAG Knowledge Sources Retrieved: dog exercise, heat safety
    '''

    3. Input:
        "My cat ingested poison and is bleeding, what should I do?"
    
    Output:
    '''
    ⚠️ Safety Alert: Your query indicates a potential veterinary emergency. Please contact your nearest emergency animal hospital immediately!
    '''