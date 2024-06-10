import os
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox
from groq import Groq
import requests
from bs4 import BeautifulSoup
import datetime

class ChatApp:
    def __init__(self, root):
        self.client = Groq(api_key='YOUR_GROQ_API_KEY')
        self.conversation_history = []
        self.max_history_length = 10
        self.web_search_api_key = 'YOUR_GOOGLE_CUSTOM_SEARCH_API_KEY'
        self.web_search_cx = 'YOUR_SEARCH_ENGINE_ID'
        
        self.root = root
        self.root.title("NPC v0.10")
        self.root.geometry("800x600")  # Updated size
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Chat Window
        self.chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
        self.chat_window.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        # Interaction Results Window
        self.web_results_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
        self.web_results_window.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        # Hide results window initially
        self.web_results_window.grid_remove()

        self.user_entry = tk.Text(root, wrap=tk.WORD, height=5)
        self.user_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
        self.user_entry.bind("<Return>", self.insert_newline)
        self.user_entry.bind("<Shift-Return>", self.check_shift_enter_key)
        
        self.send_button = tk.Button(root, text="Send", command=self.send_input)
        self.send_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.toggle_button = tk.Button(root, text="Show Results", command=self.toggle_results_window)
        self.toggle_button.grid(row=3, column=1, padx=10, pady=10, sticky='e')

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def insert_newline(self, event):
        self.user_entry.insert(tk.INSERT, "\n")
        return "break"

    def check_shift_enter_key(self, event):
        self.send_input()
        return "break"

    def advanced_summarize_history(self):
        user_entries = [entry["content"] for entry in self.conversation_history if entry["role"] == "user"]
        ai_entries = [entry["content"] for entry in self.conversation_history if entry["role"] == "assistant"]
        
        user_summary = "User queries: " + " | ".join(user_entries[-self.max_history_length:])
        ai_summary = "AI responses: " + " | ".join(ai_entries[-self.max_history_length:])
        
        return f"{user_summary}\n{ai_summary}"

    def send_input(self):
        user_input = self.user_entry.get("1.0", tk.END).strip()
        if user_input.lower() == 'quit':
            self.root.quit()
            return

        self.user_entry.delete("1.0", tk.END)  # Clear the entry field after sending
        
        self.conversation_history.append({"role": "user", "content": user_input})

        self.chat_window.config(state='normal')
        self.chat_window.insert(tk.END, f"\nYou: {user_input}\n", 'user')
        self.chat_window.tag_config('user', foreground='blue')
        self.chat_window.config(state='disabled')
        self.chat_window.see(tk.END)

        context_summary = self.advanced_summarize_history()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_prompt = (
            "1. You are a really obedient, knowledgeable and highly capable assistant. "
            "2. For complex queries, take your time to think deeply and break down the problem into smaller, manageable steps. "
            "3. Respond concisely and clearly, using bullet points and simple language when appropriate. "
            "4. Ask clarifying questions if needed to ensure you fully understand the user's request. "
            "5. Provide step-by-step solutions and explanations to help the user understand your reasoning. "
            f"6. The current date and time is {current_time}. "
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"Context summary:\n{context_summary}"},
            *self.conversation_history
        ]

        search_results = self.perform_web_search(user_input)
        self.display_search_results(search_results)  # Show interaction between agents

        try:
            search_results_text = "\n\n".join(search_results)
            messages.append({"role": "system", "content": f"Web search results:\n{search_results_text}"})

            stream = self.client.chat.completions.create(
                messages=messages,
                model="llama3-70b-8192",
                temperature=0.7,
                max_tokens=1024,
                top_p=0.9,
                stop=None,
                stream=True,
            )
            
            ai_response = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    ai_response += delta
            self.chat_window.config(state='normal')
            self.chat_window.insert(tk.END, f"\nAI: {ai_response}\n", 'ai')
            self.chat_window.tag_config('ai', foreground='green')
            self.chat_window.config(state='disabled')
            self.chat_window.see(tk.END)
            
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            if len(self.conversation_history) > self.max_history_length * 2:
                self.conversation_history = self.conversation_history[-self.max_history_length * 2:]
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def perform_web_search(self, query):
        search_results = []
        try:
            search_url = f"https://www.googleapis.com/customsearch/v1?key={self.web_search_api_key}&cx={self.web_search_cx}&q={query}"
            response = requests.get(search_url)
            if response.status_code == 200:
                results = response.json().get('items', [])
                for result in results[:3]:  # Limit to top 3 results
                    title = result.get('title')
                    snippet = result.get('snippet')
                    link = result.get('link')
                    # Fetch the full content of the page for more context
                    page_content = self.fetch_page_content(link)
                    search_results.append(f"Title: {title}\nSnippet: {snippet}\nLink: {link}\nContent: {page_content}\n")
            else:
                search_results.append("Failed to retrieve search results.")
        
        except Exception as e:
            search_results.append(f"An error occurred during web search: {e}")

        return search_results

    def fetch_page_content(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Extract the text content while ignoring HTML tags
                text_content = ' '.join(soup.stripped_strings)
                # Limit the content to a reasonable length (e.g., 1000 characters)
                return text_content[:1000] + "..." if len(text_content) > 1000 else text_content
            else:
                return "Failed to retrieve page content."
        except Exception as e:
            return f"An error occurred while fetching page content: {e}"

    def display_search_results(self, results):
        self.web_results_window.config(state='normal')
        self.web_results_window.delete('1.0', tk.END)  # Clear previous search results
        for result in results:
            self.web_results_window.insert(tk.END, f"Searcher LLM: {result}\n", 'result')
            self.web_results_window.tag_config('result', foreground='purple')
        self.web_results_window.config(state='disabled')
        self.web_results_window.see(tk.END)

    def toggle_results_window(self):
        if self.web_results_window.winfo_viewable():
            self.web_results_window.grid_remove()
            self.toggle_button.config(text="Show Results")
        else:
            self.web_results_window.grid()
            self.toggle_button.config(text="Hide Results")

    def summarize_search_results(self, results):
        return "\n".join(results[:3])  # Summarize top 3 results for context
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
