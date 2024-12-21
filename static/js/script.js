document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const progressContainer = document.querySelector('.progress-container');
    const progressBar = document.querySelector('.progress');
    const progressText = document.querySelector('.progress-text');
    const filesList = document.getElementById('filesList');
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.querySelector('.search-button');
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

    // Live search functionality
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const query = e.target.value;
            if (query.length >= 2) {
                performSearch(query);
            }
        }, 300);
    });

    searchButton.addEventListener('click', () => {
        const query = searchInput.value;
        if (query.length >= 2) {
            performSearch(query);
        }
    });

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

    // Handle search
    async function performSearch(query) {
        try {
            const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            updateSoftwareGrid(results);
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    // Update software grid with search results
    function updateSoftwareGrid(software) {
        const grid = document.querySelector('.software-grid');
        if (!grid) return;

        if (software.length === 0) {
            grid.innerHTML = '<div class="no-results">No software found matching your search.</div>';
            return;
        }

        grid.innerHTML = software.map(item => `
            <div class="software-card">
                <div class="software-image">
                    <img src="/static/images/${item.image}" alt="${item.name}">
                </div>
                <div class="software-info">
                    <h2>${item.name}</h2>
                    <div class="software-meta">
                        <span><i class="fas fa-code-branch"></i> ${item.version}</span>
                        <span><i class="fas fa-download"></i> ${item.size}</span>
                        <span><i class="fas fa-calendar"></i> ${item.date_added}</span>
                    </div>
                    <p class="software-description">${item.description}</p>
                    <div class="software-actions">
                        <a href="/download/${item.id}" class="download-button">
                            <i class="fas fa-download"></i> Download
                        </a>
                        <button class="info-button">
                            <i class="fas fa-info-circle"></i> Details
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

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
