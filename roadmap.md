# Project Roadmap: Future Features and Fixes

## Features ✨

* **System Notifications:** Implement system notifications for script completion (success/failure).
* **Audible Alerts:** Add a feature to play sounds when scripts finish successfully or encounter an error.
* **Script Stats Window:**
    * Enable functionality for the "Stats" button on the script page.
    * Clicking "Stats" should open a new window displaying the run history (time and status) of the script.
* **Console Behavior:** Add a setting to automatically clear the console on each new script run.
* **Detailed Script History/Logs:** Implement a comprehensive logging view accessible from the GUI, potentially with filtering and search capabilities for past script runs.
* **Undo/Redo for Console Clearing:** Add an undo/redo functionality for the console clearing action.

---
## Fixes 🛠️

* **SOP Buttons on Scripts Page:**
    * Reintroduce SOP buttons to each script card on the Scripts page.
    * Link these buttons to the corresponding SOPs, similar to how the SOPs page functions.
* **SOP Page Card Sizing:**
    * Address the left-alignment issue of data within SOP cards, which causes visual distortions when the window size increases.
    * Improve the layout when filtering results in a single card, preventing excessive empty space on the right. Implement a new system for better visual presentation.
* **Legacy Header Container:**
    * Re-evaluate the container holding "Script Control Panel" text, the dark/light mode toggle, and the status indicator.
    * **Proposal 1:** Move the status indicator to the navbar (left of the first button, right of the logo). Remove the rest of the container as the dark mode toggle is redundant (already in settings).
    * **Consider:** Explore alternative solutions for a cleaner and more modern UI.