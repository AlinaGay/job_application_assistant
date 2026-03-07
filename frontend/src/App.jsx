import { useState } from 'react'


function App() {
    const [resumeUploaded, setResumeUploaded] = useState(false)

    const handleResumeUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("http://localhost:8000/upload_resume/", {
            method: "POST",
            body: formData,
        });
        if (res.ok) setResumeUploaded(true);
    };

    return (
        <div>
            <h1>Job apllication assistant</h1>
            <input type="file" accept="application/pdf" onChange={handleResumeUpload} />
            {resumeUploaded && <p>Resume has uploaded</p>}
        </div>
    );
}

export default App;
