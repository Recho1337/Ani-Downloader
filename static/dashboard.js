// Dashboard JavaScript

async function loadDashboard() {
    try {
        // Load library stats
        const libraryResponse = await fetch('/api/library/list');
        const library = await libraryResponse.json();
        
        let totalAnime = 0;
        let totalEpisodes = 0;
        let totalSizeMB = 0;
        let recentItems = [];
        
        if (Array.isArray(library)) {
            // New API format returns array
            totalAnime = library.length;
            library.forEach(anime => {
                totalEpisodes += anime.total_files;
                totalSizeMB += anime.total_size_mb;
                
                recentItems.push({
                    name: anime.name,
                    episodes: anime.total_files,
                    size: anime.total_size_mb
                });
            });
        } else {
            // Old API format returns object
            for (const [animeName, data] of Object.entries(library)) {
                totalAnime++;
                totalEpisodes += data.total_files;
                totalSizeMB += data.total_size_mb;
                
                recentItems.push({
                    name: animeName,
                    episodes: data.total_files,
                    size: data.total_size_mb
                });
            }
        }
        
        // Update stats
        document.getElementById('totalAnime').textContent = totalAnime;
        document.getElementById('totalEpisodes').textContent = totalEpisodes;
        document.getElementById('totalSize').textContent = (totalSizeMB / 1024).toFixed(2) + ' GB';
        
        // Load active downloads
        const downloadsResponse = await fetch('/api/download/list');
        const downloads = await downloadsResponse.json();
        const activeDownloads = downloads.filter(d => 
            d.status === 'downloading' || 
            d.status === 'fetching_info' || 
            d.status === 'fetching_episodes' ||
            d.status === 'merging'
        ).length;
        
        document.getElementById('activeDownloads').textContent = activeDownloads;
        
        // Display active downloads
        const activeDownloadsList = document.getElementById('activeDownloadsList');
        const activeJobs = downloads.filter(d => 
            d.status === 'downloading' || 
            d.status === 'fetching_info' || 
            d.status === 'fetching_episodes' ||
            d.status === 'merging' ||
            d.status === 'initializing'
        );
        
        if (activeJobs.length === 0) {
            activeDownloadsList.innerHTML = '<div class="empty-state">No active downloads</div>';
        } else {
            activeDownloadsList.innerHTML = activeJobs.map(job => `
                <div class="job-card">
                    <div class="job-header">
                        <div class="job-title">${job.anime_title || 'Loading...'}</div>
                        <span class="status-badge status-${job.status}">${job.status.replace(/_/g, ' ')}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${job.progress}%"></div>
                    </div>
                    <div class="job-meta" style="margin-top: 8px; color: var(--text-muted); font-size: 0.9em;">
                        ${job.current_episode ? `Episode ${job.current_episode} • ` : ''}
                        ${job.completed_episodes}/${job.total_episodes} episodes
                    </div>
                </div>
            `).join('');
        }
        
        // Display recent downloads
        const recentList = document.getElementById('recentList');
        if (recentItems.length === 0) {
            recentList.innerHTML = '<div class="empty-state">No downloads yet. Start downloading anime!</div>';
        } else {
            recentList.innerHTML = recentItems.slice(0, 5).map(item => `
                <div class="anime-card">
                    <div class="anime-title">${item.name}</div>
                    <div class="anime-stats">
                        <span>🎬 ${item.episodes} episodes</span>
                        <span>💾 ${item.size.toFixed(2)} MB</span>
                    </div>
                </div>
            `).join('');
        }
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Load dashboard on page load
loadDashboard();

// Refresh every 3 seconds to show download progress
setInterval(loadDashboard, 3000);
