// Library JavaScript

async function loadLibrary() {
    try {
        const response = await fetch('/api/library/list');
        const library = await response.json();
        
        const container = document.getElementById('libraryContainer');
        
        if (Object.keys(library).length === 0) {
            container.innerHTML = '<div class="empty-state">Your library is empty. Download some anime to get started!</div>';
            return;
        }
        
        let html = '<div class="anime-grid">';
        
        for (const [animeName, data] of Object.entries(library)) {
            html += `
                <div class="anime-card">
                    <div class="anime-title">${animeName}</div>
                    <div class="anime-stats">
                        <span>🎬 ${data.total_files} files</span>
                        <span>💾 ${data.total_size_mb.toFixed(2)} MB</span>
                    </div>
                    <div class="file-list">
                        ${data.files.map(file => `
                            <div class="file-item">
                                <span class="file-name" title="${file.name}">${file.name}</span>
                                <span class="file-size">${file.size_mb} MB</span>
                                <a href="/api/download/file/${encodeURIComponent(file.name)}" 
                                   class="btn btn-success" 
                                   style="padding: 6px 12px; font-size: 0.85rem;">
                                    ⬇️ Download
                                </a>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading library:', error);
        document.getElementById('libraryContainer').innerHTML = 
            '<div class="empty-state">Error loading library. Please try again.</div>';
    }
}

// Load library on page load
loadLibrary();

// Refresh every 30 seconds
setInterval(loadLibrary, 30000);
