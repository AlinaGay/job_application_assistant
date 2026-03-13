// DataInput.jsx:
/**
 * Input component with two modes: URL scraping or manual text paste.
 * If scraping fails, automatically switches to text mode.
 */
import { useState } from "react";

const API = "http://localhost:8000";

