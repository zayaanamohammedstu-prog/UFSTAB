// Data Storage
let tournamentData = {
    tournament: null,
    teams: [],
    adjudicators: [],
    venues: [],
    rounds: [],
    results: {}
};

let publicSpeakingData = {
    event: null,
    speakers: [],
    judges: [],
    scores: {}
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    try {
        loadData();
        initializeEventListeners();
        initializeTheme();
        updateRoundSelectors();
    } catch (error) {
        console.error('Error initializing application:', error);
        showNotification('Error loading application. Please refresh the page.', 'error');
    }
});

/**
 * Initialize all event listeners for the application
 * Sets up navigation, tabs, theme toggle, and form submissions
 */
function initializeEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const page = btn.dataset.page;
            showPage(page);
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // Tab Navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tab = btn.dataset.tab;
            const subtab = btn.dataset.subtab;
            
            if (subtab) {
                // Handle sub-tabs
                const parent = btn.closest('.card');
                parent.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                parent.querySelectorAll('.subtab-content').forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                parent.querySelector(`#${subtab}`).classList.add('active');
            } else {
                // Handle main tabs
                const page = btn.closest('.page');
                page.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                page.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                page.querySelector(`#${tab}`).classList.add('active');
            }
        });
    });

    // Theme Toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);

    // Theme Radio Buttons
    document.querySelectorAll('input[name="theme"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'dark') {
                document.body.classList.add('dark-theme');
                document.getElementById('themeToggle').querySelector('.theme-icon').textContent = '☀️';
            } else {
                document.body.classList.remove('dark-theme');
                document.getElementById('themeToggle').querySelector('.theme-icon').textContent = '🌙';
            }
            localStorage.setItem('theme', e.target.value);
        });
    });

    // Forms
    document.getElementById('tournamentForm').addEventListener('submit', saveTournament);
    document.getElementById('addTeamForm').addEventListener('submit', addTeam);
    document.getElementById('addAdjudicatorForm').addEventListener('submit', addAdjudicator);
    document.getElementById('addVenueForm').addEventListener('submit', addVenue);
    document.getElementById('psEventForm').addEventListener('submit', savePSEvent);
    document.getElementById('addPSSpeakerForm').addEventListener('submit', addPSSpeaker);
    document.getElementById('addPSJudgeForm').addEventListener('submit', addPSJudge);
}

// Page Navigation
function showPage(pageName) {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById(pageName).classList.add('active');
}

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        document.getElementById('themeToggle').querySelector('.theme-icon').textContent = '☀️';
        document.querySelector('input[name="theme"][value="dark"]').checked = true;
    }
}

function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    document.getElementById('themeToggle').querySelector('.theme-icon').textContent = isDark ? '☀️' : '🌙';
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    document.querySelector(`input[name="theme"][value="${isDark ? 'dark' : 'light'}"]`).checked = true;
}

// BP Debate - Tournament Management
function saveTournament(e) {
    e.preventDefault();
    tournamentData.tournament = {
        name: document.getElementById('tournamentName').value,
        date: document.getElementById('tournamentDate').value,
        rounds: parseInt(document.getElementById('numRounds').value),
        venue: document.getElementById('tournamentVenue').value
    };
    
    displayTournamentInfo();
    updateRoundSelectors();
    saveData();
    showNotification('Tournament saved successfully!', 'success');
}

function displayTournamentInfo() {
    const info = tournamentData.tournament;
    if (info) {
        document.getElementById('tournamentInfo').style.display = 'block';
        document.getElementById('infoName').textContent = info.name;
        document.getElementById('infoDate').textContent = new Date(info.date).toLocaleDateString();
        document.getElementById('infoRounds').textContent = info.rounds;
        document.getElementById('infoVenue').textContent = info.venue || 'Not specified';
    }
}

function updateRoundSelectors() {
    const rounds = tournamentData.tournament?.rounds || 1;
    const selectors = [document.getElementById('roundSelect'), document.getElementById('resultsRoundSelect')];
    
    selectors.forEach(selector => {
        if (selector) {
            selector.innerHTML = '';
            for (let i = 1; i <= rounds; i++) {
                const option = document.createElement('option');
                option.value = i;
                option.textContent = `Round ${i}`;
                selector.appendChild(option);
            }
        }
    });
}

// BP Debate - Team Management
function showTeamForm() {
    document.getElementById('teamForm').style.display = 'block';
}

function hideTeamForm() {
    document.getElementById('teamForm').style.display = 'none';
    document.getElementById('addTeamForm').reset();
}

function addTeam(e) {
    e.preventDefault();
    const team = {
        id: Date.now(),
        name: document.getElementById('teamName').value,
        institution: document.getElementById('teamInstitution').value,
        speakers: [
            document.getElementById('speaker1').value,
            document.getElementById('speaker2').value
        ],
        points: 0,
        wins: 0,
        speakerPoints: 0
    };
    
    tournamentData.teams.push(team);
    displayTeams();
    hideTeamForm();
    saveData();
    showNotification('Team added successfully!', 'success');
}

function displayTeams() {
    const tbody = document.getElementById('teamsTableBody');
    tbody.innerHTML = '';
    
    if (tournamentData.teams.length === 0) {
        tbody.innerHTML = '<tr class="empty-state"><td colspan="5">No teams registered yet. Click "Add Team" to get started.</td></tr>';
        return;
    }
    
    tournamentData.teams.forEach(team => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${team.name}</td>
            <td>${team.institution}</td>
            <td>${team.speakers[0]}</td>
            <td>${team.speakers[1]}</td>
            <td>
                <button class="btn btn-secondary action-btn" onclick="editTeam(${team.id})">Edit</button>
                <button class="btn btn-danger action-btn" onclick="deleteTeam(${team.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function deleteTeam(id) {
    if (confirm('Are you sure you want to delete this team?')) {
        tournamentData.teams = tournamentData.teams.filter(t => t.id !== id);
        displayTeams();
        saveData();
        showNotification('Team deleted successfully!', 'success');
    }
}

// BP Debate - Adjudicator Management
function showAdjudicatorForm() {
    document.getElementById('adjudicatorForm').style.display = 'block';
}

function hideAdjudicatorForm() {
    document.getElementById('adjudicatorForm').style.display = 'none';
    document.getElementById('addAdjudicatorForm').reset();
}

function addAdjudicator(e) {
    e.preventDefault();
    const adjudicator = {
        id: Date.now(),
        name: document.getElementById('adjName').value,
        institution: document.getElementById('adjInstitution').value,
        rating: parseInt(document.getElementById('adjRating').value),
        type: document.getElementById('adjType').value
    };
    
    tournamentData.adjudicators.push(adjudicator);
    displayAdjudicators();
    hideAdjudicatorForm();
    saveData();
    showNotification('Adjudicator added successfully!', 'success');
}

function displayAdjudicators() {
    const tbody = document.getElementById('adjudicatorsTableBody');
    tbody.innerHTML = '';
    
    if (tournamentData.adjudicators.length === 0) {
        tbody.innerHTML = '<tr class="empty-state"><td colspan="5">No adjudicators registered yet. Click "Add Adjudicator" to get started.</td></tr>';
        return;
    }
    
    tournamentData.adjudicators.forEach(adj => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${adj.name}</td>
            <td>${adj.institution}</td>
            <td>${adj.rating}</td>
            <td><span style="text-transform: capitalize;">${adj.type}</span></td>
            <td>
                <button class="btn btn-danger action-btn" onclick="deleteAdjudicator(${adj.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function deleteAdjudicator(id) {
    if (confirm('Are you sure you want to delete this adjudicator?')) {
        tournamentData.adjudicators = tournamentData.adjudicators.filter(a => a.id !== id);
        displayAdjudicators();
        saveData();
        showNotification('Adjudicator deleted successfully!', 'success');
    }
}

// BP Debate - Venue Management
function showVenueForm() {
    document.getElementById('venueForm').style.display = 'block';
}

function hideVenueForm() {
    document.getElementById('venueForm').style.display = 'none';
    document.getElementById('addVenueForm').reset();
}

function addVenue(e) {
    e.preventDefault();
    const venue = {
        id: Date.now(),
        name: document.getElementById('venueName').value,
        capacity: parseInt(document.getElementById('venueCapacity').value),
        location: document.getElementById('venueLocation').value
    };
    
    tournamentData.venues.push(venue);
    displayVenues();
    hideVenueForm();
    saveData();
    showNotification('Venue added successfully!', 'success');
}

function displayVenues() {
    const tbody = document.getElementById('venuesTableBody');
    tbody.innerHTML = '';
    
    if (tournamentData.venues.length === 0) {
        tbody.innerHTML = '<tr class="empty-state"><td colspan="4">No venues added yet. Click "Add Venue" to get started.</td></tr>';
        return;
    }
    
    tournamentData.venues.forEach(venue => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${venue.name}</td>
            <td>${venue.capacity}</td>
            <td>${venue.location || 'Not specified'}</td>
            <td>
                <button class="btn btn-danger action-btn" onclick="deleteVenue(${venue.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function deleteVenue(id) {
    if (confirm('Are you sure you want to delete this venue?')) {
        tournamentData.venues = tournamentData.venues.filter(v => v.id !== id);
        displayVenues();
        saveData();
        showNotification('Venue deleted successfully!', 'success');
    }
}

// BP Debate - Draw Generation
function generateDraw() {
    const round = parseInt(document.getElementById('roundSelect').value);
    
    if (tournamentData.teams.length < 4) {
        showNotification('You need at least 4 teams to generate a draw!', 'error');
        return;
    }
    
    if (tournamentData.adjudicators.length === 0) {
        showNotification('You need at least one adjudicator to generate a draw!', 'error');
        return;
    }
    
    if (tournamentData.venues.length === 0) {
        showNotification('You need at least one venue to generate a draw!', 'error');
        return;
    }
    
    // Shuffle teams for random pairing using Fisher-Yates algorithm
    const shuffledTeams = [...tournamentData.teams];
    for (let i = shuffledTeams.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffledTeams[i], shuffledTeams[j]] = [shuffledTeams[j], shuffledTeams[i]];
    }
    const rooms = [];
    
    // Create rooms (4 teams per room for BP)
    for (let i = 0; i < shuffledTeams.length; i += 4) {
        if (i + 3 < shuffledTeams.length) {
            const venue = tournamentData.venues[rooms.length % tournamentData.venues.length];
            const panel = assignPanel();
            
            rooms.push({
                venue: venue.name,
                teams: [
                    { position: 'OG', team: shuffledTeams[i] },
                    { position: 'OO', team: shuffledTeams[i + 1] },
                    { position: 'CG', team: shuffledTeams[i + 2] },
                    { position: 'CO', team: shuffledTeams[i + 3] }
                ],
                panel: panel
            });
        }
    }
    
    tournamentData.rounds[round - 1] = { round, rooms };
    displayDraw(rooms);
    updateResultsForRound(round, rooms);
    saveData();
    showNotification(`Draw generated for Round ${round}!`, 'success');
}

function assignPanel() {
    // Ensure we have adjudicators before assigning panel
    if (tournamentData.adjudicators.length === 0) {
        return [];
    }
    
    // Sort adjudicators by rating
    const sortedAdjs = [...tournamentData.adjudicators].sort((a, b) => b.rating - a.rating);
    
    // Assign chair (highest rated)
    const chair = sortedAdjs[0];
    const panel = [{ ...chair, role: 'Chair' }];
    
    // Assign wings if available
    if (sortedAdjs.length > 1) {
        panel.push({ ...sortedAdjs[1], role: 'Wing' });
    }
    if (sortedAdjs.length > 2) {
        panel.push({ ...sortedAdjs[2], role: 'Wing' });
    }
    
    return panel;
}

function displayDraw(rooms) {
    const container = document.getElementById('drawDisplay');
    container.innerHTML = '';
    
    rooms.forEach((room, index) => {
        const roomDiv = document.createElement('div');
        roomDiv.className = 'draw-room';
        roomDiv.innerHTML = `
            <h4>Room ${index + 1}: ${room.venue}</h4>
            <div class="draw-teams">
                ${room.teams.map(t => `
                    <div class="draw-team">
                        <span class="team-position">${t.position}</span>
                        <span class="team-name">${t.team.name}</span>
                        <span class="team-institution">${t.team.institution}</span>
                    </div>
                `).join('')}
            </div>
            <div class="draw-panel">
                <h5>Panel</h5>
                <div class="panel-judges">
                    ${room.panel.map(j => `
                        <span class="judge-badge ${j.role.toLowerCase()}">${j.name} (${j.role})</span>
                    `).join('')}
                </div>
            </div>
        `;
        container.appendChild(roomDiv);
    });
}

function exportDraw() {
    const round = parseInt(document.getElementById('roundSelect').value);
    const roundData = tournamentData.rounds[round - 1];
    
    if (!roundData) {
        showNotification('No draw available for this round!', 'error');
        return;
    }
    
    let csv = 'Room,Venue,Position,Team,Institution,Adjudicators\n';
    roundData.rooms.forEach((room, index) => {
        const adjNames = room.panel.map(p => `${p.name} (${p.role})`).join('; ');
        room.teams.forEach(t => {
            csv += `${index + 1},${room.venue},${t.position},${t.team.name},${t.team.institution},"${adjNames}"\n`;
        });
    });
    
    downloadCSV(csv, `round_${round}_draw.csv`);
    showNotification('Draw exported successfully!', 'success');
}

// BP Debate - Results Entry
function updateResultsForRound(round, rooms) {
    const container = document.getElementById('resultsContainer');
    container.innerHTML = '';
    
    rooms.forEach((room, roomIndex) => {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'result-entry';
        resultDiv.innerHTML = `
            <h4>Room ${roomIndex + 1}: ${room.venue}</h4>
            <div class="result-grid">
                ${room.teams.map((t, teamIndex) => `
                    <div class="result-team">
                        <div class="result-position">${t.position}</div>
                        <div class="speaker-score">
                            <label>${t.team.speakers[0]}</label>
                            <input type="number" class="score-input" min="60" max="80" 
                                   data-round="${round}" data-room="${roomIndex}" data-team="${teamIndex}" data-speaker="0"
                                   placeholder="60-80">
                        </div>
                        <div class="speaker-score">
                            <label>${t.team.speakers[1]}</label>
                            <input type="number" class="score-input" min="60" max="80"
                                   data-round="${round}" data-room="${roomIndex}" data-team="${teamIndex}" data-speaker="1"
                                   placeholder="60-80">
                        </div>
                        <div>
                            <label style="font-size: 0.875rem; color: var(--text-secondary);">Rank</label>
                            <select class="score-input" data-round="${round}" data-room="${roomIndex}" data-team="${teamIndex}" data-rank="true">
                                <option value="">-</option>
                                <option value="1">1st</option>
                                <option value="2">2nd</option>
                                <option value="3">3rd</option>
                                <option value="4">4th</option>
                            </select>
                        </div>
                    </div>
                `).join('')}
            </div>
            <button class="btn btn-primary mt-2" onclick="saveRoomResult(${round}, ${roomIndex})">Save Results</button>
        `;
        container.appendChild(resultDiv);
    });
    
    // Load existing results if any
    loadExistingResults(round);
}

function loadExistingResults(round) {
    const key = `round_${round}`;
    if (tournamentData.results[key]) {
        const results = tournamentData.results[key];
        results.forEach((roomResult, roomIndex) => {
            roomResult.forEach((teamResult, teamIndex) => {
                // Load speaker scores
                teamResult.scores.forEach((score, speakerIndex) => {
                    const input = document.querySelector(
                        `[data-round="${round}"][data-room="${roomIndex}"][data-team="${teamIndex}"][data-speaker="${speakerIndex}"]`
                    );
                    if (input) input.value = score;
                });
                
                // Load rank
                const rankSelect = document.querySelector(
                    `[data-round="${round}"][data-room="${roomIndex}"][data-team="${teamIndex}"][data-rank="true"]`
                );
                if (rankSelect) rankSelect.value = teamResult.rank;
            });
        });
    }
}

function saveRoomResult(round, roomIndex) {
    const key = `round_${round}`;
    if (!tournamentData.results[key]) {
        tournamentData.results[key] = [];
    }
    
    const roundData = tournamentData.rounds[round - 1];
    const room = roundData.rooms[roomIndex];
    const roomResults = [];
    
    room.teams.forEach((t, teamIndex) => {
        const speaker1Input = document.querySelector(
            `[data-round="${round}"][data-room="${roomIndex}"][data-team="${teamIndex}"][data-speaker="0"]`
        );
        const speaker2Input = document.querySelector(
            `[data-round="${round}"][data-room="${roomIndex}"][data-team="${teamIndex}"][data-speaker="1"]`
        );
        const rankSelect = document.querySelector(
            `[data-round="${round}"][data-room="${roomIndex}"][data-team="${teamIndex}"][data-rank="true"]`
        );
        
        const score1 = parseFloat(speaker1Input.value) || 0;
        const score2 = parseFloat(speaker2Input.value) || 0;
        const rank = parseInt(rankSelect.value) || 0;
        
        roomResults.push({
            teamId: t.team.id,
            scores: [score1, score2],
            rank: rank
        });
    });
    
    tournamentData.results[key][roomIndex] = roomResults;
    updateTeamStandings();
    saveData();
    showNotification('Results saved successfully!', 'success');
}

function updateTeamStandings() {
    // Reset all team stats
    tournamentData.teams.forEach(team => {
        team.points = 0;
        team.wins = 0;
        team.speakerPoints = 0;
    });
    
    // Calculate standings from all results
    Object.keys(tournamentData.results).forEach(roundKey => {
        const roundResults = tournamentData.results[roundKey];
        roundResults.forEach(roomResults => {
            roomResults.forEach(result => {
                const team = tournamentData.teams.find(t => t.id === result.teamId);
                if (team && result.rank) {
                    // BP points: 1st=3pts, 2nd=2pts, 3rd=1pt, 4th=0pts
                    const points = [3, 2, 1, 0][result.rank - 1];
                    team.points += points;
                    if (result.rank === 1) team.wins++;
                    team.speakerPoints += result.scores.reduce((a, b) => a + b, 0);
                }
            });
        });
    });
    
    displayTeamTab();
    displaySpeakerTab();
}

function displayTeamTab() {
    const tbody = document.getElementById('teamTabBody');
    tbody.innerHTML = '';
    
    if (tournamentData.teams.length === 0) {
        tbody.innerHTML = '<tr class="empty-state"><td colspan="6">No results available yet. Enter results to see standings.</td></tr>';
        return;
    }
    
    // Sort teams by points, then speaker points
    const sortedTeams = [...tournamentData.teams].sort((a, b) => {
        if (b.points !== a.points) return b.points - a.points;
        return b.speakerPoints - a.speakerPoints;
    });
    
    sortedTeams.forEach((team, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${team.name}</td>
            <td>${team.institution}</td>
            <td>${team.points}</td>
            <td>${team.wins}</td>
            <td>${team.speakerPoints}</td>
        `;
        tbody.appendChild(row);
    });
}

function displaySpeakerTab() {
    const tbody = document.getElementById('speakerTabBody');
    tbody.innerHTML = '';
    
    const speakers = [];
    
    // Collect all speaker data
    Object.keys(tournamentData.results).forEach(roundKey => {
        const roundResults = tournamentData.results[roundKey];
        roundResults.forEach(roomResults => {
            roomResults.forEach(result => {
                const team = tournamentData.teams.find(t => t.id === result.teamId);
                if (team) {
                    result.scores.forEach((score, index) => {
                        const speakerName = team.speakers[index];
                        let speaker = speakers.find(s => s.name === speakerName && s.teamName === team.name);
                        if (!speaker) {
                            speaker = {
                                name: speakerName,
                                teamName: team.name,
                                institution: team.institution,
                                scores: [],
                                total: 0,
                                average: 0
                            };
                            speakers.push(speaker);
                        }
                        speaker.scores.push(score);
                        speaker.total += score;
                        speaker.average = speaker.total / speaker.scores.length;
                    });
                }
            });
        });
    });
    
    if (speakers.length === 0) {
        tbody.innerHTML = '<tr class="empty-state"><td colspan="6">No results available yet. Enter results to see speaker standings.</td></tr>';
        return;
    }
    
    // Sort speakers by total points
    speakers.sort((a, b) => b.total - a.total);
    
    speakers.forEach((speaker, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${speaker.name}</td>
            <td>${speaker.teamName}</td>
            <td>${speaker.institution}</td>
            <td>${speaker.total.toFixed(1)}</td>
            <td>${speaker.average.toFixed(2)}</td>
        `;
        tbody.appendChild(row);
    });
}

// Public Speaking - Event Management
function savePSEvent(e) {
    e.preventDefault();
    publicSpeakingData.event = {
        name: document.getElementById('eventName').value,
        date: document.getElementById('eventDate').value,
        type: document.getElementById('eventType').value,
        timeLimit: parseInt(document.getElementById('timeLimit').value),
        numJudges: parseInt(document.getElementById('numJudges').value)
    };
    
    displayPSEventInfo();
    saveData();
    showNotification('Event saved successfully!', 'success');
}

function displayPSEventInfo() {
    const info = publicSpeakingData.event;
    if (info) {
        document.getElementById('psEventInfo').style.display = 'block';
        document.getElementById('psInfoName').textContent = info.name;
        document.getElementById('psInfoType').textContent = info.type.charAt(0).toUpperCase() + info.type.slice(1);
        document.getElementById('psInfoTime').textContent = `${info.timeLimit} minutes`;
        document.getElementById('psInfoJudges').textContent = info.numJudges;
    }
}

// Public Speaking - Speaker Management
function showPSSpeakerForm() {
    document.getElementById('psSpeakerForm').style.display = 'block';
}

function hidePSSpeakerForm() {
    document.getElementById('psSpeakerForm').style.display = 'none';
    document.getElementById('addPSSpeakerForm').reset();
}

function addPSSpeaker(e) {
    e.preventDefault();
    const speaker = {
        id: Date.now(),
        name: document.getElementById('psSpeakerName').value,
        institution: document.getElementById('psSpeakerInstitution').value,
        email: document.getElementById('psSpeakerEmail').value,
        category: document.getElementById('psSpeakerCategory').value
    };
    
    publicSpeakingData.speakers.push(speaker);
    displayPSSpeakers();
    hidePSSpeakerForm();
    updatePSScoring();
    saveData();
    showNotification('Speaker added successfully!', 'success');
}

function displayPSSpeakers() {
    const tbody = document.getElementById('psSpeakersTableBody');
    tbody.innerHTML = '';
    
    if (publicSpeakingData.speakers.length === 0) {
        tbody.innerHTML = '<tr class="empty-state"><td colspan="5">No speakers registered yet. Click "Add Speaker" to get started.</td></tr>';
        return;
    }
    
    publicSpeakingData.speakers.forEach(speaker => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${speaker.name}</td>
            <td>${speaker.institution}</td>
            <td>${speaker.email || 'Not provided'}</td>
            <td><span style="text-transform: capitalize;">${speaker.category}</span></td>
            <td>
                <button class="btn btn-danger action-btn" onclick="deletePSSpeaker(${speaker.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function deletePSSpeaker(id) {
    if (confirm('Are you sure you want to delete this speaker?')) {
        publicSpeakingData.speakers = publicSpeakingData.speakers.filter(s => s.id !== id);
        displayPSSpeakers();
        updatePSScoring();
        saveData();
        showNotification('Speaker deleted successfully!', 'success');
    }
}

// Public Speaking - Judge Management
function showPSJudgeForm() {
    document.getElementById('psJudgeForm').style.display = 'block';
}

function hidePSJudgeForm() {
    document.getElementById('psJudgeForm').style.display = 'none';
    document.getElementById('addPSJudgeForm').reset();
}

function addPSJudge(e) {
    e.preventDefault();
    const judge = {
        id: Date.now(),
        name: document.getElementById('psJudgeName').value,
        institution: document.getElementById('psJudgeInstitution').value,
        expertise: document.getElementById('psJudgeExpertise').value,
        email: document.getElementById('psJudgeEmail').value
    };
    
    publicSpeakingData.judges.push(judge);
    displayPSJudges();
    hidePSJudgeForm();
    updatePSScoring();
    saveData();
    showNotification('Judge added successfully!', 'success');
}

function displayPSJudges() {
    const tbody = document.getElementById('psJudgesTableBody');
    tbody.innerHTML = '';
    
    if (publicSpeakingData.judges.length === 0) {
        tbody.innerHTML = '<tr class="empty-state"><td colspan="5">No judges registered yet. Click "Add Judge" to get started.</td></tr>';
        return;
    }
    
    publicSpeakingData.judges.forEach(judge => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${judge.name}</td>
            <td>${judge.institution}</td>
            <td><span style="text-transform: capitalize;">${judge.expertise}</span></td>
            <td>${judge.email || 'Not provided'}</td>
            <td>
                <button class="btn btn-danger action-btn" onclick="deletePSJudge(${judge.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function deletePSJudge(id) {
    if (confirm('Are you sure you want to delete this judge?')) {
        publicSpeakingData.judges = publicSpeakingData.judges.filter(j => j.id !== id);
        displayPSJudges();
        updatePSScoring();
        saveData();
        showNotification('Judge deleted successfully!', 'success');
    }
}

// Public Speaking - Scoring
function updatePSScoring() {
    const container = document.getElementById('psScoringContainer');
    
    if (publicSpeakingData.speakers.length === 0 || publicSpeakingData.judges.length === 0) {
        container.innerHTML = '<p class="empty-state-text">Add speakers and judges first to enable scoring.</p>';
        return;
    }
    
    container.innerHTML = '';
    
    publicSpeakingData.speakers.forEach(speaker => {
        const speakerDiv = document.createElement('div');
        speakerDiv.className = 'result-entry';
        speakerDiv.innerHTML = `
            <h4>${speaker.name} - ${speaker.institution}</h4>
            <div class="result-grid">
                ${publicSpeakingData.judges.map(judge => `
                    <div class="speaker-score" style="display: grid; grid-template-columns: 1fr 100px; gap: 1rem; align-items: center; padding: 0.75rem; background: var(--bg-primary); border-radius: var(--radius-md); border: 1px solid var(--border-color);">
                        <label>${judge.name}</label>
                        <input type="number" class="score-input" min="0" max="100" step="0.1"
                               data-speaker="${speaker.id}" data-judge="${judge.id}"
                               value="${publicSpeakingData.scores[`${speaker.id}_${judge.id}`] || ''}"
                               onchange="savePSScore(${speaker.id}, ${judge.id}, this.value)"
                               placeholder="0-100">
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(speakerDiv);
    });
    
    updatePSResults();
}

function savePSScore(speakerId, judgeId, score) {
    const key = `${speakerId}_${judgeId}`;
    publicSpeakingData.scores[key] = parseFloat(score) || 0;
    saveData();
    updatePSResults();
}

function updatePSResults() {
    const tbody = document.getElementById('psResultsBody');
    tbody.innerHTML = '';
    
    if (publicSpeakingData.speakers.length === 0) {
        tbody.innerHTML = '<tr class="empty-state"><td colspan="6">No scores entered yet. Enter scores to see results.</td></tr>';
        return;
    }
    
    const results = publicSpeakingData.speakers.map(speaker => {
        let total = 0;
        let count = 0;
        
        publicSpeakingData.judges.forEach(judge => {
            const key = `${speaker.id}_${judge.id}`;
            const score = publicSpeakingData.scores[key] || 0;
            if (score > 0) {
                total += score;
                count++;
            }
        });
        
        return {
            ...speaker,
            totalScore: total,
            averageScore: count > 0 ? total / count : 0,
            judgeCount: count
        };
    });
    
    // Sort by total score
    results.sort((a, b) => b.totalScore - a.totalScore);
    
    results.forEach((result, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${result.name}</td>
            <td>${result.institution}</td>
            <td><span style="text-transform: capitalize;">${result.category}</span></td>
            <td>${result.totalScore.toFixed(2)}</td>
            <td>${result.averageScore.toFixed(2)}</td>
        `;
        tbody.appendChild(row);
    });
}

function exportPSResults() {
    if (publicSpeakingData.speakers.length === 0) {
        showNotification('No results to export!', 'error');
        return;
    }
    
    let csv = 'Rank,Speaker,Institution,Category,Total Score,Average Score\n';
    
    const tbody = document.getElementById('psResultsBody');
    const rows = tbody.querySelectorAll('tr:not(.empty-state)');
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const data = Array.from(cells).map(cell => cell.textContent.trim());
        csv += data.join(',') + '\n';
    });
    
    downloadCSV(csv, 'public_speaking_results.csv');
    showNotification('Results exported successfully!', 'success');
}

// Data Management
function saveData() {
    localStorage.setItem('tournamentData', JSON.stringify(tournamentData));
    localStorage.setItem('publicSpeakingData', JSON.stringify(publicSpeakingData));
}

function loadData() {
    const savedTournamentData = localStorage.getItem('tournamentData');
    const savedPSData = localStorage.getItem('publicSpeakingData');
    
    if (savedTournamentData) {
        tournamentData = JSON.parse(savedTournamentData);
        displayTournamentInfo();
        displayTeams();
        displayAdjudicators();
        displayVenues();
        displayTeamTab();
        displaySpeakerTab();
    }
    
    if (savedPSData) {
        publicSpeakingData = JSON.parse(savedPSData);
        displayPSEventInfo();
        displayPSSpeakers();
        displayPSJudges();
        updatePSScoring();
    }
}

function exportAllData() {
    const data = {
        tournament: tournamentData,
        publicSpeaking: publicSpeakingData,
        exportDate: new Date().toISOString()
    };
    
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ufstab_backup_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    showNotification('Data exported successfully!', 'success');
}

function importData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const data = JSON.parse(event.target.result);
                if (data.tournament) tournamentData = data.tournament;
                if (data.publicSpeaking) publicSpeakingData = data.publicSpeaking;
                saveData();
                loadData();
                showNotification('Data imported successfully!', 'success');
                location.reload();
            } catch (error) {
                showNotification('Error importing data. Please check the file format.', 'error');
            }
        };
        reader.readAsText(file);
    };
    input.click();
}

function clearAllData() {
    if (confirm('Are you sure you want to clear all data? This action cannot be undone!')) {
        if (confirm('This will delete all tournaments, teams, events, and results. Are you absolutely sure?')) {
            localStorage.clear();
            tournamentData = { tournament: null, teams: [], adjudicators: [], venues: [], rounds: [], results: {} };
            publicSpeakingData = { event: null, speakers: [], judges: [], scores: {} };
            location.reload();
        }
    }
}

// Utility Functions
function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('fadeOut');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
