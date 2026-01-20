/**
 * Figure Library - State of Brain Emulation Report 2025
 * Interactive filtering and display of report figures
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = Object.assign({
        fetchTimeout: 10000, // 10 seconds
        metadataPath: 'metadata/figures-metadata.json',
        handDrawnMetadataPath: 'metadata/hand-drawn-metadata.json'
    }, window.FIGURES_CONFIG || {});

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
    let allFigures = [];
    let metadata = null;
    let activeFilters = {
        organism: 'all',
        type: 'all',
        source: 'all'
    };

    // DOM Elements
    const figuresGrid = document.getElementById('figures-grid');
    const organismFilters = document.getElementById('organism-filters');
    const typeFilters = document.getElementById('type-filters');
    const sourceFilters = document.getElementById('source-filters');
    const resultsCount = document.getElementById('results-count');
    const modal = document.getElementById('figure-modal');

    // Initialize
    async function init() {
        try {
            // Load both metadata files
            const [generatedMeta, handDrawnMeta] = await Promise.all([
                fetchWithTimeout(CONFIG.metadataPath).then(r => r.json()),
                fetchWithTimeout(CONFIG.handDrawnMetadataPath).then(r => r.json()).catch(() => ({ figures: [] }))
            ]);

            metadata = generatedMeta;

            // Process generated figures
            // path = directory, filename = base name (no extension)
            const generatedFigures = generatedMeta.figures.map(fig => ({
                ...fig,
                source: 'generated',
                pngPath: `${fig.path}/${encodeURIComponent(fig.filename)}.png`,
                svgPath: `${fig.path}/${encodeURIComponent(fig.filename)}.svg`
            }));

            // Process hand-drawn figures (filter out example/template entries)
            const handDrawnFigures = handDrawnMeta.figures
                .filter(fig => fig.id !== 'example-hand-drawn')
                .map(fig => ({
                    ...fig,
                    source: 'hand-drawn',
                    pngPath: `figures/hand-drawn/${encodeURIComponent(fig.filename)}.png`,
                    svgPath: `figures/hand-drawn/${encodeURIComponent(fig.filename)}.svg`,
                    type: [...(fig.type || []), 'hand-drawn']
                }));

            allFigures = [...generatedFigures, ...handDrawnFigures];

            // Build filter UI
            buildFilters();

            // Initial render
            renderFigures();

            // Set up event listeners
            setupEventListeners();

        } catch (error) {
            console.error('Failed to load figure metadata:', error);
            figuresGrid.innerHTML = `
                <div class="figures-empty">
                    <div class="figures-empty-icon">⚠️</div>
                    <h3>Failed to load figures</h3>
                    <p>Please try refreshing the page.</p>
                </div>
            `;
        }
    }

    // Build filter chips from metadata
    function buildFilters() {
        // Organism filters
        metadata.organisms.forEach(org => {
            if (org.id === 'all') return; // Already have "All" button
            const chip = createFilterChip(org.id, org.label, 'organism');
            organismFilters.appendChild(chip);
        });

        // Type filters - collect unique types from actual figures
        const usedTypes = new Set();
        allFigures.forEach(fig => {
            fig.type.forEach(t => usedTypes.add(t));
        });

        metadata.types
            .filter(t => usedTypes.has(t.id))
            .forEach(type => {
                const chip = createFilterChip(type.id, type.label, 'type');
                typeFilters.appendChild(chip);
            });
    }

    // Create a filter chip button
    function createFilterChip(id, label, filterType) {
        const chip = document.createElement('button');
        chip.className = 'filter-chip';
        chip.dataset.filter = id;
        chip.textContent = label;
        chip.addEventListener('click', () => handleFilterClick(chip, filterType));
        return chip;
    }

    // Handle filter chip clicks
    function handleFilterClick(chip, filterType) {
        const container = chip.parentElement;
        const filterId = chip.dataset.filter;

        // Update active state
        container.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');

        // Update filter state
        activeFilters[filterType] = filterId;

        // Re-render
        renderFigures();
    }

    // Filter figures based on active filters
    function getFilteredFigures() {
        return allFigures.filter(fig => {
            // Source filter
            if (activeFilters.source !== 'all' && fig.source !== activeFilters.source) {
                return false;
            }

            // Organism filter
            if (activeFilters.organism !== 'all') {
                const hasOrganism = fig.organism.includes(activeFilters.organism) ||
                                   fig.organism.includes('all');
                if (!hasOrganism) return false;
            }

            // Type filter
            if (activeFilters.type !== 'all') {
                if (!fig.type.includes(activeFilters.type)) return false;
            }

            return true;
        });
    }

    // Render figures grid
    function renderFigures() {
        const filtered = getFilteredFigures();
        resultsCount.textContent = filtered.length;

        if (filtered.length === 0) {
            figuresGrid.innerHTML = `
                <div class="figures-empty">
                    <div class="figures-empty-icon">🔍</div>
                    <h3>No figures found</h3>
                    <p>Try adjusting your filters to see more results.</p>
                </div>
            `;
            return;
        }

        figuresGrid.innerHTML = filtered.map(fig => createFigureCard(fig)).join('');

        // Add click handlers
        figuresGrid.querySelectorAll('.figure-card').forEach(card => {
            card.addEventListener('click', (e) => {
                // Don't open modal if clicking download buttons
                if (e.target.closest('.figure-card-actions')) return;
                const figureId = card.dataset.id;
                const figure = allFigures.find(f => f.id === figureId);
                if (figure) openModal(figure);
            });
        });
    }

    // Create figure card HTML
    function createFigureCard(fig) {
        const isHandDrawn = fig.source === 'hand-drawn';
        const organismTags = fig.organism
            .filter(o => o !== 'all')
            .map(o => {
                const org = metadata.organisms.find(m => m.id === o);
                return `<span class="figure-tag organism">${org ? org.label : o}</span>`;
            })
            .join('');

        const typeTags = fig.type
            .filter(t => t !== 'hand-drawn' && t !== 'organism-specific')
            .slice(0, 2)
            .map(t => {
                const type = metadata.types.find(m => m.id === t);
                return `<span class="figure-tag">${type ? type.label : t}</span>`;
            })
            .join('');

        return `
            <article class="figure-card ${isHandDrawn ? 'hand-drawn' : ''}" data-id="${fig.id}">
                <div class="figure-card-image">
                    ${isHandDrawn ? '<span class="figure-card-badge">Hand-Drawn</span>' : ''}
                    <img src="${fig.pngPath}" alt="${fig.title}" loading="lazy">
                </div>
                <div class="figure-card-content">
                    <h3 class="figure-card-title">${fig.title}</h3>
                    <p class="figure-card-description">${fig.description}</p>
                    <div class="figure-card-tags">
                        ${organismTags}
                        ${typeTags}
                    </div>
                    <div class="figure-card-actions">
                        <a href="${fig.pngPath}" class="btn btn-small btn-secondary" download onclick="event.stopPropagation()">PNG</a>
                        <a href="${fig.svgPath}" class="btn btn-small btn-secondary" download onclick="event.stopPropagation()">SVG</a>
                    </div>
                </div>
            </article>
        `;
    }

    // Modal functions
    function openModal(figure) {
        const modalImage = document.getElementById('modal-image');
        const modalTitle = document.getElementById('modal-title');
        const modalDescription = document.getElementById('modal-description');
        const modalTags = document.getElementById('modal-tags');
        const modalDownloadPng = document.getElementById('modal-download-png');
        const modalDownloadSvg = document.getElementById('modal-download-svg');

        modalImage.src = figure.pngPath;
        modalImage.alt = figure.title;
        modalTitle.textContent = figure.title;
        modalDescription.textContent = figure.description;

        // Build tags
        const allTags = [
            ...figure.organism.filter(o => o !== 'all').map(o => {
                const org = metadata.organisms.find(m => m.id === o);
                return `<span class="figure-tag organism">${org ? org.label : o}</span>`;
            }),
            ...figure.type.map(t => {
                const type = metadata.types.find(m => m.id === t);
                return `<span class="figure-tag">${type ? type.label : t}</span>`;
            })
        ];
        modalTags.innerHTML = allTags.join('');

        // Set download links
        modalDownloadPng.href = figure.pngPath;
        modalDownloadSvg.href = figure.svgPath;

        // Show modal
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    // Event listeners
    function setupEventListeners() {
        // Source filter clicks
        sourceFilters.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', () => handleFilterClick(chip, 'source'));
        });

        // Modal close
        modal.querySelector('.modal-close').addEventListener('click', closeModal);
        modal.querySelector('.modal-backdrop').addEventListener('click', closeModal);

        // Escape key closes modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.getAttribute('aria-hidden') === 'false') {
                closeModal();
            }
        });
    }

    // Start
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
