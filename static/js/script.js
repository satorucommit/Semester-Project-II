// Enhanced Plagiarism Detector JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
    
    // Form submission handlers
    setupFormHandlers();
    
    // File upload handlers
    setupFileUpload();
    
    // Chart initialization
    initializeCharts();
});

function initializeApp() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading states to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.type === 'submit') {
                this.classList.add('loading');
            }
        });
    });
}

function setupFormHandlers() {
    // Text form submission
    const textForm = document.getElementById('text-form');
    if (textForm) {
        textForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            submitTextAnalysis(formData);
        });
    }

    // File form submission
    const fileForm = document.getElementById('file-form');
    if (fileForm) {
        fileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            submitFileAnalysis(formData);
        });
    }
}

function setupFileUpload() {
    const fileUploadArea = document.getElementById('file-upload-area');
    const fileInput = document.getElementById('original_file');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const removeFileBtn = document.getElementById('remove-file');
    const checkFileBtn = document.getElementById('check-file-btn');

    if (fileUploadArea && fileInput) {
        // Click to upload
        fileUploadArea.addEventListener('click', function() {
            fileInput.click();
        });

        // Drag and drop
        fileUploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });

        fileUploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
        });

        fileUploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelection(files[0]);
            }
        });

        // File input change
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleFileSelection(e.target.files[0]);
            }
        });

        // Remove file
        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', function() {
                fileInput.value = '';
                fileUploadArea.classList.remove('d-none');
                fileInfo.classList.add('d-none');
                checkFileBtn.disabled = true;
            });
        }
    }
}

function handleFileSelection(file) {
    const fileUploadArea = document.getElementById('file-upload-area');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const checkFileBtn = document.getElementById('check-file-btn');

    // Validate file type
    const allowedTypes = ['.txt', '.pdf', '.docx'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
        showNotification('Please select a valid file type (TXT, PDF, or DOCX)', 'error');
        return;
    }

    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showNotification('File size must be less than 16MB', 'error');
        return;
    }

    // Show file info
    fileName.textContent = file.name;
    fileUploadArea.classList.add('d-none');
    fileInfo.classList.remove('d-none');
    checkFileBtn.disabled = false;
}

function submitTextAnalysis(formData) {
    const text = formData.get('original_text');
    
    if (!text || text.trim().length < 50) {
        showNotification('Please enter at least 50 words for accurate analysis', 'warning');
        return;
    }

    showLoading('text');
    
    fetch('/check-text', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        hideLoading('text');
        displayResults(data);
        showNotification('Analysis completed successfully!', 'success');
    })
    .catch(error => {
        hideLoading('text');
        console.error('Error:', error);
        showNotification('Error analyzing text: ' + error.message, 'error');
    });
}

function submitFileAnalysis(formData) {
    const file = formData.get('original_file');
    
    if (!file || file.size === 0) {
        showNotification('Please select a file to analyze', 'warning');
        return;
    }

    showLoading('file');
    
    fetch('/check-files', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        hideLoading('file');
        displayResults(data);
        showNotification('File analysis completed successfully!', 'success');
    })
    .catch(error => {
        hideLoading('file');
        console.error('Error:', error);
        showNotification('Error analyzing file: ' + error.message, 'error');
    });
}

function showLoading(type) {
    const spinner = document.getElementById(`${type}-spinner`);
    const button = document.getElementById(`check-${type}-btn`);
    
    if (spinner) spinner.classList.remove('d-none');
    if (button) {
        button.disabled = true;
        button.classList.add('loading');
    }
}

function hideLoading(type) {
    const spinner = document.getElementById(`${type}-spinner`);
    const button = document.getElementById(`check-${type}-btn`);
    
    if (spinner) spinner.classList.add('d-none');
    if (button) {
        button.disabled = false;
        button.classList.remove('loading');
    }
}

function displayResults(data) {
    // Show results section
    const resultsSection = document.getElementById('results-section');
    if (resultsSection) {
        resultsSection.classList.remove('d-none');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Update overall score
    updateOverallScore(data);
    
    // Update metrics
    updateMetrics(data);
    
    // Update detailed results
    updateDetailedResults(data);
    
    // Set up download report
    setupDownloadReport(data);
}

function updateOverallScore(data) {
    const overallScore = document.getElementById('overall-score');
    const plagiarismLevelBadge = document.getElementById('plagiarism-level-badge');
    const scoreDescription = document.getElementById('score-description');
    
    if (overallScore) {
        overallScore.textContent = data.similarity_scores.average_similarity;
    }
    
    if (plagiarismLevelBadge) {
        plagiarismLevelBadge.textContent = data.plagiarism_level;
        plagiarismLevelBadge.className = 'score-badge ' + data.plagiarism_level.toLowerCase().replace(' ', '-');
    }
    
    if (scoreDescription) {
        scoreDescription.textContent = getScoreDescription(data.plagiarism_level, data.similarity_scores.average_similarity);
    }
    
    // Update gauge chart
    createPlagiarismGauge(parseFloat(data.similarity_scores.average_similarity.replace('%', '')));
}

function updateMetrics(data) {
    // Update metric bars
    const patternValue = parseFloat(data.similarity_scores.cosine_similarity.replace('%', ''));
    const uniquenessValue = parseFloat(data.similarity_scores.jaccard_similarity.replace('%', ''));
    const complexityValue = 100 - uniquenessValue; // Inverted for complexity
    
    // Pattern Analysis
    const patternFill = document.getElementById('pattern-fill');
    const patternValueEl = document.getElementById('pattern-value');
    if (patternFill) {
        patternFill.style.width = patternValue + '%';
        patternFill.style.backgroundColor = getColorForScore(patternValue);
    }
    if (patternValueEl) {
        patternValueEl.textContent = patternValue + '%';
    }
    
    // Uniqueness
    const uniquenessFill = document.getElementById('uniqueness-fill');
    const uniquenessValueEl = document.getElementById('uniqueness-value');
    if (uniquenessFill) {
        uniquenessFill.style.width = uniquenessValue + '%';
        uniquenessFill.style.backgroundColor = getColorForScore(uniquenessValue);
    }
    if (uniquenessValueEl) {
        uniquenessValueEl.textContent = uniquenessValue + '%';
    }
    
    // Complexity
    const complexityFill = document.getElementById('complexity-fill');
    const complexityValueEl = document.getElementById('complexity-value');
    if (complexityFill) {
        complexityFill.style.width = complexityValue + '%';
        complexityFill.style.backgroundColor = getColorForScore(complexityValue);
    }
    if (complexityValueEl) {
        complexityValueEl.textContent = complexityValue + '%';
    }
    
    // Create metrics chart
    createMetricsChart(data.similarity_scores);
}

function updateDetailedResults(data) {
    const matchesContainer = document.getElementById('matches-container');
    
    if (!matchesContainer) return;
    
    if (!data.highlighted_content || data.highlighted_content.length === 0) {
        matchesContainer.innerHTML = `
            <div class="no-matches">
                <i class="bi bi-check-circle text-success"></i>
                <p>No significant plagiarism detected in your content.</p>
            </div>
        `;
        return;
    }
    
    // Create match items
    let matchesHTML = '';
    data.highlighted_content.forEach((match, index) => {
        const similarityPercentage = (match.similarity_ratio * 100).toFixed(1);
        matchesHTML += `
            <div class="match-item">
                <div class="match-header">
                    <div class="match-title">Potential Match #${index + 1}</div>
                    <div class="match-percentage">${similarityPercentage}% Similar</div>
                </div>
                <div class="match-content">
                    <div class="match-label">Suspicious Text</div>
                    <div class="match-text">${match.suspicious_sentence}</div>
                </div>
                <div class="match-content">
                    <div class="match-label">Potential Source</div>
                    <div class="match-text">${match.original_sentence}</div>
                </div>
            </div>
        `;
    });
    
    matchesContainer.innerHTML = matchesHTML;
}

function setupDownloadReport(data) {
    const downloadBtn = document.getElementById('download-report-btn');
    if (downloadBtn && data.report_path) {
        downloadBtn.onclick = function(e) {
            e.preventDefault();
            window.open('/download-report/' + encodeURIComponent(data.report_path), '_blank');
        };
    }
}

function createPlagiarismGauge(score) {
    const canvas = document.getElementById('plagiarism-gauge');
    if (!canvas) return;
    
    // Destroy existing chart
    if (canvas._chart) {
        canvas._chart.destroy();
    }
    
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 20;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 20;
    ctx.stroke();
    
    // Draw progress arc
    const progressAngle = (score / 100) * 2 * Math.PI;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -Math.PI / 2, -Math.PI / 2 + progressAngle);
    ctx.strokeStyle = getColorForScore(score);
    ctx.lineWidth = 20;
    ctx.lineCap = 'round';
    ctx.stroke();
    
    // Draw center circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius - 30, 0, 2 * Math.PI);
    ctx.fillStyle = 'white';
    ctx.fill();
    
    // Save chart instance
    canvas._chart = { destroy: () => {} };
}

function createMetricsChart(similarityScores) {
    const canvas = document.getElementById('metrics-chart');
    if (!canvas) return;
    
    // Destroy existing chart
    if (canvas._chart) {
        canvas._chart.destroy();
    }
    
    const patternValue = parseFloat(similarityScores.cosine_similarity.replace('%', ''));
    const uniquenessValue = parseFloat(similarityScores.jaccard_similarity.replace('%', ''));
    const complexityValue = 100 - uniquenessValue;
    
    const chart = new Chart(canvas, {
        type: 'radar',
        data: {
            labels: ['Pattern Analysis', 'Content Uniqueness', 'Text Complexity'],
            datasets: [{
                label: 'Analysis Score',
                data: [patternValue, uniquenessValue, complexityValue],
                backgroundColor: 'rgba(37, 99, 235, 0.2)',
                borderColor: 'rgba(37, 99, 235, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(37, 99, 235, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            elements: {
                line: {
                    tension: 0.1
                }
            }
        }
    });
    
    // Save chart instance
    canvas._chart = chart;
}

function getColorForScore(score) {
    if (score < 20) {
        return '#10b981'; // Green
    } else if (score < 40) {
        return '#f59e0b'; // Yellow
    } else if (score < 60) {
        return '#ef4444'; // Red
    } else {
        return '#1e293b'; // Dark
    }
}

function getScoreDescription(level, score) {
    const scoreNum = parseFloat(score.replace('%', ''));
    
    switch (level) {
        case 'Low':
            return 'Your content appears to be highly original with minimal plagiarism detected. Great work!';
        case 'Moderate':
            return 'Some similarities were found, but your content shows good originality overall.';
        case 'High':
            return 'Significant similarities detected. Consider reviewing and revising your content.';
        case 'Very High':
            return 'High plagiarism risk detected. Immediate revision recommended.';
        default:
            return 'Analysis completed. Please review the detailed results below.';
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        <i class="bi bi-${getNotificationIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success':
            return 'check-circle';
        case 'error':
        case 'danger':
            return 'exclamation-triangle';
        case 'warning':
            return 'exclamation-circle';
        default:
            return 'info-circle';
    }
}

function initializeCharts() {
    // Initialize any default charts if needed
    const canvas = document.getElementById('plagiarism-gauge');
    if (canvas) {
        // Set canvas size
        canvas.width = 200;
        canvas.height = 200;
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export functions for global access
window.PlagiarismDetector = {
    showNotification,
    getColorForScore,
    debounce,
    throttle
};