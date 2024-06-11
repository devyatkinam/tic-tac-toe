import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, \
    QFrame, QWidget, QMessageBox, QFileDialog, QMenuBar, QAction, QSizePolicy, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSize, Qt, QTimer


class PlayerDisplay(QWidget):
    def __init__(self, player_image, player_name='Игрок'):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.label = QLabel(self)
        self.setImage(player_image)
        self.layout.addWidget(self.label, alignment=Qt.AlignHCenter)

        self.indicator = QFrame(self)
        self.indicator.setFrameShape(QFrame.HLine)
        self.indicator.setFrameShadow(QFrame.Sunken)
        self.indicator.setStyleSheet("background-color: #344C11")
        self.indicator.setFixedHeight(4)
        self.layout.addWidget(self.indicator, alignment=Qt.AlignHCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addSpacing(5)

        self.indicator.setVisible(False)

        self.nameLineEdit = QLineEdit(self)
        self.nameLineEdit.setText(player_name)
        self.nameLineEdit.textChanged.connect(self.updateName)
        self.layout.addWidget(self.nameLineEdit, alignment=Qt.AlignHCenter)
        self.layout.addSpacing(5)

        self.indicator.setVisible(False)

        self.uploadButton = QPushButton("Загрузить фото", self)
        self.uploadButton.clicked.connect(self.uploadImage)
        self.layout.addWidget(self.uploadButton, alignment=Qt.AlignHCenter)
        self.layout.addSpacing(5)

    def setImage(self, image_path):
        self.label.setPixmap(QPixmap(image_path).scaled(100, 100, Qt.KeepAspectRatio))

    def updateName(self):
        self.nameLineEdit.setText(self.nameLineEdit.text().strip())

    def setActive(self, active):
        self.indicator.setVisible(active)

    def uploadImage(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть", "", "Картинки (*.png *.jpg *.bmp)")
        if file_name:
            self.setImage(file_name)


class MiniBoard(QWidget):
    def __init__(self, mainGame, boardRow, boardCol):
        super().__init__()
        self.mainGame = mainGame
        self.boardRow = boardRow
        self.boardCol = boardCol
        self.layout = QGridLayout(self)
        self.buttons = [[QPushButton(self) for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                self.layout.addWidget(self.buttons[i][j], i, j)
                self.buttons[i][j].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.buttons[i][j].setStyleSheet("color: #E8E1DB; font-size: 20px;")
                self.buttons[i][j].clicked.connect(lambda _, x=i, y=j: self.handleMove(x, y))

        self.winner = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        button_size = min(self.width() // 3, self.height() // 3)
        for row in self.buttons:
            for button in row:
                button.setFixedSize(button_size, button_size)

    def handleMove(self, x, y):
        if self.buttons[x][y].text() == '' and not self.winner:
            self.buttons[x][y].setText(self.mainGame.currentPlayer)
            self.checkMiniBoardWinner()
            self.mainGame.switchPlayer()
            if self.mainGame.miniBoards[x][y].winner is None:
                self.mainGame.setNextBoard(x, y)
            else:
                self.mainGame.setNextBoard(None, None)
            self.mainGame.checkWinner()

    def checkMiniBoardWinner(self):
        lines = [
            [self.buttons[i][0].text() for i in range(3)],
            [self.buttons[i][1].text() for i in range(3)],
            [self.buttons[i][2].text() for i in range(3)],
            [self.buttons[0][i].text() for i in range(3)],
            [self.buttons[1][i].text() for i in range(3)],
            [self.buttons[2][i].text() for i in range(3)],
            [self.buttons[i][i].text() for i in range(3)],
            [self.buttons[i][2 - i].text() for i in range(3)]
        ]

        for line in lines:
            if line[0] == line[1] == line[2] and line[0] != '':
                self.winner = line[0]
                self.setWinner(line[0])
                break

    def setWinner(self, winner):
        for row in self.buttons:
            for button in row:
                button.setText(winner)
                button.setEnabled(False)

    def resetBoard(self):
        for row in self.buttons:
            for button in row:
                button.setText('')
                button.setEnabled(True)
        self.winner = None


class UltimateTicTacToe(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ultimate Tic Tac Toe')
        self.setStyleSheet("background-color: #362E23;")
        self.setFixedSize(1000, 800)  # Fixed maximum size for the window

        self.initUI()

    def initUI(self):
        self.centralWidget = QWidget(self)
        self.centralWidget.setStyleSheet("background-color: #3A3C26;")
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QHBoxLayout(self.centralWidget)

        self.playerXDisplay = PlayerDisplay("default_x.png")
        self.playerODisplay = PlayerDisplay("default_o.png")

        self.mainLayout.addWidget(self.playerXDisplay)

        self.boardWidget = QWidget(self)
        self.boardLayout = QGridLayout(self.boardWidget)
        self.mainLayout.addWidget(self.boardWidget)

        self.miniBoards = [[MiniBoard(self, i, j) for j in range(3)] for i in range(3)]

        for i in range(3):
            for j in range(3):
                self.boardLayout.addWidget(self.miniBoards[i][j], i, j)

        self.mainLayout.addWidget(self.playerODisplay)

        self.currentPlayer = 'X'
        self.nextBoard = None
        self.updateBoardStates()
        self.updatePlayerIndicators()

        self.createMenu()

    def createMenu(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        gameMenu = menubar.addMenu("Игра")
        saveAction = QAction("Сохранить", self)
        saveAction.triggered.connect(self.saveGame)
        loadAction = QAction("Загрузить", self)
        loadAction.triggered.connect(self.loadGame)

        gameMenu.addAction(saveAction)
        gameMenu.addAction(loadAction)

    def switchPlayer(self):
        self.currentPlayer = 'O' if self.currentPlayer == 'X' else 'X'
        self.updatePlayerIndicators()

    def setNextBoard(self, i, j):
        if i is not None and j is not None and self.miniBoards[i][j].winner is None:
            self.nextBoard = (i, j)
        else:
            self.nextBoard = None  
        self.updateBoardStates()

    def updateBoardStates(self):
        for i in range(3):
            for j in range(3):
                if self.nextBoard is None:
                    if self.miniBoards[i][j].winner is None:
                        self.miniBoards[i][j].setEnabled(True)
                        self.miniBoards[i][j].setStyleSheet("background-color: #A9AC5D;")
                    else:
                        self.miniBoards[i][j].setEnabled(False)
                        self.miniBoards[i][j].setStyleSheet("background-color: #6D6C3C;")
                else:
                    if (i, j) == self.nextBoard:
                        self.miniBoards[i][j].setEnabled(True)
                        self.miniBoards[i][j].setStyleSheet("background-color: #A9AC5D;")
                    else:
                        self.miniBoards[i][j].setEnabled(False)
                        self.miniBoards[i][j].setStyleSheet("background-color: #6D6C3C;")

    def updatePlayerIndicators(self):
        self.playerXDisplay.setActive(self.currentPlayer == 'X')
        self.playerODisplay.setActive(self.currentPlayer == 'O')

    def checkWinner(self):
        lines = [
            [(i, 0) for i in range(3)],
            [(i, 1) for i in range(3)],
            [(i, 2) for i in range(3)],
            [(0, i) for i in range(3)],
            [(1, i) for i in range(3)],
            [(2, i) for i in range(3)],
            [(i, i) for i in range(3)],
            [(i, 2 - i) for i in range(3)]
        ]

        for line in lines:
            symbols = [self.miniBoards[i][j].winner for i, j in line]
            if symbols[0] == symbols[1] == symbols[2] and symbols[0] is not None:
                winner_name = self.playerXDisplay.nameLineEdit.text() if symbols[0] == 'X' else self.playerODisplay.nameLineEdit.text()
                QMessageBox.information(self, 'Игра закончена!', f' {winner_name} выиграл(а)!')
                self.resetGame()
                return

    def resetGame(self):
        for row in self.miniBoards:
            for board in row:
                board.resetBoard()
        self.currentPlayer = 'X'
        self.nextBoard = None
        self.updateBoardStates()
        self.updatePlayerIndicators()

    def saveGame(self):
        game_state = {
            'currentPlayer': self.currentPlayer,
            'nextBoard': self.nextBoard,
            'boards': [
                [[cell.text() for cell in row] for row in board.buttons] for board_row in self.miniBoards for board in board_row
            ],
            'winners': [
                [board.winner for board in row] for row in self.miniBoards
            ]
        }

        with open("save.txt", 'w') as file:
            json.dump(game_state, file)

    def loadGame(self):
        if not os.path.exists("save.txt"):
            QMessageBox.information(self, 'Load Game', 'Сохранения нет!')
            return

        with open("save.txt", 'r') as file:
            game_state = json.load(file)
            self.currentPlayer = game_state['currentPlayer']
            self.nextBoard = tuple(game_state['nextBoard']) if game_state['nextBoard'] else None

            for i, board_row in enumerate(self.miniBoards):
                for j, board in enumerate(board_row):
                    for x, row in enumerate(board.buttons):
                        for y, button in enumerate(row):
                            button.setText(game_state['boards'][i*3+j][x][y])
                            button.setEnabled(game_state['boards'][i*3+j][x][y] == '')

                    board.winner = game_state['winners'][i][j]

            self.updateBoardStates()
            self.updatePlayerIndicators()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UltimateTicTacToe()
    window.show()
    sys.exit(app.exec_())

