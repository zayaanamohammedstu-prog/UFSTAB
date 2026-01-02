/**
 * Tournament Customization and Import Functionality
 * Handles tournament customization settings and bulk data import
 */

// Initialize customization and import event listeners
document.addEventListener('DOMContentLoaded', () => {
    const customizeForm = document.getElementById('customizeForm');
    const importForm = document.getElementById('importForm');
    
    if (customizeForm) {
        customizeForm.addEventListener('submit', handleCustomizationSubmit);
    }
    
    if (importForm) {
        importForm.addEventListener('submit', handleImportSubmit);
    }
});

/**
 * Handle tournament customization form submission
 */
async function handleCustomizationSubmit(e) {
    e.preventDefault();
    
    // Get current tournament ID from local storage
    const tournamentData = JSON.parse(localStorage.getItem('bpTournamentData') || '{}');
    const tournamentId = tournamentData.tournament?.id;
    
    if (!tournamentId) {
        showNotification('Please create a tournament first', 'error');
        return;
    }
    
    const customLogoUrl = document.getElementById('customLogoUrl').value;
    const primaryColor = document.getElementById('primaryColor').value;
    const secondaryColor = document.getElementById('secondaryColor').value;
    const showPublicTab = document.getElementById('showPublicTab').checked;
    
    const customizationData = {
        custom_logo_url: customLogoUrl || null,
        primary_color: primaryColor,
        secondary_color: secondaryColor,
        show_public_tab: showPublicTab
    };
    
    try {
        // If OratorHub API client is available, use it
        if (window.OratorHub && window.OratorHub.api && window.OratorHub.tournaments) {
            const response = await OratorHub.tournaments.update(tournamentId, customizationData);
            
            if (response.tournament) {
                // Update local storage
                const updatedTournamentData = { ...tournamentData };
                updatedTournamentData.tournament = { ...updatedTournamentData.tournament, ...response.tournament };
                localStorage.setItem('bpTournamentData', JSON.stringify(updatedTournamentData));
                
                // Show public URL if enabled
                if (showPublicTab && response.tournament.slug) {
                    const publicUrl = `${window.location.origin}/public-display?slug=${response.tournament.slug}`;
                    document.getElementById('publicUrl').value = publicUrl;
                    document.getElementById('publicUrlDisplay').style.display = 'block';
                }
                
                showNotification('Customization saved successfully!', 'success');
            }
        } else {
            // Fallback: store in local storage only
            const updatedTournamentData = { ...tournamentData };
            updatedTournamentData.tournament = { 
                ...updatedTournamentData.tournament, 
                ...customizationData 
            };
            localStorage.setItem('bpTournamentData', JSON.stringify(updatedTournamentData));
            showNotification('Customization saved locally', 'success');
        }
        
    } catch (error) {
        console.error('Error saving customization:', error);
        showNotification('Failed to save customization: ' + error.message, 'error');
    }
}

/**
 * Copy public URL to clipboard
 */
function copyPublicUrl() {
    const publicUrlInput = document.getElementById('publicUrl');
    const url = publicUrlInput.value;
    
    // Use modern Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(url).then(() => {
            showNotification('Public URL copied to clipboard!', 'success');
        }).catch(() => {
            // Fallback to older method
            copyToClipboardFallback(publicUrlInput);
        });
    } else {
        // Fallback for older browsers or non-secure contexts
        copyToClipboardFallback(publicUrlInput);
    }
}

/**
 * Fallback method for copying to clipboard
 */
function copyToClipboardFallback(input) {
    input.select();
    input.setSelectionRange(0, 99999); // For mobile devices
    
    try {
        document.execCommand('copy');
        showNotification('Public URL copied to clipboard!', 'success');
    } catch (err) {
        showNotification('Failed to copy URL. Please copy manually.', 'error');
    }
}

/**
 * Handle import form submission
 */
async function handleImportSubmit(e) {
    e.preventDefault();
    
    // Get current tournament ID
    const tournamentData = JSON.parse(localStorage.getItem('bpTournamentData') || '{}');
    const tournamentId = tournamentData.tournament?.id;
    
    if (!tournamentId) {
        showNotification('Please create a tournament first', 'error');
        return;
    }
    
    const fileInput = document.getElementById('importFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Please select a file to import', 'error');
        return;
    }
    
    // Check file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
        showNotification('File size exceeds 10MB limit', 'error');
        return;
    }
    
    try {
        showNotification('Importing data...', 'info');
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        
        // Check if API client is available
        if (window.OratorHub && window.OratorHub.api) {
            const token = localStorage.getItem('auth_token');
            
            if (!token) {
                showNotification('Please login to import data', 'error');
                return;
            }
            
            // Make API call
            const response = await fetch(`/api/registrations/tournament/${tournamentId}/import`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Import failed');
            }
            
            // Display results
            displayImportResults(result);
            
            // Clear file input
            fileInput.value = '';
            
        } else {
            // Fallback: Parse CSV locally (basic implementation)
            if (file.name.endsWith('.csv')) {
                const text = await file.text();
                const result = await parseCSVLocally(text, tournamentId);
                displayImportResults(result);
                fileInput.value = '';
            } else {
                showNotification('Excel import requires backend API. Please use CSV format or login.', 'error');
            }
        }
        
    } catch (error) {
        console.error('Error importing data:', error);
        showNotification('Import failed: ' + error.message, 'error');
    }
}

/**
 * Parse CSV file locally (fallback when API is not available)
 */
async function parseCSVLocally(csvText, tournamentId) {
    const lines = csvText.split('\n');
    if (lines.length < 2) {
        throw new Error('CSV file is empty or invalid');
    }
    
    // Parse header
    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
    const emailIndex = headers.findIndex(h => h.includes('email'));
    
    if (emailIndex === -1) {
        throw new Error('Email column not found in CSV');
    }
    
    let importedCount = 0;
    const errors = [];
    
    // Get existing data
    const tournamentData = JSON.parse(localStorage.getItem('bpTournamentData') || '{}');
    if (!tournamentData.registrations) {
        tournamentData.registrations = [];
    }
    
    // Parse rows
    for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        
        const values = lines[i].split(',').map(v => v.trim());
        const email = values[emailIndex];
        
        if (!email) {
            errors.push(`Row ${i + 1}: Missing email`);
            continue;
        }
        
        // Check for duplicates
        if (tournamentData.registrations.some(r => r.email === email)) {
            errors.push(`Row ${i + 1}: ${email} already registered`);
            continue;
        }
        
        // Add registration
        tournamentData.registrations.push({
            id: Date.now() + importedCount,
            email: email,
            name: values[headers.findIndex(h => h.includes('name'))] || email.split('@')[0],
            tournament_id: tournamentId,
            status: 'confirmed',
            created_at: new Date().toISOString()
        });
        
        importedCount++;
    }
    
    // Save to local storage
    localStorage.setItem('bpTournamentData', JSON.stringify(tournamentData));
    
    return {
        message: `Import completed. ${importedCount} registrations imported.`,
        imported_count: importedCount,
        errors: errors
    };
}

/**
 * Display import results
 */
function displayImportResults(result) {
    const resultsDiv = document.getElementById('importResults');
    const resultsContent = document.getElementById('importResultsContent');
    
    let html = `<p style="color: var(--success); font-weight: 600;">${result.message}</p>`;
    
    if (result.errors && result.errors.length > 0) {
        html += `
            <div style="margin-top: 1rem; padding: 1rem; background: #fee; border-radius: 0.5rem;">
                <h5 style="margin-top: 0; color: #c33;">Errors (${result.errors.length}):</h5>
                <ul style="margin: 0; padding-left: 1.5rem; max-height: 200px; overflow-y: auto;">
                    ${result.errors.map(err => `<li>${err}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    resultsContent.innerHTML = html;
    resultsDiv.style.display = 'block';
    
    showNotification(`Successfully imported ${result.imported_count} registrations`, 'success');
}

/**
 * Show notification (using existing notification system if available)
 */
function showNotification(message, type = 'info') {
    // Check if global notification function exists
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
        return;
    }
    
    // Fallback: simple alert
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Create a simple notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        background: ${type === 'error' ? '#fee' : type === 'success' ? '#efe' : '#eef'};
        color: ${type === 'error' ? '#c33' : type === 'success' ? '#3c3' : '#33c'};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 10000;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Make functions globally accessible
window.copyPublicUrl = copyPublicUrl;
