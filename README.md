# NPC v0.10: 

AI Chatbot with Web Search and Code Execution

NPC v0.10 is a sophisticated AI chatbot that combines the power of Llama 3 70B with real-time web search capabilities and an integrated code interpreter. This project showcases the potential of large language models when augmented with external knowledge sources and execution environments.

### Features

- Llama 3 70B Integration: Leverages the Groq API to access one of the most advanced language models available.
- Real-time Web Search: Utilizes Google Custom Search API to extend the AI's knowledge beyond its training cutoff date (December 2023).
- Code Interpreter: Allows the AI to write, execute, and iteratively improve Python code in real-time.
- User-friendly GUI: Built with Tkinter, offering a clean and intuitive interface for interacting with the AI.
- Conversation History: Maintains context across multiple interactions for more coherent and relevant responses.
- Dual-window Display: Separate windows for chat interactions and web search results.

How It Works

- The user inputs a query or request.
- The system performs a web search to gather relevant, up-to-date information.
- The Llama 3 70B model processes the query, incorporating both its training data and the web search results.
- For coding tasks, the AI can generate, execute, and refine Python code based on user requirements.
- The response, including any code output, is displayed in the chat window.

Installation and Setup

- Install Python
- Generate Groq API key
- Generate Google custom search key
- Generate Search engine ID

then replace these things into the code by your own keys and ID and then just hit run and you are good to go.

Usage

- You can use it for alot of Question answering, problem solving and coding problems
- The api keys are free to generate from the respoective sites

Limitations and Future Work

- Currently limited to Python code execution
- Web search results may not always be perfectly relevant
- Future versions may include multi-modal capabilities and integration with more specialized tools

Contributing
We welcome contributions! I will be adding CONTRIBUTING.md for details on how to get started shortly.


License
This project is licensed under the MIT License - see the LICENSE.md file for details.

Acknowledgments

- Meta for the Llama 3 70B model
- Groq for their API services
- Google for the Custom Search API
