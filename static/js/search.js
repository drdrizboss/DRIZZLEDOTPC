document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const searchStatus = document.getElementById('searchStatus');
    const softwareGrid = document.querySelector('.software-grid');
    let currentSearchRequest = null;

    function updateSearchStatus(message, isError = false) {
        if (!searchStatus) return;
        searchStatus.textContent = message;
        searchStatus.className = `search-status ${isError ? 'error' : ''}`;
        searchStatus.style.display = message ? 'block' : 'none';
    }

    async function performSearch(e) {
        if (e) e.preventDefault();
        
        try {
            const query = searchInput.value.trim();

            // Validate input
            if (!query) {
                updateSearchStatus('Please enter a search term', true);
                return;
            }

            if (query.length < 2) {
                updateSearchStatus('Please enter at least 2 characters', true);
                return;
            }

            // Cancel any pending request
            if (currentSearchRequest) {
                currentSearchRequest.abort();
            }

            // Update UI state
            searchButton.disabled = true;
            updateSearchStatus('Searching...');
            softwareGrid.innerHTML = '<div class="loading">Searching...</div>';

            // Create AbortController for this request
            const controller = new AbortController();
            currentSearchRequest = controller;

            // Make API call to search endpoint
            const response = await fetch(`/search?q=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                },
                signal: controller.signal
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }

            if (data.status === 'error') {
                throw new Error(data.message || 'Server error');
            }

            const results = data.results || [];
            const resultCount = data.count || 0;

            // Update status
            updateSearchStatus(
                resultCount > 0 
                    ? `Found ${resultCount} result${resultCount !== 1 ? 's' : ''}`
                    : 'No results found'
            );

            // Display results
            if (resultCount === 0) {
                softwareGrid.innerHTML = `
                    <div class="no-results">
                        <h2>No results found for "${query}"</h2>
                        <p>Try different keywords or browse our categories</p>
                    </div>
                `;
                return;
            }

            // Build HTML for results
            const resultsHTML = results.map((software, index) => `
                <div class="software-card" data-category="${software.category || ''}" data-name="${software.name || ''}">
                    <div class="software-info">
                        <div class="card">
                            <div class="card-image ${!software.image_url ? 'no-image' : 'loading'}" id="search-img-${index}">
                                ${software.image_url ? `
                                <img src="${software.image_url}" 
                                     alt="${software.name}" 
                                     loading="lazy"
                                     onload="this.parentElement.classList.remove('loading')"
                                     onerror="handleImageError(this)"
                                     data-fallback="/static/img/placeholder.jpg">
                                ` : ''}
                            </div>
                            <div class="card-content">
                                <div class="card-header">
                                    <h2>${software.name}</h2>
                                    <div class="downloads-badge">
                                        <i class="fas fa-download"></i> ${software.downloads || 0}+ Downloads
                                    </div>
                                </div>
                                <div class="meta-info">
                                    ${software.version ? `<span class="version">Version: ${software.version}</span>` : ''}
                                    ${software.size ? `<span class="size">Size: ${software.size}</span>` : ''}
                                    ${software.category ? `<span class="category">Category: ${software.category}</span>` : ''}
                                </div>
                                ${software.genre ? `
                                <div class="genre-tags">
                                    ${software.genre.map(genre => `
                                        <span class="genre-tag">${genre}</span>
                                    `).join('')}
                                </div>
                                ` : ''}
                                <div class="description-container">
                                    <div class="description-preview">${software.description ? software.description.slice(0, 150) + (software.description.length > 150 ? '...' : '') : ''}</div>
                                    ${software.description && software.description.length > 150 ? `
                                    <div class="description-full" style="display: none;">
                                        ${software.description}
                                    </div>
                                    <button class="show-more-btn" onclick="toggleDescription(this)">Show More</button>
                                    ` : ''}
                                </div>
                                <div class="card-actions">
                                    ${software.download_links ? Object.entries(software.download_links).map(([platform, url]) => `
                                        <a href="${url}" class="download-btn ${platform.toLowerCase()}-btn" target="_blank" rel="noopener">
                                            <i class="fas fa-download"></i> Download (${platform.charAt(0).toUpperCase() + platform.slice(1)})
                                        </a>
                                    `).join('') : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');

            softwareGrid.innerHTML = resultsHTML;

        } catch (error) {
            if (error.name === 'AbortError') {
                // Request was aborted, do nothing
                return;
            }

            console.error('Search error:', error);
            updateSearchStatus(error.message || 'An error occurred while searching', true);
            softwareGrid.innerHTML = `
                <div class="error" style="text-align: center; padding: 20px;">
                    <h2 style="color: #ff4444;">An error occurred while searching</h2>
                    <p style="color: #ccc;">${error.message || 'Please try again later'}</p>
                </div>
            `;
        } finally {
            searchButton.disabled = false;
            currentSearchRequest = null;
        }
    }

    // Handle form submission (button click or Enter key)
    if (searchForm) {
        searchForm.addEventListener('submit', performSearch);
    }

    // Handle input changes - just clear any error messages
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            updateSearchStatus('');
        });

        // Clear status when input is focused
        searchInput.addEventListener('focus', function() {
            updateSearchStatus('');
        });
    }
});
