from flask import Flask, request, render_template_string
import os
import PyPDF2
from docx import Document
import google.generativeai as genai

# Configure Gemini
GOOGLE_API_KEY = "AIzaSyAqorzqgNeKInifCEjsxziK2-OQ4DfC0_g"  # Replace this with your actual key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Flask app
app = Flask(__name__)

# HTML Template
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Gemini Prompt App</title>
</head>
<body>
    <h2>Upload File or Paste Text</h2>
    <form method="POST" enctype="multipart/form-data">
        <label>Upload PDF/DOCX:</label><br>
        <input type="file" name="file"><br><br>

        <label>Or paste text here:</label><br>
        <textarea name="text" rows="10" cols="60"></textarea><br><br>

        <input type="submit" value="Submit">
    </form>

    {% if responses and responses|length > 0 %}
        <h2>Gemini Responses</h2>
        {% for response in responses[3:] %}
            <h3>Response {{ loop.index + 3 }}</h3>
            <pre>{{ response }}</pre>
        {% endfor %}
    {% endif %}

    {% if final_response %}
        <h2>Final Gemini Output</h2>
        <pre>{{ final_response }}</pre>
    {% endif %}

    {% if combined_custom_response %}
        <h2>Combined Response (1 + 5 + 3)</h2>
        <pre>{{ combined_custom_response }}</pre>
    {% endif %}
</body>
</html>
"""

def extract_text(file):
    filename = file.filename.lower()
    if filename.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif filename.endswith('.docx'):
        document = Document(file)
        return "\n".join([p.text for p in document.paragraphs])
    else:
        return "Unsupported file format."

def send_to_gemini(content):
    prompts = [
        rf"""Please carefully review the attached job description and extract relevant, ATS-friendly technical keywords that would meaningfully strengthen the resume.

Focus only on the Basic, Minimum, and Preferred Qualifications/Requirements sections to guide your extraction.

Your task is to update the LaTeX-formatted "Technical Skills" section below by doing the following:

Retain the LaTeX format exactly as-is, including section headers, spacing, and syntax.

Do not modify the Certifications section.

Limit the total number of categories to no more than 6.

Only include clearly technical skills (e.g., programming languages, frameworks, libraries, tools, platforms). Avoid concepts like "data analysis" or "causal inference."

When adding tools or technologies, prefer specific technologies over broad categories.

✅ For example, replace:

"Relational Databases" → PostgreSQL, MySQL, SQL Server

"Non-Relational Databases" → MongoDB, Cassandra, DynamoDB

"Cloud Platforms" → AWS, Azure, GCP

"ETL Tools" → Airflow, AWS Glue, dbt

Only include technologies that can be justified through projects or experience (i.e., don't list anything that isn't referenced elsewhere in the resume).

Do not label any skills as “preferred” or “familiar,” even if sourced from the Preferred Qualifications section.

Ensure the final output consists of:
✅ the updated Technical Skills section (in LaTeX format), followed by
✅ the unchanged Certifications section below it.

Begin your modifications from the LaTeX section provided below, and return only the updated LaTeX output.


%----------------------------------------------------------------------------------------
% TECHNICAL SKILLS
%----------------------------------------------------------------------------------------

{{\begin{{rSection}}{{TECHNICAL SKILLS}}}}
    {{\vspace{{-0.3em}}}}
    {{\textbf{{Programming Languages}}}}: Python, Shell Scripting, SQL. \\
    {{\textbf{{Python Frameworks \& Libraries}}}}: Django, Flask, FastAPI, Pandas, NumPy, SciPy, Scikit-learn. \\
    {{\textbf{{Databases}}}}: PostgreSQL, MySQL, SQL Server. \\
    {{\textbf{{API \& Web Services}}}}: RESTful APIs, Experience with API integration. \\
    {{\textbf{{Version Control}}}}: Git, GitHub, GitLab. \\
    {{\textbf{{Development Tools}}}}: Jupyter, PyCharm.
{{\end{{rSection}}}}
\vspace{{-0.70em}}


%----------------------------------------------------------------------------------------
% CERTIFICATIONS
%----------------------------------------------------------------------------------------

{{\begin{{rSection}}{{Certifications}}}}

AWS Data Analytics Certification{{\textsuperscript{{\href{{https://www.linkedin.com/in/akashbaidya15/overlay/1635505411454/single-media-viewer/?profileId=ACoAACQj3aABd422xdO0mtNSKRSYGpLP60sE2eQ}}{{\tiny view credential}}}}}} \\
Azure Data Scientist Associate{{\textsuperscript{{\href{{https://learn.microsoft.com/api/credentials/share/en-us/AkashBaidya-5020/7D289823FFBEAEC4?sharingId=222B26176EB0813B}}{{\tiny view credential}}}}}} \\
GCP Data Engineering Skills Boost{{\textsuperscript{{\href{{https://www.cloudskillsboost.google/public_profiles/f975a4aa-8ccf'-4fc1-8859-9569c6822a40}}{{\tiny view credential}}}}}}

{{\end{{rSection}}}}
\vspace{{-0.70em}}



This is where the Latex template ends, make sure to return everything thats witing latex

This is the Job Description which starts here:

{content}
""",rf"""Important Task Begins Here

You will be provided with a job description at the end of this prompt. Your task is to generate strong, technically accurate, and quantifiable resume bullet points that align with the role — going far beyond generic rewording of job descriptions.

🧠 Guidelines for Output
Most importantly, extract and include only high-value, ATS-friendly technical keywords directly from the job description. 

Your bullet points must reflect real-world experience — not repeat vague responsibilities or use abstract concepts.

Use precise technical language that clearly demonstrates impact, tools, and outcomes.

Avoid using action verbs repetitively (e.g., avoid repeating “Developed,” “Built,” “Implemented”). Vary the structure of sentences — for example, start with the impact or outcome first, followed by how it was achieved.

Please donot reference the name of the company in the bullet points anywhere

Also Highlight the qunaitifiable impacts in each Bullet point using \textbf{{}}

Eliminate fluff or generic terms (like “machine learning algorithms,” “data-driven insights,” “cross-functional teams”) unless justified with details.

Ensure all claims are realistic and justifiable — no vague buzzwords or unsupported metrics.

✅ Formatting Instructions
Use LaTeX bullet point format (see example below).

Escape special characters (e.g., %, $, &).

Each bullet should be a full sentence and clearly express:

What was done

How it was done

What the measurable outcome was 

Kind of Like STAR method,

S - What was the Situation
T - What was the Task to be done
A - What was the Action take
R - What was the Result

Just See some examples here how star format looks like

Created dashboards using Tableau for the finance team (What), by automating weekly reporting with filters and visual KPIs (How), which saved 8 hours/week and improved decision-making speed (Impact).
Cleaned and standardized vendor payment data (What), using Python and Excel to process exports from SAP (How), resulting in 20% higher invoice accuracy and fewer downstream payment issues (Impact).

And Also Make Sure they Sound like how a Human would write it, little imperfect rather than being written by LLM

Your final output should consist of 7 bullet points in LaTeX format only.


\item ........
\item .......


This is where the Job Description starts :
{content}
Developed a regression model using Random Forest with 94% accuracy to predict student churn in a capstone project; integrated it into
internal IT systems to automate workflows and improve monthly retention by 12 basis points.

Partnered with product and analytics teams to analyze A/B testing outcomes for new feature rollouts, driving data-backed iterations that
led to a 12% increase in user engagement and a 35% rise in click-through rates.

Oversaw migration of Oracle/MySQL to Redshift, redesigning schemas with data modeling best practices to boost reporting by 14%.

Spearheaded the development of scalable ETL pipelines using Azure Data Factory and Databricks to transform 20TB+ from HDFS in
a Hadoop-based system to Azure Data Lake, cutting data latency by 40% compared to the legacy batch processing workflows.
• Partnered with Warehouse Operations leadership to perform advanced root cause analysis, identifying bottlenecks and streamlining
decision-making processes for operational improvements.


"""
     ,
        f"""
        "AI chatbot for mental health support
Drug discovery using molecule property prediction
Portfolio optimization using reinforcement learning
Credit risk scoring with ensemble models
Chatbot for customer service with sentiment-aware responses
Fleet maintenance prediction using sensor data
Model drift detection and retraining automation


        Based On the Job description below could you Please provide no more than One unique Project which is non generic Tailored to the Job description and inlcudes most relevant skills and delivering impact in the format below
        Please maintain the intergrity of the format of the Latex below 
        
        For projects make sure to use escape characters before using overleaf specific characters.
        Also Make sure the Project Dates dont go Past March 2025
        Also Make sure to not include more than three bullet points under each project.
        Also make sure to use "\ vspace{{-0.70em}}" between each bullet point to maintain spacing

        And Return to me and nothing else 
        
        And More Request, Dont just state a generic Project names it has to be some real life use case projecct name 
        And Finally for your reference, at the top you can find some topics that you can explore for the names of projects

        Please Please Make Sure not to Referecne the name of the company anywhere in the Projects
        


    

        Also i would really like when you are tailoring projects if the description/Explanation of the Project follows this tone/flow of words like in this example:
    
Sample Project Name Just for Reference | Data Science 
• Performed exploratory data analysis (EDA) on healthcare datasets, uncovering patterns and anomalies that improved fraud 
detection accuracy by 25%. 
• Applied machine learning algorithms, achieving a 30% increase in the identification of fraudulent activities compared to 
traditional methods. 
        

This is where the Latex Starts Make sure to give projects in the similar fashion as below and include everything starting here in the ouput that you provide.

%----------------------------------------------------------------------------------------
% PROJECTS
%----------------------------------------------------------------------------------------

\ begin{{rSection}}{{Projects}}



\ textbf{{StyleGenie (AIATL Hackathon - 36 Hrs)}} (Gen AI, React, Stable Diffusion, LLM, Vector DB)   \hfill Nov 2024  
\begin{{itemize}} 
\vspace{{-0.30em}}
\item Designed a scalable RAG-based fashion recommendation system, integrating MongoDB to store user data to serve as RAG, Pinecone for caching results from recurring prompts, and Gemini AI for image auto-captioning, optimizing real-time outfit recommendations.

\vspace{{-0.50em}}

\item Deployed the model using a robust MLOps pipeline, ensuring reliable and efficient forecasting for various industrial sectors.

\end{{itemize}} 

\end{{document}}



This is where the Latex ends

This is where the Job description starts
          
            {content}""",
        f"""Please provide a single professional summary tailored to the job description (provided below) by extracting relevant keywords that effectively summarize the role. Keep the format and tone consistent with the examples shared below.

🔹 Instructions:

Keep the summary concise, with no more than 15 words.

Maintain a tone and structure similar to the examples.

Avoid using the following buzzwords:
Hardworking, Go-getter, Team player, Detail-oriented, Results-driven, Synergy, Self-starter, Strategic thinker, Dynamic, Problem-solver, Responsible for, Motivated, Innovative, Fast learner, Excellent communication skills, Proven track record, Rockstar, Ninja, Guru, Passionate, Leveraged synergies, Think outside the box

Focus on technical skills, relevant tools, industry domains, and specialization areas.

Do not mention location.

Remember the following about me:

Total experience: 5 years

Education: Master’s Degree

Certifications:

AWS Certified Data Analytics – Specialty

Azure Data Scientist Associate

🔹 Format Examples:

Data Scientist with 5 years of experience specializing in SQL development, AWS-based solutions, and data governance.

Data professional with 5 years of experience in building data pipelines and delivering machine learning solutions.


2nd Task 

Based on the same job description, craft a short, professional message to a hiring manager expressing interest in the role.
Also, suggest an appropriate email subject line for this message.

Message:
Hi Tina,

I hope you're doing well! My name is Akash Baidya. I have 5 years of experience and a Master's degree specializing in Big Data and Analytics. I recently applied for the {{Job Title}} position at {{Company Name}}, and I’d love to hear about your experience at the company and how data-driven solutions shape decision-making there.

With my background as a {{Job Title}} at IBM and Accenture, and a Research {{Role}} at Georgia State University, I’ve worked extensively on data processing, visualization, and predictive analytics—aligning well with {{Company Name}}’s focus on leveraging data for business insights. I believe my skills in {{Relevant Skillset from the Job Description}} would allow me to contribute meaningfully to your team.

If you're available, I’d really appreciate a brief chat or call to learn more about the role and your insights into the company. I’ve attached my resume and would be happy to share more details.

Looking forward to hearing from you!

Additional Request:
If possible, identify the location mentioned in the job description and return a nearby address that includes a ZIP code.


         
         This is where the job description starts
          \n{content} 
        
        """
    ]

    responses = []
    for prompt in prompts:
        try:
            response = model.generate_content([prompt])
            responses.append(response.text)
        except Exception as e:
            responses.append(f"Error: {str(e)}")
    return responses

def send_final_prompt(responses):
    combined = f"Response 2:\n{responses[1]}"

    constant_final_prompt = """
          
                """
    full_prompt = full_prompt = rf"""{constant_final_prompt} Bullet Points  : {combined}

Could you please copy the first 3 bullet points from the first company and paste them at the top of the existing bullet points for that company in the LaTeX format below—without making any changes?

Then, for the second company, paste the next 2 bullet points below its current bullet points, and do the same for the third company, adding the next 2 bullet points under its existing bullet list—while making sure to preserve the LaTeX formatting exactly as it is.

Also, please do not make any changes to the Education section. Return only the modified Work Experience section along with the unchanged Education section, and nothing else.

This is where the Latex starts

%----------------------------------------------------------------------------------------
% WORK EXPERIENCE
%----------------------------------------------------------------------------------------
\begin{{rSection}}{{Work Experience}}

\textbf{{Research Data Scientist}}, \textbf{{Georgia State University}},{{ Atlanta, GA}} \hspace{{\fill}} \textbf{{Jan 2024 – Present}}

\vspace{{-0.3em}} % Tighten spacing before the bullet points
\begin{{itemize}}
\itemsep -4pt % Reduce space between bullet points

\item  Developed a regression model using Random Forest with \textbf{{94}}\% accuracy to predict student churn in a capstone project; integrated it into internal IT systems to automate workflows and improve monthly retention by \textbf{{12}} basis points.

\item Achieved \textbf{{87}}\% accuracy in detecting online threats by engineering a real-time NLP system to classify social media content into categories like violence, abuse, and criminal intent; developed to alert authorities of potential dangers.

\end{{itemize}}


\vspace{{-0.2em}} % Adjust spacing between job entries

\textbf{{Data Analyst}}, \textbf{{Accenture}},{{ Mumbai, IN}}
\textbf{{}}   \hspace{{\fill}}           \textbf{{Dec 2022 – Jan 2024}}

\vspace{{-0.3em}}
\begin{{itemize}}
    \itemsep -4pt


\item Partnered with product and analytics teams to analyze A/B testing outcomes for new feature rollouts, driving data-backed iterations that led to a \textbf{{12}}\% increase in user engagement and a \textbf{{35}}\% rise in click-through rates.
\item Collaborated with stakeholders in \textbf{{Agile}} sprints to gather requirements, conduct exploratory data analysis (EDA), and deliver interactive dashboards, adhering to \textbf{{SDLC}} best practices to drive data-informed decisions in real estate analytics and operations.         
\item
\item

  





\end{{itemize}}







\vspace{{-0.3em}}
\textbf{{Data Engineer}}, \textbf{{IBM}},{{ Hyderabad, IN}}
 \hspace{{\fill}} \textbf{{Jan 2020 – Dec 2022}}
\vspace{{-0.3em}}
\begin{{itemize}}

    \itemsep -4pt

     \item  Improved deployment efficiency and minimized operational overhead by automating \textbf{{CI/CD}} pipelines for data workflows, implementing
 Git-based version control strategies using Terraform, Azure DevOps, and GitHub Actions.
 \item Consolidated siloed data into a centralized warehouse, unlocking cross-team insights and revealing \$\textbf{{500K}} in missed revenue.
 \item  Led Initiatives to refactor and optimize stored procedures and SQL queries for IBM Db2 improving data retrieval speed by \textbf{{60}}\%.
\item
\item

\end{{itemize}}

\vspace{{-0.70em}}

%----------------------------------------------------------------------------------------
% EDUCATION
%----------------------------------------------------------------------------------------

\begin{{rSection}}{{Education}}
\vspace{{-0.2em}}
\textbf{{MS in Computer Information Systems $|$ Track - Big Data \& Analytics}} , Georgia State University  \hfill Jan 2024 - Dec 2024\\
\textbf{{Relevant Coursework}}: Data Science, Distributed Computing, Machine Learning , AI for Business, Computer Vision  \\ Natural Language Processing (NLP), LLM Fine Tuning, Big Data Processing, Statistical Modeling and Inference
\vspace{{-0.3em}}


\textbf{{Bachelor of Science in Electronics and Telecommunication}}, University of Mumbai \hfill \ May 2015 - Jul 2019
     
\vspace{{-0.70em}}



"""

    try:
        final_response = model.generate_content([full_prompt])
        return final_response.text
    except Exception as e:
        return f"Error in final prompt: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    responses = None
    final_response = None
    combined_custom_response = None  # This will be our 6th response

    if request.method == 'POST':
        content = ""

        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            content = extract_text(file)
        elif 'text' in request.form:
            content = request.form['text']

        if content:
            responses = send_to_gemini(content)
            if responses:
                final_response = send_final_prompt(responses)
                # --- Combine 1st, 5th (final), and 3rd ---
                parts = [
                    responses[0] if len(responses) > 0 else "",
                    final_response if final_response else "",
                    responses[2] if len(responses) > 2 else ""
                ]
                combined_custom_response = "\n\n".join(parts)
                # 🧽 Remove unwanted markdown wrappers
                combined_custom_response = combined_custom_response.replace("```latex", "").replace("```", "")

    return render_template_string(HTML, responses=responses, final_response=final_response, combined_custom_response=combined_custom_response)



if __name__ == '__main__':
    app.run(debug=True)
