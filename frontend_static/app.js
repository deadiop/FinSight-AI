// Application State
const state = {
    backendUrl: localStorage.getItem('backend_url') || 'https://finsight-backend-k35w.onrender.com',
    isConnected: false,
    chart: null,
    filesUploading: 0
};

// DOM Elements
const elements = {
    connectionStatus: document.getElementById('connectionStatus'),
    settingsBtn: document.getElementById('settingsBtn'),
    settingsModal: document.getElementById('settingsModal'),
    backendUrlInput: document.getElementById('backendUrlInput'),
    saveSettings: document.getElementById('saveSettings'),
    cancelSettings: document.getElementById('cancelSettings'),
    closeSettingsModal: document.getElementById('closeSettingsModal'),
    
    resetBtn: document.getElementById('resetBtn'),
    downloadBtn: document.getElementById('downloadBtn'),
    insightsBtn: document.getElementById('insightsBtn'),
    insightsContent: document.getElementById('insightsContent'),
    
    incomeValue: document.getElementById('incomeValue'),
    expenseValue: document.getElementById('expenseValue'),
    netValue: document.getElementById('netValue'),
    
    dropzone: document.getElementById('dropzone'),
    fileInput: document.getElementById('fileInput'),
    fileList: document.getElementById('fileList'),
    
    tableBody: document.getElementById('tableBody'),
    transactionsTable: document.getElementById('transactionsTable'),
    tablePlaceholder: document.getElementById('tablePlaceholder'),
    chartPlaceholder: document.getElementById('chartPlaceholder'),
    expenseChart: document.getElementById('expenseChart'),
    
    chatbotSidebar: document.getElementById('chatbotSidebar'),
    toggleSidebar: document.getElementById('toggleSidebar'),
    sidebarTrigger: document.getElementById('sidebarTrigger'),
    chatMessages: document.getElementById('chatMessages'),
    chatForm: document.getElementById('chatForm'),
    chatInput: document.getElementById('chatInput'),
    chatSendBtn: document.getElementById('chatSendBtn')
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    // Set settings input value
    elements.backendUrlInput.value = state.backendUrl;
    
    // Bind Event Listeners
    setupEventListeners();
    
    // Check Connection & Load Dashboard
    checkConnection();
    
    // Start Connection Polling (every 8 seconds)
    setInterval(checkConnection, 8000);
});

// Setup Event Listeners
function setupEventListeners() {
    // Settings Modal
    elements.settingsBtn.addEventListener('click', () => {
        elements.backendUrlInput.value = state.backendUrl;
        elements.settingsModal.classList.add('open');
    });
    
    const closeModal = () => elements.settingsModal.classList.remove('open');
    elements.cancelSettings.addEventListener('click', closeModal);
    elements.closeSettingsModal.addEventListener('click', closeModal);
    
    elements.saveSettings.addEventListener('click', () => {
        let url = elements.backendUrlInput.value.trim();
        if (url.endsWith('/')) url = url.slice(0, -1);
        state.backendUrl = url || 'http://127.0.0.1:8000';
        localStorage.setItem('backend_url', state.backendUrl);
        closeModal();
        checkConnection(true); // Force reload
    });
    
    // Reset Data
    elements.resetBtn.addEventListener('click', () => {
        if (confirm("Are you sure you want to erase all financial transactions? This action is permanent.")) {
            clearDatabase();
        }
    });
    
    // Generate Insights
    elements.insightsBtn.addEventListener('click', generateInsights);
    
    // Download Report
    elements.downloadBtn.addEventListener('click', downloadReport);
    
    // Drag & Drop Ingestion
    elements.dropzone.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
    
    elements.dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.dropzone.classList.add('dragover');
    });
    
    elements.dropzone.addEventListener('dragleave', () => {
        elements.dropzone.classList.remove('dragover');
    });
    
    elements.dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.dropzone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });
    
    // Sidebar Chatbot Toggle
    elements.toggleSidebar.addEventListener('click', () => {
        elements.chatbotSidebar.classList.add('collapsed');
        elements.sidebarTrigger.style.display = 'block';
    });
    
    elements.sidebarTrigger.addEventListener('click', () => {
        elements.chatbotSidebar.classList.remove('collapsed');
        elements.sidebarTrigger.style.display = 'none';
        scrollToBottom();
    });
    
    // Chatbot Submit
    elements.chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        handleChatSubmit();
    });
    
    elements.chatInput.addEventListener('input', () => {
        elements.chatSendBtn.disabled = !elements.chatInput.value.trim();
    });
}

// Check Connection to FastAPI
async function checkConnection(forceReload = false) {
    const defaultFallback = 'https://finsight-backend-k35w.onrender.com';
    try {
        const res = await fetch(`${state.backendUrl}/health`, { method: 'GET', mode: 'cors' });
        if (res.ok) {
            updateConnectionStatus(true);
            if (!state.isConnected || forceReload) {
                state.isConnected = true;
                loadDashboardData();
            }
            return;
        }
    } catch (e) {
        console.warn("Connection to primary backend failed:", e);
    }

    // Self-healing: if connection to primary failed, and we have a custom URL saved in localStorage,
    // try to fall back to the default active tunnel URL (in case the saved one is an expired tunnel)
    if (state.backendUrl !== defaultFallback) {
        try {
            console.log("Trying active fallback tunnel URL:", defaultFallback);
            const res = await fetch(`${defaultFallback}/health`, { method: 'GET', mode: 'cors' });
            if (res.ok) {
                state.backendUrl = defaultFallback;
                localStorage.setItem('backend_url', defaultFallback);
                updateConnectionStatus(true);
                state.isConnected = true;
                loadDashboardData();
                return;
            }
        } catch (e) {
            console.warn("Fallback connection also failed:", e);
        }
    }

    updateConnectionStatus(false);
}

function updateConnectionStatus(isOnline) {
    if (isOnline) {
        elements.connectionStatus.className = 'connection-status online';
        elements.connectionStatus.querySelector('.status-text').textContent = 'API Connected';
        elements.chatSendBtn.disabled = !elements.chatInput.value.trim();
        elements.insightsBtn.disabled = false;
        elements.resetBtn.disabled = false;
    } else {
        elements.connectionStatus.className = 'connection-status offline';
        elements.connectionStatus.querySelector('.status-text').textContent = 'API Offline';
        elements.chatSendBtn.disabled = true;
        elements.insightsBtn.disabled = true;
        elements.resetBtn.disabled = true;
        state.isConnected = false;
    }
}

// Load Dashboard Metrics, Charts and Data
async function loadDashboardData() {
    if (!state.isConnected) return;
    
    try {
        // 1. Fetch Metrics Summary
        const summaryRes = await fetch(`${state.backendUrl}/summary`, { mode: 'cors' });
        const summary = await summaryRes.json();
        
        elements.incomeValue.textContent = `₹${parseFloat(summary.income || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        elements.expenseValue.textContent = `₹${parseFloat(summary.expense || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        elements.netValue.textContent = `₹${parseFloat(summary.net || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        
        // Style Net savings green/red
        if (parseFloat(summary.net || 0) < 0) {
            elements.netValue.style.color = 'var(--danger-color)';
        } else {
            elements.netValue.style.color = 'var(--success-color)';
        }
        
        // 2. Fetch Transactions List
        const transactionsRes = await fetch(`${state.backendUrl}/transactions`, { mode: 'cors' });
        const transactions = await transactionsRes.json();
        renderTransactionsTable(transactions);
        
        // Enable/Disable download button
        elements.downloadBtn.disabled = transactions.length === 0;
        
        // 3. Fetch Category Distribution
        const categoriesRes = await fetch(`${state.backendUrl}/categories`, { mode: 'cors' });
        const categories = await categoriesRes.json();
        renderCategoryChart(categories);
        
    } catch (e) {
        console.error("Error loading dashboard data:", e);
    }
}

// Render Transactions Table
function renderTransactionsTable(transactions) {
    elements.tableBody.innerHTML = '';
    
    if (!transactions || transactions.length === 0) {
        elements.tablePlaceholder.style.display = 'flex';
        elements.transactionsTable.style.display = 'none';
        return;
    }
    
    elements.tablePlaceholder.style.display = 'none';
    elements.transactionsTable.style.display = 'table';
    
    transactions.forEach(tx => {
        const row = document.createElement('tr');
        
        const dateCell = document.createElement('td');
        dateCell.textContent = tx.date || 'N/A';
        
        const descCell = document.createElement('td');
        descCell.textContent = tx.description || 'N/A';
        
        const amountCell = document.createElement('td');
        const amount = parseFloat(tx.amount || 0);
        amountCell.className = `amount-col ${amount >= 0 ? 'positive' : 'negative'}`;
        amountCell.textContent = `${amount >= 0 ? '+' : '-'} ₹${Math.abs(amount).toFixed(2)}`;
        
        const categoryCell = document.createElement('td');
        const badge = document.createElement('span');
        const categoryLower = (tx.category || '').toLowerCase();
        badge.className = `badge badge-${categoryLower === 'credit' ? 'credit' : categoryLower === 'debit' ? 'debit' : 'other'}`;
        badge.textContent = tx.category || 'Uncategorized';
        categoryCell.appendChild(badge);
        
        const fileCell = document.createElement('td');
        fileCell.className = 'font-small';
        fileCell.style.color = 'var(--text-secondary)';
        fileCell.textContent = tx.source_file || 'N/A';
        
        row.appendChild(dateCell);
        row.appendChild(descCell);
        row.appendChild(amountCell);
        row.appendChild(categoryCell);
        row.appendChild(fileCell);
        
        elements.tableBody.appendChild(row);
    });
}

// Render Category distribution Doughnut Chart (Neobrutalist Style)
function renderCategoryChart(categories) {
    // Extract only expense categories
    const expenseCategories = (categories || []).filter(cat => parseFloat(cat.expense || 0) > 0);
    
    if (expenseCategories.length === 0) {
        elements.chartPlaceholder.style.display = 'flex';
        elements.expenseChart.style.display = 'none';
        if (state.chart) {
            state.chart.destroy();
            state.chart = null;
        }
        return;
    }
    
    elements.chartPlaceholder.style.display = 'none';
    elements.expenseChart.style.display = 'block';
    
    const labels = expenseCategories.map(cat => cat.category);
    const data = expenseCategories.map(cat => parseFloat(cat.expense));
    
    // Vibrant Brutalist Color Palette (Primary saturated blocks)
    const backgroundColors = [
        '#facc15', // Neon Yellow
        '#3b82f6', // Electric Blue
        '#ec4899', // Neon Pink
        '#22c55e', // Neon Green
        '#f97316', // Bright Orange
        '#a855f7', // Neon Purple
        '#6b7280'  // Medium Gray
    ];
    
    if (state.chart) {
        state.chart.data.labels = labels;
        state.chart.data.datasets[0].data = data;
        state.chart.update();
    } else {
        const ctx = elements.expenseChart.getContext('2d');
        state.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: backgroundColors.slice(0, data.length),
                    borderWidth: 3,
                    borderColor: '#000000' // Matches thick black borders
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%', // Bold ring width
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#000000',
                            padding: 15,
                            usePointStyle: true,
                            pointStyle: 'rectRounded',
                            font: { family: 'Inter', size: 10, weight: '800' }
                        }
                    }
                }
            }
        });
    }
}

// Ingest files via dropzone
async function handleFiles(files) {
    if (!state.isConnected || files.length === 0) return;
    
    elements.fileList.innerHTML = '';
    
    for (const file of files) {
        const extension = file.name.split('.').pop().toLowerCase();
        if (!['pdf', 'csv', 'xlsx', 'xls'].includes(extension)) {
            addFileToListUI(file.name, 'error', 'Unsupported extension');
            continue;
        }
        
        const fileItem = addFileToListUI(file.name, 'pending', 'Uploading...');
        state.filesUploading++;
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const res = await fetch(`${state.backendUrl}/upload/`, {
                method: 'POST',
                mode: 'cors',
                body: formData
            });
            const result = await res.json();
            
            if (res.ok && result.status === 'success') {
                updateFileItemStatus(fileItem, 'success', `Saved ${result.transactions_saved} rows`);
            } else {
                updateFileItemStatus(fileItem, 'error', result.error || 'Failed');
            }
        } catch (e) {
            updateFileItemStatus(fileItem, 'error', 'Connection error');
        } finally {
            state.filesUploading--;
            if (state.filesUploading === 0) {
                // Refresh dashboard when all uploads finish
                loadDashboardData();
            }
        }
    }
}

function addFileToListUI(fileName, status, statusText) {
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.innerHTML = `
        <div class="file-info">
            <i class="fa-solid fa-file-invoice"></i>
            <span class="file-name">${fileName}</span>
        </div>
        <span class="file-status ${status}">${statusText}</span>
    `;
    elements.fileList.appendChild(fileItem);
    return fileItem;
}

function updateFileItemStatus(fileItem, status, statusText) {
    const badge = fileItem.querySelector('.file-status');
    badge.className = `file-status ${status}`;
    badge.textContent = statusText;
}

// Reset Database API Call
async function clearDatabase() {
    if (!state.isConnected) return;
    
    try {
        const res = await fetch(`${state.backendUrl}/transactions`, {
            method: 'DELETE',
            mode: 'cors'
        });
        const result = await res.json();
        
        if (res.ok && result.status === 'success') {
            elements.fileList.innerHTML = '';
            elements.insightsContent.innerHTML = '<p class="placeholder-text">Click "Generate Insights" to run AI diagnostics on your financial data.</p>';
            loadDashboardData();
        } else {
            alert("Failed to reset database: " + (result.message || "Unknown error"));
        }
    } catch (e) {
        alert("Connection error occurred while clearing database.");
    }
}

// Generate AI Insights
async function generateInsights() {
    if (!state.isConnected) return;
    
    elements.insightsContent.innerHTML = `
        <div class="placeholder-text">
            <i class="fa-solid fa-circle-notch fa-spin"></i> Generating financial report insights using Groq AI...
        </div>
    `;
    elements.insightsBtn.disabled = true;
    
    try {
        const res = await fetch(`${state.backendUrl}/insights`, { mode: 'cors' });
        const result = await res.json();
        
        if (res.ok && result.status === 'success') {
            elements.insightsContent.innerHTML = formatMarkdown(result.insights);
        } else {
            elements.insightsContent.innerHTML = `<p class="placeholder-text" style="color: var(--danger-color)">Error: ${result.error || 'Failed to generate insights.'}</p>`;
        }
    } catch (e) {
        elements.insightsContent.innerHTML = '<p class="placeholder-text" style="color: var(--danger-color)">Connection error. Could not contact AI server.</p>';
    } finally {
        elements.insightsBtn.disabled = false;
    }
}

// Simple Markdown parser to compile report markdown to HTML
function formatMarkdown(text) {
    if (!text) return '';
    let html = text;
    
    // Escape HTML tags to prevent XSS
    html = html.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    
    // Bold tags
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Bullet points
    html = html.replace(/^\s*-\s+(.*)/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // Numeric Lists
    html = html.replace(/^\s*\d+\.\s+(.*)/gm, '<li>$1</li>');
    
    // Line breaks
    html = html.replace(/\n/g, '<br>');
    
    return html;
}

// Download TXT report file
async function downloadReport() {
    if (!state.isConnected) return;
    
    const income = elements.incomeValue.textContent;
    const expenses = elements.expenseValue.textContent;
    const net = elements.netValue.textContent;
    
    const tableRows = Array.from(elements.tableBody.querySelectorAll('tr'));
    let transactionsText = '';
    
    tableRows.forEach(row => {
        const cells = Array.from(row.querySelectorAll('td'));
        if (cells.length > 0) {
            transactionsText += `${cells[0].textContent} | ${cells[1].textContent} | ${cells[2].textContent} | ${cells[3].textContent} | ${cells[4].textContent}\n`;
        }
    });
    
    const reportText = `FINANCIAL ANALYSIS REPORT
==================================
Income:       ${income}
Expenses:     ${expenses}
Net Cashflow: ${net}

TRANSACTIONS
==================================
Date       | Description | Amount | Category | Source
--------------------------------------------------
${transactionsText}
`;

    const blob = new Blob([reportText], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `financial_report_${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// AI Chatbot Submit
async function handleChatSubmit() {
    const question = elements.chatInput.value.trim();
    if (!question || !state.isConnected) return;
    
    // Clear Input
    elements.chatInput.value = '';
    elements.chatSendBtn.disabled = true;
    
    // Add user message
    addChatMessage(question, 'user');
    scrollToBottom();
    
    // Add loader typing bubble
    const loaderId = addChatLoaderUI();
    scrollToBottom();
    
    try {
        const res = await fetch(`${state.backendUrl}/agent/chat`, {
            method: 'POST',
            mode: 'cors',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });
        const result = await res.json();
        
        removeChatLoaderUI(loaderId);
        
        if (res.ok && result.answer) {
            addChatMessage(result.answer, 'assistant');
        } else {
            addChatMessage("I'm sorry, I encountered an error answering your question.", 'assistant');
        }
    } catch (e) {
        removeChatLoaderUI(loaderId);
        addChatMessage("Connection error. Please check your FastAPI settings.", 'assistant');
    } finally {
        scrollToBottom();
    }
}

function addChatMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.innerHTML = `<div class="message-bubble">${text.replace(/\n/g, '<br>')}</div>`;
    elements.chatMessages.appendChild(messageDiv);
}

function addChatLoaderUI() {
    const loaderId = 'loader_' + Date.now();
    const loaderDiv = document.createElement('div');
    loaderDiv.className = 'message assistant';
    loaderDiv.id = loaderId;
    loaderDiv.innerHTML = `
        <div class="message-bubble" style="opacity: 0.7;">
            <i class="fa-solid fa-ellipsis fa-fade"></i> Typing...
        </div>
    `;
    elements.chatMessages.appendChild(loaderDiv);
    return loaderId;
}

function removeChatLoaderUI(loaderId) {
    const loader = document.getElementById(loaderId);
    if (loader) loader.remove();
}

function scrollToBottom() {
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}