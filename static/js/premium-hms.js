/**
 * Premium HMS JavaScript Framework
 * Ultra-modern hospital management system frontend
 */

class PremiumHMS {
    constructor() {
        this.notifications = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupTheme();
        this.setupSearch();
        this.setupNotifications();
    }

    setupEventListeners() {
        // Mobile menu toggle
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        const sidebar = document.getElementById('premiumSidebar');
        const sidebarOverlay = document.getElementById('sidebarOverlay');
        const sidebarClose = document.getElementById('sidebarClose');

        if (mobileMenuToggle && sidebar) {
            mobileMenuToggle.addEventListener('click', () => {
                sidebar.classList.add('active');
                if (sidebarOverlay) sidebarOverlay.classList.add('active');
            });
        }

        if (sidebarClose && sidebar) {
            sidebarClose.addEventListener('click', () => {
                sidebar.classList.remove('active');
                if (sidebarOverlay) sidebarOverlay.classList.remove('active');
            });
        }

        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', () => {
                sidebar.classList.remove('active');
                sidebarOverlay.classList.remove('active');
            });
        }

        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        // Global search shortcut
        document.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.focusSearch();
            }
        });

        // Auto-hide loading overlay
        window.addEventListener('load', () => {
            this.hideLoading();
        });
    }

    initializeComponents() {
        // Initialize tooltips
        this.initTooltips();
        
        // Initialize dropdowns
        this.initDropdowns();
        
        // Initialize charts
        this.initCharts();
        
        // Initialize forms
        this.initForms();
    }

    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    initDropdowns() {
        const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
        dropdownElementList.map(function (dropdownToggleEl) {
            return new bootstrap.Dropdown(dropdownToggleEl);
        });
    }

    initCharts() {
        const chartElements = document.querySelectorAll('.premium-chart');
        chartElements.forEach(element => {
            this.createChart(element);
        });
    }

    createChart(element) {
        const chartType = element.dataset.chartType || 'line';
        const chartData = JSON.parse(element.dataset.chartData || '{}');
        
        const ctx = element.getContext('2d');
        
        const config = {
            type: chartType,
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                elements: {
                    line: {
                        tension: 0.4
                    },
                    point: {
                        radius: 4,
                        hoverRadius: 6
                    }
                }
            }
        };

        new Chart(ctx, config);
    }

    initForms() {
        // Enhanced form validation
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    this.showNotification('Please fill in all required fields', 'warning');
                }
                form.classList.add('was-validated');
            });
        });

        // Auto-save functionality
        const autoSaveForms = document.querySelectorAll('[data-auto-save]');
        autoSaveForms.forEach(form => {
            this.setupAutoSave(form);
        });
    }

    setupAutoSave(form) {
        let saveTimeout;
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => {
                    this.autoSaveForm(form);
                }, 2000);
            });
        });
    }

    autoSaveForm(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Save to localStorage
        const formId = form.id || 'auto-save-form';
        localStorage.setItem(`auto-save-${formId}`, JSON.stringify(data));
        
        this.showNotification('Draft saved automatically', 'info', 2000);
    }

    setupTheme() {
        const savedTheme = localStorage.getItem('premium-hms-theme') || 'light';
        this.setTheme(savedTheme);
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('premium-hms-theme', theme);
        
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const lightIcon = themeToggle.querySelector('.light-icon');
            const darkIcon = themeToggle.querySelector('.dark-icon');
            
            if (theme === 'dark') {
                lightIcon?.classList.add('d-none');
                darkIcon?.classList.remove('d-none');
            } else {
                lightIcon?.classList.remove('d-none');
                darkIcon?.classList.add('d-none');
            }
        }
    }

    setupSearch() {
        const searchInput = document.getElementById('globalSearch');
        const searchSuggestions = document.getElementById('searchSuggestions');
        
        if (searchInput && searchSuggestions) {
            let searchTimeout;
            
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const query = e.target.value.trim();
                
                if (query.length > 2) {
                    searchTimeout = setTimeout(() => {
                        this.performSearch(query, searchSuggestions);
                    }, 300);
                } else {
                    searchSuggestions.innerHTML = '';
                    searchSuggestions.style.display = 'none';
                }
            });
            
            // Hide suggestions when clicking outside
            document.addEventListener('click', (e) => {
                if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
                    searchSuggestions.style.display = 'none';
                }
            });
        }
    }

    async performSearch(query, suggestionsContainer) {
        try {
            // Mock search results - replace with actual API call
            const results = await this.mockSearchAPI(query);
            this.displaySearchSuggestions(results, suggestionsContainer);
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    mockSearchAPI(query) {
        // Mock search results
        return new Promise(resolve => {
            setTimeout(() => {
                const mockResults = [
                    { type: 'patient', name: 'John Doe', id: 'P001', url: '/patients/1/' },
                    { type: 'doctor', name: 'Dr. Smith', id: 'D001', url: '/doctors/1/' },
                    { type: 'appointment', name: 'Appointment with Dr. Johnson', id: 'A001', url: '/appointments/1/' }
                ].filter(item => 
                    item.name.toLowerCase().includes(query.toLowerCase()) ||
                    item.id.toLowerCase().includes(query.toLowerCase())
                );
                resolve(mockResults);
            }, 200);
        });
    }

    displaySearchSuggestions(results, container) {
        if (results.length === 0) {
            container.innerHTML = '<div class="search-no-results">No results found</div>';
        } else {
            container.innerHTML = results.map(result => `
                <a href="${result.url}" class="search-suggestion-item">
                    <div class="suggestion-icon">
                        <i class="bi bi-${this.getIconForType(result.type)}"></i>
                    </div>
                    <div class="suggestion-content">
                        <div class="suggestion-name">${result.name}</div>
                        <div class="suggestion-type">${result.type} • ${result.id}</div>
                    </div>
                </a>
            `).join('');
        }
        container.style.display = 'block';
    }

    getIconForType(type) {
        const icons = {
            patient: 'person',
            doctor: 'person-badge',
            appointment: 'calendar-event',
            bill: 'receipt'
        };
        return icons[type] || 'search';
    }

    focusSearch() {
        const searchInput = document.getElementById('globalSearch');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    setupNotifications() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notificationContainer')) {
            const container = document.createElement('div');
            container.id = 'notificationContainer';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
    }

    showNotification(message, type = 'info', duration = 5000) {
        const notification = this.createNotification(message, type);
        const container = document.getElementById('notificationContainer');
        
        if (container) {
            container.appendChild(notification);
            
            // Auto-remove after duration
            setTimeout(() => {
                this.removeNotification(notification);
            }, duration);
        }
    }

    createNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: 'check-circle',
            warning: 'exclamation-triangle',
            error: 'x-circle',
            info: 'info-circle'
        };
        
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="bi bi-${icons[type] || 'info-circle'}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="PremiumHMS.removeNotification(this.parentElement)">
                <i class="bi bi-x"></i>
            </button>
        `;
        
        return notification;
    }

    removeNotification(notification) {
        if (notification && notification.parentElement) {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }

    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            const loadingText = overlay.querySelector('.loading-text');
            if (loadingText) {
                loadingText.textContent = message;
            }
            overlay.style.display = 'flex';
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    // Utility methods
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }

    formatDate(date) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(new Date(date));
    }

    formatTime(time) {
        return new Intl.DateTimeFormat('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        }).format(new Date(`2000-01-01T${time}`));
    }

    debounce(func, wait) {
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

    // API helper methods
    async apiCall(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };

        const mergedOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, mergedOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            this.showNotification(`API Error: ${error.message}`, 'error');
            throw error;
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// Initialize Premium HMS when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.PremiumHMS = new PremiumHMS();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PremiumHMS;
}
