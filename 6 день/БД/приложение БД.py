import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from mysql.connector import Error
import csv

# ========== Параметры подключения - отредактируй ==========
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '2006-Vika',
    'database': 'variant2_work'
}
# ==========================================================

def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к БД:\n{e}")
        return None

def get_tables():
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = %s ORDER BY table_name", (DB_CONFIG['database'],))
        rows = [r[0] for r in cur.fetchall()]
        return rows
    except Error as e:
        messagebox.showerror("Ошибка БД", str(e))
        return []
    finally:
        cur.close()
        conn.close()

def get_table_columns(table_name):
    """
    Возвращает список колонок в порядке ORDINAL_POSITION.
    Каждый элемент: {'name','data_type','is_pk'(bool),'is_auto'(bool),'column_type'}
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, COLUMN_KEY, EXTRA, COLUMN_TYPE
            FROM information_schema.columns
            WHERE table_schema=%s AND table_name=%s
            ORDER BY ORDINAL_POSITION
        """, (DB_CONFIG['database'], table_name))
        cols = []
        for name, data_type, column_key, extra, column_type in cur.fetchall():
            cols.append({
                'name': name,
                'data_type': data_type,
                'is_pk': (column_key == 'PRI'),
                'is_auto': ('auto_increment' in (extra or '').lower()),
                'column_type': column_type
            })
        return cols
    except Error as e:
        messagebox.showerror("Ошибка БД", str(e))
        return []
    finally:
        cur.close()
        conn.close()

class TableFrame:
    def __init__(self, parent, table_name):
        self.parent = parent
        self.table = table_name
        self.columns = get_table_columns(table_name)
        if not self.columns:
            messagebox.showerror("Ошибка", f"Не удалось получить колонки таблицы {table_name}")
            return
        self.build_ui()

    def build_ui(self):
        # Контейнер
        self.frame = tk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)

        # Панель поиска (динамическая)
        search_box = tk.LabelFrame(self.frame, text="Поиск / фильтры")
        search_box.pack(fill='x', padx=8, pady=6)

        self.search_widgets = {}
        row = 0
        for col in self.columns:
            name = col['name']
            dtype = col['data_type']
            # Для текстовых типов — поле "содержит"
            if dtype in ('varchar', 'text', 'char', 'longtext', 'mediumtext'):
                tk.Label(search_box, text=f"{name} содержит:").grid(row=row, column=0, sticky='e', padx=4, pady=2)
                ent = tk.Entry(search_box, width=25)
                ent.grid(row=row, column=1, padx=4, pady=2)
                self.search_widgets[name] = ('like', ent)
                row += 1
            # Для числовых типов — min/max
            elif dtype in ('int','bigint','smallint','decimal','double','float','tinyint','mediumint'):
                tk.Label(search_box, text=f"{name} от:").grid(row=row, column=0, sticky='e', padx=4, pady=2)
                e1 = tk.Entry(search_box, width=12)
                e1.grid(row=row, column=1, padx=4, pady=2, sticky='w')
                tk.Label(search_box, text="до:").grid(row=row, column=2, sticky='e')
                e2 = tk.Entry(search_box, width=12)
                e2.grid(row=row, column=3, padx=4, pady=2, sticky='w')
                self.search_widgets[name] = ('range', (e1, e2))
                row += 1
            # Для дат - от/до как текст (YYYY-MM-DD)
            elif dtype in ('date','datetime','timestamp'):
                tk.Label(search_box, text=f"{name} от (ГГГГ-ММ-ДД):").grid(row=row, column=0, sticky='e', padx=4, pady=2)
                e1 = tk.Entry(search_box, width=14)
                e1.grid(row=row, column=1, padx=4, pady=2, sticky='w')
                tk.Label(search_box, text="до:").grid(row=row, column=2, sticky='e')
                e2 = tk.Entry(search_box, width=14)
                e2.grid(row=row, column=3, padx=4, pady=2, sticky='w')
                self.search_widgets[name] = ('range_str', (e1, e2))
                row += 1
            else:
                # По умолчанию — contains
                tk.Label(search_box, text=f"{name} содержит:").grid(row=row, column=0, sticky='e', padx=4, pady=2)
                ent = tk.Entry(search_box, width=25)
                ent.grid(row=row, column=1, padx=4, pady=2)
                self.search_widgets[name] = ('like', ent)
                row += 1

        tk.Button(search_box, text="🔎 Поиск", command=self.search).grid(row=0, column=6, padx=8, pady=4)
        tk.Button(search_box, text="♻️ Сброс", command=self.reset_search).grid(row=1, column=6, padx=8, pady=4)

        # Поля ввода для CRUD
        input_frm = tk.LabelFrame(self.frame, text="Запись")
        input_frm.pack(fill='x', padx=8, pady=6)

        self.entry_vars = {}
        col_idx = 0
        for col in self.columns:
            name = col['name']
            if col['is_pk'] and col['is_auto']:
                # показываем поле id readonly
                tk.Label(input_frm, text=f"{name}:").grid(row=0, column=col_idx*2, sticky='e', padx=4, pady=4)
                v = tk.Entry(input_frm, width=18)
                v.grid(row=0, column=col_idx*2+1, padx=4, pady=4)
                v.configure(state='readonly')
                self.entry_vars[name] = v
            else:
                tk.Label(input_frm, text=f"{name}:").grid(row=0, column=col_idx*2, sticky='e', padx=4, pady=4)
                v = tk.Entry(input_frm, width=25)
                v.grid(row=0, column=col_idx*2+1, padx=4, pady=4)
                self.entry_vars[name] = v
            col_idx += 1

        # Кнопки CRUD и экспорт
        btn_frm = tk.Frame(self.frame)
        btn_frm.pack(pady=6)
        tk.Button(btn_frm, text="➕ Добавить", command=self.add_record, width=12, bg="#90EE90").grid(row=0, column=0, padx=5)
        tk.Button(btn_frm, text="✏️ Обновить", command=self.update_record, width=12, bg="#FFD700").grid(row=0, column=1, padx=5)
        tk.Button(btn_frm, text="🗑️ Удалить", command=self.delete_record, width=12, bg="#FF6347").grid(row=0, column=2, padx=5)
        tk.Button(btn_frm, text="Очистить", command=self.clear_entries, width=12).grid(row=0, column=3, padx=5)
        tk.Button(btn_frm, text="🔄 Показать всех", command=self.refresh_table, width=12).grid(row=0, column=4, padx=5)
        tk.Button(btn_frm, text="⬇️ Экспорт всех (CSV)", command=self.export_all_csv, width=16).grid(row=0, column=5, padx=8)
        tk.Button(btn_frm, text="⬇️ Экспорт выбранных (CSV)", command=self.export_selected_csv, width=20).grid(row=0, column=6, padx=8)

        # Treeview
        cols = [c['name'] for c in self.columns]
        self.tree = ttk.Treeview(self.frame, columns=cols, show='headings', selectmode='extended')
        for c in cols:
            self.tree.heading(c, text=c)
            # ширина: id узкий, остальное шире
            if c.lower() in ('id','id_','idnumber'):
                self.tree.column(c, width=70, anchor='center')
            else:
                self.tree.column(c, width=150)
        self.tree.pack(fill='both', expand=True, padx=8, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Load initial data
        self.refresh_table()

    def build_select_query(self, use_filters=False):
        base = f"SELECT {', '.join([c['name'] for c in self.columns])} FROM `{self.table}`"
        where = []
        params = []
        if use_filters:
            for name, (mode, widget) in self.search_widgets.items():
                if mode == 'like':
                    val = widget.get().strip()
                    if val:
                        where.append(f"`{name}` LIKE %s")
                        params.append(f"%{val}%")
                elif mode == 'range':
                    a = widget[0].get().strip()
                    b = widget[1].get().strip()
                    if a:
                        where.append(f"`{name}` >= %s")
                        params.append(a)
                    if b:
                        where.append(f"`{name}` <= %s")
                        params.append(b)
                elif mode == 'range_str':
                    a = widget[0].get().strip()
                    b = widget[1].get().strip()
                    if a:
                        where.append(f"`{name}` >= %s")
                        params.append(a)
                    if b:
                        where.append(f"`{name}` <= %s")
                        params.append(b)
        if where:
            base += " WHERE " + " AND ".join(where)
        base += " ORDER BY " + self.columns[0]['name']
        return base, params

    def refresh_table(self):
        conn = get_connection()
        if not conn:
            return
        try:
            q = f"SELECT {', '.join([c['name'] for c in self.columns])} FROM `{self.table}` ORDER BY {self.columns[0]['name']}"
            cur = conn.cursor()
            cur.execute(q)
            rows = cur.fetchall()
            self.tree.delete(*self.tree.get_children())
            for r in rows:
                self.tree.insert("", "end", values=r)
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cur.close()
            conn.close()

    def clear_entries(self):
        for name, widget in self.entry_vars.items():
            widget.configure(state='normal')
            widget.delete(0, tk.END)
            if any(c['name']==name and c['is_pk'] and c['is_auto'] for c in self.columns):
                widget.configure(state='readonly')
        self.tree.selection_remove(self.tree.selection())

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], 'values')
        for i, col in enumerate(self.columns):
            name = col['name']
            w = self.entry_vars.get(name)
            if not w:
                continue
            w.configure(state='normal')
            w.delete(0, tk.END)
            if vals and len(vals) > i:
                w.insert(0, vals[i])
            if col['is_pk'] and col['is_auto']:
                w.configure(state='readonly')

    def validate_and_collect(self, require_pk=False):
        data = {}
        pk_vals = {}
        for col in self.columns:
            n = col['name']
            w = self.entry_vars.get(n)
            if not w:
                continue
            val = w.get().strip()
            if col['is_pk']:
                if require_pk and not val:
                    messagebox.showwarning("Валидация", "Запись не выбрана (PK пустой).")
                    return None, None
                pk_vals[n] = val
                # don't skip for update usage
            # basic numeric validation for numeric types
            if col['data_type'] in ('int','bigint','smallint','mediumint','tinyint'):
                if val=='':
                    data[n] = None
                else:
                    try:
                        data[n] = int(val)
                    except:
                        messagebox.showwarning("Валидация", f"Поле {n} должно быть целым числом.")
                        return None, None
            elif col['data_type'] in ('decimal','double','float'):
                if val=='':
                    data[n] = None
                else:
                    try:
                        data[n] = float(val)
                    except:
                        messagebox.showwarning("Валидация", f"Поле {n} должно быть числом.")
                        return None, None
            else:
                data[n] = val if val!='' else None
        return data, pk_vals

    def add_record(self):
        data, _ = self.validate_and_collect(require_pk=False)
        if data is None:
            return
        # remove auto PKs
        ins_cols = []
        ins_vals = []
        for col in self.columns:
            if col['is_pk'] and col['is_auto']:
                continue
            ins_cols.append(col['name'])
            ins_vals.append(data.get(col['name']))
        placeholders = ", ".join(["%s"] * len(ins_cols))
        q = f"INSERT INTO `{self.table}` ({', '.join(['`'+c+'`' for c in ins_cols])}) VALUES ({placeholders})"
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(q, tuple(ins_vals))
            conn.commit()
            messagebox.showinfo("Успех", "Запись добавлена.")
            self.refresh_table()
            self.clear_entries()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cur.close()
            conn.close()

    def update_record(self):
        data, pk = self.validate_and_collect(require_pk=True)
        if data is None:
            return
        # build SET excluding PKs that are auto and maybe others
        set_parts = []
        params = []
        pk_parts = []
        pk_params = []
        for col in self.columns:
            name = col['name']
            if col['is_pk']:
                pk_parts.append(f"`{name}` = %s")
                pk_params.append(pk.get(name))
            else:
                set_parts.append(f"`{name}` = %s")
                params.append(data.get(name))
        if not pk_parts:
            messagebox.showwarning("Обновление", "В таблице нет PK — обновление не поддерживается.")
            return
        q = f"UPDATE `{self.table}` SET {', '.join(set_parts)} WHERE {' AND '.join(pk_parts)}"
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(q, tuple(params + pk_params))
            conn.commit()
            if cur.rowcount == 0:
                messagebox.showwarning("Обновление", "Запись не найдена или не изменена.")
            else:
                messagebox.showinfo("Успех", "Запись обновлена.")
            self.refresh_table()
            self.clear_entries()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cur.close()
            conn.close()

    def delete_record(self):
        # require PK
        _, pk = self.validate_and_collect(require_pk=True)
        if pk is None:
            return
        if not messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            return
        pk_parts = [f"`{k}` = %s" for k in pk.keys()]
        q = f"DELETE FROM `{self.table}` WHERE {' AND '.join(pk_parts)}"
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(q, tuple(pk.values()))
            conn.commit()
            if cur.rowcount == 0:
                messagebox.showwarning("Удаление", "Запись не найдена.")
            else:
                messagebox.showinfo("Успех", "Запись удалена.")
            self.refresh_table()
            self.clear_entries()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cur.close()
            conn.close()

    def search(self):
        q, params = self.build_select_query(use_filters=True)
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(q, tuple(params))
            rows = cur.fetchall()
            self.tree.delete(*self.tree.get_children())
            for r in rows:
                self.tree.insert("", "end", values=r)
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cur.close()
            conn.close()

    def reset_search(self):
        for mode, widget in self.search_widgets.values():
            if mode == 'like':
                widget.delete(0, tk.END)
            else:
                widget[0].delete(0, tk.END)
                widget[1].delete(0, tk.END)
        self.refresh_table()

    def export_rows_to_csv(self, rows):
        if not rows:
            messagebox.showinfo("Экспорт", "Нет данных для экспорта.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        try:
            # UTF-8 with BOM + semicolon delimiter -> Excel корректно откроет
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                headers = [c['name'] for c in self.columns]
                writer.writerow(headers)
                for r in rows:
                    writer.writerow(r)
            messagebox.showinfo("Экспорт", f"Экспортировано {len(rows)} записей в {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить CSV:\n{e}")

    def export_all_csv(self):
        rows = [self.tree.item(i, 'values') for i in self.tree.get_children()]
        self.export_rows_to_csv(rows)

    def export_selected_csv(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Экспорт", "Нет выбранных записей.")
            return
        rows = [self.tree.item(i, 'values') for i in sel]
        self.export_rows_to_csv(rows)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DB Manager - выбор таблицы")
        self.root.geometry("900x650")
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill='both', expand=True)
        self.current_table_frame = None

        top = tk.Frame(self.main_frame)
        top.pack(fill='x', pady=8)

        tk.Label(top, text="Выберите таблицу:").pack(side='left', padx=8)
        self.table_combo = ttk.Combobox(top, values=get_tables(), state='readonly', width=40)
        self.table_combo.pack(side='left', padx=8)
        tk.Button(top, text="Открыть", command=self.open_table).pack(side='left', padx=6)
        tk.Button(top, text="Обновить список таблиц", command=self.reload_tables).pack(side='left', padx=6)

        # placeholder frame for table UI
        self.container = tk.Frame(self.main_frame)
        self.container.pack(fill='both', expand=True)

        # подсказка
        hint = tk.Label(self.main_frame, text="Примечание: приложение динамически строит форму по структуре таблицы.\nPK с AUTO_INCREMENT отображается как readonly ID.", fg='gray')
        hint.pack(pady=4)

    def reload_tables(self):
        self.table_combo['values'] = get_tables()
        messagebox.showinfo("Готово", "Список таблиц обновлён.")

    def open_table(self):
        tbl = self.table_combo.get().strip()
        if not tbl:
            messagebox.showwarning("Выбор", "Выберите таблицу.")
            return
        # очищаем старую рамку
        for w in self.container.winfo_children():
            w.destroy()
        self.current_table_frame = TableFrame(self.container, tbl)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
