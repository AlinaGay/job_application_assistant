// FileUpload.jsx
/**
 * Reusable file upload component.
 * Uploads a file to the specified backend endpoint
 * and shows a success message.
 */
import { useState } from 'react'

const API = "http://localhost:8000";

export default function FileUpload({ label, hint, accept, endpoint }) {
    const [uploaded, setUploaded] = useState(false);

    const handleUpload = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API}/${endpoint}/`, {
          method: "POST",
          body: formData,
      });
      if (res.ok) setUploaded(true);
    };

    return (
        <div className="section">
          <h3>{label}</h3>
          {hint && <p className="hint">{hint}</p>}
          <input type="file" accept={accept} onChange={handleUpload} />
          {uploaded && <p className="success">{label} uploaded!</p>}
        </div>
    );
}
