import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library (Личная кинотека)")
        self.root.geometry("900x600")
        
        # Файл для хранения данных
        self.data_file = "movies.json"
        self.movies = []
        
        # Доступные жанры
        self.genres = [
            "Все", "Боевик", "Комедия", "Драма", "Фантастика", 
            "Ужасы", "Триллер", "Мелодрама", "Документальный", 
            "Приключения", "Детектив", "Мультфильм", "Аниме"
        ]
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных
        self.load_movies()
        
    def create_widgets(self):
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление фильма", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Поля ввода
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w", pady=5)
        self.title_entry = ttk.Entry(input_frame, width=40)
        self.title_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        ttk.Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky="w", pady=5)
        self.genre_combo = ttk.Combobox(input_frame, values=self.genres[1:], width=37)
        self.genre_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        ttk.Label(input_frame, text="Год выпуска:").grid(row=2, column=0, sticky="w", pady=5)
        self.year_entry = ttk.Entry(input_frame, width=40)
        self.year_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        ttk.Label(input_frame, text="Рейтинг (0-10):").grid(row=3, column=0, sticky="w", pady=5)
        self.rating_entry = ttk.Entry(input_frame, width=40)
        self.rating_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Кнопка добавления
        self.add_button = ttk.Button(input_frame, text="Добавить фильм", command=self.add_movie)
        self.add_button.grid(row=4, column=0, columnspan=3, pady=10)
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        ttk.Label(filter_frame, text="По жанру:").grid(row=0, column=0, sticky="w", pady=5)
        self.filter_genre_combo = ttk.Combobox(filter_frame, values=self.genres, width=18)
        self.filter_genre_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_genre_combo.set("Все")
        self.filter_genre_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        ttk.Label(filter_frame, text="По году:").grid(row=0, column=2, sticky="w", pady=5, padx=(20, 5))
        self.filter_year_entry = ttk.Entry(filter_frame, width=15)
        self.filter_year_entry.grid(row=0, column=3, padx=5, pady=5)
        
        self.filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filters)
        self.filter_button.grid(row=0, column=4, padx=10, pady=5)
        
        self.clear_filter_button = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.clear_filters)
        self.clear_filter_button.grid(row=0, column=5, padx=10, pady=5)
        
        # Таблица для отображения фильмов
        table_frame = ttk.LabelFrame(self.root, text="Список фильмов", padding="10")
        table_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Настройка колонок
        columns = ("title", "genre", "year", "rating")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("title", text="Название")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год выпуска")
        self.tree.heading("rating", text="Рейтинг")
        
        self.tree.column("title", width=300)
        self.tree.column("genre", width=150)
        self.tree.column("year", width=100)
        self.tree.column("rating", width=100)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Кнопка удаления
        self.delete_button = ttk.Button(table_frame, text="Удалить выбранный фильм", command=self.delete_movie)
        self.delete_button.grid(row=1, column=0, pady=10)
        
        # Настройка расширения
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
    def validate_input(self, title, genre, year_str, rating_str):
        """Валидация введенных данных"""
        if not title.strip():
            messagebox.showerror("Ошибка", "Введите название фильма")
            return False
            
        if not genre:
            messagebox.showerror("Ошибка", "Выберите жанр фильма")
            return False
            
        try:
            year = int(year_str)
            current_year = datetime.now().year
            if year < 1888 or year > current_year:
                messagebox.showerror("Ошибка", f"Год должен быть между 1888 и {current_year}")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть числом")
            return False
            
        try:
            rating = float(rating_str)
            if rating < 0 or rating > 10:
                messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 10")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом от 0 до 10")
            return False
            
        return True
        
    def add_movie(self):
        """Добавление нового фильма"""
        title = self.title_entry.get()
        genre = self.genre_combo.get()
        year_str = self.year_entry.get()
        rating_str = self.rating_entry.get()
        
        if self.validate_input(title, genre, year_str, rating_str):
            movie = {
                "title": title.strip(),
                "genre": genre,
                "year": int(year_str),
                "rating": float(rating_str)
            }
            
            self.movies.append(movie)
            self.save_movies()
            self.update_table()
            self.clear_input_fields()
            messagebox.showinfo("Успех", f"Фильм '{title}' добавлен в библиотеку")
            
    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите фильм для удаления")
            return
            
        item = self.tree.item(selected_item)
        movie_title = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить фильм '{movie_title}'?"):
            # Поиск и удаление фильма из списка
            self.movies = [m for m in self.movies if not (m['title'] == item['values'][0] and 
                                                         m['genre'] == item['values'][1] and 
                                                         m['year'] == item['values'][2] and 
                                                         m['rating'] == item['values'][3])]
            self.save_movies()
            self.update_table()
            
    def apply_filters(self, event=None):
        """Применение фильтров"""
        filtered_movies = self.movies.copy()
        
        # Фильтр по жанру
        selected_genre = self.filter_genre_combo.get()
        if selected_genre and selected_genre != "Все":
            filtered_movies = [m for m in filtered_movies if m['genre'] == selected_genre]
            
        # Фильтр по году
        year_filter = self.filter_year_entry.get()
        if year_filter:
            try:
                year = int(year_filter)
                filtered_movies = [m for m in filtered_movies if m['year'] == year]
            except ValueError:
                messagebox.showerror("Ошибка", "Год в фильтре должен быть числом")
                return
                
        self.update_table(filtered_movies)
        
    def clear_filters(self):
        """Сброс фильтров"""
        self.filter_genre_combo.set("Все")
        self.filter_year_entry.delete(0, tk.END)
        self.update_table()
        
    def update_table(self, movies=None):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Если фильмы не переданы, показываем все
        if movies is None:
            movies = self.movies
            
        # Добавление фильмов в таблицу
        for movie in movies:
            self.tree.insert("", "end", values=(
                movie['title'],
                movie['genre'],
                movie['year'],
                movie['rating']
            ))
            
    def clear_input_fields(self):
        """Очистка полей ввода"""
        self.title_entry.delete(0, tk.END)
        self.genre_combo.set('')
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)
        
    def save_movies(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as file:
                json.dump(self.movies, file, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
            
    def load_movies(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as file:
                    self.movies = json.load(file)
                self.update_table()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
                self.movies = []
        else:
            # Создание пустого файла при первом запуске
            self.save_movies()

def main():
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()

if __name__ == "__main__":
    main()
