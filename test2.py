# app.py
# This Flask application serves a single-page web app for a trading journal.
# It uses JavaScript on the frontend to handle user authentication with Google
# and data persistence with Firestore, providing a secure and dynamic experience.

import os
from flask import Flask, render_template_string

app = Flask(__name__)

# The HTML template is defined as a string to keep the app self-contained.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Journal App</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-left-color: #3b82f6;
            border-radius: 50%;
            width: 3rem;
            height: 3rem;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        /* Custom scrollbar styles */
        .table-container::-webkit-scrollbar { width: 8px; }
        .table-container::-webkit-scrollbar-track { background: #f1f1f1; }
        .table-container::-webkit-scrollbar-thumb { background: #888; border-radius: 4px; }
        .table-container::-webkit-scrollbar-thumb:hover { background: #555; }
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center p-4 md:p-8">
    <div id="loading-screen" class="fixed inset-0 flex items-center justify-center bg-gray-100 z-50 transition-opacity duration-300 opacity-100">
        <div class="text-center">
            <div class="spinner mx-auto mb-4"></div>
            <p class="text-gray-600">Loading...</p>
        </div>
    </div>
    
    <!-- Login/Auth Container -->
    <div id="auth-container" class="hidden max-w-lg w-full bg-white p-8 rounded-2xl shadow-2xl text-center transition-transform duration-500 transform scale-95 opacity-0">
        <h1 class="text-4xl font-extrabold text-gray-900 mb-4">Trading Journal</h1>
        <p class="text-gray-600 mb-8">Sign in to track your trades and analyze your performance.</p>
        <button id="google-login-btn" class="w-full flex items-center justify-center px-6 py-3 border border-gray-300 rounded-xl shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200">
            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 48 48">
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.63-6.63C35.85 2.15 30.15 0 24 0 14.58 0 6.54 5.38 2.51 13.06l7.5 5.86c3.21-2.92 7.42-4.92 11.99-4.92z"/>
                <path fill="#4285F4" d="M46.7 24.5c0-1.57-.14-3.1-.41-4.57H24v8.66h12.59c-.64 3.42-2.73 6.32-5.75 8.16l-7.23 5.66c4.68 3.5 10.5 5.4 16.51 5.4 9.42 0 17.48-6.15 20.29-14.86z"/>
                <path fill="#FBBC05" d="M10.01 29.56c-.63-1.88-.98-3.9-.98-6.06s.35-4.18.98-6.06L2.51 13.06C.93 16.09 0 20.01 0 24s.93 7.91 2.51 10.94l7.5-5.86z"/>
                <path fill="#34A853" d="M24 48c6.68 0 12.8-2.3 17.5-6.17l-7.23-5.66c-3.02 1.84-5.11 4.74-5.75 8.16H24c-5.83 0-11.1-2.9-14.28-7.73l-7.5 5.86C6.52 42.62 14.58 48 24 48z"/>
            </svg>
            Sign in with Google
        </button>
    </div>

    <!-- Main App Container -->
    <div id="main-app-container" class="hidden container mx-auto bg-white rounded-2xl shadow-2xl p-6 md:p-12 transition-transform duration-500 transform scale-95 opacity-0">
        <!-- User Info and Logout -->
        <header class="flex flex-col md:flex-row items-center justify-between mb-8 pb-4 border-b border-gray-200">
            <h1 class="text-3xl md:text-4xl font-extrabold text-gray-800 tracking-tight mb-2 md:mb-0">My Trading Journal</h1>
            <div class="flex items-center space-x-4">
                <span id="user-info" class="text-gray-600 text-sm md:text-base"></span>
                <button id="logout-btn" class="text-sm font-medium text-red-600 hover:text-red-800 transition-colors duration-200">
                    Logout
                </button>
            </div>
        </header>

        <!-- Summary Section -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="bg-gray-50 p-6 rounded-xl shadow-sm">
                <h3 class="font-bold text-gray-600 mb-2">Total Trades</h3>
                <p id="total-trades" class="text-4xl font-extrabold text-blue-600">0</p>
            </div>
            <div class="bg-gray-50 p-6 rounded-xl shadow-sm">
                <h3 class="font-bold text-gray-600 mb-2">Win Rate</h3>
                <p id="win-rate" class="text-4xl font-extrabold text-purple-600">0.00%</p>
            </div>
            <div class="bg-gray-50 p-6 rounded-xl shadow-sm">
                <h3 class="font-bold text-gray-600 mb-2">Total P/L</h3>
                <p id="total-pl" class="text-4xl font-extrabold text-gray-600">0.00</p>
            </div>
            <div class="bg-gray-50 p-6 rounded-xl shadow-sm">
                <h3 class="font-bold text-gray-600 mb-2">Largest Trade</h3>
                <p class="text-lg font-semibold text-green-500">Win: <span id="largest-win">0.00</span></p>
                <p class="text-lg font-semibold text-red-500">Loss: <span id="largest-loss">0.00</span></p>
            </div>
        </div>

        <!-- Trade Entry Form -->
        <div class="bg-white p-8 rounded-xl shadow-lg mb-8">
            <h2 id="form-title" class="text-2xl font-bold text-gray-800 mb-6">Add New Trade</h2>
            <form id="trade-form" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <input type="hidden" id="trade-id-input" name="id">
                <div>
                    <label for="script_name" class="block text-sm font-medium text-gray-700">Script Name</label>
                    <input type="text" id="script_name" name="script_name" required>
                </div>
                <div>
                    <label for="long_short" class="block text-sm font-medium text-gray-700">Long/Short</label>
                    <select id="long_short" name="long_short" required>
                        <option value="">Select...</option>
                        <option value="Long">Long</option>
                        <option value="Short">Short</option>
                    </select>
                </div>
                <div>
                    <label for="entry_price" class="block text-sm font-medium text-gray-700">Entry Price</label>
                    <input type="number" step="0.01" id="entry_price" name="entry_price" required>
                </div>
                <div>
                    <label for="exit_price" class="block text-sm font-medium text-gray-700">Exit Price</label>
                    <input type="number" step="0.01" id="exit_price" name="exit_price" required>
                </div>
                <div>
                    <label for="pl" class="block text-sm font-medium text-gray-700">P/L</label>
                    <input type="number" step="0.01" id="pl" name="pl" required>
                </div>
                <div>
                    <label for="follow_rules" class="block text-sm font-medium text-gray-700">Did I follow MY RULES?</label>
                    <select id="follow_rules" name="follow_rules">
                        <option value="Yes">Yes</option>
                        <option value="No">No</option>
                    </select>
                </div>
                <div class="col-span-1 md:col-span-2 lg:col-span-4 flex justify-end">
                    <button type="submit" id="submit-btn" class="bg-blue-600 text-white font-bold py-3 px-6 rounded-xl shadow-md hover:bg-blue-700 transition duration-200">
                        Add Trade
                    </button>
                    <button type="button" id="cancel-edit-btn" class="hidden ml-4 bg-gray-400 text-white font-bold py-3 px-6 rounded-xl shadow-md hover:bg-gray-500 transition duration-200">
                        Cancel Edit
                    </button>
                </div>
            </form>
        </div>

        <!-- Trading Journal Table -->
        <div class="bg-white p-8 rounded-xl shadow-lg">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">Trade History</h2>
            <div class="table-container max-h-[500px] overflow-y-auto rounded-lg">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50 sticky top-0">
                        <tr>
                            <th class="p-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Script Name</th>
                            <th class="p-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Long/Short</th>
                            <th class="p-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P/L</th>
                            <th class="p-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Followed Rules?</th>
                            <th class="p-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="journal-body" class="bg-white divide-y divide-gray-200">
                        <!-- Trade rows will be added here by JavaScript -->
                    </tbody>
                </table>
            </div>
            <p id="no-trades-message" class="text-center text-gray-500 py-8 hidden">No trades recorded yet. Add your first trade above!</p>
        </div>
    </div>
    
    <!-- Toast Notification / Message Box -->
    <div id="toast-message" class="fixed bottom-4 right-4 bg-gray-800 text-white px-6 py-3 rounded-xl shadow-lg opacity-0 transition-opacity duration-300">
        Message goes here
    </div>

    <!-- Firebase SDKs -->
    <script src="https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js"></script>
    <script src="https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js"></script>

    <script>
        // Use the global variables provided by the canvas environment
        const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
        const firebaseConfig = JSON.parse(typeof __firebase_config !== 'undefined' ? __firebase_config : '{}');
        const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;
        
        // Firebase initialization
        const firebaseApp = firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();
        const db = firebase.firestore();

        // DOM Elements
        const loadingScreen = document.getElementById('loading-screen');
        const authContainer = document.getElementById('auth-container');
        const mainAppContainer = document.getElementById('main-app-container');
        const googleLoginBtn = document.getElementById('google-login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const userInfoSpan = document.getElementById('user-info');
        const tradeForm = document.getElementById('trade-form');
        const formTitle = document.getElementById('form-title');
        const submitBtn = document.getElementById('submit-btn');
        const cancelEditBtn = document.getElementById('cancel-edit-btn');
        const journalBody = document.getElementById('journal-body');
        const noTradesMessage = document.getElementById('no-trades-message');
        const toastMessage = document.getElementById('toast-message');

        let currentUserId = null;
        let isEditing = false;
        
        // --- UI UTILITY FUNCTIONS ---
        function showToast(message) {
            toastMessage.textContent = message;
            toastMessage.classList.remove('opacity-0');
            toastMessage.classList.add('opacity-100');
            setTimeout(() => {
                toastMessage.classList.remove('opacity-100');
                toastMessage.classList.add('opacity-0');
            }, 3000);
        }

        function showApp() {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
                mainAppContainer.classList.remove('hidden', 'scale-95', 'opacity-0');
                mainAppContainer.classList.add('scale-100', 'opacity-100');
            }, 300);
        }
        
        function showAuth() {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
                authContainer.classList.remove('hidden', 'scale-95', 'opacity-0');
                authContainer.classList.add('scale-100', 'opacity-100');
            }, 300);
        }

        function clearForm() {
            tradeForm.reset();
            document.getElementById('trade-id-input').value = '';
            formTitle.textContent = 'Add New Trade';
            submitBtn.textContent = 'Add Trade';
            cancelEditBtn.classList.add('hidden');
            isEditing = false;
        }
        
        // --- FIREBASE AUTHENTICATION ---
        googleLoginBtn.addEventListener('click', () => {
            const provider = new firebase.auth.GoogleAuthProvider();
            auth.signInWithPopup(provider)
                .then((result) => {
                    showToast('Signed in successfully!');
                }).catch((error) => {
                    console.error("Google Sign-In Error:", error);
                    showToast('Sign-in failed. Please try again.');
                });
        });

        logoutBtn.addEventListener('click', () => {
            auth.signOut().then(() => {
                showToast('Signed out successfully!');
                mainAppContainer.classList.add('hidden');
                showAuth();
                clearForm();
                journalBody.innerHTML = ''; // Clear table
                updateSummary({}); // Clear summary
            }).catch((error) => {
                console.error("Sign-Out Error:", error);
                showToast('Sign-out failed. Please try again.');
            });
        });

        auth.onAuthStateChanged(async (user) => {
            if (user) {
                currentUserId = user.uid;
                userInfoSpan.textContent = `Hello, ${user.displayName || 'User'}! | User ID: ${currentUserId}`;
                showApp();
                setupFirestoreListener(currentUserId);
            } else {
                currentUserId = null;
                // Sign in with custom token if available
                if (initialAuthToken) {
                    try {
                        await auth.signInWithCustomToken(initialAuthToken);
                    } catch (error) {
                        console.error("Custom Token Sign-In Error:", error);
                        // Fallback to anonymous sign-in if custom token fails
                        try {
                            await auth.signInAnonymously();
                        } catch (anonError) {
                            console.error("Anonymous Sign-In Error:", anonError);
                            showAuth();
                        }
                    }
                } else {
                    // Sign in anonymously if no token is available
                    try {
                        await auth.signInAnonymously();
                    } catch (error) {
                        console.error("Anonymous Sign-In Error:", error);
                        showAuth();
                    }
                }
            }
        });

        // --- FIREBASE FIRESTORE DATA HANDLING ---
        function setupFirestoreListener(userId) {
            const tradesRef = db.collection('artifacts').doc(appId).collection('users').doc(userId).collection('trades');
            
            tradesRef.onSnapshot(snapshot => {
                const trades = [];
                snapshot.forEach(doc => {
                    trades.push({ id: doc.id, ...doc.data() });
                });
                renderJournal(trades);
                updateSummary(trades);
            }, error => {
                console.error("Firestore snapshot error:", error);
                showToast("Error loading data. Please try again.");
            });
        }
        
        async function addOrUpdateTrade(trade) {
            const userId = auth.currentUser.uid;
            if (!userId) {
                showToast("Please sign in to add or edit trades.");
                return;
            }
            const tradesRef = db.collection('artifacts').doc(appId).collection('users').doc(userId).collection('trades');
            
            try {
                if (trade.id) {
                    await tradesRef.doc(trade.id).set(trade);
                    showToast('Trade updated successfully!');
                } else {
                    delete trade.id; // Ensure no ID is sent for a new entry
                    await tradesRef.add(trade);
                    showToast('Trade added successfully!');
                }
                clearForm();
            } catch (e) {
                console.error("Error adding/updating document: ", e);
                showToast("Failed to save trade. Please try again.");
            }
        }
        
        async function deleteTrade(tradeId) {
            const userId = auth.currentUser.uid;
            if (!userId) { return; }
            
            if (window.confirm("Are you sure you want to delete this trade?")) {
                try {
                    await db.collection('artifacts').doc(appId).collection('users').doc(userId).collection('trades').doc(tradeId).delete();
                    showToast('Trade deleted successfully!');
                } catch (e) {
                    console.error("Error removing document: ", e);
                    showToast("Failed to delete trade. Please try again.");
                }
            }
        }
        
        tradeForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(tradeForm);
            const tradeData = {
                script_name: formData.get('script_name'),
                long_short: formData.get('long_short'),
                entry_price: parseFloat(formData.get('entry_price')),
                exit_price: parseFloat(formData.get('exit_price')),
                pl: parseFloat(formData.get('pl')),
                follow_rules: formData.get('follow_rules'),
                // Add more fields if needed
            };
            
            // Check if we are in edit mode
            const tradeId = formData.get('id');
            if (tradeId) {
                tradeData.id = tradeId;
            }

            addOrUpdateTrade(tradeData);
        });
        
        cancelEditBtn.addEventListener('click', clearForm);

        // --- UI RENDERING & LOGIC ---
        function renderJournal(trades) {
            journalBody.innerHTML = '';
            if (trades.length === 0) {
                noTradesMessage.classList.remove('hidden');
                return;
            }
            noTradesMessage.classList.add('hidden');
            
            trades.forEach(trade => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="p-4 text-sm text-gray-900 font-medium">${trade.script_name || ''}</td>
                    <td class="p-4 text-sm text-gray-500">${trade.long_short || ''}</td>
                    <td class="p-4 text-sm font-semibold ${trade.pl > 0 ? 'text-green-600' : (trade.pl < 0 ? 'text-red-600' : 'text-gray-600')}">${trade.pl || 0}</td>
                    <td class="p-4 text-sm text-gray-500">${trade.follow_rules || ''}</td>
                    <td class="p-4 text-sm font-medium">
                        <button class="text-blue-600 hover:text-blue-900 transition-colors duration-200 mr-2 edit-btn" data-id="${trade.id}">Edit</button>
                        <button class="text-red-600 hover:text-red-900 transition-colors duration-200 delete-btn" data-id="${trade.id}">Delete</button>
                    </td>
                `;
                journalBody.appendChild(tr);
            });
            
            // Attach event listeners to the new buttons
            document.querySelectorAll('.edit-btn').forEach(button => {
                button.addEventListener('click', (e) => {
                    const tradeId = e.target.dataset.id;
                    const trade = trades.find(t => t.id === tradeId);
                    if (trade) {
                        editTrade(trade);
                    }
                });
            });

            document.querySelectorAll('.delete-btn').forEach(button => {
                button.addEventListener('click', (e) => {
                    deleteTrade(e.target.dataset.id);
                });
            });
        }
        
        function editTrade(trade) {
            document.getElementById('trade-id-input').value = trade.id;
            document.getElementById('script_name').value = trade.script_name;
            document.getElementById('long_short').value = trade.long_short;
            document.getElementById('entry_price').value = trade.entry_price;
            document.getElementById('exit_price').value = trade.exit_price;
            document.getElementById('pl').value = trade.pl;
            document.getElementById('follow_rules').value = trade.follow_rules;
            
            formTitle.textContent = 'Edit Trade';
            submitBtn.textContent = 'Update Trade';
            cancelEditBtn.classList.remove('hidden');
            isEditing = true;
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        function updateSummary(trades) {
            const totalTrades = trades.length;
            const winningTrades = trades.filter(t => t.pl > 0).length;
            const losingTrades = trades.filter(t => t.pl < 0).length;
            const totalPL = trades.reduce((sum, t) => sum + (t.pl || 0), 0);
            
            const winRate = totalTrades > 0 ? (winningTrades / totalTrades * 100).toFixed(2) : '0.00';
            const largestWin = trades.reduce((max, t) => t.pl > max ? t.pl : max, 0).toFixed(2);
            const largestLoss = trades.reduce((min, t) => t.pl < min ? t.pl : min, 0).toFixed(2);
            
            document.getElementById('total-trades').textContent = totalTrades;
            document.getElementById('win-rate').textContent = `${winRate}%`;
            document.getElementById('total-pl').textContent = totalPL.toFixed(2);
            document.getElementById('total-pl').classList.remove('text-green-600', 'text-red-600', 'text-gray-600');
            document.getElementById('total-pl').classList.add(totalPL > 0 ? 'text-green-600' : (totalPL < 0 ? 'text-red-600' : 'text-gray-600'));
            document.getElementById('largest-win').textContent = largestWin;
            document.getElementById('largest-loss').textContent = largestLoss;
        }

        // Initially sign in with the custom token or anonymously, then show the appropriate UI
        if (initialAuthToken) {
            auth.signInWithCustomToken(initialAuthToken).then(() => {
                console.log("Signed in with custom token.");
            }).catch(e => {
                console.error("Error with custom token, falling back to anonymous sign-in", e);
                auth.signInAnonymously();
            });
        } else {
            auth.signInAnonymously();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Renders the main HTML template."""
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)
