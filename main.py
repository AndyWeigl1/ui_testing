"""Entry point for the Script Runner application"""

from app import ModernUI


def main():
    """Run the application"""
    app = ModernUI()
    app.mainloop()


if __name__ == "__main__":
    main()