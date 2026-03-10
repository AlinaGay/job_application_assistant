// App.jsx

import { useState } from 'react'

const API = "http://localhost:8000";


function App() {
    const [resumeUploaded, setResumeUploaded] = useState(false);
    const [aboutMeUploaded, setAboutMeUploaded] = useState(false);
    const [companyText, setCompanyText] = useState("");
    const [coverLetter, setCoverLetter] = useState("");
    const [loading, setLoading] = useState(false);

    const handleFileUpload = async (e, endpoint, onSuccess) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch(`${API}/${endpoint}/`, {
            method: "POST",
            body: formData,
        });
        if (res.ok) onSuccess(true);
    };

    const handleGenerate = async () => {
        if (!resumeUploaded || !aboutMeUploaded || !companyText) {
            alert("Please upload all files and fill in company info.");
            return;
        }

        setLoading(true)
        setCoverLetter("")

        const formData = new FormData()
        formData.append("company_text", companyText)

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
        <div style={{ maxWidth: "700px", margin: "0 auto", padding: "20px" }}>
          <h1>Job Application Assistant</h1>

          {/* Resume */}
          <div style={{ marginBottom: "20px" }}>
            <h3>Resume (PDF)</h3>
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => handleFileUpload(e, "upload_resume", setResumeUploaded)}
            />
            {resumeUploaded && <p style={{ color: "green" }}>Resume uploaded!</p>}
          </div>

          {/* About Me */}
          <div style={{ marginBottom: "20px" }}>
            <h3>About Me (PDF or TXT)</h3>
            <p style={{ color: "gray", fontSize: "14px" }}>
              Your motivation, personal stories, values — anything beyond the resume
            </p>
            <input
              type="file"
              accept=".pdf,.txt"
              onChange={(e) => handleFileUpload(e, "upload_about_me", setAboutMeUploaded)}
            />
            {aboutMeUploaded && <p style={{ color: "green" }}>About Me uploaded!</p>}
          </div>

          {/* Company info */}
          <div style={{ marginBottom: "20px" }}>
            <h3>About the Company</h3>
            <textarea
              rows={5}
              style={{ width: "100%" }}
              placeholder="Paste company description, mission, values..."
              value={companyText}
              onChange={(e) => setCompanyText(e.target.value)}
            />
          </div>

          {/* Generate */}
          <button
            onClick={handleGenerate}
            disabled={loading}
            style={{ padding: "10px 20px", fontSize: "16px" }}
          >
            {loading ? "Generating..." : "Generate Cover Letter"}
          </button>

          {/* Result */}
          {coverLetter && (
            <div style={{ marginTop: "30px" }}>
              <h2>Your Cover Letter</h2>
              <textarea rows={15} style={{ width: "100%" }} value={coverLetter} readOnly />
              <button
                onClick={() => navigator.clipboard.writeText(coverLetter)}
                style={{ marginTop: "10px", padding: "8px 16px" }}
              >
                Copy to Clipboard
              </button>
            </div>
          )}
        </div>
      );
}

export default App;
