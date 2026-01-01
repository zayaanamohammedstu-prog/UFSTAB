# UFSTAB - BP Debate & Public Speaking Tabulation System

A modern, user-friendly web-based tabulation system for British Parliamentary (BP) debate tournaments and public speaking events. Built with pure HTML, CSS, and JavaScript - no frameworks required!

## 🌟 Features

### BP Debate Tournament Management
- **Tournament Setup**: Configure tournament details including name, date, venue, and number of rounds
- **Team Registration**: Register teams with institution details and speaker names
- **Adjudicator Management**: Add and manage adjudicators with ratings and types (Chair/Wing/Trainee)
- **Venue Management**: Track debate rooms and their capacities
- **Automatic Draw Generation**: Generate BP-format draws with 4 teams per room (OG, OO, CG, CO)
- **Results Entry**: Enter speaker scores (60-80 points) and team rankings
- **Team Tab**: View team standings with points, wins, and speaker points
- **Speaker Tab**: Individual speaker rankings with total and average scores

### Public Speaking Events
- **Event Configuration**: Set up various event types (Impromptu, Prepared, Persuasive, Informative, Storytelling)
- **Speaker Registration**: Register speakers with categories (Novice, Intermediate, Advanced, Open)
- **Judge Management**: Manage judges with expertise levels
- **Flexible Scoring**: Enter scores from multiple judges
- **Results Calculation**: Automatic tabulation with rankings
- **Export Results**: Download results as CSV files

### Additional Features
- **Dark/Light Theme**: Toggle between beautiful dark and light modes
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Auto-Save**: All data is automatically saved to browser localStorage
- **Data Export/Import**: Backup and restore your tournament data
- **Print-Friendly**: Optimized views for printing draws and results
- **Modern UI**: Clean, intuitive interface inspired by modern design principles

## 🚀 Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/zayaanamohammedstu-prog/UFSTAB.git
cd UFSTAB
```

2. Open `index.html` in your web browser, or serve it using a local web server:

**Using Python:**
```bash
python3 -m http.server 8000
```

**Using Node.js (http-server):**
```bash
npx http-server
```

3. Navigate to `http://localhost:8000` in your browser

### No Installation Required
Simply open the `index.html` file directly in any modern web browser!

## 📖 User Guide

### Setting Up a BP Debate Tournament

1. **Configure Tournament**
   - Navigate to BP Debate → Tournament
   - Enter tournament name, date, venue, and number of rounds
   - Click "Save Tournament"

2. **Register Teams**
   - Go to the Teams tab
   - Click "Add Team"
   - Fill in team name, institution, and both speakers' names
   - Save the team

3. **Add Adjudicators**
   - Navigate to Adjudicators tab
   - Click "Add Adjudicator"
   - Enter name, institution, rating (1-10), and type
   - Save the adjudicator

4. **Add Venues**
   - Go to Venues tab
   - Click "Add Venue"
   - Enter venue name, capacity, and location
   - Save the venue

5. **Generate Draw**
   - Navigate to Draw tab
   - Select the round number
   - Click "Generate Draw"
   - The system will automatically pair teams and assign adjudicators

6. **Enter Results**
   - Go to Results tab
   - Enter speaker scores (60-80) for each speaker
   - Select team rankings (1st, 2nd, 3rd, 4th)
   - Click "Save Results" for each room

7. **View Standings**
   - Navigate to Tab tab
   - View Team Tab for team standings
   - View Speaker Tab for individual speaker rankings

### Setting Up a Public Speaking Event

1. **Create Event**
   - Navigate to Public Speaking → Events
   - Enter event details and configure settings
   - Click "Save Event"

2. **Register Speakers**
   - Go to Speakers tab
   - Add speakers with their details
   - Assign categories

3. **Add Judges**
   - Navigate to Judges tab
   - Register all judges for the event

4. **Enter Scores**
   - Go to Scoring tab
   - Enter scores from each judge for each speaker
   - Scores are auto-saved as you type

5. **View Results**
   - Navigate to Results tab
   - See ranked speakers with total and average scores
   - Export results using the "Export Results" button

## 💾 Data Management

### Auto-Save
All data is automatically saved to your browser's localStorage as you make changes. No manual save required!

### Export Data
1. Go to Settings
2. Click "Export All Data"
3. A JSON file will be downloaded containing all your tournament and event data

### Import Data
1. Go to Settings
2. Click "Import Data"
3. Select a previously exported JSON file
4. Your data will be restored

### Clear All Data
⚠️ **Warning**: This action cannot be undone!
1. Go to Settings
2. Click "Clear All Data"
3. Confirm the action twice

## 🎨 Theme Customization

Toggle between light and dark themes using:
- The moon/sun icon in the header
- Settings → Theme options

Your theme preference is saved automatically.

## 🏗️ Technical Details

### Technology Stack
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS Grid and Flexbox
- **Vanilla JavaScript**: No frameworks or dependencies
- **localStorage**: Client-side data persistence

### Browser Compatibility
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

### File Structure
```
UFSTAB/
├── index.html      # Main HTML structure
├── styles.css      # All styling and themes
├── script.js       # Application logic
└── README.md       # This file
```

## 🔒 Privacy & Security

- All data is stored locally in your browser
- No data is sent to any external servers
- Your tournament information remains completely private
- Data persists until you clear it or clear browser data

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is open source and available for use in debate tournaments and public speaking events.

## 🙏 Acknowledgments

- Inspired by Calico and other debate tabulation systems
- Built for the debate and public speaking community
- Designed with tournament organizers in mind

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Built with ❤️ for the debate community**

© 2026 UFSTAB. All rights reserved.
