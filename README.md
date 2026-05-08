# Hippocratic AI: Bedtime Story Weaver

An agentic, multi-stage story generation pipeline designed to create safe, engaging, and age-appropriate (5-10 years) bedtime stories. 

# How to run
1. Before running **_main.py_**, run the following command in the terminal to install the correct packages if they aren't already installed on your machine.
``` bash
    pip install -r requirements.txt
```
2. Ensure you have a functional API key in the **_keys.env_** file as a string in the line: **OPENAI_API_KEY="[Your API Key]"**
3. Run **_main.py_** and interact with the prompts in the terminal!

## System Architecture: The Actor-Critic Loop
To ensure high quality and safety, this system does not rely on zero-shot generation. Instead, it utilizes an Actor-Critic architecture where two distinct LLM personas interact programmatically.

```mermaid
graph TD
    User([User Request]) --> Author[Author Agent: GPT-3.5]
    Author -->|Generates Draft| Judge[Judge Agent: GPT-3.5]
    Judge -->|JSON Evaluation| Logic{Approved?}
    Logic -->|No + Critique| Author
    Logic -->|Yes| Output([Safe Bedtime Story])

    subgraph Rubric ["Evaluation Rubric"]
    Judge --- Safety[Safety Score]
    Judge --- Age[Age Relevance]
    Judge --- Quality[Narrative Quality]
    end

    style User fill:#f9f,stroke:#333,stroke-width:2px,color:#000
    style Output fill:#bfb,stroke:#333,stroke-width:2px,color:#000
    style Logic fill:#f96,stroke:#333,stroke-width:2px,color:#000
