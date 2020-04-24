# Hypixel Skyblock Guild Stats

This script lets you put your guild members in a spreadsheet and then get their stats

# Usage

## Set the environment variables
1. `HYPIXEL_API_KEY` is set to your hypixel api key. Do `/api` in-game to get this value
2. `STATS_SHEETS_ID` is set to the id of your google spreadsheet. Look in the url for this id

### Setting environment variables in Windows
In command prompt, `setx HYPIXEL_API_KEY thisistheapikeyhere` to set a variable. Close command prompt and open again in order for this change to take effect.

### Setting environment variables in Linux and MacOS
Enter your `~/.bashrc` or `~/.zshrc` file and at the bottom put in `export HYPIXEL_API_KEY=thisistheapikeyhere` to set an environment variable.

## Set up the Google Sheet
1. Run the program once to set up the api connection with Google Sheets
2. The values will start to be filled at the 3rd row of the sheet, freeze the first two rows and use them for a header. A header is located in the **About** section of this page.
3. Fill in the first two columns with the username and profile of each member

## About
The Third column `Failed?` is for determining whether the api call was a success. If this value ends up with `T` after the program is run, most likely that member's API settings are turned off. Occasionally a member's API settings are on, but the API call failed for some reason. Running the program again should fix this. Changing the `check_failure` variable near the top of `main.py` to `True` will only get the API results from members flagged with `T`.

Header:
`Name, Profile, Failed?, Skill Average, Slayer XP, Combat, Foraging, Mining, Fishing, Farming, Alchemy, Enchanting, Zombie, Spider, Wolf, Gifts, Given, Deaths, Purse`

# TODO
- The columns should be more customizable to the user, the program should read the header and then populate the columns accordingly.
- Add more values that can be used in the spreadsheet
- Organize code into separate files
- Remove magic numbers
- Find a better way to limit API calls than time.sleep
