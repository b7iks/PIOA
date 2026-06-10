from db.backend.memory import DatabaseError


class StudentTUI:
    def __init__(self, db):
        self.db = db

    def _print_menu(self) -> None:
        print("\n=== База студентов (ООП) ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти по фильтру")
        print("4. Сортировать записи (Доп. задание)")
        print("0. Выход")

    def _read_int(self, prompt: str) -> int:
        while True:
            try:
                return int(input(prompt).strip())
            except ValueError:
                print("Ошибка: введите целое число.")

    def _add_student(self) -> None:
        print("\n--- Добавление новой записи ---")
        try:
            res = self.db.create_record(
                self._read_int("id: "),
                input("Имя: "),
                input("Фамилия: "),
                self._read_int("Возраст: "),
                input("Пол: ")
            )
            print(f"Успешно добавлено: {res}")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except DatabaseError as e:
            print(f"Системная ошибка СУБД при сохранении: {e}")

    def _find_students(self) -> None:
        print("\n--- Поиск по фильтру (Enter — пропустить поле) ---")

        # Точечная обработка ValueError для фильтрации (Замечание ревью)
        def read_opt_int(prompt: str) -> Optional[int]:
            while True:
                raw = input(prompt).strip()
                if not raw:
                    return None
                try:
                    return int(raw)
                except ValueError:
                    print("Ошибка ввода: требуется целое число. Повторите попытку.")

        sid = read_opt_int("id: ")
        fn = input("Имя: ").strip() or None
        sn = input("Фамилия: ").strip() or None
        age = read_opt_int("Возраст: ")
        sex = input("Пол: ").strip() or None

        try:
            results = self.db.select_record(
                id=sid, first_name=fn, second_name=sn, age=age, sex=sex
            )
            self._print_records(results)
        except DatabaseError as e:
            print(f"Системная ошибка СУБД при чтении: {e}")

    def _sort_students(self) -> None:
        print("\n--- Сортировка записей ---")
        field = input("Введите поле для сортировки (id, first_name, second_name, age, sex): ").strip()
        print("Выберите порядок:")
        print("1. По возрастанию\n2. По убыванию")
        order = input("Ваш выбор: ").strip()

        reverse = True if order == "2" else False

        try:
            sorted_data = self.db.sort_records(field, reverse=reverse)
            print(f"\nРезультат сортировки по полю '{field}':")
            self._print_records(sorted_data)
        except ValueError as e:
            print(f"Ошибка параметров: {e}")
        except DatabaseError as e:
            print(f"Системная ошибка СУБД при обработке: {e}")

    def _print_records(self, records: list) -> None:
        if not records:
            print("Записи не найдены.")
            return
        for record in records:
            print(record)

    def run(self) -> None:
        while True:
            try:
                self._print_menu()
                action = input("Выберите действие: ").strip()
                if action == "1":
                    self._add_student()
                elif action == "2":
                    print("\n--- Все записи ---")
                    self._print_records(self.db.select_record())
                elif action == "3":
                    self._find_students()
                elif action == "4":
                    self._sort_students()
                elif action == "0":
                    print("Выход из программы.")
                    break
                else:
                    print("Неизвестная команда. Повторите ввод.")
            except Exception as e:
                print(f"Непредвиденный сбой приложения: {e}")
