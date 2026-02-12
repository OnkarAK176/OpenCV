// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Global state
const appState = {
    currentFile: null,
    currentFileId: null,
    violations: [],
    isProcessing: false,
    stats: {
        totalViolations: 0,
        videosProcessed: 0,
        avgViolations: 0
    }
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    checkBackendHealth();
});

// Event Listeners
function initializeEventListeners() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const processBtn = document.getElementById('processBtn');
    const confidenceSlider = document.getElementById('confidenceSlider');
    const navLinks = document.querySelectorAll('.nav-link');

    // Upload area drag and drop
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // File input change
    fileInput.addEventListener('change', (e) => handleFileSelect(e.target.files[0]));

    // Process button
    processBtn.addEventListener('click', processFile);

    // Confidence slider
    confidenceSlider.addEventListener('input', (e) => {
        document.getElementById('confidenceValue').textContent = parseFloat(e.target.value).toFixed(2);
    });

    // Navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            const target = link.getAttribute('href');
            if (target && target !== '#') {
                document.querySelector(target)?.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').style.background = 
        'linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%)';
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').style.background = 
        'linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%)';
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').style.background = 
        'linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%)';
    
    if (e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
}

function handleFileSelect(file) {
    if (!file) return;

    const validTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'image/jpeg', 'image/png'];
    const maxSize = 500 * 1024 * 1024;

    if (!validTypes.some(type => file.type.includes(type.split('/')[1]))) {
        showToast('Invalid file type. Please upload a video or image.', 'error');
        return;
    }

    if (file.size > maxSize) {
        showToast('File size exceeds 500MB limit.', 'error');
        return;
    }

    appState.currentFile = file;
    updateUploadArea();
    document.getElementById('processBtn').disabled = false;
    showToast(`File selected: ${file.name}`, 'success');
}

function updateUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const file = appState.currentFile;

    if (file) {
        const sizeMB = (file.size / 1024 / 1024).toFixed(2);
        uploadArea.innerHTML = `
            <svg class="upload-icon" viewBox="0 0 24 24" fill="currentColor" style="color: #10b981;">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
            <h3 style="color: #10b981;">✓ File Ready</h3>
            <p><strong>${file.name}</strong></p>
            <p style="font-size: 0.85rem; color: #6b7280; margin-top: 0.5rem;">
                Size: ${sizeMB} MB | Type: ${file.type.split('/')[1].toUpperCase()}
            </p>
        `;
    }
}

async function processFile() {
    if (!appState.currentFile) {
        showToast('Please select a file first.', 'error');
        return;
    }

    appState.isProcessing = true;
    document.getElementById('processBtn').disabled = true;
    showLoadingModal(true, '🚀 Real-Time Processing', 'Starting fast detection...');
    updateStatus('Processing...', 'processing');

    try {
        // Step 1: Upload file
        showLoadingModal(true, '📤 Uploading file...', 'Preparing for real-time detection');
        const fileId = await uploadFile(appState.currentFile);
        
        if (!fileId) {
            throw new Error('Upload failed');
        }

        appState.currentFileId = fileId;
        showToast('File uploaded - Starting real-time analysis', 'success');

        // Step 2: Start real-time processing (MUCH FASTER!)
        showLoadingModal(true, '⚡ Real-Time Detection', 'Processing with frame skipping...');
        
        const result = await fetch(`${API_BASE_URL}/process/realtime`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_id: fileId,
                frame_skip: 2  // Process every 2nd frame for speed
            })
        }).then(r => r.json());

        if (!result.success) {
            throw new Error(result.error || 'Processing failed');
        }

        // Update state
        appState.violations = result.violations || [];
        updateStats(result);
        displayResults(result);
        displayViolations(result.violations);

        updateStatus('✓ Complete', 'success');
        showToast(`✓ Real-time detection complete! Found ${result.violations_detected} violations.`, 'success');

    } catch (error) {
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'error');
        updateStatus('✗ Error', 'error');
    } finally {
        appState.isProcessing = false;
        document.getElementById('processBtn').disabled = false;
        showLoadingModal(false);
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }

        return data.file_id;
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
}

function displayResults(result) {
    const resultsContent = document.getElementById('resultsContent');
    
    const stats = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
            <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 0.5rem; text-align: center;">
                <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">Total Frames</p>
                <p style="font-size: 1.875rem; font-weight: bold; color: #2563eb;">${result.total_frames || 0}</p>
            </div>
            <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 0.5rem; text-align: center;">
                <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">Frame Rate</p>
                <p style="font-size: 1.875rem; font-weight: bold; color: #2563eb;">${result.fps ? result.fps.toFixed(2) : 'N/A'} fps</p>
            </div>
            <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 0.5rem; text-align: center;">
                <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">Violations Found</p>
                <p style="font-size: 1.875rem; font-weight: bold; color: #ef4444;">${result.violations_detected || 0}</p>
            </div>
        </div>
    `;

    if (result.violations && result.violations.length > 0) {
        resultsContent.innerHTML = stats + '<h3 style="margin-bottom: 1rem; color: #1f2937;">Top Violations</h3>' + 
                                   displayViolationsList(result.violations.slice(0, 3));
    } else {
        resultsContent.innerHTML = stats + '<p style="text-align: center; color: #6b7280; padding: 2rem;">No violations detected</p>';
    }
}

function displayViolations(violations) {
    const violationsList = document.getElementById('violationsList');

    if (!violations || violations.length === 0) {
        violationsList.innerHTML = '<p class="placeholder">No violations detected</p>';
        return;
    }

    violationsList.innerHTML = displayViolationsList(violations);
}

function displayViolationsList(violations) {
    return violations.map((violation, index) => `
        <div class="violation-item ${violation.is_violation ? '' : 'normal'}">
            <div class="violation-header">
                <div>
                    <h4 style="margin: 0 0 0.5rem; color: #1f2937;">Violation #${index + 1}</h4>
                    <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">
                        Frame ${violation.frame} @ ${(violation.timestamp || 0).toFixed(2)}s
                    </p>
                </div>
                <span class="violation-badge ${violation.is_violation ? '' : 'normal'}">
                    ${violation.is_violation ? violation.violation_type : 'NORMAL'}
                </span>
            </div>
            <div class="violation-details">
                <div class="detail-item">
                    <span class="detail-label">License Plate</span>
                    <span class="detail-value" style="font-family: monospace;">${violation.plate_text || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Plate Confidence</span>
                    <span class="detail-value">${(violation.plate_confidence * 100).toFixed(1)}%</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Speed</span>
                    <span class="detail-value" style="color: ${violation.is_violation ? '#ef4444' : '#10b981'};">
                        ${violation.estimated_speed.toFixed(1)} km/h
                    </span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Excess Speed</span>
                    <span class="detail-value">${violation.excess_speed.toFixed(1)} km/h</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Speed Limit</span>
                    <span class="detail-value">${violation.speed_limit} km/h</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Vehicle Confidence</span>
                    <span class="detail-value">${(violation.vehicle_confidence * 100).toFixed(1)}%</span>
                </div>
            </div>
        </div>
    `).join('');
}

function updateStats(result) {
    appState.stats.videosProcessed++;
    appState.stats.totalViolations += result.violations_detected || 0;
    appState.stats.avgViolations = appState.stats.videosProcessed > 0 
        ? (appState.stats.totalViolations / appState.stats.videosProcessed).toFixed(2)
        : 0;

    document.getElementById('totalViolations').textContent = appState.stats.totalViolations;
    document.getElementById('videosProcessed').textContent = appState.stats.videosProcessed;
    document.getElementById('avgViolations').textContent = appState.stats.avgViolations;
    document.getElementById('detectionAccuracy').textContent = '95.2%'; // Mock data
}

function updateStatus(text, status) {
    const badge = document.getElementById('statusBadge');
    badge.textContent = text;
    badge.className = `status-badge ${status}`;
}

function showLoadingModal(show, title = 'Processing your file...', message = 'Please wait, this may take a few moments') {
    const modal = document.getElementById('loadingModal');
    const loadingText = document.getElementById('loadingText');
    const progressText = document.getElementById('progressText');

    if (show) {
        loadingText.textContent = title;
        progressText.textContent = message;
        modal.classList.add('active');
    } else {
        modal.classList.remove('active');
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✓ Backend is running');
            showToast('System ready', 'success');
        }
    } catch (error) {
        console.warn('Backend not available:', error);
        showToast('Backend connection failed. Please ensure the server is running.', 'error');
    }
}
