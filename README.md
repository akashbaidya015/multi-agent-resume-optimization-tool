# Multi-agent-resume-optimization-tool

# 🧠 AI-Powered Resume Optimizer (LaTeX + Gemini + Flask)

An intelligent, LLM-driven resume assistant that parses job descriptions and dynamically rewrites LaTeX-formatted resume sections, including:

- **Technical Skills Section**
- **Projects Section**
- **Work Experience**
- **Professional Summary**
- **Customized Outreach Message & Subject Line**

All tailored directly from the job description using Gemini 2.0 Flash, and presented via a simple web UI powered by Flask.

---

## 🚀 Key Features

- 🔍 **ATS-Optimized Output**  
  Extracts relevant technical keywords from the JD and updates your LaTeX-formatted resume accordingly.

- 🧩 **Modular Prompt Chaining**  
  Uses structured multi-prompt workflows (like agents) to handle each resume section intelligently.

- 💼 **Work Experience Refinement**  
  Inserts quantifiable, STAR-format bullet points from the job description into your resume — no fluff, all impact.

- 📫 **Auto-generated Message to Hiring Manager**  
  Creates a tailored message + subject line you can send over LinkedIn or email, instantly.

- 🖼️ **Flask-Based UI**  
  Upload your resume or paste text, and view LLM responses in real-time.

---

## 🧠 Tech Stack

- `Flask` – Web Interface  
- `PyPDF2` / `python-docx` – File Parsing  
- `Google Generative AI (Gemini)` – Prompt-based logic engine  
- `LaTeX` – Structured Resume Formatting  
- `Python` – Backend workflow  
- (Optional) `Pinecone` / `Vector DB` – For image or prompt caching

---

## 📂 Folder Structure

