/**
 * Premium HMS - Components JavaScript
 * Advanced UI Components and Interactions
 */

class PremiumComponents {
    constructor() {
        this.charts = new Map();
        this.modals = new Map();
        this.datatables = new Map();
        
        this.init();
    }

    init() {
        this.setupDataTables();
        this.setupCharts();
        this.setupModals();
        this.setupForms();
        this.setupCalendar();
        this.setupFileUpload();
        this.setupRealTimeUpdates();
        
        console.log('🎨 Premium Components initialized');
    }

    /**
     * Enhanced Data Tables
     */
    setupDataTables() {
        const tables = document.querySelectorAll('.premium-datatable');
        
        tables.forEach(table => {
            const config = {
                responsive: true,
                pageLength: 25,
                lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
                language: {
                    search: "Search:",
                    lengthMenu: "Show _MENU_ entries",
                    info: "Showing _START_ to _END_ of _TOTAL_ entries",
                    paginate: {
                        first: "First",
                        last: "Last",
                        next: "Next",
                        previous: "Previous"
                    }
                },
                dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
                     '<"row"<"col-sm-12"tr>>' +
                     '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
                columnDefs: [
                    {
                        targets: 'no-sort',
                        orderable: false
                    }
                ],
                initComplete: function() {
                    this.api().columns().every(function() {
                        const column = this;
                        const header = $(column.header());
                        
                        if (header.hasClass('searchable')) {
                            const input = $('<input type="text" placeholder="Search..." class="form-control form-control-sm">')
                                .appendTo($(column.footer()).empty())
                                .on('keyup change clear', function() {
                                    if (column.search() !== this.value) {
                                        column.search(this.value).draw();
                                    }
                                });
                        }
                    });
                }
            };

            if (typeof $.fn.DataTable !== 'undefined') {
                const dt = $(table).DataTable(config);
                this.datatables.set(table.id, dt);
            }
        });
    }

    /**
     * Interactive Charts
     */
    setupCharts() {
        // Patient Statistics Chart
        this.createPatientChart();
        
        // Appointment Trends Chart
        this.createAppointmentChart();
        
        // Revenue Chart
        this.createRevenueChart();
    }

    createPatientChart() {
        const ctx = document.getElementById('patientChart');
        if (!ctx || typeof Chart === 'undefined') return;

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Active Patients', 'New This Month', 'Inactive'],
                datasets: [{
                    data: [150, 25, 10],
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(34, 197, 94, 0.8)',
                        'rgba(156, 163, 175, 0.8)'
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });

        this.charts.set('patientChart', chart);
    }

    createAppointmentChart() {
        const ctx = document.getElementById('appointmentChart');
        if (!ctx || typeof Chart === 'undefined') return;

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Appointments',
                    data: [12, 19, 15, 25, 22, 8, 5],
                    borderColor: 'rgba(59, 130, 246, 1)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
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
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });

        this.charts.set('appointmentChart', chart);
    }

    createRevenueChart() {
        const ctx = document.getElementById('revenueChart');
        if (!ctx || typeof Chart === 'undefined') return;

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [15000, 18000, 22000, 19000, 25000, 28000],
                    backgroundColor: 'rgba(34, 197, 94, 0.8)',
                    borderColor: 'rgba(34, 197, 94, 1)',
                    borderWidth: 1,
                    borderRadius: 8,
                    borderSkipped: false
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
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });

        this.charts.set('revenueChart', chart);
    }

    /**
     * Enhanced Modals
     */
    setupModals() {
        const modalTriggers = document.querySelectorAll('[data-premium-modal]');
        
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-premium-modal');
                this.showModal(modalId);
            });
        });
    }

    showModal(modalId, options = {}) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.add('animate-fade-in-scale');
        
        if (typeof bootstrap !== 'undefined') {
            const bsModal = new bootstrap.Modal(modal, options);
            bsModal.show();
            this.modals.set(modalId, bsModal);
        }
    }

    /**
     * Enhanced Forms
     */
    setupForms() {
        // Real-time validation
        const forms = document.querySelectorAll('.premium-form');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            
            inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', () => this.clearFieldError(input));
            });

            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    this.showFormErrors(form);
                }
            });
        });

        // Auto-save functionality
        this.setupAutoSave();
    }

    validateField(field) {
        const value = field.value.trim();
        const rules = field.getAttribute('data-validation');
        
        if (!rules) return true;

        const validationRules = JSON.parse(rules);
        let isValid = true;
        let errorMessage = '';

        // Required validation
        if (validationRules.required && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }

        // Email validation
        if (validationRules.email && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
        }

        // Phone validation
        if (validationRules.phone && value) {
            const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            if (!phoneRegex.test(value.replace(/\s/g, ''))) {
                isValid = false;
                errorMessage = 'Please enter a valid phone number';
            }
        }

        // Min length validation
        if (validationRules.minLength && value.length < validationRules.minLength) {
            isValid = false;
            errorMessage = `Minimum ${validationRules.minLength} characters required`;
        }

        if (!isValid) {
            this.showFieldError(field, errorMessage);
        } else {
            this.clearFieldError(field);
        }

        return isValid;
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        let errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            field.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        field.classList.add('animate-shake');
        
        setTimeout(() => {
            field.classList.remove('animate-shake');
        }, 500);
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.remove();
        }
    }

    validateForm(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    showFormErrors(form) {
        const firstError = form.querySelector('.is-invalid');
        if (firstError) {
            firstError.focus();
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    setupAutoSave() {
        const autoSaveForms = document.querySelectorAll('[data-auto-save]');
        
        autoSaveForms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            let saveTimeout;

            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    clearTimeout(saveTimeout);
                    saveTimeout = setTimeout(() => {
                        this.autoSaveForm(form);
                    }, 2000);
                });
            });
        });
    }

    autoSaveForm(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Save to localStorage as backup
        localStorage.setItem(`autosave_${form.id}`, JSON.stringify(data));
        
        // Show auto-save indicator
        this.showAutoSaveIndicator();
    }

    showAutoSaveIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'auto-save-indicator';
        indicator.innerHTML = '<i class="bi bi-check-circle text-success"></i> Auto-saved';
        indicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 8px 16px;
            border-radius: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            font-size: 14px;
        `;
        
        document.body.appendChild(indicator);
        
        setTimeout(() => {
            indicator.remove();
        }, 2000);
    }

    /**
     * Calendar Component
     */
    setupCalendar() {
        const calendarEl = document.getElementById('premiumCalendar');
        if (!calendarEl || typeof FullCalendar === 'undefined') return;

        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            events: '/api/appointments/',
            eventClick: function(info) {
                // Handle event click
                console.log('Event clicked:', info.event);
            },
            dateClick: function(info) {
                // Handle date click
                console.log('Date clicked:', info.dateStr);
            }
        });

        calendar.render();
    }

    /**
     * File Upload Component
     */
    setupFileUpload() {
        const uploadAreas = document.querySelectorAll('.premium-upload');
        
        uploadAreas.forEach(area => {
            const input = area.querySelector('input[type="file"]');
            
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('dragover');
            });

            area.addEventListener('dragleave', () => {
                area.classList.remove('dragover');
            });

            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                this.handleFileUpload(files, area);
            });

            if (input) {
                input.addEventListener('change', (e) => {
                    this.handleFileUpload(e.target.files, area);
                });
            }
        });
    }

    handleFileUpload(files, uploadArea) {
        Array.from(files).forEach(file => {
            if (this.validateFile(file)) {
                this.uploadFile(file, uploadArea);
            }
        });
    }

    validateFile(file) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
        
        if (file.size > maxSize) {
            window.premiumHMS.showNotification('File size must be less than 10MB', 'error');
            return false;
        }
        
        if (!allowedTypes.includes(file.type)) {
            window.premiumHMS.showNotification('File type not allowed', 'error');
            return false;
        }
        
        return true;
    }

    uploadFile(file, uploadArea) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Create progress indicator
        const progressBar = this.createProgressBar();
        uploadArea.appendChild(progressBar);
        
        // Simulate upload progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 30;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                setTimeout(() => {
                    progressBar.remove();
                    window.premiumHMS.showNotification('File uploaded successfully', 'success');
                }, 500);
            }
            progressBar.querySelector('.progress-bar').style.width = progress + '%';
        }, 200);
    }

    createProgressBar() {
        const progressContainer = document.createElement('div');
        progressContainer.className = 'progress mt-2';
        progressContainer.innerHTML = '<div class="progress-bar" style="width: 0%"></div>';
        return progressContainer;
    }

    /**
     * Real-time Updates
     */
    setupRealTimeUpdates() {
        // Simulate real-time updates
        setInterval(() => {
            this.updateNotificationBadge();
            this.updateDashboardStats();
        }, 30000);
    }

    updateNotificationBadge() {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            const currentCount = parseInt(badge.textContent) || 0;
            const newCount = Math.max(0, currentCount + Math.floor(Math.random() * 3) - 1);
            badge.textContent = newCount;
            badge.style.display = newCount > 0 ? 'flex' : 'none';
        }
    }

    updateDashboardStats() {
        const counters = document.querySelectorAll('.stat-counter');
        counters.forEach(counter => {
            const currentValue = parseInt(counter.textContent) || 0;
            const variation = Math.floor(Math.random() * 5) - 2;
            const newValue = Math.max(0, currentValue + variation);
            
            this.animateCounter(counter, currentValue, newValue);
        });
    }

    animateCounter(element, start, end) {
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const current = Math.floor(start + (end - start) * progress);
            
            element.textContent = current.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
}

// Initialize Premium Components when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.premiumComponents = new PremiumComponents();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PremiumComponents;
}
