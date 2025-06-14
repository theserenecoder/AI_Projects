# MultiModal RAG Agent with Tavily

This repository contains a LangChain-powered MultiModal RAG (Retrieval Augmented Generation) agent. The agent is designed to answer user queries by leveraging both textual and visual information from a document, and can also utilize external tools like Tavily Search for information outside its internal knowledge base.

## Features

* **Multi-Modal RAG:** Processes and retrieves information from both text and image elements within PDF documents.
* **Intelligent Routing:** A supervisor agent intelligently routes user queries to either the internal RAG system (for LLM/Transformer-related topics) or a general LLM with tool-use capabilities (for broader or real-time information needs).
* **Dynamic Tool Use:** Integrates with Tavily Search to access up-to-date external information when required.
* **Response Validation:** Includes a validation step to ensure the generated responses are relevant and accurate to the original query.
* **Scalable Storage:** Utilizes AstraDB Vector Store for efficient similarity search and InMemoryStore for document storage.

## Architecture

The agent's workflow is orchestrated using LangGraph, defining a state machine with the following key nodes:

1.  **Supervisor:** Analyzes the incoming user query and determines if it's "Related" to LLM/Transformer concepts (requiring RAG) or "Not Related" (can be handled by a general LLM with tools).
2.  **RAG:**
    * Retrieves relevant text and image chunks from the pre-processed document store based on the user's query.
    * Constructs a multi-modal prompt incorporating both text context and image descriptions.
    * Generates an answer using `gpt-4o-mini`.
3.  **LLM:**
    * For "Not Related" queries, directly interacts with `gpt-4o-mini`.
    * Can invoke external tools (currently Tavily Search) to gather real-time or broader information if needed.
4.  **Tools:** Executes any tool calls made by the `LLM` node (e.g., Tavily Search).
5.  **Validation:** Evaluates the generated response (from either RAG or LLM) against the original query to determine if it's a "pass" (adequate answer) or "fail" (irrelevant, incomplete, etc.).
6.  **Router Nodes:** Direct the flow of the graph based on the output of the Supervisor, LLM (for tool calls), and Validation nodes.

```mermaid
graph TD
    A[START] --> B(Supervisor);
    B --> C{Router};
    C -- "Related" --> D(RAG);
    C -- "Not Related" --> E(LLM);
    E --> F{Tools Condition};
    F -- "tools" --> G(tools);
    G --> E;
    D --> H(Validation);
    F -- "Validation" --> H;
    H --> I{Validation Router};
    I -- "pass" --> J[END];
    I -- "fail" --> B;