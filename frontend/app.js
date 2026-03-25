/* ============================================
   BugMind AI - Frontend Application Logic
   Connects to FastAPI backend for auth,
   code execution, AI analysis, and dashboard.
   ============================================ */

// ===== CONFIGURATION =====
const API_BASE = 'http://localhost:8000/api';

const FILES = {
  'main.py': `age = input('Enter your age:')\n\nif age > 18\n    print('You can vote!')\n    if int(age) > 18:`,
  'utils.py': `# Utility functions for BugMind AI\n\ndef validate_input(value, expected_type):\n    """Validate and convert input to expected type"""\n    try:\n        return expected_type(value)\n    except (ValueError, TypeError) as e:\n        return None\n\ndef format_output(result):\n    """Format the output for display"""\n    if result is None:\n        return "No output"\n    return str(result)`,
  'input.txt': `# Sample Input File\n18\nHello World\n42`
};

// ===== GLOBAL STATE =====
let editor = null;
let currentFile = 'main.py';

// ===== AUTH HELPER =====
function getToken() {
  return localStorage.getItem('bugmind_token');
}

function getUser() {
  const u = localStorage.getItem('bugmind_user');
  return u ? JSON.parse(u) : null;
}

function setAuth(token, user) {
  localStorage.setItem('bugmind_token', token);
  localStorage.setItem('bugmind_user', JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem('bugmind_token');
  localStorage.removeItem('bugmind_user');
}

function authHeaders() {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
}

async function apiCall(endpoint, method = 'GET', body = null) {
  const opts = { method, headers: authHeaders() };
  if (body) opts.body = JSON.stringify(body);
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, opts);
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Request failed');
    }
    return data;
  } catch (err) {
    if (err.message === 'Failed to fetch') {
      throw new Error('Cannot connect to server. Make sure the backend is running on port 8000.');
    }
    throw err;
  }
}

// ===== MONACO EDITOR SETUP =====
function initMonacoEditor() {
  require.config({
    paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }
  });

  require(['vs/editor/editor.main'], function () {
    // Custom dark theme
    monaco.editor.defineTheme('bugmind-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '5a6380', fontStyle: 'italic' },
        { token: 'keyword', foreground: 'c792ea' },
        { token: 'string', foreground: 'ecc48d' },
        { token: 'number', foreground: 'f78c6c' },
        { token: 'type', foreground: 'ffcb6b' },
        { token: 'function', foreground: '82aaff' },
        { token: 'variable', foreground: 'e8ecf4' },
        { token: 'operator', foreground: '89ddff' },
      ],
      colors: {
        'editor.background': '#141828',
        'editor.foreground': '#e8ecf4',
        'editor.lineHighlightBackground': '#1e2440',
        'editor.selectionBackground': '#2a3560',
        'editorCursor.foreground': '#4a7cff',
        'editorLineNumber.foreground': '#3d4560',
        'editorLineNumber.activeForeground': '#8b95b0',
        'editorIndentGuide.background': '#1e2440',
        'editorGutter.background': '#0f1424',
      }
    });

    editor = monaco.editor.create(document.getElementById('monaco-editor'), {
      value: FILES[currentFile],
      language: 'python',
      theme: 'bugmind-dark',
      fontSize: 15,
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
      fontLigatures: true,
      lineNumbers: 'on',
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      automaticLayout: true,
      padding: { top: 16, bottom: 16 },
      renderLineHighlight: 'all',
      cursorBlinking: 'smooth',
      cursorSmoothCaretAnimation: 'on',
      smoothScrolling: true,
      tabSize: 4,
      wordWrap: 'on',
      bracketPairColorization: { enabled: true },
      guides: { bracketPairs: true, indentation: true },
    });

    // Add error markers
    addErrorMarkers();

    console.log('✅ Monaco Editor initialized');
  });
}

function addErrorMarkers() {
  if (!editor) return;
  const model = editor.getModel();
  monaco.editor.setModelMarkers(model, 'bugmind', [
    {
      startLineNumber: 3, startColumn: 1,
      endLineNumber: 3, endColumn: 15,
      message: 'SyntaxError: Missing colon after if statement',
      severity: monaco.MarkerSeverity.Error
    },
    {
      startLineNumber: 3, startColumn: 4,
      endLineNumber: 3, endColumn: 14,
      message: 'TypeError: Cannot compare str with int.',
      severity: monaco.MarkerSeverity.Warning
    }
  ]);
}

// ===== RUN CODE — BACKEND API =====
async function runCode() {
  if (!editor) return;

  const code = editor.getValue();
  const btn = document.getElementById('btn-run');
  const token = getToken();

  // If not logged in, still try (mock mode)
  if (!token) {
    showToast('⚠️ Login first for full features. Running in demo mode...', 'info');
    runCodeMock(code);
    return;
  }

  // Show running state
  btn.classList.add('running');
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
  appendOutput('⏳ Executing code...', 'info');

  try {
    const result = await apiCall('/code/run', 'POST', {
      code: code,
      language: 'python'
    });

    if (result.success) {
      appendOutput(`✅ Output (${result.execution_time}s):`, 'info');
      appendOutput(result.output, 'success');
    } else {
      appendOutput(`❌ ${result.error_type || 'Error'}:`, 'info');
      appendOutput(result.error, 'error');

      // Show AI analysis
      if (result.ai_analysis) {
        updateAIPanelWithAnalysis(result.ai_analysis);
      }
    }
  } catch (err) {
    appendOutput('❌ ' + err.message, 'error');
  } finally {
    btn.classList.remove('running');
    btn.innerHTML = '<i class="fas fa-play"></i> Run';
  }
}

// Mock run for when backend is not connected
function runCodeMock(code) {
  const btn = document.getElementById('btn-run');
  btn.classList.add('running');
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';

  setTimeout(() => {
    const hasTypeError = code.includes('age > 18') && !code.includes('int(age)');
    const hasSyntaxError = code.match(/if\s+.+[^:]\s*$/m);

    if (hasSyntaxError) {
      appendOutput("❌ SyntaxError: expected ':'", 'error');
      appendOutput("  Line 3: if age > 18", 'error');
    } else if (hasTypeError) {
      appendOutput("❌ TypeError: '>' not supported between instances of 'str' and 'int'", 'error');
    } else {
      appendOutput('✅ Code executed successfully!', 'success');
      appendOutput('(No output — demo mode)', 'info');
    }

    btn.classList.remove('running');
    btn.innerHTML = '<i class="fas fa-play"></i> Run';
  }, 800);
}

// ===== OUTPUT CONSOLE =====
function appendOutput(text, type = 'normal') {
  let console_el = document.getElementById('output-console');
  if (!console_el) {
    // Create output console if it doesn't exist
    const editorArea = document.querySelector('.editor-container');
    console_el = document.createElement('div');
    console_el.id = 'output-console';
    console_el.className = 'output-console';
    editorArea.parentNode.insertBefore(console_el, editorArea.nextSibling);
  }

  const line = document.createElement('div');
  if (type === 'error') line.className = 'output-error';
  else if (type === 'info') line.className = 'output-info';
  else if (type === 'success') line.style.color = 'var(--accent-green)';
  line.textContent = text;
  console_el.appendChild(line);
  console_el.scrollTop = console_el.scrollHeight;
}

function clearConsole() {
  const console_el = document.getElementById('output-console');
  if (console_el) console_el.innerHTML = '';
  showToast('🧹 Console cleared', 'info');
}

// ===== SAVE CODE =====
function saveCode() {
  if (!editor) return;
  FILES[currentFile] = editor.getValue();
  showToast('💾 Code saved!', 'success');
}

// ===== AUTO FIX =====
async function applyAutoFix() {
  if (!editor) return;
  const code = editor.getValue();
  const token = getToken();

  if (token) {
    try {
      const result = await apiCall('/code/autofix', 'POST', {
        code: code,
        error_type: 'TypeError',
        error_message: "'>' not supported between instances of 'str' and 'int'"
      });
      if (result.fixed_code) {
        editor.setValue(result.fixed_code);
        showToast('✅ Auto fix applied!', 'success');
      }
    } catch (err) {
      // Fall back to local fix
      applyLocalFix();
    }
  } else {
    applyLocalFix();
  }

  // Hide error popup
  const popup = document.getElementById('error-popup');
  if (popup) {
    popup.style.opacity = '0';
    popup.style.transform = 'translateY(-8px)';
    setTimeout(() => popup.style.display = 'none', 300);
  }

  // Clear error markers
  if (editor) {
    monaco.editor.setModelMarkers(editor.getModel(), 'bugmind', []);
  }
}

function applyLocalFix() {
  if (!editor) return;
  let code = editor.getValue();
  code = code.replace(/if age > 18\b/g, 'if int(age) > 18:');
  code = code.replace(/if int\(age\) > 18([^:])/g, 'if int(age) > 18:$1');
  editor.setValue(code);
  showToast('✅ Auto fix applied!', 'success');
}

// ===== UPDATE AI PANEL =====
function updateAIPanelWithAnalysis(analysis) {
  const messageText = document.querySelector('.ai-message .message-text');
  const codeBlock = document.querySelector('.ai-code-block');

  if (messageText && analysis.explanation) {
    messageText.innerHTML = analysis.explanation;
  }
  if (codeBlock && analysis.suggested_fix) {
    codeBlock.innerHTML = `<span class="code-label">suggested fix</span>${analysis.suggested_fix}`;
  }
}

// ===== EXPLAIN ERROR =====
function explainError() {
  const aiBody = document.querySelector('.ai-panel-body');
  const btn = document.getElementById('btn-explain');

  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
  btn.style.opacity = '0.7';
  btn.style.pointerEvents = 'none';

  setTimeout(() => {
    const explanation = `
      <div style="background:var(--bg-card); border:1px solid var(--border-color); border-radius:var(--radius-md); padding:16px; margin-bottom:16px;">
        <p style="font-size:13px; color:var(--text-secondary); line-height:1.8;">
          🔍 <strong>What happened?</strong><br>
          The <code>input()</code> function always returns a <strong>string</strong>. When you write <code>age > 18</code>, you're comparing a string with an integer, which Python doesn't allow.<br><br>
          🔧 <strong>How to fix it:</strong><br>
          Convert the string to an integer: <code>age = int(input('Enter your age:'))</code><br><br>
          📚 <strong>Learning Tip:</strong><br>
          Always remember: <code>input()</code> returns a string. Use <code>int()</code> for numbers, <code>float()</code> for decimals.
        </p>
      </div>
    `;

    const explDiv = document.createElement('div');
    explDiv.className = 'ai-message';
    explDiv.style.animation = 'popupSlideIn 0.4s ease';
    explDiv.innerHTML = explanation;

    const insightsSection = aiBody.querySelector('.ai-section');
    aiBody.insertBefore(explDiv, insightsSection);

    btn.innerHTML = 'Explain this error...<span class="btn-sub">submit</span>';
    btn.style.opacity = '1';
    btn.style.pointerEvents = 'auto';
    aiBody.scrollTop = explDiv.offsetTop - 20;
  }, 1000);
}

// ===== FILE EXPLORER =====
function selectFile(element, filename) {
  document.querySelectorAll('.file-tree .tree-item').forEach(el => el.classList.remove('active'));
  element.classList.add('active');
  currentFile = filename;

  if (editor && FILES[filename]) {
    editor.setValue(FILES[filename]);
    const activeTab = document.querySelector('.editor-tab.active');
    if (activeTab) {
      const icon = filename.endsWith('.py') ? '<i class="fab fa-python"></i>' : '<i class="fas fa-file-alt"></i>';
      activeTab.innerHTML = `<span class="tab-icon">${icon}</span> ${filename} <span class="tab-close" onclick="event.stopPropagation()">&times;</span>`;
    }
    const lang = filename.endsWith('.py') ? 'Python' : 'Text';
    const langIcon = filename.endsWith('.py') ? '<i class="fab fa-python"></i>' : '<i class="fas fa-file-alt"></i>';
    document.querySelector('.tab-language').innerHTML = `${langIcon} <span>${lang}</span>`;
  }

  const popup = document.getElementById('error-popup');
  if (popup) popup.style.display = filename === 'main.py' ? 'block' : 'none';
}

function toggleFolder(element) {
  const arrow = element.querySelector('.tree-arrow');
  const folderIcon = element.querySelector('.file-icon i');
  const subtree = element.nextElementSibling;
  if (arrow) arrow.classList.toggle('open');
  if (folderIcon) {
    folderIcon.classList.toggle('fa-folder-open');
    folderIcon.classList.toggle('fa-folder');
  }
  if (subtree && subtree.classList.contains('sub-tree')) subtree.classList.toggle('hidden');
}

// ===== BOTTOM TABS =====
function switchBottomTab(element, tabName) {
  document.querySelectorAll('.bottom-tab').forEach(tab => tab.classList.remove('active'));
  element.classList.add('active');
}

// ===== TOAST NOTIFICATIONS =====
function showToast(message, type = 'info') {
  const existing = document.querySelector('.toast-notification');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast-notification';
  const bgColor = type === 'success' ? 'var(--accent-green-dim)' : type === 'error' ? 'var(--accent-red-dim)' : 'var(--accent-blue-dim)';
  const textColor = type === 'success' ? 'var(--accent-green)' : type === 'error' ? 'var(--accent-red)' : 'var(--accent-blue)';

  toast.style.cssText = `
    position:fixed; bottom:60px; right:24px;
    background:${bgColor}; color:${textColor};
    padding:12px 20px; border-radius:10px;
    font-size:13px; font-weight:500; font-family:'Inter',sans-serif;
    z-index:9999; animation:popupSlideIn 0.3s ease;
    backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.06);
    box-shadow:0 8px 32px rgba(0,0,0,0.3);
  `;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(8px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ===== KEYBOARD SHORTCUTS =====
document.addEventListener('keydown', function (e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    runCode();
  }
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault();
    saveCode();
  }
  if (e.key === 'Escape') {
    const popup = document.getElementById('error-popup');
    if (popup && popup.style.display !== 'none') popup.style.display = 'none';
  }
});

// ===== INIT =====
document.addEventListener('DOMContentLoaded', function () {
  if (document.getElementById('monaco-editor')) {
    initMonacoEditor();
  }

  // Update user display
  const user = getUser();
  const userName = document.querySelector('.user-name');
  const userAvatar = document.querySelector('.user-avatar');
  if (user && userName) {
    userName.textContent = user.name || 'User';
    if (userAvatar) userAvatar.textContent = (user.name || 'U').substring(0, 2).toUpperCase();
  }

  console.log('🧠 BugMind AI frontend loaded');
});
