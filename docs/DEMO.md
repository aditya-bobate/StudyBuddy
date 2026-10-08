# StudyBuddy Demo Instructions

This document outlines a standard ~2-minute demo flow for showcasing StudyBuddy.

## Setup
Before starting the demo, ensure the virtual environment is activated and Ollama is running in the background.

```powershell
.\setup.ps1  # (Or activate environment and ensure models are pulled)
```

## Demo Steps

1. **Start Ollama**
   Show the terminal where `ollama serve` is running or mention it's running in the system tray.

2. **Start StudyBuddy**
   Run the application in a new terminal:
   ```bash
   streamlit run app/app.py
   ```

3. **Upload Sample Notes**
   In the Streamlit UI sidebar, use the file uploader to select `sample_data/biology_notes.txt`. Note how the system rapidly chunks and embeds the document locally.

4. **Ask a Question**
   In the main chat interface, ask: *"What is the cell theory?"*

5. **Show Grounded Answer**
   Highlight the generated answer. Emphasize the following talking point: 
   *"After the required models are downloaded, inference and document processing can run locally without sending study documents to a cloud LLM API."*

6. **Show Sources**
   Click the "Sources" expander under the answer to show exactly which snippet of the notes was used to ground the model.

7. **Generate Summary**
   Click the "Generate Summary" button in the sidebar. Show how it condenses the entire document.

8. **Generate Quiz**
   Navigate to the "Quiz" tab and click "Generate Quiz". Answer a multiple-choice question to demonstrate the interactive learning flow.

9. **Generate Flashcards**
   Navigate to the "Flashcards" tab to show the two-sided study cards.

10. **Explain Local Architecture**
    Conclude by briefly referencing the offline nature of `ChromaDB`, `gemma3:4b`, and `nomic-embed-text`.
