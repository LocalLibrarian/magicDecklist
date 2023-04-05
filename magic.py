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
card name (str)
T/F foil (bool)
TCG URL to card (str)
TCG price (float)
TCG market price (float)
card type (str)
card rarity (str)
card category (str)
card placement in category (int)
last date card price was updated (datetime)
quantity of card (int)

Category is defaulted to "Cards" with placement at the bottom of the category.
"""

global PAGEWAIT 
PAGEWAIT = 2 #future support for changing time spent waiting for webpages to load 
SCALE = 1 #future support for scaling window size

#Defines data attributes common to cards, as well as some useful string formatting
class card:
    def __init__(self, name, foil, url, price, mrktPrice, type, rarity, category, place, lastUpdate, quantity):
        self.name = name
        self.foil  = foil
        self.url = url
        self.price = price
        self.mrktPrice = mrktPrice
        self.type = type
        self.rarity = rarity
        self.category = category
        self.place = place
        self.lastUpdate = lastUpdate
        self.quantity = quantity
        
    #Returns good debug string
    def getString(self):
        return self.name + ', ' + str(self.foil) + ', ' + self.url + ', ' + str(self.price) + ', ' + str(self.mrktPrice) + ', ' + self.type + ', ' + self.rarity + ', ' + self.category + ', ' + str(self.place) + ', ' + self.lastUpdate.strftime("%Y-%m-%d %H:%M:%S") + ', ' + str(self.quantity)
    
    def save(self, fileName):
        file = open(fileName, "a")
        for attribute, value in vars(self).items():
            file.write(str(value) + "\n")
        file.close()

#Loads database info from file into listbox in GUI
def loadDatabase():
    global cards
    global fileName
    global deckDisplay
    file = fd.askopenfile(title = "Choose Database File", filetypes = (("Text Files","*.txt"),("All Files","*.*")))
    fileName = file.name
    #Reads line-by-line and adds card names to listbox and cards list
    lineNum = 0
    empty = True
    for line in file:
        lineNum += 1
        if lineNum == 1:
            empty = False
            temp = card(line.strip(), 'null', 'null', 0, 0, 'null', 'null', 'Cards', 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        elif lineNum == 2:
            temp.foil = bool(line.strip())
        elif lineNum == 3:
            temp.url = line.strip()
        elif lineNum == 4:
            temp.price = float(line.strip())
        elif lineNum == 5:
            temp.mrktPrice = float(line.strip())
        elif lineNum == 6:
            temp.type = line.strip()
        elif lineNum == 7:
            temp.rarity = line.strip()
        elif lineNum == 8:
            temp.category = line.strip()
        elif lineNum == 9:
            temp.place = int(line.strip())
        elif lineNum == 10:
            temp.lastUpdate = datetime.strptime(line.strip(), "%Y-%m-%d %H:%M:%S")
            if not cards or oldest > temp.lastUpdate:
                oldest = temp.lastUpdate
        elif lineNum == 11:
            temp.quantity = int(line.strip())
            lineNum = 0
            cards.append(temp)
            print('Added card data: ' + temp.getString())
    for item in cards:
        deckDisplay.insert(tk.END, item.name)
    file.close()
    if not empty:
        oldDate.set("Oldest database item is from " + oldest.ctime() + ".")
    
#Updates prices in the database
def updateDatabase():
    global PAGEWAIT 
    global cards
    global fileName
    oldDate.set("Oldest database item is from " + datetime.now().ctime() + ".")
    file = open(fileName, "w")
    file.close()
    for card in cards:
        driver = webdriver.Chrome()
        driver.get(card.url)
        driver.implicitly_wait(PAGEWAIT) #Necessary to let page load
        price = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/section[2]/section[1]/div/section[2]/span")
        price = float(price.get_attribute("innerHTML")[1:])
        mrktPrice = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/section[3]/div/section[1]/table/tr[2]/td[2]/span")
        mrktPrice = float(mrktPrice.get_attribute("innerHTML")[1:])
        card.price = price
        card.mrktPrice = mrktPrice
        card.lastUpdate = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        card.save(fileName)

#Scrapes image for card selected from TCGPlayer and displays in GUI
def genImage():
    global PAGEWAIT 
    global deckDisplay
    global cards
    card = cards[deckDisplay.curselection()[0]]
    print("Getting image from url: " + card.url) #Debug function
    driver = webdriver.Chrome()
    driver.get(card.url)
    driver.maximize_window()
    driver.implicitly_wait(PAGEWAIT) #Necessary to let page load
    img = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/section[1]/section/div/div/div/div/div/div/img")   
    #Saves screenshot of card image to file for display
    with open('card.png', 'wb') as image:
        image.write(img.screenshot_as_png)
    pic = Image.open("card.png")
    picture = ImageTk.PhotoImage(pic)
    cardPic = tk.Label(image=picture)
    cardPic.image = picture
    cardPic.grid(row = 2, column = 1)
    
#Adds card from TCGPlayer URL
def addCard():
    global PAGEWAIT 
    global fileName
    global cardLink
    global deckDisplay
    global cards
    search = webdriver.Chrome()
    search.get(cardLink.get())
    search.implicitly_wait(PAGEWAIT) #Necessary to let page load
    #Scrapes name, price, market price, card type, and rarity from webpage
    name = search.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/div/h1")
    name = name.get_attribute("innerHTML")
    foil = False #temp, will allow specifying in future
    price = search.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/section[2]/section[1]/div/section[2]/span")
    price = float(price.get_attribute("innerHTML")[1:])
    mrktPrice = search.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/section[3]/div/section[1]/table/tr[2]/td[2]/span")
    mrktPrice = float(mrktPrice.get_attribute("innerHTML")[1:])
    type = search.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/section[2]/section[3]/div/div/div/ul/li[3]/span")
    type = type.get_attribute("innerHTML")
    rarity = search.find_element(By.XPATH, "/html/body/div[2]/div/div/section[2]/section/div/div[2]/section[2]/section[3]/div/div/div/ul/li[1]/span")
    rarity = rarity.get_attribute("innerHTML")
    category = "Cards" #Temp, will allow specifying in future
    place = 0 #Temp, will allow specifying in future
    new = card(name, foil, cardLink.get(), price, mrktPrice, type, rarity, category, place, datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"), 1)
    print("Added card with data: " + new.getString()) #Debug function
    #Writes card to database file
    new.save(fileName)
    cards.append(new)
    deckDisplay.insert(tk.END, new.name) #Adds card to listbox

#Deletes card from listbox and database file. Only deleted based on name currently
def delCard():
    global deckDisplay
    global fileName
    global cards
    card = cards[deckDisplay.curselection()[0]]
    card.quantity -= 1
    if card.quantity < 1:
        file = open(fileName, "r")
        tempFile = open("temp.txt", "w")
        lineNum = 0
        name = card.name
        rpts = 0
        #Searches for card with selected name in database and writes all others to temp file
        for line in file:
            card = line.split(SEP)
            if line.strip() != name and rpts == 0 or rpts == 11:
                tempFile.write(line)
            else:
                rpts += 1
                name = "null"
        tempFile.close()
        file.close()
        file = open(fileName, "w")
        tempFile = open("temp.txt", "r")
        #Rewrites temp file back to main file without deleted card
        for line in tempFile:
            file.write(line)
        tempFile.close()
        file.close()
        del cards[deckDisplay.curselection()[0]] #Deletes card from list of cards in memory
        deckDisplay.delete(deckDisplay.curselection()[0]) #Deletes selected card from listbox

#Creates new .txt file so user doesn't have to do it manually
def createDatabase():
    name = simpledialog.askstring(title="Database Name", prompt="Enter the name for the new database:")
    file = open(name + ".txt", "w")
    file.close()

#Opens settings menu pop-up
def openSettings():
    global waitEntry
    global settings
    global PAGEWAIT
    settings = tk.Toplevel(main)
    settings.geometry("400x400")
    settings.title("Settings")
    waitLabel = tk.Label(settings, text = 'Max time to let webpages to load').grid(row = 0, column = 0)
    waitEntry = tk.Entry(settings, width = 3)
    waitEntry.insert(0, PAGEWAIT)
    waitEntry.grid(row = 1, column = 0)
    settingsSave = tk.Button(settings, text = 'Save', command = saveSettings).grid(row = 2, column = 1)
    
def saveSettings():
    global waitEntry
    global settings
    global PAGEWAIT
    PAGEWAIT = int(waitEntry.get())
    settings.destroy()

#Main entry point for program
main = tk.Tk()
oldDate = tk.StringVar()
lastUpdated = tk.Label(main, textvariable=oldDate).grid(row = 0, column = 0)
main.geometry("1400x700") #Will be scaled in future via a setting
main.title("Magic")
menu = tk.Menu(main)
#Top menu of program
menu.add_command(label = "Settings", command = openSettings)
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
global cards
cards = []
main.mainloop()
