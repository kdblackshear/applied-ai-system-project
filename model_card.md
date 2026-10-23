What are the limitations or biases in your system?
    A couple limitations that the system possesses include a keyword boundary because the RAG retrieval pipeline relies on specific keywords, it may miss semantics if the input complex or contains too many nuances. Also, the system has a static knowledge base, meaning all of the veterinary information is hardcoded and can't adat to real time events. In terms of biases, there is a species scope bias. The Pawpal+ : AI system is heavily geared and optimized towards dogs and cats. This offers limited guidence for other species. 

Could your AI be misused, and how would you prevent that?
    AI missue could happen when it comes to the medical advice given. Pet owners may take it as professional advice and not take meaures to seek out a veterinarian. This has attempted to be prevented through safety guardrails that include hardcoded keyword intercept filters. Any question that contains emergency terms bypasses the RAG synthesis and the user is redirected to a professional anmal hospital.

What surprised you while testing your AI's reliability?
    During testing, I was surprised to find that the AI system could not handle exact calendar scheduling anf often hallucinated solutions. Due to this problem, I took this taks out of AI's hands and kept it in deterministic Python. 

Collaboration with AI:
    For this project, I work with Gemini AI to plan, design, and build the new and improved Pawpal+ system with RAG. I accepted it's suggestion to use a logging module to provide runtime logs clearly showing RAG document retrieval score and guardrail triggers. One of the suggestions that I rejected was the intial suggestion to use external databases with heavy C++ and API keys. This suggestion was rejected because it would make the program less reproducible and no longer a lightweight solution. Instead, we opted for Python in memoery search function that had the ability of full RAG semantics with out the external setup.

Testing Summary:
    When testing, the things that worked included time overlap detection across different pets, emergency guardrails that intercepted medical risk keywords, and the RAG retriever consistently surfacing care documentation for queries regading things like dog excersie and cat medication. 

    In terms of things that did not work, there was an inital bug with filtering mutiple pet's completed tasks. These completed task were being hidden incorrectly across pets. To fix it, the task filtering had to be made a single-pass across all pet objects. From this, I learned that relying solely on generative AI is not smart because it is untrustworthy for exact math. Using a hybrid of deterministic code and AI for logic and reasoning, respectively, is a much more reliable arichitecture.

    I opted for an automated unit and integration test. After running it, 8 out of 8 tests passed (100% pass rate). 
