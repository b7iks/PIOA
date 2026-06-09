from db.backend.memory import DatabaseError


class StudentTUI:
    """Класс текстового пользовательского интерфейса СУБД."""

    def __init__(self, db):
        """Инициализация TUI с внедрением зависимости объекта базы данных."""
        self.db = db

    def _print_menu(self) -> None:
        """Вывод главного меню в консоль."""
        print("\n=== База студентов (ООП) ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти по фильтру")
        print("4. Сортировать записи (Доп. задание)")
        print("0. Выход")

    def _read_int(self, prompt: str) -> int:
        """Безопасное чтение целого числа из консоли."""
        while True:
            try:
                return int(input(prompt).strip())
            except ValueError:
                print("Ошибка: введите целое число.")

    def _add_student(self) -> None:
        """Интерфейс добавления нового студента."""
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
            print(f"Критическая ошибка базы данных при сохранении: {e}")

    def _find_students(self) -> None:
        """Интерфейс поиска студентов по фильтрам."""
        print("\n--- Поиск по фильтру (Enter — пропустить поле) ---")

        def read_opt_int(prompt):
            raw = input(prompt).strip()
            return int(raw) if raw else None

        sid = read_opt_int("id: ")
        fn = input("Имя: ").strip() or None
        sn = input("Фамилия: ").strip() or None
        age = read_opt_int("Возраст: ")
        sex = input("Пол: ").strip() or None

        try:
            results = self.db.select_record(
                student_id=sid, first_name=fn, second_name=sn, age=age, sex=sex
            )
            self._print_records(results)
        except DatabaseError as e:
            print(f"Критическая ошибка базы данных при чтении: {e}")

    def _sort_students(self) -> None:
        """Интерфейс сортировки записей по выбранному полю."""
        print("\n--- Сортировка записей ---")
        field = input("Введите поле для сортировки (id, first_name, second_name, age, sex): ").strip().lower()
        print("Выберите порядок:")
        print("1. По возрастанию (А-Я, 0-9)")
        print("2. По убыванию (Я-А, 9-0)")
        order = input("Ваш выбор: ").strip()

        reverse = True if order == "2" else False

        try:
            sorted_data = self.db.sort_records(field, reverse=reverse)
            print(f"\nРезультат сортировки по полю '{field}':")
            self._print_records(sorted_data)
        except ValueError as e:
            print(f"Ошибка: {e}")
        except DatabaseError as e:
            print(f"Критическая ошибка базы данных при обработке данных: {e}")

    def _print_records(self, records: list) -> None:
        """Вспомогательный метод вывода списка записей."""
        if not records:
            print("Записи не найдены.")
            return
        for record in records:
            print(record)

    def run(self) -> None:
        """Основной цикл обработки команд пользователя."""
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
                    print("Выход из программы. Пока!")
                    break
                else:
                    print("Неизвестная команда. Повторите ввод.")
            except DatabaseError as e:
                print(f"Общая ошибка СУБД: {e}")
            except Exception as e:
                print(f"Непредвиденная системная ошибка приложения: {e}")
