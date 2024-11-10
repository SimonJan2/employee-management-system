// static/js/main.js

// Particle.js Configuration
particlesJS('particles-js', {
    particles: {
        number: {
            value: 80,
            density: {
                enable: true,
                value_area: 800
            }
        },
        color: {
            value: '#3B82F6'
        },
        shape: {
            type: 'circle'
        },
        opacity: {
            value: 0.5,
            random: false
        },
        size: {
            value: 3,
            random: true
        },
        line_linked: {
            enable: true,
            distance: 150,
            color: '#3B82F6',
            opacity: 0.4,
            width: 1
        },
        move: {
            enable: true,
            speed: 2,
            direction: 'none',
            random: false,
            straight: false,
            out_mode: 'out',
            bounce: false
        }
    },
    interactivity: {
        detect_on: 'canvas',
        events: {
            onhover: {
                enable: true,
                mode: 'grab'
            },
            onclick: {
                enable: true,
                mode: 'push'
            },
            resize: true
        },
        modes: {
            grab: {
                distance: 140,
                line_linked: {
                    opacity: 1
                }
            },
            push: {
                particles_nb: 4
            }
        }
    },
    retina_detect: true
});

// User Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const userMenuButton = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');
    
    if (userMenuButton && userMenu) {
        userMenuButton.addEventListener('click', function() {
            userMenu.classList.toggle('hidden');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!userMenuButton.contains(event.target) && !userMenu.contains(event.target)) {
                userMenu.classList.add('hidden');
            }
        });
    }
});

// Flash Message Handling
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const closeButton = alert.querySelector('.close-alert');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                alert.remove();
            });
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    });
});

// Form Validation
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('border-red-500');
            
            // Add error message if it doesn't exist
            let errorMessage = field.parentNode.querySelector('.error-message');
            if (!errorMessage) {
                errorMessage = document.createElement('p');
                errorMessage.className = 'text-red-500 text-sm mt-1 error-message';
                errorMessage.textContent = 'This field is required';
                field.parentNode.appendChild(errorMessage);
            }
        } else {
            field.classList.remove('border-red-500');
            const errorMessage = field.parentNode.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.remove();
            }
        }
    });

    return isValid;
}

// File Upload Preview
function handleFileUpload(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        const preview = document.querySelector('.file-preview');
        
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.classList.remove('hidden');
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// static/js/main.js

// ... (previous code remains the same until the sortTable function)

// Table Sorting
function sortTable(table, column, type = 'string') {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAscending = table.getAttribute('data-sort') !== 'asc';
    
    rows.sort((a, b) => {
        let aValue = a.cells[column].textContent.trim();
        let bValue = b.cells[column].textContent.trim();
        
        if (type === 'number') {
            aValue = parseFloat(aValue);
            bValue = parseFloat(bValue);
        } else if (type === 'date') {
            aValue = new Date(aValue);
            bValue = new Date(bValue);
        }
        
        if (aValue < bValue) return isAscending ? -1 : 1;
        if (aValue > bValue) return isAscending ? 1 : -1;
        return 0;
    });
    
    table.setAttribute('data-sort', isAscending ? 'asc' : 'desc');
    
    // Update sort indicators
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sorting-asc', 'sorting-desc');
    });
    table.querySelector(`th:nth-child(${column + 1})`).classList.add(
        isAscending ? 'sorting-asc' : 'sorting-desc'
    );
    
    // Reorder rows
    rows.forEach(row => tbody.appendChild(row));
}

// Search functionality
function initializeSearch(searchInput, tableId) {
    const table = document.getElementById(tableId);
    if (!table || !searchInput) return;

    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

// Pagination
class Pagination {
    constructor(table, itemsPerPage = 10) {
        this.table = table;
        this.itemsPerPage = itemsPerPage;
        this.currentPage = 1;
        this.rows = Array.from(table.querySelectorAll('tbody tr'));
        this.totalPages = Math.ceil(this.rows.length / this.itemsPerPage);
        
        this.init();
    }
    
    init() {
        this.createPaginationControls();
        this.showPage(1);
    }
    
    showPage(page) {
        this.currentPage = page;
        const start = (page - 1) * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        
        this.rows.forEach((row, index) => {
            row.style.display = (index >= start && index < end) ? '' : 'none';
        });
        
        this.updatePaginationControls();
    }
    
    createPaginationControls() {
        const container = document.createElement('div');
        container.className = 'pagination-controls flex justify-center space-x-2 mt-4';
        
        // Previous button
        const prevButton = document.createElement('button');
        prevButton.textContent = 'Previous';
        prevButton.className = 'btn-secondary';
        prevButton.addEventListener('click', () => {
            if (this.currentPage > 1) this.showPage(this.currentPage - 1);
        });
        
        // Next button
        const nextButton = document.createElement('button');
        nextButton.textContent = 'Next';
        nextButton.className = 'btn-secondary';
        nextButton.addEventListener('click', () => {
            if (this.currentPage < this.totalPages) this.showPage(this.currentPage + 1);
        });
        
        // Page numbers
        const pageNumbers = document.createElement('div');
        pageNumbers.className = 'flex space-x-2';
        
        container.appendChild(prevButton);
        container.appendChild(pageNumbers);
        container.appendChild(nextButton);
        
        this.table.parentNode.appendChild(container);
        this.paginationControls = {
            container,
            prevButton,
            nextButton,
            pageNumbers
        };
    }
    
    updatePaginationControls() {
        const { prevButton, nextButton, pageNumbers } = this.paginationControls;
        
        prevButton.disabled = this.currentPage === 1;
        nextButton.disabled = this.currentPage === this.totalPages;
        
        // Update page numbers
        pageNumbers.innerHTML = '';
        for (let i = 1; i <= this.totalPages; i++) {
            const pageButton = document.createElement('button');
            pageButton.textContent = i;
            pageButton.className = `px-3 py-1 rounded ${
                i === this.currentPage 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 hover:bg-gray-300'
            }`;
            pageButton.addEventListener('click', () => this.showPage(i));
            pageNumbers.appendChild(pageButton);
        }
    }
}

// Modal handling
class Modal {
    constructor(id) {
        this.modal = document.getElementById(id);
        this.init();
    }
    
    init() {
        if (!this.modal) return;
        
        const closeButtons = this.modal.querySelectorAll('[data-close-modal]');
        closeButtons.forEach(button => {
            button.addEventListener('click', () => this.close());
        });
        
        // Close on outside click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.close();
        });
    }
    
    open() {
        this.modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
    
    close() {
        this.modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
}

// Initialize all components
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all sortable tables
    document.querySelectorAll('table[data-sortable]').forEach(table => {
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach((header, index) => {
            header.addEventListener('click', () => {
                sortTable(table, index, header.dataset.type || 'string');
            });
        });
    });
    
    // Initialize all search inputs
    document.querySelectorAll('[data-search-table]').forEach(input => {
        initializeSearch(input, input.dataset.searchTable);
    });
    
    // Initialize pagination for tables that need it
    document.querySelectorAll('table[data-paginate]').forEach(table => {
        new Pagination(table, parseInt(table.dataset.itemsPerPage) || 10);
    });
    
    // Initialize all modals
    document.querySelectorAll('[data-modal]').forEach(trigger => {
        const modal = new Modal(trigger.dataset.modal);
        trigger.addEventListener('click', () => modal.open());
    });
});