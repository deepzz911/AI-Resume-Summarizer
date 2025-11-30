import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import PyPDF2

# -------------------- Load Environment & Configure API --------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# -------------------- Extract text from uploaded PDF --------------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        st.error(f"⚠️ Could not read PDF: {e}")
    return text.strip()

# -------------------- Generate structured summary --------------------
def generate_resume_analysis(resume_text):
    if not resume_text:
        return {
            "summary": "⚠️ No readable text found in the uploaded resume.",
            "skills": "—",
            "experience": "—",
        }

    prompt = f"""
    You are an expert HR recruiter and career analyst.
    Read the following resume text and generate three well-structured sections:

    1️⃣ Professional Summary – Concise overview (≤ 150 words) highlighting strengths, expertise, and value.
    2️⃣ Key Skills – List 5-10 technical and soft skills in bullet form.
    3️⃣ Experience Highlights – List 3-7 bullet points summarizing relevant work achievements or projects.

    Maintain clear formatting with headings and bullet points.
    Resume Text:
    {resume_text}
    """

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Split sections if model uses headings
        sections = {"summary": "", "skills": "", "experience": ""}
        lower_text = text.lower()
        if "key skills" in lower_text:
            parts = text.split("Key Skills")
            sections["summary"] = parts[0].strip()
            if "Experience" in parts[1]:
                sub = parts[1].split("Experience")
                sections["skills"] = sub[0].strip()
                sections["experience"] = sub[1].strip()
            else:
                sections["skills"] = parts[1].strip()
        else:
            sections["summary"] = text

        return sections
    except Exception as e:
        return {
            "summary": f"⚠️ Error generating analysis: {e}",
            "skills": "—",
            "experience": "—",
        }

# -------------------- Streamlit App UI --------------------
st.set_page_config(page_title="AI Resume Analyzer (Gemini 2.0 Flash)", layout="centered")
st.title("🧠 AI Resume Analyzer (Gemini 2.0 Flash)")
st.write("Upload a resume and get a Professional Summary, Key Skills, and Experience Highlights ⚡")

uploaded_file = st.file_uploader("📂 Upload your Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ Resume uploaded successfully!")

    with st.spinner("Extracting text from your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    if resume_text:
        st.text_area("📄 Extracted Resume Text (editable):", resume_text, height=200)

        if st.button("✨ Generate Analysis"):
            with st.spinner("Analyzing resume with Gemini 2.0 Flash..."):
                result = generate_resume_analysis(resume_text)

            st.markdown("## 🧾 Professional Summary")
            st.write(result["summary"])

            st.markdown("## 🧰 Key Skills")
            st.write(result["skills"])

            st.markdown("## 💼 Experience Highlights")
            st.write(result["experience"])

            # Download full report
            download_text = (
                "Professional Summary:\n" + result["summary"] +
                "\n\nKey Skills:\n" + result["skills"] +
                "\n\nExperience Highlights:\n" + result["experience"]
            )

            st.download_button(
                label="📥 Download Full Analysis",
                data=download_text,
                file_name="AI_Resume_Analysis.txt",
                mime="text/plain"
            )
    else:
        st.warning("⚠️ Could not extract any text from the uploaded file.")
else:
    st.info("Please upload a PDF resume to start.")
