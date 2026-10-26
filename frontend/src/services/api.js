const API_BASE = import.meta.env.VITE_API_URL || '';

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`, { method: 'GET' });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    return { status: 'error', error: err.message };
  }
}

export async function fetchExamples() {
  try {
    const res = await fetch(`${API_BASE}/api/examples`, { method: 'GET' });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function runCode(source) {
  try {
    const res = await fetch(`${API_BASE}/api/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ source }),
    });

    if (!res.ok) {
      throw new Error(`Server returned HTTP ${res.status}: ${res.statusText}`);
    }

    return await res.json();
  } catch (err) {
    return {
      success: false,
      tokens: [],
      ast: null,
      ir: [],
      ir_formatted: [],
      generated_code: [],
      generated_code_raw: '',
      output: '',
      robot_history: [],
      final_state: null,
      errors: [
        `Connection Error: Could not reach the Python FastAPI backend (${err.message}). ` +
        `Ensure backend is running at http://127.0.0.1:8000 using 'python -m uvicorn web_api.app:app --reload'`
      ],
    };
  }
}
