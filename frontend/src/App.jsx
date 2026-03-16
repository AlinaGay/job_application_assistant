// App.jsx

import { useState } from 'react'

import FileUpload from "./components/FileUpload";
import DataInput from "./components/DataInput";
import CoverLetterResult from "./components/CoverLetterResult";
import "./App.css";

const API = "http://localhost:8000";


function App() {
    const [companyText, setCompanyText] = useState("");
    const [jobText, setJobText] = useState("");
    const [coverLetter, setCoverLetter] = useState("");
    const [loading, setLoading] = useState(false);

    

    const handleGenerate = async () => {
        if (!companyText || !jobText) {
            alert("Please fill in all fields and upload all files.");
            return;
        }

        setLoading(true);
        setCoverLetter("");

        const formData = new FormData();
        formData.append("company_text", companyText);
        formData.append("job_text", jobText);

        try {
            const res = await fetch(`${API}/generate/`, {
                method: "POST",
                body: formData,
            });
            const data = await res.json();
            setCoverLetter(data.cover_letter);
        } catch {
            alert("Error generating cover letter");
        } finally {
            setLoading(false);
        }
    };

    return (
      <div className="app">
        <h1>Job Application Assistant</h1>
  
        {/* Resume */}
        <FileUpload
          label="Resume"
          accept="application/pdf"
          endpoint="upload_resume"
        />
  
        {/* About Me */}
        <FileUpload
          label="About me"
          hint="Your motivation, personal stories, values — anything beyond the resume"
          accept=".pdf, .txt"
          endpoint="upload_about_me"
        />
  
        {/* Company info */}
        <DataInput
          label="About the Company"
          urlPlaceholder="https://company.com/about"
          placeholder="Paste company description, mission, values..."
          onTextReady={setCompanyText}
        />
  
        {/* Job description */}
        <DataInput
          label="Job Description"
          urlPlaceholder="https://hh.ru/vacancy/..."
          placeholder="Paste job description, requirements, responsibilities..."
          onTextReady={setJobText}
        />
  
        {/* Generate */}
        <button
          className="generate-btn"
          onClick={handleGenerate}
          disabled={loading}
        >
          {loading ? "Generating..." : "Generate Cover Letter"}
        </button>
  
        <CoverLetterResult coverLetter={coverLetter} />
      </div>
    );
}

export default App;
