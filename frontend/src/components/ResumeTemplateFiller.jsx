/**
 * Component for uploading a DOCX resume template,
 * filling it with AI-generated content, and downloading the result.
 */

import { useState } from "react";

const API = "http://localhost:8000";

export default function ResumeTemplateFiller({ jobText }) {
    const [resumeTemplateUploaded, setResumeTemplateUploaded] = useState(false);
    const [placeholders, setPlaceholders] = useState([]);
    const [filling, setFilling] = useState(false);
    const [filled, setFilled] = useState(false);
    const [filledPlaceholders, setFilledPlaceholders] = useState([])

    const handleResumeTemplateUploaded = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch(`${API}/upload_template/`, {
                method: "POST",
                body: formData,
            });
            const data = await res.json();
            setResumeTemplateUploaded(true);
            setPlaceholders(data.placeholders);
            setFilled(false);
        } catch {
            alert("Error uploading template")
        }
    };

    const handleFill = async () => {
        if (!jobText) {
            alert("Please fill in the job description first.");
            return;
        }

        setFilling(true);
        const formData = new FormData();
        formData.append("job_text", jobText);

        try {
            const res = await fetch(`${API}/fill_template/`, {
                method: "POST",
                body: formData,
            });

            const data = await res.join();

            if (data.error) {
              alert(data.error);
            } else {
                setFilled(true);
                setFilledPlaceholders(data.placeholders_filled);
            }
        } catch {
            alert("Error filling template")
        } finally {
            setFilling(false);
        }
    };

    const handleDownload = async () => {
        try {
            const res = await fetch(`${API}/dowmnload_filled_resume/`, {
                method: "POST,
            });
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "resume.docx";
            link.click();
            window.URL.revokeObjectURL(url);
        } catch {
            alert("Error downloading resume");
        }
    };

}
