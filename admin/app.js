// API Base URL
const API_BASE = "http://localhost:8007";

// State
let currentSection = "prompts";
let currentFile = null;
let originalContent = "";
let editor = null;

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  initMonacoEditor();
  initEventListeners();
  loadFiles("prompts");
});

// Initialize Monaco Editor
function initMonacoEditor() {
  require.config({
    paths: {
      vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs",
    },
  });

  require(["vs/editor/editor.main"], function () {
    editor = monaco.editor.create(document.getElementById("editor"), {
      value: "",
      language: "python",
      theme: "vs-dark",
      automaticLayout: true,
      fontSize: 14,
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      wordWrap: "on",
    });

    // Listen for content changes
    editor.onDidChangeModelContent(() => {
      const hasChanges = editor.getValue() !== originalContent;
      document.getElementById("btn-save").disabled =
        !hasChanges || !currentFile;
      document.getElementById("btn-reset").disabled =
        !hasChanges || !currentFile;
    });
  });
}

// Event Listeners
function initEventListeners() {
  // Navigation
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const section = e.currentTarget.dataset.section;
      switchSection(section);
    });
  });

  // Sync buttons
  document.getElementById("sync-product").addEventListener("click", () => {
    syncVectorStore("product");
  });

  document.getElementById("sync-warranty").addEventListener("click", () => {
    syncVectorStore("warranty");
  });

  // Editor actions
  document.getElementById("btn-save").addEventListener("click", saveFile);
  document.getElementById("btn-reset").addEventListener("click", resetEditor);
}

// Switch Section
function switchSection(section) {
  currentSection = section;

  // Update navigation
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.section === section);
  });

  // Update title
  const titles = {
    prompts: "Prompts",
    data: "Data Files",
  };
  document.getElementById("section-title").textContent = titles[section];

  // Update breadcrumb
  const breadcrumbs = {
    prompts: "app/prompts",
    data: "data/",
  };
  document.getElementById("breadcrumb").textContent = breadcrumbs[section];

  // Load files
  loadFiles(section);

  // Clear editor
  clearEditor();
}

// Load Files
async function loadFiles(section) {
  const fileList = document.getElementById("file-list");
  fileList.innerHTML = '<div class="loading">Loading files...</div>';

  try {
    const endpoint =
      section === "prompts" ? "/api/files/prompts" : "/api/files/data";
    const response = await fetch(`${API_BASE}${endpoint}`);

    if (!response.ok) throw new Error("Failed to load files");

    const files = await response.json();

    if (files.length === 0) {
      fileList.innerHTML = '<div class="loading">No files found</div>';
      return;
    }

    // Group files by directory for data section
    if (section === "data") {
      renderDataFiles(files);
    } else {
      renderPromptFiles(files);
    }
  } catch (error) {
    console.error("Error loading files:", error);
    fileList.innerHTML =
      '<div class="loading" style="color: var(--danger)">Error loading files</div>';
    showToast("Error loading files: " + error.message, "error");
  }
}

// Render Prompt Files
function renderPromptFiles(files) {
  const fileList = document.getElementById("file-list");
  fileList.innerHTML = "";

  // Filter only Python files
  const pythonFiles = files.filter(
    (f) => f.type === "file" && f.extension === ".py"
  );

  pythonFiles.forEach((file) => {
    const item = createFileItem(file);
    fileList.appendChild(item);
  });
}

// Render Data Files
function renderDataFiles(files) {
  const fileList = document.getElementById("file-list");
  fileList.innerHTML = "";

  // Group by subdirectory
  const groups = {};
  files.forEach((file) => {
    if (file.type === "file") {
      const parts = file.path.split("/");
      const dir = parts.length > 2 ? parts[1] : "root";
      if (!groups[dir]) groups[dir] = [];
      groups[dir].push(file);
    }
  });

  // Render groups
  Object.keys(groups)
    .sort()
    .forEach((dir) => {
      const header = document.createElement("div");
      header.className = "file-group-header";
      header.style.cssText =
        "padding: 0.5rem 1rem; font-weight: 600; color: var(--text-secondary); font-size: 0.75rem; text-transform: uppercase; margin-top: 1rem;";
      header.textContent = dir;
      fileList.appendChild(header);

      groups[dir].forEach((file) => {
        const item = createFileItem(file);
        fileList.appendChild(item);
      });
    });
}

// Create File Item Element
function createFileItem(file) {
  const item = document.createElement("div");
  item.className = "file-item";

  const icon = getFileIcon(file.extension);

  item.innerHTML = `
        <span class="file-icon">${icon}</span>
        <div class="file-details">
            <div class="name">${file.name}</div>
            <div class="path">${file.path}</div>
        </div>
    `;

  item.addEventListener("click", () => loadFileContent(file));

  return item;
}

// Get File Icon
function getFileIcon(extension) {
  const icons = {
    ".py": "🐍",
    ".json": "📋",
    ".txt": "📄",
    ".md": "📝",
    ".db": "🗄️",
  };
  return icons[extension] || "📄";
}

// Load File Content
async function loadFileContent(file) {
  try {
    const response = await fetch(
      `${API_BASE}/api/file/content?path=${encodeURIComponent(file.path)}`
    );

    if (!response.ok) throw new Error("Failed to load file content");

    const data = await response.json();

    // Update current file
    currentFile = file;
    originalContent = data.content;

    // Update UI
    document.getElementById("current-file").textContent = file.name;
    document.getElementById("current-path").textContent = file.path;

    // Set editor language
    const language = getEditorLanguage(file.extension);
    const model = monaco.editor.createModel(data.content, language);
    editor.setModel(model);

    // Show editor
    document.querySelector(".editor").classList.add("active");
    document.querySelector(".editor-placeholder").classList.add("hidden");

    // Highlight active file
    document.querySelectorAll(".file-item").forEach((item) => {
      item.classList.remove("active");
    });
    event.currentTarget.classList.add("active");

    // Disable buttons initially
    document.getElementById("btn-save").disabled = true;
    document.getElementById("btn-reset").disabled = true;
  } catch (error) {
    console.error("Error loading file:", error);
    showToast("Error loading file: " + error.message, "error");
  }
}

// Get Editor Language
function getEditorLanguage(extension) {
  const languages = {
    ".py": "python",
    ".json": "json",
    ".txt": "plaintext",
    ".md": "markdown",
    ".js": "javascript",
    ".html": "html",
    ".css": "css",
  };
  return languages[extension] || "plaintext";
}

// Save File
async function saveFile() {
  if (!currentFile) return;

  const content = editor.getValue();
  const saveBtn = document.getElementById("btn-save");
  const originalText = saveBtn.textContent;

  saveBtn.disabled = true;
  saveBtn.textContent = "💾 Saving...";

  try {
    const response = await fetch(`${API_BASE}/api/file/content`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        path: currentFile.path,
        content: content,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to save file");
    }

    const result = await response.json();

    // Update original content
    originalContent = content;

    showToast(`✅ ${result.message}`, "success");
    saveBtn.textContent = originalText;
    saveBtn.disabled = true;
    document.getElementById("btn-reset").disabled = true;
  } catch (error) {
    console.error("Error saving file:", error);
    showToast("Error saving file: " + error.message, "error");
    saveBtn.textContent = originalText;
    saveBtn.disabled = false;
  }
}

// Reset Editor
function resetEditor() {
  if (!currentFile) return;

  const model = monaco.editor.createModel(
    originalContent,
    getEditorLanguage(currentFile.extension)
  );
  editor.setModel(model);

  document.getElementById("btn-save").disabled = true;
  document.getElementById("btn-reset").disabled = true;
}

// Clear Editor
function clearEditor() {
  currentFile = null;
  originalContent = "";

  document.getElementById("current-file").textContent = "No file selected";
  document.getElementById("current-path").textContent = "";

  document.querySelector(".editor").classList.remove("active");
  document.querySelector(".editor-placeholder").classList.remove("hidden");

  document.getElementById("btn-save").disabled = true;
  document.getElementById("btn-reset").disabled = true;

  document.querySelectorAll(".file-item").forEach((item) => {
    item.classList.remove("active");
  });
}

// Sync Vector Store
async function syncVectorStore(type) {
  const btnId = type === "product" ? "sync-product" : "sync-warranty";
  const btn = document.getElementById(btnId);
  const statusDiv = document.getElementById("sync-status");

  const originalHTML = btn.innerHTML;
  btn.disabled = true;
  btn.classList.add("loading");
  btn.innerHTML = '<span class="icon">🔄</span> Syncing...';

  statusDiv.className = "sync-status";
  statusDiv.textContent = "Rebuilding vector store... This may take a minute.";
  statusDiv.style.display = "block";

  try {
    const endpoint =
      type === "product"
        ? "/api/sync/vector-store"
        : "/api/sync/warranty-vector-store";
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Sync failed");
    }

    const result = await response.json();

    statusDiv.className = "sync-status success";
    statusDiv.textContent = `✅ ${result.message}`;

    showToast(`✅ ${result.message}`, "success");
  } catch (error) {
    console.error("Error syncing:", error);
    statusDiv.className = "sync-status error";
    statusDiv.textContent = `❌ Error: ${error.message}`;
    showToast("Sync failed: " + error.message, "error");
  } finally {
    btn.innerHTML = originalHTML;
    btn.disabled = false;
    btn.classList.remove("loading");

    // Hide status after 5 seconds
    setTimeout(() => {
      statusDiv.style.display = "none";
    }, 5000);
  }
}

// Show Toast Notification
function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast ${type} show`;

  setTimeout(() => {
    toast.classList.remove("show");
  }, 4000);
}
