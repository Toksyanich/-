import win32com.client as win32
import os


def solve_in_excel():
    # --- 1. Подготовка ---
    excel = None
    try:
        # Создаем экземпляр Excel. Делаем его видимым для наглядности.
        excel = win32.Dispatch("Excel.Application")
        excel.Visible = True

        # Создаем новую рабочую книгу
        workbook = excel.Workbooks.Add()
        worksheet = workbook.Worksheets("Лист1")

        # --- 2. Заполнение данных и формул в ячейках ---
        print("Заполнение Excel данными...")
        # Заголовки
        worksheet.Cells(1, "B").Value = "Regular (x_R)"
        worksheet.Cells(1, "C").Value = "Extra (x_E)"
        worksheet.Cells(1, "D").Value = "Puppy Delite (x_P)"
        worksheet.Cells(1, "F").Value = "Расход"
        worksheet.Cells(1, "G").Value = "Знак"
        worksheet.Cells(1, "H").Value = "Запас"

        # Прибыль
        worksheet.Cells(2, "A").Value = "Прибыль"
        worksheet.Cells(2, "B").Value = 20
        worksheet.Cells(2, "C").Value = 18
        worksheet.Cells(2, "D").Value = 25

        # Переменные решения (сюда Solver запишет результат)
        worksheet.Cells(3, "A").Value = "План (кг)"
        worksheet.Cells(3, "B").Value = 0  # Начальное значение
        worksheet.Cells(3, "C").Value = 0  # Начальное значение
        worksheet.Cells(3, "D").Value = 0  # Начальное значение

        # Целевая функция (Общая прибыль)
        worksheet.Cells(4, "A").Value = "Общая прибыль"
        worksheet.Cells(4, "E").Formula = "=SUMPRODUCT(B2:D2, B3:D3)"

        # Ограничения
        # Ингредиент А
        worksheet.Cells(6, "A").Value = "Ингредиент A"
        worksheet.Cells(6, "B").Value = 1/3
        worksheet.Cells(6, "C").Value = 0.5
        worksheet.Cells(6, "D").Value = 0
        worksheet.Cells(6, "F").Formula = "=SUMPRODUCT(B6:D6, $B$3:$D$3)"
        worksheet.Cells(6, "G").Value = "<="
        worksheet.Cells(6, "H").Value = 1900

        # Ингредиент B
        worksheet.Cells(7, "A").Value = "Ингредиент B"
        worksheet.Cells(7, "B").Value = 1/3
        worksheet.Cells(7, "C").Value = 0.25
        worksheet.Cells(7, "D").Value = 0.1
        worksheet.Cells(7, "F").Formula = "=SUMPRODUCT(B7:D7, $B$3:$D$3)"
        worksheet.Cells(7, "G").Value = "<="
        worksheet.Cells(7, "H").Value = 1100

        # Ингредиент C
        worksheet.Cells(8, "A").Value = "Ингредиент C"
        worksheet.Cells(8, "B").Value = 1/3
        worksheet.Cells(8, "C").Value = 0.25
        worksheet.Cells(8, "D").Value = 0.9
        worksheet.Cells(8, "F").Formula = "=SUMPRODUCT(B8:D8, $B$3:$D$3)"
        worksheet.Cells(8, "G").Value = "<="
        worksheet.Cells(8, "H").Value = 1000

        # --- 3. Настройка и запуск "Поиска решения" (Solver) ---
        print("Настройка и запуск Поиска решения...")

        # Полный путь к ячейкам
        obj_cell = worksheet.Range("E4").GetAddress(True, True, 1)
        var_cells = worksheet.Range("B3:D3").GetAddress(True, True, 1)

        # Сбрасываем предыдущие настройки Solver
        excel.Application.Run("SolverReset")

        # Настраиваем Solver
        # SolverOk(Целевая_ячейка, Тип_оптимизации (1=Max), Ячейки_переменных)
        excel.Application.Run("SolverOk", obj_cell, 1, var_cells)

        # Добавляем ограничения
        # SolverAdd(Левая_часть, Отношение (1 for <=), Правая_часть)
        excel.Application.Run("SolverAdd", worksheet.Range(
            "F6").GetAddress(), 1, worksheet.Range("H6").GetAddress())
        excel.Application.Run("SolverAdd", worksheet.Range(
            "F7").GetAddress(), 1, worksheet.Range("H7").GetAddress())
        excel.Application.Run("SolverAdd", worksheet.Range(
            "F8").GetAddress(), 1, worksheet.Range("H8").GetAddress())

        # Указываем, что переменные неотрицательные
        # 5 означает, что переменные >= 0
        excel.Application.Run("SolverAdd", var_cells, 5, "integer")

        # Запускаем решение и генерируем отчет об устойчивости
        # SolverSolve(UserFinish, ShowRef)
        # Reports:=Array(2) означает "создать отчет об устойчивости"
        excel.Application.Run("SolverSolve", True)
        excel.Application.Run("SolverFinish", Reports=2)

        print("\nРешение найдено! Отчет об устойчивости создан в новой вкладке Excel.")
        print("Для продолжения закройте Excel.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        print("Убедитесь, что Excel установлен и надстройка 'Поиск решения' включена.")
    finally:
        # Закрываем Excel (если он был открыт)
        if excel:
            # workbook.Close(False) # Закрыть без сохранения
            # excel.Quit()
            # Важно! Если оставить Excel открытым, процесс может "зависнуть" в памяти.
            # Но для демонстрации мы его оставим открытым, чтобы вы увидели результат.
            # В реальном скрипте нужно раскомментировать строки выше.
            pass


# Запускаем функцию
solve_in_excel()
