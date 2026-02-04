/**
 * Provider Verification Dashboard - JavaScript
 * Handles filtering, search, pagination, and sorting functionality
 */

// Global state
let currentPage = 1;
const rowsPerPage = 50;
let filteredRows = [];
let allRows = [];
let sortState = {
    column: null,
    ascending: true
};

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    
    // Get all table rows
    const tableBody = document.getElementById('tableBody');
    if (!tableBody) {
        console.warn('Table body not found');
        return;
    }
    
    allRows = Array.from(tableBody.querySelectorAll('.result-row'));
    filteredRows = [...allRows];
    
    console.log(`Total rows: ${allRows.length}`);
    
    // Set up event listeners
    setupEventListeners();
    
    // Initial display
    displayPage(1);
});

/**
 * Set up all event listeners
 */
function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const fileFilter = document.getElementById('fileFilter');
    const statusFilter = document.getElementById('statusFilter');
    const confidenceFilter = document.getElementById('confidenceFilter');
    const cityFilter = document.getElementById('cityFilter');
    const zipcodeFilter = document.getElementById('zipcodeFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(applyFilters, 300));
    }
    
    if (fileFilter) {
        fileFilter.addEventListener('change', handleFileFilterChange);
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', applyFilters);
    }
    
    if (confidenceFilter) {
        confidenceFilter.addEventListener('change', applyFilters);
    }
    
    if (cityFilter) {
        cityFilter.addEventListener('change', applyFilters);
    }
    
    if (zipcodeFilter) {
        zipcodeFilter.addEventListener('input', debounce(applyFilters, 300));
    }
}

/**
 * Handle file filter change - reload page with selected file
 */
function handleFileFilterChange() {
    const fileId = document.getElementById('fileFilter').value;
    if (fileId === 'all') {
        window.location.href = '/dashboard';
    } else {
        window.location.href = '/dashboard?file_id=' + fileId;
    }
}

/**
 * Debounce function to limit function calls
 */
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

/**
 * Apply all filters to the data
 */
function applyFilters() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('statusFilter')?.value || 'all';
    const confidenceFilter = document.getElementById('confidenceFilter')?.value || 'all';
    const cityFilter = document.getElementById('cityFilter')?.value || 'all';
    const zipcodeFilter = document.getElementById('zipcodeFilter')?.value.toLowerCase() || '';
    
    console.log('Applying filters:', { searchTerm, statusFilter, confidenceFilter, cityFilter, zipcodeFilter });
    
    // Start with all rows
    filteredRows = allRows.filter(row => {
        // Search filter (provider name or NPI)
        const providerName = row.querySelector('.provider-name')?.textContent.toLowerCase() || '';
        const npi = row.querySelector('.npi-cell')?.textContent.toLowerCase() || '';
        const matchesSearch = searchTerm === '' || 
                             providerName.includes(searchTerm) || 
                             npi.includes(searchTerm);
        
        // Status filter
        const rowStatus = row.dataset.status;
        const matchesStatus = statusFilter === 'all' || rowStatus === statusFilter;
        
        // Confidence filter
        const confidence = parseInt(row.dataset.confidence) || 0;
        let matchesConfidence = true;
        
        if (confidenceFilter === 'high') {
            matchesConfidence = confidence > 80;
        } else if (confidenceFilter === 'medium') {
            matchesConfidence = confidence >= 50 && confidence <= 80;
        } else if (confidenceFilter === 'low') {
            matchesConfidence = confidence < 50;
        }
        
        // City filter
        const rowCity = row.dataset.city || '';
        const matchesCity = cityFilter === 'all' || rowCity === cityFilter;
        
        // Zipcode filter
        const rowZipcode = row.dataset.zipcode || '';
        const matchesZipcode = zipcodeFilter === '' || rowZipcode.toLowerCase().includes(zipcodeFilter);
        
        return matchesSearch && matchesStatus && matchesConfidence && matchesCity && matchesZipcode;
    });
    
    console.log(`Filtered to ${filteredRows.length} rows`);
    
    // Update visible count
    updateVisibleCount();
    
    // Reset to page 1 and display
    currentPage = 1;
    displayPage(1);
}

/**
 * Display specific page of results
 */
function displayPage(page) {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;
    
    // Hide all rows first
    allRows.forEach(row => {
        row.style.display = 'none';
    });
    
    // Calculate range for current page
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    
    // Show filtered rows for this page
    const rowsToShow = filteredRows.slice(start, end);
    rowsToShow.forEach(row => {
        row.style.display = '';
    });
    
    console.log(`Displaying page ${page}: rows ${start} to ${end}`);
    
    // Update pagination controls
    updatePagination(page);
}

/**
 * Update pagination controls
 */
function updatePagination(page) {
    const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
    
    // Update page info
    const pageInfo = document.getElementById('pageInfo');
    if (pageInfo) {
        pageInfo.textContent = `Page ${page} of ${totalPages || 1}`;
    }
    
    // Update button states
    const prevButton = document.getElementById('prevPage');
    const nextButton = document.getElementById('nextPage');
    
    if (prevButton) {
        prevButton.disabled = page === 1;
    }
    
    if (nextButton) {
        nextButton.disabled = page >= totalPages;
    }
}

/**
 * Update visible count display
 */
function updateVisibleCount() {
    const visibleCount = document.getElementById('visibleCount');
    if (visibleCount) {
        visibleCount.textContent = filteredRows.length;
    }
}

/**
 * Go to next page
 */
function nextPage() {
    const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        displayPage(currentPage);
        scrollToTop();
    }
}

/**
 * Go to previous page
 */
function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        displayPage(currentPage);
        scrollToTop();
    }
}

/**
 * Scroll to top of results
 */
function scrollToTop() {
    const resultsTable = document.querySelector('.results-table-container');
    if (resultsTable) {
        resultsTable.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Sort table by column
 */
function sortTable(columnIndex) {
    console.log(`Sorting by column ${columnIndex}`);
    
    // Toggle sort direction if same column, otherwise default to ascending
    if (sortState.column === columnIndex) {
        sortState.ascending = !sortState.ascending;
    } else {
        sortState.column = columnIndex;
        sortState.ascending = true;
    }
    
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;
    
    // Get all rows (both filtered and unfiltered)
    const rows = Array.from(tbody.querySelectorAll('.result-row'));
    
    // Sort rows
    rows.sort((a, b) => {
        let aValue = a.cells[columnIndex]?.textContent.trim() || '';
        let bValue = b.cells[columnIndex]?.textContent.trim() || '';
        
        // Special handling for different column types
        switch(columnIndex) {
            case 0: // Status
                // Extract just the status word
                aValue = aValue.split(' ')[1] || aValue;
                bValue = bValue.split(' ')[1] || bValue;
                break;
                
            case 5: // Confidence (numeric)
                aValue = parseInt(aValue) || 0;
                bValue = parseInt(bValue) || 0;
                break;
                
            case 6: // Sources (numeric)
                aValue = parseInt(aValue) || 0;
                bValue = parseInt(bValue) || 0;
                break;
        }
        
        // Compare values
        let comparison = 0;
        if (typeof aValue === 'number' && typeof bValue === 'number') {
            comparison = aValue - bValue;
        } else {
            comparison = String(aValue).localeCompare(String(bValue));
        }
        
        return sortState.ascending ? comparison : -comparison;
    });
    
    // Re-append rows in sorted order
    rows.forEach(row => tbody.appendChild(row));
    
    // Update filteredRows to match new order
    filteredRows = allRows.filter(row => filteredRows.includes(row));
    
    // Re-display current page with new sort order
    displayPage(currentPage);
    
    // Update column headers to show sort direction
    updateSortIndicators(columnIndex);
}

/**
 * Update sort direction indicators in column headers
 */
function updateSortIndicators(sortedColumn) {
    const headers = document.querySelectorAll('.results-table th');
    headers.forEach((header, index) => {
        const text = header.textContent.replace(/[▴▾]/g, '').trim();
        
        if (index === sortedColumn) {
            const arrow = sortState.ascending ? '▴' : '▾';
            header.textContent = `${text} ${arrow}`;
        } else {
            header.textContent = `${text} ▾`;
        }
    });
}

/**
 * Reset all filters
 */
function resetFilters() {
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const confidenceFilter = document.getElementById('confidenceFilter');
    
    if (searchInput) searchInput.value = '';
    if (statusFilter) statusFilter.value = 'all';
    if (confidenceFilter) confidenceFilter.value = 'all';
    
    applyFilters();
}

/**
 * Export results (handled by Flask backend)
 */
function exportResults() {
    // This function is defined in dashboard.html template
    // as it needs the batch_id from the template context
    console.log('Export triggered');
}

// Make functions available globally
window.nextPage = nextPage;
window.previousPage = previousPage;
window.sortTable = sortTable;
window.resetFilters = resetFilters;
window.applyFilters = applyFilters;

console.log('Dashboard JavaScript loaded');
