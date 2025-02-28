import streamlit as st
import google.generativeai as genai
import re
import fitz

API_KEY = "AIzaSyBp9rS_x0Tw_kIrwpvD3_f3NFSEp2McbQs"  # Replace with a valid API key (USE YOUR OWN!)

# Configure Gemini API
def configure_gemini():
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel('gemini-1.5-pro')

def suggest_courses_gemini(domain, expertise):
    """Fetches AI-generated course recommendations."""
    model = configure_gemini()

    prompt = f"""
    I am interested in {domain} and my expertise level is {expertise}.
    Suggest relevant courses with a short description, platform, and a valid course URL.

    Format:
    **Course Title**  
    *Description:* Brief description.  
    *Platform:* (Coursera/Udemy/etc.)  
    *Link:* [Course Link](https://example.com)
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error fetching recommendations: {e}"

def parse_courses(response_text):
    """Extract structured course details from AI response."""
    course_pattern = re.findall(r"\*\*(.*?)\*\*\s+\*Description:\* (.*?)\s+\*Platform:\* (.*?)\s+\*Link:\* \[(.*?)\]", response_text)
    return [{"title": title, "description": desc, "platform": platform, "link": link} for title, desc, platform, link in course_pattern]

def extract_text_from_pdf(pdf_file):
    """Extract text from an uploaded PDF file."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "\n".join([page.get_text("text") for page in doc])
    return text

def extract_experience(text):
    """Extract job roles, companies, and descriptions under Experience."""
    experience_pattern = r"(?i)(Experience|Work Experience|Internships)\s*[:\-\n]([\s\S]*?)(?=\n(?:Projects|Education|Technical Skills|Certificates|$))"
    match = re.search(experience_pattern, text)

    # if not match:
    #     return "❌ Experience section not found."

    experience_text = match.group(2).strip()

    job_entries = re.findall(r"([\w\s]+(?:Intern|Developer|Engineer|Manager))\s+(\w{3,9}\s\d{4}\s*–?\s*\w{0,9}\s?\d{0,4})\s+([\w\s&.,()-]+)", experience_text)
    job_descriptions = re.split(r"[\w\s]+(?:Intern|Developer|Engineer|Manager)\s+\w{3,9}\s\d{4}\s*–?\s*\w{0,9}\s?\d{0,4}\s+[\w\s&.,()-]+", experience_text)

    experience_list = []
    for i, job in enumerate(job_entries):
        title, duration, company = job
        description = job_descriptions[i + 1].strip() if i + 1 < len(job_descriptions) else "No description provided."
        experience_list.append(f"**{title}** at **{company}** ({duration})\n\n{description}")

    return "\n\n---\n\n".join(experience_list) if experience_list else ""

def extract_technical_skills(text):
    """Extract all subsections under Technical Skills (Languages, Technology, etc.)."""
    skills_pattern = r"(?i)(Technical Skills|Skills|Relevant Skills)\s*[:\-\n]([\s\S]*?)(?=\n(?:Projects|Experience|Education|Certificates|$))"

    match = re.search(skills_pattern, text)
    # if not match:
    #     return "❌ Technical Skills section not found."

    skills_text = match.group(2).strip()

    subsections = re.findall(r"(?i)(Languages|Technology|Developer Tools|Libraries|Software|Frameworks)\s*:\s*([\s\S]*?)(?=\n[A-Z][a-z]*:|$)", skills_text)

    structured_skills = {}
    for section, content in subsections:
        structured_skills[section] = content.strip()

    return structured_skills

def mentor_page(domain):
    """Displays a list of mentors for the given domain."""
    # Replace this with your actual mentor data source (e.g., a database, a CSV file)
    mentors = {
        "Data Science": [
            {"name": "Utkarsh Gupta", "linkedin": "https://www.linkedin.com/in/utkarsh-gupta-650605253/"},
            {"name": "Rushil Sharma", "linkedin": "https://www.linkedin.com/in/rushil-sharma-803299303/"},
            {"name": "Shivansh Mahajan", "linkedin": "https://www.linkedin.com/in/shivansh1976"}
        ],
        "Web Development": [
            {"name": "Karan Yadav", "linkedin": "https://www.linkedin.com/in/karan-yadav-46228527b"},
            {"name": "Pratham Karmakar", "linkedin": "https://www.linkedin.com/in/pratham-karmarkar-6b786a293"},
        ],
        "Machine Learning": [
            {"name": "Rithuik Prakash", "linkedin": "https://www.linkedin.com/in/rithuik-prakash-61237a25b"},
            {"name": "Krish Naik", "linkedin": "https://www.linkedin.com/in/naikkrish "},
            {"name": "Andrew ng", "linkedin": "https://www.linkedin.com/in/andrewyng "},
        ],
        "Default": [
            {"name": "No mentors found", "linkedin": ""},
        ]
    }

    if domain in mentors:
        st.subheader(f"Mentors for {domain}")
        for mentor in mentors[domain]:
            if mentor["linkedin"]:
                st.write(f"[{mentor['name']}]({mentor['linkedin']})") #Linked name
            else:
                st.write(f"{mentor['name']}")

    else:
        st.subheader("No mentors available for this specific domain right now.")

def chatbot_page():
    """A simple chatbot interface."""
    st.subheader("AI Learning Path Suggestor")
    
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Tell me about your past knowledge and background education..."):
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        model = configure_gemini()
        
        instruction = f"""Given the following background about a user:\n{prompt}\nSuggest 3-5 next topics that the user should consider learning based on their background. \n
        Also, inform the user about any trending topics in their specified domain.
        Explain why each topic is important for their career, provide topic name and keywords that help explore the topic.
        Format:
        Topic: <topic_name>
        Why: <explanation>
        Keywords: <keyword1, keyword2, keyword3>
        
        Trending Topics: <List of trending topics with explanation of why they're important>
        """
        
        try:
            response = model.generate_content(instruction)
            ai_response = response.text
        except Exception as e:
            ai_response = f"Error generating response: {e}"

        st.session_state["chat_history"].append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.markdown(ai_response)

# Streamlit UI
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("Main", "Mentors", "Chatbot")) #Radio buttons in the sidebar

if page == "Main":
    st.markdown(
            """
            <style>
            .main-title {
                color: #2DAA9E; /* Change to your desired color */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<h1 class='main-title'>Skill Forge</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-title'>Crafting career success</h3>", unsafe_allow_html=True)

    st.write("Upload your resume (PDF), extract Experience & Technical Skills, and get personalized course recommendations.")

    # **Ensure extracted_content exists in session state**
    if "extracted_content" not in st.session_state:
        st.session_state["extracted_content"] = ""

    # Upload Resume
    upload_rsm = st.file_uploader("Drop your resume", type=["pdf"])

    if upload_rsm is not None:
        st.success("✅ File uploaded successfully! Extracting content...")
        resume_text = extract_text_from_pdf(upload_rsm)

        # Extract sections
        experience = extract_experience(resume_text)
        skills = extract_technical_skills(resume_text)

        # Store extracted content in session state
        extracted_content = f"**Extracted Experience:**\n\n{experience}\n\n**Extracted Technical Skills:**\n\n"

        if isinstance(skills, dict):
            extracted_content += "\n".join([f"**{key}:** {value}" for key, value in skills.items()])
        else:
            extracted_content += skills

        st.session_state["extracted_content"] = extracted_content

    # **Course Recommendation System**
    st.subheader("Get Course Recommendations")

    # **Always show input field, update value if resume is uploaded**
    domain = st.text_input("Enter your domain of interest (e.g., Data Science, Web Development, Cybersecurity)",
                           value=st.session_state["extracted_content"] if st.session_state["extracted_content"] else "")

    expertise = st.selectbox("Select your expertise level:", ["Beginner", "Intermediate", "Expert"])

    if st.button("Get Course Recommendations"):
        if domain and expertise:
            with st.spinner("Fetching course recommendations... ⏳"):
                recommendations = suggest_courses_gemini(domain, expertise)
                courses = parse_courses(recommendations)

                if courses:
                    st.subheader("Recommended Courses")
                    for course in courses:
                        with st.container():
                            st.markdown(f"### [{course['title']}]({course['link']})")
                            st.write(f"**Description:** {course['description']}")
                            st.write(f"**Platform:** {course['platform']}")
                            st.divider()  # Adds a horizontal line
                else:
                    st.error("No valid courses were extracted. Please try again.")
        else:
            st.error("Please enter all required details (Domain, Expertise) before proceeding.")

elif page == "Mentors":
    # Retrieve the domain from session state if available.
    # Otherwise, set it to a default value.
    domain = st.session_state.get("domain", "Data Science")  # Default value if not in session
    
    # Provide a text box for the user to specify their domain of interest.
    mentor_domain = st.text_input("Enter your domain of interest for finding mentors:", value=domain)
    
    # Store the entered domain in session state.
    st.session_state["domain"] = mentor_domain
    
    # Call the mentor_page function to display mentor information for the entered domain.
    mentor_page(mentor_domain)

elif page == "Chatbot":
    chatbot_page()