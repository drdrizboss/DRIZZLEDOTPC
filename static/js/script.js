// Make searchSoftware function globally accessible
function searchSoftware() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const query = searchInput.value.trim();
    
    if (!query) {
        window.location.href = '/';
        return;
    }
    
    // Show loading state
    const originalContent = searchButton.innerHTML;
    searchButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    // Perform the search
    window.location.href = `/search?q=${encodeURIComponent(query)}`;
}

document.addEventListener('DOMContentLoaded', function() {
    // Get search elements
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');

    // Function to perform search
    function performSearch() {
        const query = searchInput.value.trim();
        if (query) {
            window.location.href = '/search?q=' + encodeURIComponent(query);
        }
    }

    // Add event listener for Enter key
    searchInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            performSearch();
        }
    });

    // Add event listener for search button click
    searchButton.addEventListener('click', function() {
        performSearch();
    });

    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const progressContainer = document.querySelector('.progress-container');
    const progressBar = document.querySelector('.progress');
    const progressText = document.querySelector('.progress-text');
    const filesList = document.getElementById('filesList');
    let searchTimeout;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFiles, false);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropZone.classList.add('highlight');
    }

    function unhighlight(e) {
        dropZone.classList.remove('highlight');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles({ target: { files } });
    }

    function handleFiles(e) {
        const files = [...e.target.files];
        files.forEach(uploadFile);
        fileInput.value = ''; // Reset file input
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        progressContainer.hidden = false;
        progressBar.style.width = '0%';
        progressText.textContent = '0%';

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            progressBar.style.width = '100%';
            progressText.textContent = '100%';
            setTimeout(() => {
                progressContainer.hidden = true;
                loadFiles(); // Refresh the files list
            }, 1000);
        })
        .catch(error => {
            console.error('Error:', error);
            progressContainer.hidden = true;
            alert('Upload failed. Please try again.');
        });
    }

    function loadFiles() {
        fetch('/files')
            .then(response => response.json())
            .then(files => {
                filesList.innerHTML = '';
                files.forEach(file => {
                    const li = document.createElement('li');
                    li.textContent = file.name;
                    filesList.appendChild(li);
                });
            })
            .catch(error => console.error('Error loading files:', error));
    }

    // Update software grid with search results
    function updateSoftwareGrid(software) {
        const grid = document.querySelector('.software-grid');
        if (!grid) return;

        if (!software || software.length === 0) {
            grid.innerHTML = '<div class="no-results">No software found matching your search.</div>';
            return;
        }

        grid.innerHTML = software.map(item => `
            <div class="software-card">
                <div class="software-info">
                    <div class="card">
                        <div class="downloads-badge">
                            <i class="fas fa-download"></i> ${item.downloads}+ Downloads
                        </div>
                        ${item.image_url ? `
                            <div class="card-image">
                                <img src="${item.image_url}" 
                                     alt="${item.name}" 
                                     loading="lazy"
                                     onerror="handleImageError(this)"
                                     data-fallback="/static/img/placeholder.jpg">
                            </div>
                        ` : ''}
                        <div class="card-content">
                            <h2>${item.name}</h2>
                            <div class="meta-info">
                                <span class="version">Version: ${item.version}</span>
                                <span class="size">Size: ${item.size}</span>
                                <span class="category">Category: ${item.category}</span>
                            </div>
                            ${item.genre ? `
                                <div class="genre-tags">
                                    ${item.genre.map(g => `<span class="genre-tag">${g}</span>`).join('')}
                                </div>
                            ` : ''}
                            <div class="description-container">
                                <div class="description-preview">${item.description.slice(0, 150)}${item.description.length > 150 ? '...' : ''}</div>
                                ${item.description.length > 150 ? `
                                    <div class="description-full" style="display: none;">
                                        ${item.description}
                                    </div>
                                    <button class="show-more-btn" onclick="toggleDescription(this)">Show More</button>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Image handling
    function handleImageError(img) {
        const container = img.parentElement;
        
        // Try fallback image first
        if (img.dataset.fallback && img.src !== img.dataset.fallback) {
            img.src = img.dataset.fallback;
            return;
        }

        // If fallback fails, show error state
        container.classList.add('error');
        container.classList.remove('loading');
        img.style.display = 'none';
    }

    // Add loading class to all image containers
    const imageContainers = document.querySelectorAll('.card-image');
    imageContainers.forEach(container => {
        if (container.querySelector('img')) {
            container.classList.add('loading');
        }
    });

    // Info button click handler
    document.addEventListener('click', (e) => {
        if (e.target.closest('.info-button')) {
            const card = e.target.closest('.software-card');
            const title = card.querySelector('h2').textContent;
            const description = card.querySelector('.software-description').textContent;
            
            // Here you could show a modal with more details
            alert(`${title}\n\n${description}`);
        }
    });

    // Add smooth scrolling for navigation links
    document.querySelectorAll('nav a').forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                document.querySelector(href).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add animation on scroll for software cards
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.software-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease-out';
        observer.observe(card);
    });

    // Initial load of files
    loadFiles();
});
