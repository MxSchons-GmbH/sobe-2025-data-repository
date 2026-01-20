/**
 * Data Repository Page - State of Brain Emulation Report 2025
 * Displays categorized datasets with download links
 */

(function() {
    'use strict';

    // Configuration - can be overridden by setting window.DATA_CONFIG before this script loads
    const CONFIG = Object.assign({
        githubRepo: 'mxschons/sobe-2025-data-repository',
        githubBranch: 'main',
        metadataPath: 'metadata/data-metadata.json',
        fetchTimeout: 10000 // 10 seconds
    }, window.DATA_CONFIG || {});

    const GITHUB_BASE_URL = `https://github.com/${CONFIG.githubRepo}/blob/${CONFIG.githubBranch}`;

    // Fetch with timeout helper
    async function fetchWithTimeout(url, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.fetchTimeout);
        try {
            const response = await fetch(url, { ...options, signal: controller.signal });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response;
        } finally {
            clearTimeout(timeoutId);
        }
    }

    // State
    let currentView = 'table';
    let metadata = null;

    // DOM Elements
    const categoriesContainer = document.getElementById('data-categories');
    const totalDatasetsEl = document.getElementById('total-datasets');
    const totalCategoriesEl = document.getElementById('total-categories');

    // Icons for categories (simple SVG icons)
    const icons = {
        'cpu': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg>',
        'activity': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>',
        'share-2': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>',
        'dollar-sign': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>',
        'database': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>',
        'globe': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>',
        'archive': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="21 8 21 21 3 21 3 8"></polyline><rect x="1" y="3" width="22" height="5"></rect><line x1="10" y1="12" x2="14" y2="12"></line></svg>',
        'zap': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>',
        'file': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>',
        'rows': '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>',
        'download': '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>',
        'external': '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>'
    };

    // Initialize
    async function init() {
        try {
            const response = await fetchWithTimeout(CONFIG.metadataPath);
            metadata = await response.json();

            // Update stats
            const totalDatasets = metadata.categories.reduce((sum, cat) => sum + cat.datasets.length, 0);
            totalDatasetsEl.textContent = totalDatasets;
            totalCategoriesEl.textContent = metadata.categories.length;

            // Set up view toggle
            setupViewToggle();

            // Initial render
            render();

        } catch (error) {
            console.error('Failed to load data metadata:', error);
            categoriesContainer.innerHTML = `
                <div class="data-empty">
                    <p>Failed to load data catalog. Please try refreshing the page.</p>
                </div>
            `;
        }
    }

    // Set up view toggle buttons
    function setupViewToggle() {
        const buttons = document.querySelectorAll('.view-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentView = btn.dataset.view;
                render();
            });
        });
    }

    // Render based on current view
    function render() {
        if (currentView === 'table') {
            renderTableView(metadata.categories);
        } else {
            renderCardView(metadata.categories);
        }
    }

    // Render compact table view
    function renderTableView(categories) {
        categoriesContainer.innerHTML = categories.map(category => `
            <div class="data-category" id="category-${category.id}">
                <div class="category-header category-header-compact">
                    <div class="category-icon">
                        ${icons[category.icon] || icons['database']}
                    </div>
                    <div class="category-info">
                        <h2>${category.title}</h2>
                    </div>
                    <span class="category-count">${category.datasets.length}</span>
                </div>
                <table class="datasets-table">
                    <thead>
                        <tr>
                            <th>Dataset</th>
                            <th>Description</th>
                            <th>Rows</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${category.datasets.map(dataset => renderTableRow(dataset)).join('')}
                    </tbody>
                </table>
            </div>
        `).join('');
    }

    // Render a single table row
    function renderTableRow(dataset) {
        const downloadPath = `${dataset.path}/${encodeURIComponent(dataset.filename)}`;
        const githubPath = `${GITHUB_BASE_URL}/${dataset.path}/${encodeURIComponent(dataset.filename)}`;

        return `
            <tr class="dataset-row">
                <td class="dataset-name">
                    <span class="dataset-title-text">${dataset.title}</span>
                </td>
                <td class="dataset-desc">${dataset.description}</td>
                <td class="dataset-rows">${dataset.rows}</td>
                <td class="dataset-actions-cell">
                    <a href="${downloadPath}" class="btn-icon" title="Download CSV" download>
                        ${icons['download']}
                    </a>
                    <a href="${githubPath}" class="btn-icon" title="View on GitHub" target="_blank" rel="noopener">
                        ${icons['external']}
                    </a>
                </td>
            </tr>
        `;
    }

    // Render card view (original)
    function renderCardView(categories) {
        categoriesContainer.innerHTML = categories.map(category => `
            <div class="data-category" id="category-${category.id}">
                <div class="category-header">
                    <div class="category-icon">
                        ${icons[category.icon] || icons['database']}
                    </div>
                    <div class="category-info">
                        <h2>${category.title}</h2>
                        <p>${category.description}</p>
                    </div>
                    <span class="category-count">${category.datasets.length} dataset${category.datasets.length !== 1 ? 's' : ''}</span>
                </div>
                <div class="datasets-grid">
                    ${category.datasets.map(dataset => renderDatasetCard(dataset)).join('')}
                </div>
            </div>
        `).join('');
    }

    // Render a single dataset card
    function renderDatasetCard(dataset) {
        const downloadPath = `${dataset.path}/${encodeURIComponent(dataset.filename)}`;
        const githubPath = `${GITHUB_BASE_URL}/${dataset.path}/${encodeURIComponent(dataset.filename)}`;
        const columnsPreview = dataset.columns.slice(0, 5).join(', ') + (dataset.columns.length > 5 ? '...' : '');

        return `
            <div class="dataset-card">
                <h3 class="dataset-title">
                    ${icons['file']}
                    ${dataset.title}
                </h3>
                <p class="dataset-description">${dataset.description}</p>
                <div class="dataset-meta">
                    <span class="dataset-meta-item">
                        ${icons['rows']}
                        ${dataset.rows} rows
                    </span>
                    <span class="dataset-meta-item">
                        CSV
                    </span>
                </div>
                <div class="dataset-columns" title="${dataset.columns.join(', ')}">
                    ${columnsPreview}
                </div>
                <div class="dataset-actions">
                    <a href="${downloadPath}" class="btn btn-primary" download>
                        ${icons['download']}
                        Download CSV
                    </a>
                    <a href="${githubPath}" class="btn btn-outline" target="_blank" rel="noopener">
                        ${icons['external']}
                        View on GitHub
                    </a>
                </div>
            </div>
        `;
    }

    // Start
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
