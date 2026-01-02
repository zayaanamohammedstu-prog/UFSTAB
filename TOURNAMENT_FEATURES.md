# Tournament Customization and Import Features

This document describes the new tournament customization and data import features added to OratorHub.

## Features Overview

### 1. Tournament Customization

Tournament organizers can now customize the appearance and behavior of their tournament:

- **Custom Logo**: Add a tournament logo displayed on the public page
- **Custom Colors**: Set primary and secondary colors for tournament branding
- **Public Display Control**: Enable or disable public access to tournament information
- **Unique Tournament URL**: Each tournament gets a unique, shareable URL for public viewing

### 2. Public Display Tab

A new public display page allows anyone to view tournament information without authentication:

- **Tournament Information**: View basic details like format, venue, dates, etc.
- **Registered Teams**: See all teams registered for the tournament
- **Live Standings**: View current tournament standings with auto-refresh
- **Custom Branding**: Tournament-specific colors and logo are applied

### 3. Registration Data Import

Bulk import speaker and team registrations from CSV or Excel files:

- **CSV Support**: Import data from Google Forms exports or any CSV file
- **Excel Support**: Import from XLSX or XLS files
- **Automatic User Creation**: Creates user accounts for new registrants
- **Duplicate Detection**: Prevents duplicate registrations
- **Error Reporting**: Detailed feedback on import errors

## How to Use

### Customizing Your Tournament

1. **Create a Tournament** (if you haven't already):
   - Log in as an organizer
   - Navigate to "BP Debate" → "Tournament" tab
   - Fill in the tournament details and save

2. **Customize Appearance**:
   - Go to "BP Debate" → "Customize" tab
   - Add your tournament logo URL (optional)
   - Select primary and secondary colors
   - Enable/disable public display
   - Save customization

3. **Share Public URL**:
   - After enabling public display, copy the generated URL
   - Share this URL with participants and spectators
   - Anyone can access it without logging in

### Accessing the Public Display

**URL Format**: `http://yoursite.com/public-display?slug=tournament-slug`

The public display shows:
- Tournament information
- List of registered teams
- Current standings with live updates (refreshes every 30 seconds)

### Importing Registration Data

#### Preparing Your CSV File

Your CSV file should have the following columns (column names are case-insensitive):

| Column Name | Required | Description |
|-------------|----------|-------------|
| email or Email Address | Yes | Participant's email address |
| name or Full Name | No | Participant's full name |
| registration_type or Registration Type | No | "individual" or "team" (default: individual) |
| team_name or Team Name | No | Name of the team (for team registrations) |
| partner_name or Partner Name | No | Partner's name (for team registrations) |
| partner_email or Partner Email | No | Partner's email (for team registrations) |

**Sample CSV**:
```csv
email,name,registration_type,team_name,partner_name,partner_email
john.doe@example.com,John Doe,individual,,,
jane.smith@example.com,Jane Smith,team,Cambridge A,John Doe,john.doe@example.com
alice.johnson@example.com,Alice Johnson,individual,,,
```

#### Importing from Google Forms

1. Create a Google Form with appropriate fields (email, name, etc.)
2. After collecting responses, go to "Responses" tab
3. Click on the spreadsheet icon to create a Google Sheet
4. In the Sheet, go to File → Download → Comma-separated values (.csv)
5. Use this CSV file in OratorHub

#### Import Process

1. **Navigate to Import Tab**:
   - Log in as tournament organizer
   - Go to "BP Debate" → "Import Data" tab

2. **Upload File**:
   - Click "Select CSV or Excel File"
   - Choose your CSV or Excel file
   - Click "Import Registrations"

3. **Review Results**:
   - The system will display:
     - Number of successfully imported registrations
     - List of any errors encountered
   - Imported users receive a default password: `changeme123` (they should change it on first login)

## API Endpoints

### Tournament Customization

**Update Tournament Customization**:
```
PUT /api/tournaments/{id}
{
  "custom_logo_url": "https://example.com/logo.png",
  "primary_color": "#ff0000",
  "secondary_color": "#00ff00",
  "show_public_tab": true
}
```

### Public Display (No Authentication Required)

**Get Tournament by Slug**:
```
GET /api/tournaments/public/{slug}
```

**Get Public Teams**:
```
GET /api/tournaments/public/{slug}/teams
```

**Get Public Standings**:
```
GET /api/tournaments/public/{slug}/standings
```

### Registration Import

**Import Registrations**:
```
POST /api/registrations/tournament/{id}/import
Content-Type: multipart/form-data

file: <CSV or Excel file>
```

**Note**: For CSV files with complex data (quoted values containing commas), use Excel format or ensure your CSV generator properly escapes special characters.

## Security Considerations

### Public Display
- Only tournaments with `show_public_tab` enabled are publicly accessible
- Sensitive information (organizer details, payment status) is not exposed
- Public endpoints are read-only

### Registration Import
- Only tournament organizers can import registrations
- Duplicate email addresses are rejected
- Invalid data is reported but doesn't stop the import process
- **Default Password Security**: Imported users receive a default password (`changeme123`) that MUST be changed on first login. For production, consider implementing email-based password setup.
- **CSV Limitations**: Basic CSV parser doesn't handle RFC 4180 quoted fields. Use Excel format for complex data.

## Troubleshooting

### Public Display Not Working
- Ensure `show_public_tab` is set to `true` in tournament settings
- Verify you're using the correct slug in the URL
- Check that the tournament exists and is not deleted

### Import Errors
- **"Missing email address"**: Every row must have an email
- **"Already registered"**: User has already registered for this tournament
- **"File format not supported"**: Only CSV, XLSX, and XLS files are accepted
- **CSV parsing errors**: If you have commas in data fields, use Excel format or ensure proper CSV escaping
- **Excel support not available**: Install the `openpyxl` package: `pip install openpyxl`

### Customization Not Showing
- Clear browser cache and reload the page
- Ensure you saved the customization settings
- Check that the logo URL is publicly accessible

## Examples

### Example 1: Hosting a Hybrid Tournament

1. Create tournament with `event_type: hybrid`
2. Customize with your institution's colors and logo
3. Enable public display
4. Import registrations from Google Form
5. Share public URL with remote participants and spectators

### Example 2: Regional Championship

1. Create tournament with custom branding
2. Import registrations from Excel spreadsheet
3. Generate pairings and conduct rounds
4. Public can follow live standings via public URL
5. Export final results

## Best Practices

1. **Test Import with Small File First**: Before importing hundreds of registrations, test with a small sample file
2. **Backup Before Import**: Export existing data before performing bulk import
3. **Use Consistent Column Names**: Stick to standard column names for easier imports
4. **Validate Email Addresses**: Ensure email addresses in your import file are valid
5. **Communicate Default Password**: Inform imported users about their default password and need to change it
6. **Monitor Public Access**: Regularly check what information is visible on public display

## Future Enhancements

Planned features for future releases:
- Custom CSS support for advanced styling
- Automatic email notifications to imported users
- More flexible column mapping for imports
- Support for additional file formats (JSON, XML)
- QR code generation for public display URL
- Embedded public display widget

---

For more information, see the main [README.md](README.md) or visit the [API Documentation](API.md).
