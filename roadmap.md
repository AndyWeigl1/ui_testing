# Project Roadmap: Future Features and Fixes

## Features ✨

* ~~**System Notifications:** Implement system notifications for script completion (success/failure).~~ ✅ **COMPLETED**
* ~~**Audible Alerts:** Add a feature to play sounds when scripts finish successfully or encounter an error.~~ ✅ **COMPLETED**
* ~~**Script Stats Window:**~~ ✅ **COMPLETED**
    * ~~Enable functionality for the "Stats" button on the script page.~~
    * ~~Clicking "Stats" should open a new window displaying the run history (time and status) of the script.~~
    * **Implementation Complete:** Added comprehensive `ScriptHistoryDialog` with:
        - Detailed execution history table with filtering and search
        - Summary statistics dashboard
        - Export to CSV functionality
        - Individual run details view
        - History management (clear history option)
        - Real-time filtering by status and error messages
* **Console Behavior:** Add a setting to automatically clear the console on each new script run.
* ~~**Detailed Script History/Logs:**~~ ✅ **COMPLETED**
    * ~~Implement a comprehensive logging view accessible from the GUI, potentially with filtering and search capabilities for past script runs.~~
    * **Implementation Complete:** Full-featured history dialog with advanced filtering, search, and export capabilities.
* **Undo/Redo for Console Clearing:** Add an undo/redo functionality for the console clearing action.
* **Add ability to favorite scripts for easy run access:** Let the user favorite scripts that they frequently use which gives them quick access to run those.
* Add a search bad to the output console, along with a copy button to copy entire output (the copy button could be combined with the export button, maybe a dropdown/button combo?)

### New Enhancement Ideas 💡
Based on the completed history feature, consider these additions:
* **History Analytics Dashboard:** Create charts/graphs showing execution trends over time
* **Scheduled Script Runs:** Add ability to schedule scripts with cron-like functionality
* **Script Performance Alerts:** Notify when scripts take unusually long or fail repeatedly
* **History Data Retention Policies:** Auto-cleanup old history based on age/count limits
* **Advanced Export Options:** Export to Excel with charts, or PDF reports
* **Bulk Operations:** Run multiple scripts in sequence with combined reporting

---
## Fixes 🛠️

* ~~**SOP Buttons on Scripts Page:**~~ ✅ **COMPLETED**
    * ~~Reintroduce SOP buttons to each script card on the Scripts page.~~
    * ~~Link these buttons to the corresponding SOPs, similar to how the SOPs page functions.~~
* **SOP Page Card Sizing/Appearance:**
    * Address the left-alignment issue of data within SOP cards, which causes visual distortions when the window size increases.
    * Improve the layout when filtering results in a single card, preventing excessive empty space on the right. Implement a new system for better visual presentation.
* **Legacy Header Container:**
    * Re-evaluate the container holding "Script Control Panel" text, the dark/light mode toggle, and the status indicator.
    * **Proposal 1:** Move the status indicator to the navbar (left of the first button, right of the logo). Remove the rest of the container as the dark mode toggle is redundant (already in settings).
    * **Consider:** Explore alternative solutions for a cleaner and more modern UI.
