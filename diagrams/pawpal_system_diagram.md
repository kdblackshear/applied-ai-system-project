flowchart TD
    %% User & Input Interfaces
    subgraph UI ["User Interface (Streamlit Frontend)"]
        A1[User Inputs Task / Household Setup]
        A2[User Submits AI Advice Query]
    end

    %% Core System & Logic Layer
    subgraph Core ["Core System Logic (Scheduler & Models)"]
        B1[Scheduler Engine]
        B2[Conflict Detection System]
        B3[Daily Task Prioritizer]
    end

    %% RAG & Agentic AI Component
    subgraph AI ["AI Layer (Agent & RAG Pipeline)"]
        C1[Guardrail Safety Filter]
        C2[RAG Knowledge Base Retriever]
        C3[Veterinary Knowledge Base Docs]
        C4[AI Pet Advisor Synthesis Engine]
    end

    %% Testing & Human Verification
    subgraph Feedback ["Evaluation & Human/Testing Checks"]
        D1{Safety / Emergency Check Passed?}
        D2[Human Review / Schedule Visualizer]
        D3[System Logging & Verification]
    end

    %% Data Flow Connections
    A1 --> B1
    B1 --> B2
    B2 --> B3
    B3 --> D2

    A2 --> C1
    C1 --> D1
    
    D1 -- "No (Emergency / Toxicity)" --> A2
    D1 -- "Yes (Safe Query)" --> C2

    C3 -->|Retrieve Context| C2
    C2 -->|Augmented Prompt| C4
    B1 -->|Pet & Owner Context| C4

    C4 --> D3
    D3 --> D2