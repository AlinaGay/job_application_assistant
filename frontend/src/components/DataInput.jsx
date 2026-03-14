// DataInput.jsx:
/**
 * Input component with two modes: URL scraping or manual text paste.
 * If scraping fails, automatically switches to text mode.
 */
import { use } from "react";
import { useState } from "react";

const API = "http://localhost:8000";

export default function DataInput({label, urlPlaceholder, textPlaceholder, onTextReady}) {
    const [mode, setMode] = useState("url")
    const [url, setUrl] = useState("")
    const [text, setText] = useState("")
    const [status, setStatus] = useState("")

    const handleScrape = async () => {
        if(!url) return;
        setStatus("Loading...");

        const formData = new FormData();
        formData.append("url", url);

        try {
            const res = await fetch(`${API}/scrape/`, {
                method: "POST",
                body: formData,
            });
            const data = await res.json();

            if (data.success) {
                setText(data.text);
                onTextReady(data.text);
                setStatus("Loaded!")
            } else {
                setStatus("Could not load. Please paste text manually.");
                setMode("text");
            }
        } catch {
            setStatus("Error. Please paste text manually.");
            setMode("text");
          }
    };

    return (
      <div className="section">
        <h3>{label}</h3>
        <div className="mode-buttons">
          <button
            className={mode === "url" ? "active" : ""}
            onClick={() => setMode("url")}
          >
          By URL
          </button>
          <button
            className={mode === "text" ? "active" : ""}
            onClick={() => setMode("text")}
          >
            Paste text
          </button>
        </div>

        {mode === "url" && (
          <div>
            <div className="url-row">
              <input
                type="text"
                placeholder={urlPlaceholder}
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
              <button onClick={handleScrape}>Load</button>
            </div>
            {status && (
              <p className={status === "Loaded!" ? "success" : "warning"}>
                {status}
              </p>
            )}
          </div>
        )}

        {mode === "text" && (
          <textarea
            rows={5}
            placeholder={textPlaceholder}
            value={text}
            onChange={(e) => {
              setText(e.target.value);
              onTextReady(e.target.value);
            }}
          />
        )}
      </div>
    );
}

