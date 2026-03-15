// CoverLetterResult.jsx

/**
 * Displays the generated cover letter with a copy-to-clipboard button.
 * Only renders when coverLetter is not empty.
 */

export default function CoverLetterResult({ coverLetter }) {
    if (!coverLetter) return null;

    return (
        <div className="result">
          <h2>Your Cover Letter</h2>
          <textarea rows={15} value={coverLetter} readOnly />
          <button
            className="copy-btn"
            onClick={() => navigator.clipboard.writeText(coverLetter)}
          >
            Copy to Clipboard
          </button>
        </div>
    );
}
