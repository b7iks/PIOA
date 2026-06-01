from db.backend.memory import StudentDatabase, JsonStudentDatabase, CsvStudentDatabase
from db.tui import StudentTUI

def main():
    print("Выберите тип СУБД для запуска:")
    print("1. In-Memory (Оперативная память)")
    print("2. Файловая JSON (Основное задание)")
    print("3. Файловая CSV (Дополнительное задание)")
    choice = input("Ваш выбор: ").strip()

    if choice == "2":
        db = JsonStudentDatabase()
        print("-> Запущена JSON СУБД (данные сохраняются в students.json)")
    elif choice == "3":
        db = CsvStudentDatabase()
        print("-> Запущена CSV СУБД (данные сохраняются in students.csv)")
    else:
        db = StudentDatabase()
        print("-> Запущена In-Memory СУБД (данные сотрутся при выходе)")

    ui = StudentTUI(db)
    ui.run()

if __name__ == "__main__":
    main()
