// CoverLetterResult.jsx

/**
 * Displays the generated cover letter
 * with copy and PDF download buttons.
 */

const API = "http://localhost:8000";

export default function CoverLetterResult({ coverLetter }) {
  if (!coverLetter) return null;

  const handleDownloadPdf = async () => {
    const formData = new FormData();
    formData.append("cover_letter", coverLetter);

    try {
      const res = await fetch(`${API}/download_pdf/`, {
        method: "POST",
        body: formData,
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "cover_letter.pdf";
      link.click();
      window.URL.revokeObjectURL(url);
    } catch {
      alert("Error downloading PDF");
    }
  };

  return (
    <div className="result">
      <h2>Your Cover Letter</h2>
      <textarea rows={15} value={coverLetter} readOnly />
      <div style={{ marginTop: "10px", display: "flex", gap: "8px" }}>
        <button
          className="copy-btn"
          onClick={() => navigator.clipboard.writeText(coverLetter)}
        >
          Copy to Clipboard
        </button>
        <button className="copy-btn" onClick={handleDownloadPdf}>
          Download PDF
        </button>
      </div>
    </div>
  );
}
