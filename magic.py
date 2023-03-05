import os
import time
import tkinter as tk
from tkinter import filedialog as fd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from PIL import ImageTk, Image
from tkinter import simpledialog

"""
Database Format:
First Line: date of oldest item updated
Other Lines: pseudo-dict of (card name~T/F foil~TCG URL to card~TCG price~TCG market price~card type~card rarity~card category~card placement in category)
Category is defaulted to "Cards" with placement at the bottom of the category.
"""

PAGEWAIT = 2 #future support for changing time spent waiting for webpages to load 
SEP = "~" #future support for changing seperator for database items
SCALE = 1 #future support for scaling window size

class card:
    def __init__(self, name, foil, url, price, mrktPrice, type, rarity, category, place):
        self.name = name
        self.foil  = foil
        self.url = url
        self.price = price
        self.mrktPrice = mrktPrice
        self.type = type
        self.rarity = rarity
        self.category = category
        self.place = place
    def getString(self):
        return self.name + ": priced at " + self.price + ", market price is " + self.mrktPrice + ", of type: " + self.type + ", of rarity: " + self.rarity
    def getRaw(self):
        return self.name + "~" + str(self.foil) + "~" + self.url + "~" + self.price + "~" + self.mrktPrice + "~" + self.type + "~" + self.rarity + "~" + self.category + "~" + str(self.place)

def loadDatabase():
    global fileName
    global deckDisplay
    file = fd.askopenfile(title = "Choose Database File", filetypes = (("Text Files","*.txt"),("All Files","*.*")))
    fileName = file.name
    updated = file.readline()
    updated = datetime.strptime(updated, "%Y-%m-%d %H:%M:%S\n")
    lastUpdated = tk.Label(main, text = "Oldest database item is from " + updated.ctime() + ".").grid(row = 0, column = 0)
    for line in file:
        card = line.split("~")
        print("")
        print("Read card: ", end = "")
        i = 0
        for part in card:
            i += 1
            if i == 1:
                deckDisplay.insert(tk.END, part)
            print(part, end = ", ")
    file.close()
    
def updateDatabase():
    global fileName
    file = open(fileName, "w")
    file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
    file.close()
    
def genImage():
    global deckDisplay
    global fileName
    name = deckDisplay.get(deckDisplay.curselection(), deckDisplay.curselection())[0]
    print("Generating image for card: " + name)
    file = open(fileName, "r")
    file.readline()
    for line in file:
        card = line.split("~")
        i = 0
        found = False
        for part in card:
            i += 1
            if name == part:
                found = True
            if i == 3 and found:
                url = part
                print("Getting image from url: " + url)
                driver = webdriver.Chrome()
                driver.get(url)
                driver.maximize_window()
                time.sleep(PAGEWAIT)
                img = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/section[1]/section/div/div/div/div/div/div/img")   
                with open('card.png', 'wb') as image:
                    image.write(img.screenshot_as_png)
                pic = Image.open("card.png")
                test = ImageTk.PhotoImage(pic)
                label1 = tk.Label(image=test)
                label1.image = test
                label1.grid(row = 2, column = 1)
                break
    file.close()
    
def addCard():
    global fileName
    global cardLink
    global deckDisplay
    search = webdriver.Chrome()
    search.get(cardLink.get())
    time.sleep(PAGEWAIT) #Necessary to let page load
    name = search.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/div/h1")
    name = name.get_attribute("innerHTML")
    foil = False
    price = search.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/section[2]/section[1]/div/section[2]/span")
    price = price.get_attribute("innerHTML")
    mrktPrice = search.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/section[3]/div/section[1]/table/tr[2]/td[2]/span")
    mrktPrice = mrktPrice.get_attribute("innerHTML")
    type = search.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/section[2]/section[3]/div/div/div/ul/li[3]/span")
    type = type.get_attribute("innerHTML")
    rarity = search.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/section[2]/section[3]/div/div/div/ul/li[1]/span")
    rarity = rarity.get_attribute("innerHTML")
    category = "Cards"
    place = 0
    new = card(name, foil, cardLink.get(), price, mrktPrice, type, rarity, category, place)
    print("Added card: " + new.getString())
    file = open(fileName, "a")
    file.write(new.getRaw() + "\n")
    file.close()
    deckDisplay.insert(tk.END, new.name)

def delCard():
    global deckDisplay
    global fileName
    name = deckDisplay.get(deckDisplay.curselection(), deckDisplay.curselection())[0]
    file = open(fileName, "r")
    tempFile = open("temp.txt", "w")
    lineNum = 0
    for line in file:
        lineNum += 1
        card = line.split(SEP)
        if card[0] != name or lineNum == 1:
            tempFile.write(line)
        else:
            name = "null"
    tempFile.close()
    file.close()
    file = open(fileName, "w")
    tempFile = open("temp.txt", "r")
    for line in tempFile:
        file.write(line)
    tempFile.close()
    file.close()
    deckDisplay.delete(deckDisplay.curselection()[0])

def createDatabase():
    name = simpledialog.askstring(title="Database Name", prompt="Enter the name for the new database:")
    file = open(name + ".txt", "w")
    file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
    file.close()

main = tk.Tk()
main.geometry("1400x700")
main.title("Mabic")
menu = tk.Menu(main)
menu.add_command(label = "Create New Database", command = createDatabase)
menu.add_command(label = "Load Database File", command = loadDatabase)
menu.add_command(label = "Update Database Prices", command = updateDatabase)
main.config(menu = menu)
delButton = tk.Button(main, text = "Delete card", command = delCard).grid(row = 4, column = 0)
addButton = tk.Button(main, text = "Add new card", command = addCard).grid(row = 5, column = 0)
global cardLink
cardLink = tk.Entry(main, width = 50)
cardLink.insert(0, "Card TCGPlayer URL")
cardLink.grid(row = 6, column = 0)
deckLabel = tk.Label(main, text = "Cards:").grid(row = 1, column = 0)
global deckDisplay
deckDisplay = tk.Listbox(main, width = 100, height = 30)
deckDisplay.grid(row = 2, column = 0)
genImageButton = tk.Button(main, text = "Display card", command = genImage).grid(row = 3, column = 0)
main.mainloop()
