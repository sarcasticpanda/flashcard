/**
 * SMARTCRAM Frontend JavaScript
 * Implements the complete flowchart pattern:
 * User Input -> Frontend -> Backend -> OpenAI -> Database -> Response -> Content Rendering
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
const STORAGE_KEYS = {
    TOKEN: 'smartcram_token',
    USER: 'smartcram_user'
};

// Global state
let currentUser = null;
let authToken = null;

// DOM Elements
const elements = {
    // Sections
    welcomeSection: document.getElementById('welcomeSection'),
    authSection: document.getElementById('authSection'),
    dashboardSection: document.getElementById('dashboardSection'),
    flashcardSection: document.getElementById('flashcardSection'),
    quizSection: document.getElementById('quizSection'),
    
    // Auth elements
    loginBtn: document.getElementById('loginBtn'),
    registerBtn: document.getElementById('registerBtn'),
    logoutBtn: document.getElementById('logoutBtn'),
    loginForm: document.getElementById('loginForm'),
    registerForm: document.getElementById('registerForm'),
    showRegister: document.getElementById('showRegister'),
    showLogin: document.getElementById('showLogin'),
    
    // Forms
    loginFormElement: document.getElementById('loginFormElement'),
    registerFormElement: document.getElementById('registerFormElement'),
    flashcardForm: document.getElementById('flashcardForm'),
    quizForm: document.getElementById('quizForm'),
    
    // Loading and notifications
    loadingOverlay: document.getElementById('loadingOverlay'),
    loadingText: document.getElementById('loadingText'),
    toastContainer: document.getElementById('toastContainer'),
    
    // Content areas
    userName: document.getElementById('userName'),
    myContentList: document.getElementById('myContentList'),
    flashcardResult: document.getElementById('flashcardResult'),
    quizResult: document.getElementById('quizResult')
};

/**
 * Initialize the application
 * Step 1: User Opens Web App
 */
function init() {
    console.log('🚀 SMARTCRAM Initializing...');
    
    // Check for existing authentication
    checkAuth();
    
    // Set up event listeners
    setupEventListeners();
    
    // Show appropriate section
    showWelcomeSection();
    
    console.log('✅ SMARTCRAM Initialized');
}

/**
 * Check if user is already authenticated
 */
function checkAuth() {
    const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
    const user = localStorage.getItem(STORAGE_KEYS.USER);
    
    if (token && user) {
        try {
            authToken = token;
            currentUser = JSON.parse(user);
            updateAuthUI(true);
        } catch (error) {
            console.error('Error parsing stored user data:', error);
            clearAuth();
        }
    }
}

/**
 * Set up all event listeners
 */
function setupEventListeners() {
    // Authentication events
    elements.loginBtn.addEventListener('click', showAuthSection);
    elements.registerBtn.addEventListener('click', showAuthSection);
    elements.logoutBtn.addEventListener('click', logout);
    
    // Auth form switches
    elements.showRegister.addEventListener('click', (e) => {
        e.preventDefault();
        showRegisterForm();
    });
    
    elements.showLogin.addEventListener('click', (e) => {
        e.preventDefault();
        showLoginForm();
    });
    
    // Form submissions
    elements.loginFormElement.addEventListener('submit', handleLogin);
    elements.registerFormElement.addEventListener('submit', handleRegister);
    elements.flashcardForm.addEventListener('submit', handleFlashcardGeneration);
    elements.quizForm.addEventListener('submit', handleQuizGeneration);
}

/**
 * Authentication Functions
 */

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    showLoading('Logging in...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store authentication data
            authToken = data.access_token;
            localStorage.setItem(STORAGE_KEYS.TOKEN, authToken);
            
            // Get user info
            await fetchUserInfo();
            
            showToast('Login successful!', 'success');
            showDashboard();
        } else {
            showToast(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const fullName = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    showLoading('Creating account...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password, full_name: fullName })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Account created successfully! Please login.', 'success');
            showLoginForm();
        } else {
            showToast(data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function fetchUserInfo() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const userData = await response.json();
            currentUser = userData;
            localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(userData));
            elements.userName.textContent = userData.full_name || userData.email;
        }
    } catch (error) {
        console.error('Error fetching user info:', error);
    }
}

function logout() {
    clearAuth();
    showToast('Logged out successfully', 'success');
    showWelcomeSection();
}

function clearAuth() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem(STORAGE_KEYS.TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER);
    updateAuthUI(false);
}

function updateAuthUI(isAuthenticated) {
    if (isAuthenticated) {
        elements.loginBtn.style.display = 'none';
        elements.registerBtn.style.display = 'none';
        elements.logoutBtn.style.display = 'inline-flex';
    } else {
        elements.loginBtn.style.display = 'inline-flex';
        elements.registerBtn.style.display = 'inline-flex';
        elements.logoutBtn.style.display = 'none';
    }
}

/**
 * Flashcard Generation Functions
 * Step 3-15: Following the flowchart pattern
 */

async function handleFlashcardGeneration(e) {
    e.preventDefault();
    
    // Step 3: User Inputs Topic & Chooses 'Flashcards'
    const topic = document.getElementById('flashcardTopic').value;
    const sourceText = document.getElementById('flashcardText').value;
    const numCards = parseInt(document.getElementById('flashcardCount').value);
    const description = document.getElementById('flashcardDescription').value;
    
    // Step 4: User Clicks 'Generate'
    // Step 5: JS Captures Input & Sends Request to Backend API
    showLoading('Generating flashcards with AI...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/flashcards/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                topic,
                source_text: sourceText,
                num_cards: numCards,
                description
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Step 13: Frontend: JS Receives JSON & Dynamically Renders Content
            // Step 14: User Views Flashcards
            displayFlashcards(data);
            showToast('Flashcards generated successfully!', 'success');
        } else {
            showToast(data.detail || 'Failed to generate flashcards', 'error');
        }
    } catch (error) {
        console.error('Flashcard generation error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function displayFlashcards(flashcardSet) {
    const resultDiv = elements.flashcardResult;
    
    resultDiv.innerHTML = `
        <div class="flashcard-header">
            <h3>${flashcardSet.topic}</h3>
            <p>${flashcardSet.description || ''}</p>
            <div class="flashcard-actions">
                <button class="btn btn-secondary" onclick="exportFlashcards(${flashcardSet.id})">Export</button>
                <button class="btn btn-primary" onclick="showDashboard()">Create More</button>
            </div>
        </div>
        <div class="flashcard-container">
            ${flashcardSet.flashcards.map((card, index) => `
                <div class="flashcard" onclick="flipFlashcard(this)">
                    <div class="flashcard-number">${index + 1}</div>
                    <div class="flashcard-front">
                        <h4>Question:</h4>
                        <p>${card.question}</p>
                        <small>Click to see answer</small>
                    </div>
                    <div class="flashcard-back">
                        <h4>Answer:</h4>
                        <p>${card.answer}</p>
                        <small>Click to see question</small>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    resultDiv.style.display = 'block';
}

function flipFlashcard(card) {
    card.classList.toggle('flipped');
}

/**
 * Quiz Generation Functions
 * Step 3-15: Following the flowchart pattern
 */

async function handleQuizGeneration(e) {
    e.preventDefault();
    
    // Step 3: User Inputs Topic & Chooses 'Quiz'
    const topic = document.getElementById('quizTopic').value;
    const sourceText = document.getElementById('quizText').value;
    const numQuestions = parseInt(document.getElementById('quizCount').value);
    
    // Step 4: User Clicks 'Generate'
    // Step 5: JS Captures Input & Sends Request to Backend API
    showLoading('Generating quiz with AI...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/quiz/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                topic,
                source_text: sourceText,
                num_questions: numQuestions
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Step 13: Frontend: JS Receives JSON & Dynamically Renders Content
            // Step 14: User Views Quiz
            displayQuiz(data);
            showToast('Quiz generated successfully!', 'success');
        } else {
            showToast(data.detail || 'Failed to generate quiz', 'error');
        }
    } catch (error) {
        console.error('Quiz generation error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function displayQuiz(quiz) {
    const resultDiv = elements.quizResult;
    
    resultDiv.innerHTML = `
        <div class="quiz-header">
            <h3>${quiz.title}</h3>
            <p>Topic: ${quiz.topic}</p>
            <div class="quiz-actions">
                <button class="btn btn-secondary" onclick="exportQuiz(${quiz.id})">Export</button>
                <button class="btn btn-primary" onclick="submitQuiz(${quiz.id})">Submit Quiz</button>
                <button class="btn btn-primary" onclick="showDashboard()">Create More</button>
            </div>
        </div>
        <form id="quizSubmissionForm" class="quiz-container">
            ${quiz.questions.map((question, index) => `
                <div class="quiz-question">
                    <h4>Question ${index + 1}:</h4>
                    <p>${question.question}</p>
                    <div class="quiz-options">
                        ${question.option_a ? `<label class="quiz-option">
                            <input type="radio" name="q${index}" value="0" required>
                            <span>A) ${question.option_a}</span>
                        </label>` : ''}
                        ${question.option_b ? `<label class="quiz-option">
                            <input type="radio" name="q${index}" value="1" required>
                            <span>B) ${question.option_b}</span>
                        </label>` : ''}
                        ${question.option_c ? `<label class="quiz-option">
                            <input type="radio" name="q${index}" value="2" required>
                            <span>C) ${question.option_c}</span>
                        </label>` : ''}
                        ${question.option_d ? `<label class="quiz-option">
                            <input type="radio" name="q${index}" value="3" required>
                            <span>D) ${question.option_d}</span>
                        </label>` : ''}
                    </div>
                </div>
            `).join('')}
        </form>
    `;
    
    resultDiv.style.display = 'block';
}

async function submitQuiz(quizId) {
    const form = document.getElementById('quizSubmissionForm');
    const formData = new FormData(form);
    
    const answers = [];
    for (let i = 0; i < 20; i++) { // Max 20 questions
        const answer = formData.get(`q${i}`);
        if (answer !== null) {
            answers.push(parseInt(answer));
        }
    }
    
    if (answers.length === 0) {
        showToast('Please answer at least one question', 'warning');
        return;
    }
    
    showLoading('Submitting quiz...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/quiz/${quizId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ answers })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showQuizResults(data);
            showToast('Quiz submitted successfully!', 'success');
        } else {
            showToast(data.detail || 'Failed to submit quiz', 'error');
        }
    } catch (error) {
        console.error('Quiz submission error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function showQuizResults(results) {
    const resultDiv = elements.quizResult;
    
    resultDiv.innerHTML = `
        <div class="quiz-results">
            <h3>Quiz Results</h3>
            <div class="results-summary">
                <p><strong>Score:</strong> ${results.correct_answers}/${results.total_questions} (${results.score_percentage.toFixed(1)}%)</p>
                <p><strong>Correct Answers:</strong> ${results.correct_answers}</p>
                <p><strong>Total Questions:</strong> ${results.total_questions}</p>
            </div>
            <div class="results-actions">
                <button class="btn btn-primary" onclick="showDashboard()">Back to Dashboard</button>
            </div>
        </div>
    `;
}

/**
 * Content Management Functions
 */

async function loadMyContent(type = 'flashcards') {
    try {
        const endpoint = type === 'flashcards' ? 'flashcards' : 'quiz';
        const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayMyContent(data, type);
        }
    } catch (error) {
        console.error(`Error loading ${type}:`, error);
        showToast(`Failed to load ${type}`, 'error');
    }
}

function displayMyContent(content, type) {
    const listDiv = elements.myContentList;
    
    if (content.length === 0) {
        listDiv.innerHTML = `<p class="text-center">No ${type} found. Create your first ${type.slice(0, -1)}!</p>`;
        return;
    }
    
    listDiv.innerHTML = content.map(item => `
        <div class="content-item">
            <div class="content-info">
                <h4>${type === 'flashcards' ? item.topic : item.title}</h4>
                <p>${type === 'flashcards' ? `${item.num_cards} cards` : `${item.num_questions} questions`} • Created ${new Date(item.created_at).toLocaleDateString()}</p>
            </div>
            <div class="content-actions">
                <button class="btn btn-secondary" onclick="view${type.charAt(0).toUpperCase() + type.slice(1)}(${item.id})">View</button>
                <button class="btn btn-secondary" onclick="export${type.charAt(0).toUpperCase() + type.slice(1)}(${item.id})">Export</button>
                <button class="btn btn-secondary" onclick="delete${type.charAt(0).toUpperCase() + type.slice(1)}(${item.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

/**
 * Export Functions
 */

async function exportFlashcards(setId) {
    try {
        const response = await fetch(`${API_BASE_URL}/flashcards/${setId}/export`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            downloadJSON(data, `flashcards-${setId}.json`);
            showToast('Flashcards exported successfully!', 'success');
        }
    } catch (error) {
        console.error('Export error:', error);
        showToast('Failed to export flashcards', 'error');
    }
}

async function exportQuiz(quizId) {
    try {
        const response = await fetch(`${API_BASE_URL}/quiz/${quizId}/export`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            downloadJSON(data, `quiz-${quizId}.json`);
            showToast('Quiz exported successfully!', 'success');
        }
    } catch (error) {
        console.error('Export error:', error);
        showToast('Failed to export quiz', 'error');
    }
}

function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Navigation Functions
 */

function showWelcomeSection() {
    hideAllSections();
    elements.welcomeSection.style.display = 'block';
}

function showAuthSection() {
    hideAllSections();
    elements.authSection.style.display = 'block';
    showLoginForm();
}

function showLoginForm() {
    elements.loginForm.style.display = 'block';
    elements.registerForm.style.display = 'none';
}

function showRegisterForm() {
    elements.loginForm.style.display = 'none';
    elements.registerForm.style.display = 'block';
}

function showDashboard() {
    if (!authToken) {
        showToast('Please login first', 'warning');
        return;
    }
    
    hideAllSections();
    elements.dashboardSection.style.display = 'block';
    loadMyContent('flashcards');
}

function showFlashcardForm() {
    hideAllSections();
    elements.flashcardSection.style.display = 'block';
}

function showQuizForm() {
    hideAllSections();
    elements.quizSection.style.display = 'block';
}

function showMyFlashcards() {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    loadMyContent('flashcards');
}

function showMyQuizzes() {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    loadMyContent('quiz');
}

function hideAllSections() {
    const sections = [
        elements.welcomeSection,
        elements.authSection,
        elements.dashboardSection,
        elements.flashcardSection,
        elements.quizSection
    ];
    
    sections.forEach(section => {
        if (section) section.style.display = 'none';
    });
}

/**
 * Utility Functions
 */

function showLoading(message = 'Loading...') {
    elements.loadingText.textContent = message;
    elements.loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    elements.toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}
 
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Get the span element by its ID
    const yearSpan = document.getElementById('current-year');

    // Get the current year
    const currentYear = new Date().getFullYear();

    // Set the text content of the span to the current year
    yearSpan.textContent = currentYear;
   });
</script>

// Export functions for global access
window.showFlashcardForm = showFlashcardForm;
window.showQuizForm = showQuizForm;
window.showDashboard = showDashboard;
window.showMyFlashcards = showMyFlashcards;
window.showMyQuizzes = showMyQuizzes;
window.flipFlashcard = flipFlashcard;
window.exportFlashcards = exportFlashcards;
window.exportQuiz = exportQuiz;
