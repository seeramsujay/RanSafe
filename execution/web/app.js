// RanSafe Frontend SRE Dashboard Controller

// System Clock
function updateClock() {
    const now = new Date();
    const pad = (n) => n.toString().padStart(2, '0');
    document.getElementById('clock').textContent = 
        `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
}
setInterval(updateClock, 1000);
updateClock();

// Connect to SSE event stream
const eventSource = new EventSource('/events');

eventSource.onmessage = function(event) {
    try {
        const state = JSON.parse(event.data);
        updateDashboard(state);
    } catch (err) {
        console.error('Failed to parse state event:', err);
    }
};

eventSource.onerror = function() {
    const consoleBox = document.getElementById('console-output');
    consoleBox.innerHTML += `<div class="log-line log-error">[SYSTEM] Loss of SSE connection. Retrying...</div>`;
    consoleBox.scrollTop = consoleBox.scrollHeight;
};

// UI State memory to prevent redundant renders
let lastStateStatus = null;
let lastLogCount = 0;

function updateDashboard(state) {
    // 1. Update status header indicators
    const pulseIndicator = document.getElementById('status-pulse');
    const badge = document.getElementById('system-status-badge');
    const desc = document.getElementById('system-status-desc');
    
    pulseIndicator.className = 'pulse-indicator';
    badge.className = 'status-badge';
    
    if (state.status === 'NOMINAL') {
        pulseIndicator.classList.add('status-nominal');
        badge.classList.add('status-nominal');
        badge.textContent = 'NOMINAL';
        desc.textContent = 'Continuous metric evaluation active. VPC environment clean.';
    } else if (state.status === 'PENDING_CONFIRMATION') {
        pulseIndicator.classList.add('status-warn');
        badge.classList.add('status-warn');
        badge.textContent = 'CONFIRMATION REQUIRED';
        desc.textContent = 'High anomaly entropy/CPU spike matched ransomware rules. Awaiting operator input.';
    } else if (state.status === 'AIRGAP_ACTIVE' || state.status === 'AIRGAP_NODE') {
        pulseIndicator.classList.add('status-danger');
        badge.classList.add('status-danger');
        badge.textContent = 'AIRGAP ACTIVE';
        desc.textContent = 'Critical threat isolated. VPC Firewall DENY rule deployed. GKE workloads locked.';
    } else if (state.status === 'MONITOR_INTENSE') {
        pulseIndicator.classList.add('status-warn');
        badge.classList.add('status-warn');
        badge.textContent = 'MONITOR INTENSE';
        desc.textContent = 'Elevated metrics detected. Observability polling frequency scaled to 1s.';
    } else if (state.status === 'REALLOCATE_RESOURCES') {
        pulseIndicator.classList.add('status-nominal');
        badge.classList.add('status-nominal');
        badge.textContent = 'SCALING ACTIVE';
        desc.textContent = 'High CPU compute load balanced. Kubernetes pods scaled successfully.';
    }

    // 2. Update metadata fields
    document.getElementById('node-id').textContent = state.target_node_id || 'N/A';
    document.getElementById('auth-token').textContent = state.authorization_token || 'N/A';

    // 3. Update Telemetry Gauges
    const metrics = state.metrics || { cpu_utilization_percentage: 0, filesystem_write_ops_per_sec: 0, entropy_coefficient: 0 };
    
    updateGauge('cpu', metrics.cpu_utilization_percentage, 100, '%');
    updateGauge('writes', metrics.filesystem_write_ops_per_sec, 1000, '');
    updateGauge('entropy', metrics.entropy_coefficient, 1.0, '', true);

    // 4. Handle Overlay Alerts & Panels based on status
    const alertBox = document.getElementById('threat-alert-box');
    const restorePanel = document.getElementById('restore-panel-box');
    
    if (state.status === 'PENDING_CONFIRMATION') {
        alertBox.classList.remove('hidden');
        restorePanel.classList.add('hidden');
        document.getElementById('reasoning-summary').textContent = state.reasoning_summary || 'Threat matching rules.';
    } else if (state.status === 'AIRGAP_ACTIVE' || state.status === 'AIRGAP_NODE') {
        alertBox.classList.add('hidden');
        restorePanel.classList.remove('hidden');
    } else {
        alertBox.classList.add('hidden');
        restorePanel.classList.add('hidden');
    }

    // 5. Update Containment steps list from log scan
    updateContainmentSteps(state.logs);

    // 6. Append logs if count changed
    if (state.logs && state.logs.length !== lastLogCount) {
        renderLogs(state.logs);
        lastLogCount = state.logs.length;
    }
    
    lastStateStatus = state.status;
}

function updateGauge(name, value, max, unit, isFloat = false) {
    const percent = Math.min((value / max) * 100, 100);
    const circle = document.getElementById(`${name}-circle`);
    const valText = document.getElementById(`${name}-val`);
    
    circle.style.setProperty('--percent', percent);
    valText.textContent = isFloat ? value.toFixed(3) : Math.round(value);
}

function updateContainmentSteps(logs) {
    const steps = [
        { id: 'step-armor', keywords: ['CLOUD ARMOR', 'security-policies'] },
        { id: 'step-vpc', keywords: ['VPC FIREWALL', 'firewall-rules'] },
        { id: 'step-iam', keywords: ['GCP IAM', 'remove-iam-policy-binding'] },
        { id: 'step-gke-kill', keywords: ['GKE CONTAINER OPS', 'delete pod'] },
        { id: 'step-gke-roll', keywords: ['GKE REPLICATOR', 'rollout restart'] }
    ];

    const logsStr = logs.join('\n');

    steps.forEach(step => {
        const el = document.getElementById(step.id);
        const icon = el.querySelector('.step-icon');
        
        let matched = false;
        let success = false;
        let error = false;

        step.keywords.forEach(kw => {
            if (logsStr.includes(kw)) {
                matched = true;
                if (logsStr.includes('Success') || logsStr.includes('✅') || logsStr.includes('successfully') || logsStr.includes('started')) {
                    success = true;
                } else if (logsStr.includes('ERROR') || logsStr.includes('❌')) {
                    error = true;
                }
            }
        });

        // Reset
        el.className = 'step-item';
        icon.className = 'step-icon';

        if (success) {
            el.classList.add('success');
            icon.className = 'fa-solid fa-circle-check step-icon';
        } else if (error) {
            el.classList.add('error');
            icon.className = 'fa-solid fa-circle-xmark step-icon';
        } else if (matched) {
            el.classList.add('active');
            icon.className = 'fa-solid fa-circle-notch fa-spin step-icon';
        } else {
            icon.className = 'fa-regular fa-circle step-icon';
        }
    });
}

function renderLogs(logs) {
    const consoleBox = document.getElementById('console-output');
    consoleBox.innerHTML = '';
    
    logs.forEach(log => {
        let typeClass = 'log-text';
        if (log.includes('[INFO]')) typeClass = 'log-info';
        else if (log.includes('[WARN]')) typeClass = 'log-warn';
        else if (log.includes('[ERROR]')) typeClass = 'log-error';
        else if (log.includes('[SUCCESS]')) typeClass = 'log-success';
        
        consoleBox.innerHTML += `<div class="log-line ${typeClass}">${escapeHtml(log)}</div>`;
    });
    
    consoleBox.scrollTop = consoleBox.scrollHeight;
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// User Action Triggering APIs
function confirmAirgap() {
    fetch('/api/confirm', { method: 'POST' })
        .then(res => res.json())
        .then(data => console.log('Confirm action response:', data))
        .catch(err => console.error('Confirm request failed:', err));
}

function cancelAirgap() {
    fetch('/api/cancel', { method: 'POST' })
        .then(res => res.json())
        .then(data => console.log('Cancel action response:', data))
        .catch(err => console.error('Cancel request failed:', err));
}

function triggerRestore() {
    fetch('/api/restore', { method: 'POST' })
        .then(res => res.json())
        .then(data => console.log('Restore action response:', data))
        .catch(err => console.error('Restore request failed:', err));
}
