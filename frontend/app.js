/* ============================================
   BugMind AI - Frontend Application Logic
   ============================================ */

// ===== CONFIGURATION =====
const DEMO_CODE = `age = input('Enter your age:')

if age > 18
    print('You can vote!')
    if int(age) > 18:`;

const FILES = {
  'main.py': `age = input('Enter your age:')\n\nif age > 18\n    print('You can vote!')\n    if int(age) > 18:`,
  'utils.py': `# Utility functions for BugMind AI\n\ndef validate_input(value, expected_type):\n    """Validate and convert input to expected type"""\n    try:\n        return expected_type(value)\n    except (ValueError, TypeError) as e:\n        return None\n\ndef format_output(result):\n    """Format the output for display"""\n    if result is None:\n        return "No output"\n    return str(result)`,
  'input.txt': `# Sample Input File\n18\nHello World\n42`
};

// AI mock responses for different error types
const AI_RESPONSES = {
  TypeError: {
    message: "Oops! It looks like you're comparing <strong>a string</strong> to an integer. Try converting the input to an integer!",
    fix: 'if int(age) > 18:',
    explanation: `🔍 <strong>What happened?</strong><br>
The <code>input()</code> function in Python always returns a <strong>string</strong>. When you write <code>age > 18</code>, you're trying to compare a string with an integer, which Python doesn't allow.<br><br>
🔧 <strong>How to fix it:</strong><br>
Convert the string to an integer using <code>int()</code>:<br>
<code>age = int(input('Enter your age:'))</code><br><br>
📚 <strong>Learning Tip:</strong><br>
Always remember: <code>input()</code> returns a string. Use <code>int()</code> for numbers, <code>float()</code> for decimals.`
  },
  SyntaxError: {
    message: "It looks like you're missing a <strong>colon (:)</strong> at the end of your <code>if</code> statement.",
    fix: 'if age > 18:',
    explanation: `🔍 <strong>What happened?</strong><br>
In Python, every <code>if</code>, <code>elif</code>, <code>else</code>, <code>for</code>, <code>while</code>, and <code>def</code> statement must end with a colon <code>:</code>.<br><br>
🔧 <strong>How to fix it:</strong><br>
Add a colon at the end: <code>if age > 18:</code><br><br>
📚 <strong>Learning Tip:</strong><br>
Think of the colon as saying "here's what's next" — it tells Python that an indented block follows.`
  }
};

// ===== GLOBAL STATE =====
let editor = null;
let currentFile = 'main.py';
let errorPopupVisible = true;

// ===== MONACO EDITOR SETUP =====
function initMonacoEditor() {
  require.config({
    paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }
  });

  require(['vs/editor/editor.main'], function () {
    // Define custom dark theme matching BugMind colors
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
        'editor.selectionHighlightBackground': '#2a356040',
        'editorIndentGuide.background': '#1e2440',
        'editorIndentGuide.activeBackground': '#2a3560',
        'editorGutter.background': '#0f1424',
        'editorOverviewRuler.border': '#141828',
      }
    });

    editor = monaco.editor.create(document.getElementById('monaco-editor'), {
      value: FILES[currentFile],
      language: 'python',
      theme: 'bugmind-dark',
      fontSize: 15,
      fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
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
      suggest: {
        showKeywords: true,
        showSnippets: true,
      },
    });

    // Add error markers (squiggly lines)
    addErrorMarkers();

    // Listen for code changes
    editor.onDidChangeModelContent(() => {
      const code = editor.getValue();
      analyzeCode(code);
    });

    console.log('✅ Monaco Editor initialized with BugMind theme');
  });
}

// ===== ERROR MARKERS =====
function addErrorMarkers() {
  if (!editor) return;

  const model = editor.getModel();
  monaco.editor.setModelMarkers(model, 'bugmind', [
    {
      startLineNumber: 3,
      startColumn: 1,
      endLineNumber: 3,
      endColumn: 15,
      message: 'SyntaxError: Missing colon after if statement',
      severity: monaco.MarkerSeverity.Error
    },
    {
      startLineNumber: 3,
      startColumn: 4,
      endLineNumber: 3,
      endColumn: 14,
      message: 'TypeError: Cannot compare str with int. Use int(age) instead.',
      severity: monaco.MarkerSeverity.Warning
    }
  ]);
}

// ===== CODE ANALYSIS (Mock) =====
function analyzeCode(code) {
  // Simple mock error detection
  const errors = [];

  if (code.includes('input(') && code.includes('> 18') && !code.includes('int(')) {
    errors.push({
      type: 'TypeError',
      message: "Comparing string to integer",
      line: code.split('\n').findIndex(l => l.includes('> 18')) + 1
    });
  }

  if (code.match(/if\s+.+[^:]\s*$/m)) {
    errors.push({
      type: 'SyntaxError',
      message: "Missing colon after if statement",
      line: code.split('\n').findIndex(l => l.match(/if\s+.+[^:]\s*$/)) + 1
    });
  }

  updateProblemsCount(errors.length);
}

function updateProblemsCount(count) {
  const badge = document.querySelector('.bottom-tab.active .tab-badge');
  if (badge) {
    badge.textContent = count;
    badge.style.display = count > 0 ? 'inline' : 'none';
  }
}

// ===== FILE EXPLORER =====
function selectFile(element, filename) {
  // Remove active from all tree items
  document.querySelectorAll('.file-tree .tree-item').forEach(el => {
    el.classList.remove('active');
  });

  // Set active
  element.classList.add('active');
  currentFile = filename;

  // Update editor content
  if (editor && FILES[filename]) {
    editor.setValue(FILES[filename]);

    // Update tab
    const activeTab = document.querySelector('.editor-tab.active');
    if (activeTab) {
      const icon = filename.endsWith('.py') ? '<i class="fab fa-python"></i>' : '<i class="fas fa-file-alt"></i>';
      activeTab.innerHTML = `<span class="tab-icon">${icon}</span> ${filename} <span class="tab-close" onclick="event.stopPropagation()">&times;</span>`;
    }

    // Update language indicator
    const lang = filename.endsWith('.py') ? 'Python' : 'Text';
    const langIcon = filename.endsWith('.py') ? '<i class="fab fa-python"></i>' : '<i class="fas fa-file-alt"></i>';
    document.querySelector('.tab-language').innerHTML = `${langIcon} <span>${lang}</span>`;
  }

  // Toggle error popup based on file
  const popup = document.getElementById('error-popup');
  if (popup) {
    popup.style.display = filename === 'main.py' ? 'block' : 'none';
  }
}

function toggleFolder(element) {
  const arrow = element.querySelector('.tree-arrow');
  const folderIcon = element.querySelector('.file-icon i');
  const subtree = element.nextElementSibling;

  if (arrow) arrow.classList.toggle('open');

  if (folderIcon) {
    if (folderIcon.classList.contains('fa-folder-open')) {
      folderIcon.classList.replace('fa-folder-open', 'fa-folder');
    } else {
      folderIcon.classList.replace('fa-folder', 'fa-folder-open');
    }
  }

  if (subtree && subtree.classList.contains('sub-tree')) {
    subtree.classList.toggle('hidden');
  }
}

// ===== AUTO FIX =====
function applyAutoFix() {
  if (!editor) return;

  const model = editor.getModel();
  const code = model.getValue();

  // Apply fix: replace 'if age > 18' with 'if int(age) > 18:'
  let fixed = code.replace(/if age > 18\b/g, 'if int(age) > 18:');
  // Also fix the missing colon case  
  fixed = fixed.replace(/if int\(age\) > 18([^:])/g, 'if int(age) > 18:$1');

  editor.setValue(fixed);

  // Clear error markers
  monaco.editor.setModelMarkers(model, 'bugmind', []);

  // Hide error popup
  const popup = document.getElementById('error-popup');
  if (popup) {
    popup.style.animation = 'none';
    popup.style.opacity = '0';
    popup.style.transform = 'translateY(-8px)';
    setTimeout(() => popup.style.display = 'none', 300);
  }

  // Update AI panel
  updateAIPanel('fix-applied');

  // Show success toast
  showToast('✅ Auto fix applied successfully!', 'success');
}

// ===== EXPLAIN ERROR =====
function explainError() {
  const aiBody = document.querySelector('.ai-panel-body');
  const btn = document.getElementById('btn-explain');

  // Show loading
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
  btn.style.opacity = '0.7';
  btn.style.pointerEvents = 'none';

  setTimeout(() => {
    const explanation = AI_RESPONSES.TypeError.explanation;

    // Insert explanation
    const explDiv = document.createElement('div');
    explDiv.className = 'ai-message';
    explDiv.style.animation = 'popupSlideIn 0.4s ease';
    explDiv.innerHTML = `
      <div style="background:var(--bg-card); border:1px solid var(--border-color); border-radius:var(--radius-md); padding:16px; margin-bottom:16px;">
        <p style="font-size:13px; color:var(--text-secondary); line-height:1.8;">${explanation}</p>
      </div>
    `;

    // Insert before insights section
    const insightsSection = aiBody.querySelector('.ai-section');
    aiBody.insertBefore(explDiv, insightsSection);

    // Restore button
    btn.innerHTML = 'Explain this error...<span class="btn-sub">submit</span>';
    btn.style.opacity = '1';
    btn.style.pointerEvents = 'auto';

    // Scroll to explanation
    aiBody.scrollTop = explDiv.offsetTop - 20;
  }, 1200);
}

// ===== UPDATE AI PANEL =====
function updateAIPanel(action) {
  const messageText = document.querySelector('.ai-message .message-text');
  const codeBlock = document.querySelector('.ai-code-block');

  if (action === 'fix-applied') {
    if (messageText) {
      messageText.innerHTML = '✅ <strong>Fix applied!</strong> The type error has been resolved. Your code now correctly converts the input to an integer before comparison.';
    }
    if (codeBlock) {
      codeBlock.innerHTML = `<span class="code-label">fixed code</span>age = int(input('Enter your age:'))<br>if int(age) > 18:<br>&nbsp;&nbsp;&nbsp;&nbsp;print('You can vote!')`;
    }
  }
}

// ===== BOTTOM TABS =====
function switchBottomTab(element, tabName) {
  document.querySelectorAll('.bottom-tab').forEach(tab => tab.classList.remove('active'));
  element.classList.add('active');

  // For now just visual tab switching
  console.log(`Switched to ${tabName} tab`);
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
    position: fixed;
    bottom: 60px;
    right: 24px;
    background: ${bgColor};
    color: ${textColor};
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
    z-index: 9999;
    animation: popupSlideIn 0.3s ease;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
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

// ===== RUN CODE (Mock) =====
function runCode() {
  if (!editor) return;

  const code = editor.getValue();
  showToast('▶️ Running code...', 'info');

  // Mock execution
  setTimeout(() => {
    const hasError = code.includes('age > 18') && !code.includes('int(age)');
    if (hasError) {
      showToast("❌ TypeError: '>' not supported between 'str' and 'int'", 'error');
    } else {
      showToast('✅ Code executed successfully!', 'success');
    }
  }, 800);
}

// ===== KEYBOARD SHORTCUTS =====
document.addEventListener('keydown', function (e) {
  // Ctrl+Enter to run code
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    runCode();
  }

  // Escape to close error popup
  if (e.key === 'Escape') {
    const popup = document.getElementById('error-popup');
    if (popup && popup.style.display !== 'none') {
      popup.style.display = 'none';
    }
  }
});

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function () {
  // Only init Monaco if we're on the editor page
  if (document.getElementById('monaco-editor')) {
    initMonacoEditor();
  }

  console.log('🧠 BugMind AI frontend loaded');
});
