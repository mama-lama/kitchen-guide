import sys
import sqlite3
import csv
from PyQt5 import QtCore

from PIL import Image
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QFileDialog, QTableWidget
from PyQt5.QtWidgets import QLabel, QAbstractItemView, QMessageBox, QHeaderView, QInputDialog


class RecipeTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super(RecipeTableWidget, self).__init__(parent)
        self.setStyleSheet('background-color: white')
        self.mouse_press = None

    def mouseDoubleClickEvent(self, event):
        super(RecipeTableWidget, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.LeftButton:
            self.parentWidget().open_recipe()


class StartForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui_prog/startWindow.ui', self)
        self.setFixedSize(900, 720)
        self.recipesBtn.clicked.connect(self.open_recipe)
        self.myBtn.clicked.connect(self.open_directory)
        self.setWindowIcon(QIcon('web.jpg'))

    def open_recipe(self):
        self.recipe = RecipeForm()
        self.recipe.show()
        self.st_form = StartForm()
        self.st_form.hide()

    def open_directory(self):
        self.directory = DirectoryForm()
        self.directory.show()
        self.st_form = StartForm()
        self.st_form.hide()


class RecipeForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui_prog/recipeWindow.ui', self)
        self.setFixedSize(900, 720)
        self.setWindowIcon(QIcon('web.jpg'))
        self.con = sqlite3.connect("Progect.sqlite")
        self.cur = self.con.cursor()
        self.addBtn.clicked.connect(self.open_addRecipe)
        self.poiskBtn.clicked.connect(self.poiskResipe)
        self.openBtn.clicked.connect(self.open_recipe)
        self.backBtn.clicked.connect(self.back)
        self.tableWidget = RecipeTableWidget(self)
        self.tableWidget.move(360, 10)
        self.tableWidget.resize(521, 611)
        self.ud_date()
        self.run()

    def keyPressEvent(self, event):
        if event.key() == 16777220:
            self.open_recipe()

    def run(self):
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(self.res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.con.commit()
        self.con.close()

    def ud_date(self):
        self.lineDish.clear()
        self.text.clear()
        self.res = self.cur.execute("""SELECT title FROM Dishes""").fetchall()
        self.tip_dish = self.cur.execute("""SELECT title FROM Types""")
        self.tip_dish = [str(i[0]) for i in list(self.tip_dish)] + ['Все']
        self.tipBox.addItems(self.tip_dish)
        self.tipBox.setCurrentIndex(self.tip_dish.index('Все'))
        self.country_dish = self.cur.execute("""SELECT title FROM Country""")
        self.country_dish = [str(i[0]) for i in list(self.country_dish) if len(str(i[0])) > 0]
        self.world_dish = self.cur.execute("""SELECT title FROM World""")
        self.world_dish = [str(i[0]) for i in list(self.world_dish)]
        self.kitchen = self.country_dish + self.world_dish + ['Все']
        self.countryBox.addItems(self.kitchen)
        self.countryBox.setCurrentIndex(self.kitchen.index('Все'))

    def open_addRecipe(self):
        self.addR = AddRecipeForm()
        self.addR.show()
        self.hide()

    def open_recipe(self):
        title = self.tableWidget.currentItem().text()
        self.viewR = ViewRecipe(title)
        self.viewR.show()
        self.hide()

    def back(self):
        self.hide()

    def poiskResipe(self):
        self.con = sqlite3.connect("Progect.sqlite")
        self.cur = self.con.cursor()
        dish = self.lineDish.text().capitalize()
        tipe = self.tipBox.currentText()
        kitchen = self.countryBox.currentText()
        food = self.text.toPlainText()
        regions = [i[0] for i in self.cur.execute("""SELECT title FROM World""").fetchall()]

        if food:
            inf = QMessageBox()
            inf.setWindowTitle("Внимание!!!")
            inf.setText('Поле "Ваши продукты" должно быть заполнено по обрацу:\n'
                        'Продукт1, продукт2, продукт3 и т.д.')
            inf.setIcon(QMessageBox.Warning)
            inf.setStandardButtons(QMessageBox.Ok)
            inf.exec()

        if tipe == 'Все' and kitchen == 'Все' and (len(dish) == 0 or len(food) == 0):
            if len(dish) == 0 and len(food) == 0:
                self.res = self.cur.execute("""SELECT title FROM Dishes""").fetchall()
            elif len(dish) == 0 and len(food) > 0:
                list_dish = tuple(self.choiceOfDishes(0) + ['', ''])
                self.res = self.cur.execute(f"""SELECT title FROM Dishes WHERE title 
                                                IN {list_dish}""").fetchall()

            elif len(dish) > 0 and len(food) == 0:
                self.res = self.cur.execute(f"""SELECT title FROM Dishes WHERE title LIKE '%{dish}%'""").fetchall()

            elif len(dish) > 0 and len(food) > 0:
                list_dish = tuple(self.choiceOfDishes(11, dish))
                self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                                WHERE title LIKE '%{dish}%'
                                                AND title in {list_dish}""").fetchall()

        elif kitchen in regions and tipe == 'Все' and \
                len(dish) == 0 and len(food) == 0:
            self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                            WHERE regions = (SELECT id FROM World
                                            WHERE title = '{kitchen}')""").fetchall()

        elif kitchen != 'Все' and tipe == 'Все' and len(dish) == 0 and len(food) == 0:
            self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                            WHERE kitchen = (SELECT id FROM Country
                                            WHERE title = '{kitchen}')""").fetchall()

        elif tipe != 'Все' and kitchen == 'Все' and len(dish) == 0 and len(food) == 0:
            self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                            WHERE type in (SELECT id FROM Types
                                            WHERE title = '{tipe}')""").fetchall()

        elif tipe != 'Все' and kitchen == 'Все' and (len(dish) > 0 or len(food) > 0):
            if len(dish) > 0 and len(food) == 0:
                self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                                WHERE type = (SELECT id FROM Types
                                                WHERE title = '{tipe}')
                                                AND title LIKE '%{dish}%'""").fetchall()

            if len(dish) == 0 and len(food) > 0:
                list_dish = tuple(self.choiceOfDishes(2, tipe) + ['', ''])
                self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                                WHERE type = (SELECT id FROM Types
                                                WHERE title = '{tipe}')
                                                AND title in {list_dish}""").fetchall()

            if len(dish) > 0 and len(food) > 0:
                list_dish = tuple(self.choiceOfDishes(1, dish, tipe) + ['', ''])
                self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                                WHERE type = (SELECT id FROM Types
                                                WHERE title = '{tipe}')
                                                AND title LIKE '%{dish}'%
                                                AND title in {list_dish}""").fetchall()

        elif tipe == 'Все' and kitchen != 'Все' and (len(dish) > 0 or len(food) > 0):
            if kitchen in regions and len(dish) > 0 and len(food) == 0:
                self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                                WHERE regions = (SELECT id FROM World
                                                WHERE title = '{kitchen}')
                                                AND title LIKE '%{dish}%'""").fetchall()

            elif len(dish) > 0 and len(food) == 0:
                self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                                WHERE kitchen = (SELECT id FROM Country
                                                WHERE title = '{kitchen}')
                                                AND title LIKE '%{dish}%'""", (kitchen, dish)).fetchall()

            elif kitchen in regions and len(dish) == 0 and len(food) > 0:
                list_dish = tuple(self.choiceOfDishes(3, kitchen) + ['', ''])
                self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                                WHERE regions = (SELECT id FROM World
                                                WHERE title = '{kitchen}')
                                                AND title in {list_dish}""").fetchall()

            elif len(dish) == 0 and len(food) > 0:
                list_dish = tuple(self.choiceOfDishes(4, kitchen) + ['', ''])
                self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                                WHERE kitchen = (SELECT id FROM Country
                                                WHERE title = '{kitchen}')
                                                AND title in {list_dish}""", (kitchen, list_dish)).fetchall()

            elif kitchen in regions and len(dish) > 0 and len(food) > 0:
                list_dish = tuple(self.choiceOfDishes(5, kitchen, dish) + ['', ''])
                self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                                WHERE regions = (SELECT id FROM World
                                                WHERE title = '{kitchen}')
                                                AND title LIKE '%{dish}%'
                                                AND title in {list_dish}""").fetchall()

            elif len(dish) > 0 and len(food) > 0:
                list_dish = tuple(self.choiceOfDishes(6, kitchen, dish) + ['', ''])
                self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                                WHERE kitchen = (SELECT id FROM Country
                                                WHERE title = '{kitchen}')
                                                AND title LIKE '%{dish}%'
                                                AND title in {list_dish}""").fetchall()

        elif kitchen in regions and tipe != 'Все' \
                and len(dish) > 0 and len(food) == 0:
            self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                            WHERE regions = (SELECT id FROM World
                                            WHERE title = '{kitchen}')
                                            AND type = (SELECT id FROM Types
                                            WHERE title = '{tipe}')
                                            AND title LIKE '%{dish}%'""").fetchall()

        elif tipe != 'Все' and kitchen != 'Все' and len(dish) > 0 and len(food) == 0:
            self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                            WHERE kitchen = (SELECT id FROM Country
                                            WHERE title = '{kitchen}')
                                            AND type = (SELECT id FROM Types
                                            WHERE title = '{tipe}')
                                            AND title LIKE '%{dish}%'""").fetchall()

        elif kitchen in regions and tipe != 'Все' \
                and len(dish) == 0 and len(food) == 0:
            self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                            WHERE regions = (SELECT id FROM World
                                            WHERE title = '{kitchen}')
                                            AND type = (SELECT id FROM Types
                                            WHERE title = '{tipe}')""").fetchall()

        elif tipe != 'Все' and kitchen != 'Все' and len(dish) == 0 and len(food) == 0:
            self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                            WHERE kitchen = (SELECT id FROM Country
                                            WHERE title = '{kitchen}')
                                            AND type = (SELECT id FROM Types
                                            WHERE title = '{tipe}')""").fetchall()

        elif kitchen in regions and tipe != 'Все' \
                and len(dish) == 0 and len(food) > 0:
            list_dish = tuple(self.choiceOfDishes(7, kitchen, tipe) + ['', ''])
            self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                            WHERE regions = (SELECT id FROM World
                                            WHERE title = '{kitchen}')
                                            AND type = (SELECT id FROM Types
                                            WHERE title = '{tipe}')
                                            AND title in {list_dish}""").fetchall()

        elif tipe != 'Все' and kitchen != 'Все' and len(dish) == 0 and len(food) > 0:
            list_dish = tuple(self.choiceOfDishes(8, kitchen, tipe) + ['', ''])
            self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                            WHERE kitchen = (SELECT id FROM Country
                                            WHERE title = '{kitchen}')
                                            AND type = (SELECT id FROM Types
                                            WHERE title = '{tipe}')
                                            AND title LIKE {list_dish}""").fetchall()

        elif kitchen in regions and tipe != 'Все' \
                and len(dish) > 0 and len(food) > 0:
            list_dish = tuple(self.choiceOfDishes(9, kitchen, tipe, dish) + ['', ''])
            self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                            WHERE regions = (SELECT id FROM World
                                            WHERE title = '{kitchen}')
                                            AND type = (SELECT id FROM Types
                                            WHERE title = '{tipe}')
                                            AND title in {list_dish}
                                            AND title LIKE '%{dish}%'""").fetchall()

        elif tipe != 'Все' and kitchen != 'Все' and len(dish) > 0 and len(food) > 0:
            list_dish = tuple(self.choiceOfDishes(10, kitchen, tipe, dish) + ['', ''])
            self.res = self.cur.execute(f"""SELECT title FROM Dishes
                                            WHERE kitchen = (SELECT id FROM Country
                                            WHERE title = '{kitchen}')
                                            AND type = (SELECT id FROM Types
                                            WHERE title = '{tipe}')
                                            AND title in {list_dish}
                                            AND title LIKE '%{dish}%'""").fetchall()
        self.run()

    def choiceOfDishes(self, n, *args):
        self.con = sqlite3.connect("Progect.sqlite")
        self.cur = self.con.cursor()
        user_ingr = self.text.toPlainText().split(', ')
        if n == 1:
            name, tip = args
            self.res = self.cur.execute(f"""SELECT title, ingredients FROM Dishes
                                            WHERE title = '%{name}%'
                                            AND type = (SELECT id FROM Types
                                            WHERE title = '{tip}'""").fetchall()
        elif n == 0:
            self.res = self.cur.execute("""SELECT title, ingredients FROM Dishes""").fetchall()

        elif n == 2:
            tip = args[0]
            self.res = self.cur.execute(f"""SELECT title, ingredients FROM Dishes
                                            WHERE type = (SELECT id FROM Types
                                            WHERE title = '{tip}')""").fetchall()
        elif n == 3:
            reg = args[0]
            self.res = self.cur.execute(f"""SELECT title, ingredients FROM Dishes
                                            WHERE type = (SELECT id FROM World
                                            WHERE title = '{reg}')""").fetchall()
        elif n == 4:
            cou = args[0]
            self.res = self.cur.execute(f"""SELECT title, ingredients FROM Dishes
                                            WHERE type = (SELECT id FROM Country
                                            WHERE title = {cou})""").fetchall()
        elif n == 5:
            reg, name = args[0], args[1]
            self.res = self.cur.execute(f"""SELECT title, ingredients FROM Dishes
                                            WHERE type = (SELECT id FROM World
                                            WHERE title = '{reg}')
                                            AND title LIKE '%{name}%'""").fetchall()
        elif n == 6:
            cou, name = args[0], args[1]
            self.res = self.cur.execute(f"""SELECT title, ingredients FROM Dishes
                                            WHERE type = (SELECT id FROM Country
                                            WHERE title = '{cou}')
                                            AND title LIKE '%{name}%'""").fetchall()
        elif n == 7:
            reg, tip = args[0], args[1]
            self.res = self.cur.execute(f"""SELECT title, ingredients FROM Dishes
                                            WHERE type = (SELECT id FROM World
                                            WHERE title = '{reg}')
                                            AND type = (SELECT id FROM Types
                                            WHERE title = '{tip}')""").fetchall()
        elif n == 8:
            cou, tip = args
            self.res = self.cur.execute(f"""SELECT title, ingredients FROM Dishes
                                            WHERE type = (SELECT id FROM Country
                                            WHERE title = '{cou}')
                                            AND type = (SELECT id FROM Types
                                            WHERE title = '{tip}')""").fetchall()
        elif n == 9:
            reg, tip, name = args[0], args[1], args[3]
            self.res = self.cur.execute(f"""SELECT title, ingredients FROM Dishes
                                            WHERE type = (SELECT id FROM World
                                            WHERE title = '{reg}')
                                            AND type = (SELECT id FROM Types
                                            WHERE title = '{tip}')
                                            AND title LIKE '%{name}%'""").fetchall()
        elif n == 10:
            cou, tip, name = args[0], args[1], args[2]
            self.res = self.cur.execute(f"""SELECT title, ingredients FROM Dishes
                                            WHERE kitchen = (SELECT id FROM Country
                                            WHERE title = '{cou}')
                                            AND type = (SELECT id FROM Types
                                            WHERE title = '{tip}') 
                                            AND title LIKE '%{name}%'""").fetchall()
        elif n == 11:
            name = args
            self.res = self.cur.execute(f"""SELECT title, ingredients FROM Dishes
                                            WHERE title = '%{name}%'""").fetchall()
        dish = []
        for line in self.res:
            name = line[0]
            ingr = line[1].split('!')
            count = 0
            for i in user_ingr:
                for j in ingr:
                    if i.capitalize() in j or i.lower() in j:
                        count += 1
                if count:
                    dish.append(name)
        return dish


class ViewRecipe(QMainWindow):
    def __init__(self, dish):
        super().__init__()
        self.initUI(dish)

    def initUI(self, dish):
        uic.loadUi('ui_prog/recipe.ui', self)
        self.setFixedSize(900, 720)
        self.setWindowIcon(QIcon('web.jpg'))
        self.backBtn.clicked.connect(self.back)
        self.con = sqlite3.connect("Progect.sqlite")
        self.cur = self.con.cursor()
        ingred = self.cur.execute(f"""SELECT ingredients FROM Dishes
                                      WHERE title = '{dish}'""").fetchall()
        process = self.cur.execute(f"""SELECT process FROM Dishes
                                       WHERE title = '{dish}'""").fetchall()
        tip = self.cur.execute(f"""SELECT title FROM Types
                                   WHERE id = (SELECT type FROM Dishes
                                   WHERE title = '{dish}')""").fetchall()
        country = self.cur.execute(f"""SELECT title FROM Country
                                       WHERE id = (SELECT kitchen FROM Dishes
                                       WHERE title = '{dish}')""").fetchall()
        portions = self.cur.execute(f"""SELECT portions FROM Dishes
                                         WHERE title = '{dish}'""").fetchall()
        regions = self.cur.execute(f"""SELECT title FROM World
                                       WHERE id = (SELECT regions FROM Dishes
                                       WHERE title = '{dish}')""").fetchall()
        calories = self.cur.execute(f"""SELECT calories FROM Dishes
                                        WHERE title = '{dish}'""").fetchall()
        picture = self.cur.execute(f"""SELECT picture FROM Dishes
                                       WHERE title = '{dish}'""").fetchall()
        self.con.commit()
        self.con.close()

        self.nameLable.setText(dish)
        self.portionLabel.setText(f"Порций: {portions[0][0]}")
        self.typeLabel.setText(f"{tip[0][0]}")
        self.text.setText("Ингредиенты:")
        for i in ingred[0][0].split('!'):
            self.text.append(i)
        self.text.append(f"\nПроцесс:\n{process[0][0]}\n")
        if country:
            self.text.append(f"Кухня: {country[0][0]}\n")
        if regions:
            self.text.append(f"Регион: {regions[0][0]}\n")
        if calories[0][0] is not None:
            self.text.append(f"Калорий: {calories[0][0]}")
        if picture[0][0] is not None:
            a = "imgs/" + picture[0][0]
            pic = self.compress_photo(a)
            self.pixmap = QPixmap(pic)
            self.image = QLabel(self)
            self.image.move(450, 5)
            self.image.resize(400, 200)
            self.image.setPixmap(self.pixmap)

    def compress_photo(self, pict):
        im = Image.open(pict)
        im2 = im.resize((400, 200))
        im2.save(pict)
        return pict

    def back(self):
        self.rec_form = RecipeForm()
        self.rec_form.show()
        self.hide()


class AddRecipeForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui_prog/addRecipe.ui', self)
        self.setFixedSize(900, 720)
        self.setWindowIcon(QIcon('web.jpg'))
        self.con = sqlite3.connect("Progect.sqlite")
        self.cur = self.con.cursor()
        self.tip_dish = self.cur.execute("""SELECT title FROM Types""")
        self.pict = ''
        self.tip_dish = [str(i[0]) for i in list(self.tip_dish)]
        self.typeBox.addItems(self.tip_dish)
        self.world_dish = self.cur.execute("""SELECT title FROM World""")
        self.world_dish = [str(i[0]) for i in list(self.world_dish)] + ['Другое']
        self.regionBox.addItems(self.world_dish)
        self.country_dish = self.cur.execute("""SELECT title FROM Country""")
        self.country_dish = [str(i[0]) for i in self.country_dish]
        self.addBtn.clicked.connect(self.add_recipe)
        self.pictureBtn.clicked.connect(self.picture)
        self.backBtn.clicked.connect(self.back)
        self.portionBox.setMinimum(2)
        self.portionBox.setMaximum(36)
        dlg = QInputDialog(self)
        dlg.setInputMode(QInputDialog.TextInput)
        dlg.resize(500, 100)
        count, ok_pressed = dlg.getInt(
            self, "Количество ингредиентов", "Сколько будет ингредиентов?                                  ",
            4, 1, 999, 1)
        self.tableIngr.setColumnCount(2)
        for i in range(count):
            self.tableIngr.setRowCount(count)
            for j in range(2):
                self.tableIngr.setItem(
                    i, j, QTableWidgetItem())
        self.tableIngr.resizeColumnsToContents()
        self.tableIngr.setHorizontalHeaderLabels(['Ингредиент', 'Количество'])
        header = self.tableIngr.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

    def save_2_csv(self):
        with open('ingr.csv', 'w', newline='') as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='"',
                quoting=csv.QUOTE_MINIMAL)
            writer.writerow(
                [self.tableIngr.horizontalHeaderItem(i).text()
                 for i in range(self.tableIngr.columnCount())])
            for i in range(self.tableIngr.rowCount()):
                row = []
                for j in range(self.tableIngr.columnCount()):
                    item = self.tableIngr.item(i, j)
                    if item is not None:
                        row.append(item.text())
                writer.writerow(row)

    def picture(self):
        self.pict = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Картинка (*.jpg);;Все файлы (*)')[0]
        img = Image.open(self.pict)
        img.save(f"imgs/{self.pict.split('/')[-1]}")

    def search_region(self, r):
        self.reg = self.cur.execute(f"""SELECT id FROM World
                                                WHERE title = '{r}'""").fetchall()[0][0]

    def search_country(self, c):
        if c not in self.country_dish:
            self.cur.execute(f"INSERT INTO Country(title) VALUES('{c}')")
        self.cou = self.cur.execute(f"""SELECT id FROM Country
                                                WHERE title = '{c}'""").fetchall()[0][0]

    def search_type(self, t):
        self.tip = self.cur.execute(f"""SELECT id FROM Types
                                        WHERE title = '{t}'""").fetchall()
        return self.tip[0][0]

    def add_recipe(self):
        try:
            self.save_2_csv()
            name = self.nameLine.text()
            with open("ingr.csv") as csvf:
                reader = csv.reader(csvf, delimiter=';', quotechar='"')
                ingr = ''
                title = next(reader)
                for index, row in enumerate(reader):
                    titl, kol = row
                    strok = f"{titl}: {kol}!"
                    ingr += strok
            portion = self.portionBox.value()
            process = self.textProcess.toPlainText()
            region = self.regionBox.currentText()
            country = self.kitchenLine.text()
            tipe = self.search_type(self.typeBox.currentText())
            calories = self.caloriesBox.value()
            pict = self.pict.split('/')[-1]
            if name and ingr and portion and process and tipe:
                if region != 'Другое' and len(country) == 0 and calories < 1 and len(pict) == 0:
                    self.search_region(region)
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type, regions, portions) "
                                     "VALUES(?, ?, ?, ?, ?, ?)", (name, ingr, process, tipe, self.reg, portion))

                elif region != 'Другое' and len(country) > 0 and calories < 1 and len(pict) == 0:
                    self.search_region(region)
                    self.search_country(country)
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type, kitchen,"
                                     " regions, portions) VALUES(?, ?, ?, ?, ?, ?, ?)",
                                     (name, ingr, process, tipe, self.cou, self.reg, portion))

                elif region != 'Другое' and len(country) > 0 and calories < 1 and len(pict) == 0:
                    calories = int(calories)
                    self.search_region(region)
                    self.search_country(country)
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type, kitchen, regions,"
                                     " portions, calories) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                                     (name, ingr, process, tipe, self.cou, self.reg, portion, calories))

                elif region != 'Другое' and len(country) > 0 and calories > 0 and len(pict) > 0:
                    calories = int(calories)
                    self.search_region(region)
                    self.search_country(country)
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, "
                                     "process, type, kitchen, regions, portions, calories, picture) "
                                     "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                     (name, ingr, process, tipe, self.cou, self.reg, portion, calories, pict))

                elif region != 'Другое' and len(country) > 0 and calories < 1 and len(pict) > 0:
                    self.search_region(region)
                    self.search_country(country)
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type, kitchen, "
                                     "regions, portions, picture) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                                     (name, ingr, process, tipe, self.cou, self.reg, portion, pict))

                elif region == 'Другое' and len(country) > 0 and calories > 0 and len(pict) > 0:
                    calories = int(calories)
                    self.search_country(country)
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type, kitchen, "
                                     "portions, picture, calories) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                                     (name, ingr, process, tipe, self.cou, portion, pict, calories))

                elif region == 'Другое' and len(country) > 0 and calories < 1 and len(pict) == 0:
                    self.search_country(country)
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type, kitchen, portions) "
                                     "VALUES(?, ?, ?, ?, ?, ?)", (name, ingr, process, tipe, self.cou, portion))

                elif region == 'Другое' and len(country) == 0 and calories > 0 and len(pict) == 0:
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type, calories, portions) "
                                     "VALUES(?, ?, ?, ?, ?, ?)", (name, ingr, process, tipe, calories, portion))

                elif region == 'Другое' and len(country) == 0 and calories < 1 and len(pict) > 0:
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type, picture, portions) "
                                     "VALUES(?, ?, ?, ?, ?, ?)", (name, ingr, process, tipe, pict, portion))

                elif region != 'Другое' and len(country) == 0 and calories > 0 and len(pict) == 0:
                    calories = int(calories)
                    self.search_region(region)
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type, regions,"
                                     " portions, calories) VALUES(?, ?, ?, ?, ?, ?, ?)",
                                     (name, ingr, process, tipe, self.reg, portion, calories))

                elif region != 'Другое' and len(country) == 0 and calories < 1 and len(pict) > 0:
                    self.search_region(region)
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type,"
                                     "regions, portions, picture) VALUES(?, ?, ?, ?, ?, ?, ?)",
                                     (name, ingr, process, tipe, self.reg, portion, pict))

                elif region == 'Другое' and len(country) > 0 and calories > 0 and len(pict) == 0:
                    calories = int(calories)
                    self.search_country(country)
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type, kitchen, "
                                     "portions, calories) VALUES(?, ?, ?, ?, ?, ?, ?)",
                                     (name, ingr, process, tipe, self.cou, portion, calories))

                elif region == 'Другое' and len(country) > 0 and calories > 0 and len(pict) == 0:
                    calories = int(calories)
                    self.search_country(country)
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type, kitchen, "
                                     "portions, calories) VALUES(?, ?, ?, ?, ?, ?, ?)",
                                     (name, ingr, process, tipe, self.cou, portion, calories))

                elif region == 'Другое' and len(country) == 0 and calories > 0 and len(pict) > 0:
                    calories = int(calories)
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type, "
                                     "portions, calories, picture) VALUES(?, ?, ?, ?, ?, ?, ?)",
                                     (name, ingr, process, tipe, portion, calories, pict))

                elif region == 'Другое' and len(country) == 0 and calories < 1 and len(pict) == 0:
                    self.cur.execute("INSERT INTO 'Dishes'(title, ingredients, process, type, portions) "
                                     "VALUES(?, ?, ?, ?, ?)", (name, ingr, process, tipe, portion))

                self.con.commit()
                self.con.close()
                self.back()

            else:
                error = QMessageBox()
                error.setWindowTitle("Ошибка!!!")
                error.setText('Обязательно должны быть заполнены поля:\n'
                              '"Название", "Ингредиенты", "Процесс", "Порции", "Тип блюда".')
                error.setIcon(QMessageBox.Critical)
                error.setStandardButtons(QMessageBox.Ok)
                error.exec()

        except sqlite3.IntegrityError:
            error = QMessageBox()
            error.setWindowTitle("Ошибка!!!")
            error.setText('Такое название уже есть в базе.\n'
                          'Попробуйте другое.')
            error.setIcon(QMessageBox.Critical)
            error.setStandardButtons(QMessageBox.Ok)
            error.exec()

    def back(self):
        self.rec = RecipeForm()
        self.rec.show()
        self.hide()


class DirectioryTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super(DirectioryTableWidget, self).__init__(parent)
        self.setStyleSheet('background-color: white')
        self.mouse_press = None

    def mouseDoubleClickEvent(self, event):
        super(DirectioryTableWidget, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.LeftButton:
            self.parentWidget().open_directory()


class DirectoryForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui_prog/directoryWindow.ui', self)
        self.setFixedSize(900, 720)
        self.setWindowIcon(QIcon('web.jpg'))
        self.addBtn.clicked.connect(self.open_addDirectory)
        self.openBtn.clicked.connect(self.open_directory)
        self.backBtn.clicked.connect(self.back)
        self.poiskBtn.clicked.connect(self.poisk)
        self.con = sqlite3.connect("Progect.sqlite")
        self.cur = self.con.cursor()
        self.res = self.cur.execute("""SELECT title FROM Directory""")
        self.tableWidget = DirectioryTableWidget(self)
        self.tableWidget.move(10, 80)
        self.tableWidget.resize(881, 481)
        self.run()

    def keyPressEvent(self, event):
        if event.key() == 16777220:
            self.open_directory()

    def poisk(self):
        self.con = sqlite3.connect("Progect.sqlite")
        self.cur = self.con.cursor()
        title = self.statyaLine.text().capitalize()
        if title:
            self.res = self.cur.execute(f"""SELECT title FROM Directory
                                            WHERE title LIKE '%{title}%'""")
        else:
            self.res = self.cur.execute("""SELECT title FROM Directory""")

        self.run()

    def run(self):
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(self.res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.con.commit()
        self.con.close()

    def open_addDirectory(self):
        self.addD = AddDirectoryForm()
        self.addD.show()
        self.hide()

    def open_directory(self):
        title = self.tableWidget.currentItem().text()
        self.viewD = ViewDirectoryForm(title)
        self.viewD.show()
        self.hide()

    def back(self):
        self.hide()


class ViewDirectoryForm(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.initUI(title)

    def initUI(self, title):
        uic.loadUi('ui_prog/directory.ui', self)
        self.setFixedSize(900, 720)
        self.setWindowIcon(QIcon('web.jpg'))
        self.backBtn.clicked.connect(self.back)
        self.con = sqlite3.connect("Progect.sqlite")
        self.cur = self.con.cursor()
        inf = self.cur.execute(f"""SELECT information FROM Directory WHERE title = '{title}'""").fetchall()[0][0]
        self.titleLine.setText(title)
        self.text.setText(f"Совет:\n{inf}")

    def back(self):
        self.direc_form = DirectoryForm()
        self.direc_form.show()
        self.hide()


class AddDirectoryForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui_prog/addDirectory.ui', self)
        self.setFixedSize(900, 720)
        self.setWindowIcon(QIcon('web.jpg'))
        self.con = sqlite3.connect("Progect.sqlite")
        self.cur = self.con.cursor()
        self.addBtn.clicked.connect(self.addDirectory)
        self.backBtn.clicked.connect(self.back)

    def addDirectory(self):
        self.con = sqlite3.connect("Progect.sqlite")
        self.cur = self.con.cursor()
        title = self.titleLine.text()
        inf = self.textEdit.toPlainText()
        try:
            if title and inf:
                self.cur.execute("INSERT INTO Directory(title, information) "
                                 "VALUES(?, ?)", (title, inf))
                self.con.commit()
                self.con.close()
                self.back()
            else:
                error = QMessageBox()
                error.setWindowTitle("Ошибка!!!")
                error.setText('Обязательно должны быть заполнены поля:\n'
                              '"Название", "Информация".')
                error.setIcon(QMessageBox.Critical)
                error.setStandardButtons(QMessageBox.Ok)
                error.exec()

        except sqlite3.IntegrityError:
            error = QMessageBox()
            error.setWindowTitle("Ошибка!!!")
            error.setText('Такое название уже есть в базе.\n'
                          'Попробуйте другое.')
            error.setIcon(QMessageBox.Critical)
            error.setStandardButtons(QMessageBox.Ok)
            error.exec()

    def back(self):
        self.direc_form = DirectoryForm()
        self.direc_form.show()
        self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StartForm()
    ex.show()
    sys.exit(app.exec_())
