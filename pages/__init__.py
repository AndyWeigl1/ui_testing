"""Pages package for application views"""

from .base_page import BasePage
from .about_page import AboutPage
from .process_page import ProcessPage
from .projects_page import ProjectsPage
from .settings_page import SettingsPage
from .sops_page import SOPsPage

__all__ = [
    'BasePage',
    'AboutPage', 
    'ProcessPage',
    'ProjectsPage',
    'SOPsPage',
    'SettingsPage'
]
