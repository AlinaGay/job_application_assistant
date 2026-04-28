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

}
