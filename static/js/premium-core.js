/**
 * Premium HMS - Core JavaScript
 * Ultra-Modern Hospital Management System
 * Advanced Frontend Framework
 */

class PremiumHMS {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.sidebarState = localStorage.getItem('sidebarState') || 'open';
        this.notifications = [];
        this.searchCache = new Map();
        this.websockets = {};
        this.apiBaseUrl = '/api/v1/';
        this.wsBaseUrl = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        this.wsBaseUrl += window.location.host + '/ws/';
        this.isOnline = navigator.onLine;
        this.unreadCount = 0;
        this.eventEmitter = new EventTarget();

        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.setupTheme();
        this.setupSidebar();
        this.setupSearch();
        this.setupNotifications();
        this.setupTooltips();
        this.setupAnimations();
        this.setupKeyboardShortcuts();
        this.setupPerformanceMonitoring();
        this.setupWebSockets();
        this.setupOfflineHandling();
        this.setupServiceWorker();
        this.setupRealTimeFeatures();
        this.setupAdvancedUI();

        console.log('🏥 Premium HMS v2.0 initialized successfully');
    }

    /**
     * Theme Management
     */
    setupTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('theme', this.theme);
        
        this.showNotification(`Switched to ${this.theme} theme`, 'success');
    }

    /**
     * Sidebar Management
     */
    setupSidebar() {
        const sidebar = document.getElementById('premiumSidebar');
        const overlay = document.getElementById('sidebarOverlay');
        const mobileToggle = document.getElementById('mobileMenuToggle');
        const sidebarClose = document.getElementById('sidebarClose');

        if (mobileToggle) {
            mobileToggle.addEventListener('click', () => this.toggleSidebar());
        }

        if (sidebarClose) {
            sidebarClose.addEventListener('click', () => this.closeSidebar());
        }

        if (overlay) {
            overlay.addEventListener('click', () => this.closeSidebar());
        }

        // Set active navigation item
        this.setActiveNavItem();
    }

    toggleSidebar() {
        const sidebar = document.getElementById('premiumSidebar');
        const overlay = document.getElementById('sidebarOverlay');
        const toggle = document.getElementById('mobileMenuToggle');

        if (sidebar && overlay && toggle) {
            const isOpen = sidebar.classList.contains('open');
            
            if (isOpen) {
                this.closeSidebar();
            } else {
                sidebar.classList.add('open');
                overlay.classList.add('active');
                toggle.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        }
    }

    closeSidebar() {
        const sidebar = document.getElementById('premiumSidebar');
        const overlay = document.getElementById('sidebarOverlay');
        const toggle = document.getElementById('mobileMenuToggle');

        if (sidebar && overlay && toggle) {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
            toggle.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    setActiveNavItem() {
        const currentPath = window.location.pathname;
        const navItems = document.querySelectorAll('.nav-item');

        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === currentPath) {
                item.classList.add('active');
            }
        });
    }

    /**
     * Global Search
     */
    setupSearch() {
        const searchInput = document.getElementById('globalSearch');
        const searchSuggestions = document.getElementById('searchSuggestions');

        if (searchInput && searchSuggestions) {
            let searchTimeout;

            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const query = e.target.value.trim();

                if (query.length < 2) {
                    searchSuggestions.style.display = 'none';
                    return;
                }

                searchTimeout = setTimeout(() => {
                    this.performSearch(query, searchSuggestions);
                }, 300);
            });

            searchInput.addEventListener('blur', () => {
                setTimeout(() => {
                    searchSuggestions.style.display = 'none';
                }, 200);
            });

            searchInput.addEventListener('focus', () => {
                if (searchInput.value.trim().length >= 2) {
                    searchSuggestions.style.display = 'block';
                }
            });
        }
    }

    async performSearch(query, suggestionsContainer) {
        // Check cache first
        if (this.searchCache.has(query)) {
            this.displaySearchResults(this.searchCache.get(query), suggestionsContainer);
            return;
        }

        try {
            // Simulate API call - replace with actual endpoint
            const mockResults = this.generateMockSearchResults(query);
            
            this.searchCache.set(query, mockResults);
            this.displaySearchResults(mockResults, suggestionsContainer);
        } catch (error) {
            console.error('Search error:', error);
            this.showNotification('Search failed. Please try again.', 'error');
        }
    }

    generateMockSearchResults(query) {
        const mockData = [
            { type: 'patient', name: 'John Doe', id: '001', url: '/patients/1/' },
            { type: 'doctor', name: 'Dr. Smith', id: '002', url: '/doctors/1/' },
            { type: 'appointment', name: 'Appointment with Dr. Johnson', id: '003', url: '/appointments/1/' }
        ];

        return mockData.filter(item => 
            item.name.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 5);
    }

    displaySearchResults(results, container) {
        if (results.length === 0) {
            container.innerHTML = '<div class="p-3 text-muted">No results found</div>';
        } else {
            container.innerHTML = results.map(result => `
                <a href="${result.url}" class="d-block p-3 text-decoration-none border-bottom">
                    <div class="d-flex align-items-center">
                        <i class="bi bi-${this.getIconForType(result.type)} me-3"></i>
                        <div>
                            <div class="fw-medium">${result.name}</div>
                            <small class="text-muted">${result.type.charAt(0).toUpperCase() + result.type.slice(1)}</small>
                        </div>
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

    /**
     * Notification System
     */
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
        const container = document.getElementById('notificationContainer');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show premium-alert animate-slide-in-right`;
        notification.innerHTML = `
            <div class="alert-content">
                <i class="bi bi-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        container.appendChild(notification);

        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 150);
            }
        }, duration);

        return notification;
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    /**
     * Tooltips
     */
    setupTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                delay: { show: 500, hide: 100 }
            });
        });
    }

    /**
     * Animations
     */
    setupAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-scale');
                }
            });
        }, observerOptions);

        // Observe elements with animation classes
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }

    /**
     * Keyboard Shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('globalSearch');
                if (searchInput) {
                    searchInput.focus();
                }
            }

            // Ctrl/Cmd + Shift + T for theme toggle
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.toggleTheme();
            }

            // Escape to close sidebar on mobile
            if (e.key === 'Escape') {
                this.closeSidebar();
            }
        });
    }

    /**
     * Performance Monitoring
     */
    setupPerformanceMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
            
            if (loadTime > 3000) {
                console.warn(`Slow page load detected: ${loadTime}ms`);
            }
        });

        // Monitor memory usage
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                if (memory.usedJSHeapSize > 50 * 1024 * 1024) { // 50MB
                    console.warn('High memory usage detected');
                }
            }, 30000);
        }
    }

    /**
     * Utility Methods
     */
    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('active');
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    }

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

    /**
     * WebSocket Management
     */
    setupWebSockets() {
        if (!window.WebSocket) {
            console.warn('WebSocket not supported');
            return;
        }

        // Get user ID from DOM
        const userId = document.body.dataset.userId;
        if (userId) {
            this.connectNotificationWebSocket(userId);
        }

        this.connectSystemStatusWebSocket();
    }

    connectNotificationWebSocket(userId) {
        const wsUrl = `${this.wsBaseUrl}notifications/${userId}/`;

        try {
            this.websockets.notifications = new WebSocket(wsUrl);

            this.websockets.notifications.onopen = () => {
                console.log('🔔 Notification WebSocket connected');
                this.showNotification('Real-time notifications enabled', 'success');
            };

            this.websockets.notifications.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleNotificationMessage(data);
            };

            this.websockets.notifications.onclose = () => {
                console.log('🔔 Notification WebSocket disconnected');
                setTimeout(() => this.connectNotificationWebSocket(userId), 5000);
            };

            this.websockets.notifications.onerror = (error) => {
                console.error('🔔 Notification WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to connect notification WebSocket:', error);
        }
    }

    connectSystemStatusWebSocket() {
        const wsUrl = `${this.wsBaseUrl}system/status/`;

        try {
            this.websockets.systemStatus = new WebSocket(wsUrl);

            this.websockets.systemStatus.onopen = () => {
                console.log('📊 System Status WebSocket connected');
            };

            this.websockets.systemStatus.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleSystemStatusMessage(data);
            };

            this.websockets.systemStatus.onclose = () => {
                console.log('📊 System Status WebSocket disconnected');
                setTimeout(() => this.connectSystemStatusWebSocket(), 10000);
            };
        } catch (error) {
            console.error('Failed to connect system status WebSocket:', error);
        }
    }

    handleNotificationMessage(data) {
        switch (data.type) {
            case 'notification':
                this.addRealTimeNotification(data.notification);
                break;
            case 'system_alert':
                this.showSystemAlert(data.alert);
                break;
            case 'unread_count':
                this.updateNotificationBadge(data.count);
                break;
        }
    }

    handleSystemStatusMessage(data) {
        if (data.type === 'system_status') {
            this.updateSystemStatus(data.status, data.metrics);
        }
    }

    addRealTimeNotification(notification) {
        this.notifications.unshift(notification);
        this.unreadCount++;
        this.updateNotificationBadge();

        // Show browser notification if permission granted
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(notification.title, {
                body: notification.message,
                icon: '/static/images/logo.png',
                tag: notification.id
            });
        }

        // Show in-app notification
        this.showNotification(notification.title, 'info', 3000);
    }

    updateNotificationBadge(count = null) {
        if (count !== null) {
            this.unreadCount = count;
        }

        const badge = document.querySelector('.notification-badge');
        if (badge) {
            if (this.unreadCount > 0) {
                badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
                badge.style.display = 'block';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    showSystemAlert(alert) {
        this.showNotification(alert.title, alert.type || 'warning', 0); // Persistent
    }

    /**
     * Offline Handling
     */
    setupOfflineHandling() {
        window.addEventListener('online', () => this.handleOnlineStatus(true));
        window.addEventListener('offline', () => this.handleOnlineStatus(false));

        this.handleOnlineStatus(navigator.onLine);
    }

    handleOnlineStatus(isOnline) {
        this.isOnline = isOnline;

        const statusIndicator = document.querySelector('.footer-status');
        if (statusIndicator) {
            if (isOnline) {
                statusIndicator.innerHTML = '<i class="bi bi-circle-fill text-success"></i> System Status: Online';
            } else {
                statusIndicator.innerHTML = '<i class="bi bi-circle-fill text-warning"></i> System Status: Offline';
            }
        }

        const message = isOnline ? 'Connection restored' : 'Working offline';
        const type = isOnline ? 'success' : 'warning';
        this.showNotification(message, type);

        // Emit event for other components
        this.eventEmitter.dispatchEvent(new CustomEvent('connectionStatusChanged', {
            detail: { isOnline }
        }));
    }

    /**
     * Service Worker
     */
    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/sw.js')
                .then((registration) => {
                    console.log('🔧 Service Worker registered:', registration);
                })
                .catch((error) => {
                    console.error('🔧 Service Worker registration failed:', error);
                });
        }
    }

    /**
     * Real-time Features
     */
    setupRealTimeFeatures() {
        // Request notification permission
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }

        // Setup real-time data refresh
        this.setupDataRefresh();

        // Setup live chat if available
        this.setupLiveChat();
    }

    setupDataRefresh() {
        // Refresh dashboard data every 30 seconds
        if (document.querySelector('.dashboard-content')) {
            setInterval(() => {
                if (this.isOnline) {
                    this.refreshDashboardData();
                }
            }, 30000);
        }
    }

    async refreshDashboardData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}dashboard/stats/`);
            if (response.ok) {
                const data = await response.json();
                this.updateDashboardStats(data);
            }
        } catch (error) {
            console.error('Failed to refresh dashboard data:', error);
        }
    }

    updateDashboardStats(data) {
        // Update various dashboard statistics
        Object.keys(data).forEach(key => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                element.textContent = data[key];
                element.classList.add('animate-pulse');
                setTimeout(() => element.classList.remove('animate-pulse'), 1000);
            }
        });
    }

    setupLiveChat() {
        const chatContainer = document.getElementById('liveChatContainer');
        if (chatContainer) {
            // Initialize live chat functionality
            this.initializeLiveChat();
        }
    }

    /**
     * Advanced UI Components
     */
    setupAdvancedUI() {
        this.setupDataTables();
        this.setupCharts();
        this.setupCalendar();
        this.setupFormEnhancements();
        this.setupProgressBars();
    }

    setupDataTables() {
        const tables = document.querySelectorAll('.premium-datatable');
        tables.forEach(table => {
            this.enhanceTable(table);
        });
    }

    enhanceTable(table) {
        // Add sorting functionality
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.sortTable(table, header);
            });
        });

        // Add search functionality
        const searchInput = table.parentElement.querySelector('.table-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterTable(table, e.target.value);
            });
        }
    }

    sortTable(table, header) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const columnIndex = Array.from(header.parentElement.children).indexOf(header);
        const isAscending = !header.classList.contains('sort-asc');

        rows.sort((a, b) => {
            const aValue = a.children[columnIndex].textContent.trim();
            const bValue = b.children[columnIndex].textContent.trim();

            if (isAscending) {
                return aValue.localeCompare(bValue, undefined, { numeric: true });
            } else {
                return bValue.localeCompare(aValue, undefined, { numeric: true });
            }
        });

        // Update header classes
        header.parentElement.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');

        // Reorder rows
        rows.forEach(row => tbody.appendChild(row));
    }

    filterTable(table, searchTerm) {
        const tbody = table.querySelector('tbody');
        const rows = tbody.querySelectorAll('tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(searchTerm.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
    }

    setupCharts() {
        // Initialize Chart.js charts if available
        const chartElements = document.querySelectorAll('.premium-chart');
        chartElements.forEach(element => {
            this.initializeChart(element);
        });
    }

    initializeChart(element) {
        const chartType = element.dataset.chartType || 'line';
        const chartData = JSON.parse(element.dataset.chartData || '{}');

        // This would integrate with Chart.js or similar library
        console.log(`Initializing ${chartType} chart with data:`, chartData);
    }

    setupCalendar() {
        const calendarElements = document.querySelectorAll('.premium-calendar');
        calendarElements.forEach(element => {
            this.initializeCalendar(element);
        });
    }

    initializeCalendar(element) {
        // Calendar initialization logic
        console.log('Initializing calendar:', element);
    }

    setupFormEnhancements() {
        // Auto-save functionality
        const autoSaveForms = document.querySelectorAll('[data-auto-save]');
        autoSaveForms.forEach(form => {
            this.setupAutoSave(form);
        });

        // Smart validation
        const smartForms = document.querySelectorAll('.smart-form');
        smartForms.forEach(form => {
            this.setupSmartValidation(form);
        });
    }

    setupAutoSave(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', this.debounce(() => {
                this.autoSaveForm(form);
            }, 2000));
        });
    }

    async autoSaveForm(form) {
        const formData = new FormData(form);
        const autoSaveUrl = form.dataset.autoSave;

        try {
            const response = await fetch(autoSaveUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                this.showNotification('Draft saved automatically', 'success', 2000);
            }
        } catch (error) {
            console.error('Auto-save failed:', error);
        }
    }

    setupSmartValidation(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });
    }

    validateField(field) {
        // Smart field validation logic
        const value = field.value.trim();
        const fieldType = field.type || field.tagName.toLowerCase();

        // Remove existing validation classes
        field.classList.remove('is-valid', 'is-invalid');

        // Basic validation
        if (field.required && !value) {
            field.classList.add('is-invalid');
            return false;
        }

        // Type-specific validation
        switch (fieldType) {
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (value && !emailRegex.test(value)) {
                    field.classList.add('is-invalid');
                    return false;
                }
                break;
            case 'tel':
                const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
                if (value && !phoneRegex.test(value.replace(/\s/g, ''))) {
                    field.classList.add('is-invalid');
                    return false;
                }
                break;
        }

        if (value) {
            field.classList.add('is-valid');
        }
        return true;
    }

    setupProgressBars() {
        const progressBars = document.querySelectorAll('.premium-progress');
        progressBars.forEach(bar => {
            this.animateProgressBar(bar);
        });
    }

    animateProgressBar(progressBar) {
        const targetValue = progressBar.dataset.value || 0;
        const progressFill = progressBar.querySelector('.progress-bar');

        if (progressFill) {
            let currentValue = 0;
            const increment = targetValue / 50; // 50 steps

            const animate = () => {
                currentValue += increment;
                if (currentValue >= targetValue) {
                    currentValue = targetValue;
                    progressFill.style.width = `${currentValue}%`;
                    return;
                }

                progressFill.style.width = `${currentValue}%`;
                requestAnimationFrame(animate);
            };

            // Start animation when element is visible
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        animate();
                        observer.unobserve(entry.target);
                    }
                });
            });

            observer.observe(progressBar);
        }
    }

    /**
     * API Utilities
     */
    async apiCall(endpoint, options = {}) {
        const url = `${this.apiBaseUrl}${endpoint}`;
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
            console.error('API call failed:', error);
            if (!this.isOnline) {
                this.showNotification('Request failed - you are offline', 'warning');
            }
            throw error;
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    updateSystemStatus(status, metrics) {
        // Update system status indicators
        const statusElements = document.querySelectorAll('.system-status');
        statusElements.forEach(element => {
            element.textContent = status;
            element.className = `system-status status-${status.toLowerCase()}`;
        });

        // Update performance metrics if dashboard is visible
        if (metrics && document.querySelector('.performance-metrics')) {
            this.updatePerformanceMetrics(metrics);
        }
    }

    updatePerformanceMetrics(metrics) {
        // Update CPU usage
        const cpuElement = document.querySelector('.cpu-usage');
        if (cpuElement && metrics.cpu) {
            cpuElement.textContent = `${metrics.cpu.percent}%`;
        }

        // Update memory usage
        const memoryElement = document.querySelector('.memory-usage');
        if (memoryElement && metrics.memory) {
            memoryElement.textContent = `${metrics.memory.percent}%`;
        }

        // Update disk usage
        const diskElement = document.querySelector('.disk-usage');
        if (diskElement && metrics.disk) {
            diskElement.textContent = `${metrics.disk.percent}%`;
        }
    }
}

// Initialize Premium HMS when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.premiumHMS = new PremiumHMS();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PremiumHMS;
}
