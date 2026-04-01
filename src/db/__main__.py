from db.backend.memory import StudentDatabase
from db.tui import StudentTUI

def main():
    db = StudentDatabase()
    ui = StudentTUI(db)
    ui.run()

if __name__ == "__main__":
    main()
