class StudentTUI:
    def __init__(self, db):
        self.db = db

    def _print_menu(self) -> None:
        print("\n=== База студентов (ООП) ===")
        print("1. Добавить запись\n2. Показать все\n3. Найти по фильтру\n0. Выход")

    def _read_int(self, prompt: str) -> int:
        while True:
            try: return int(input(prompt).strip())
            except ValueError: print("Ошибка: введите целое число.")

    def run(self) -> None:
        while True:
            self._print_menu()
            action = input("Выберите действие: ").strip()
            if action == "1":
                try:
                    res = self.db.create_record(
                        self._read_int("id: "), input("Имя: "),
                        input("Фамилия: "), self._read_int("Возраст: "), input("Пол: ")
                    )
                    print(f"Успех: {res}")
                except ValueError as e: print(f"Ошибка: {e}")
            elif action == "2":
                print(self.db.select_record())
            elif action == "0":
                break
