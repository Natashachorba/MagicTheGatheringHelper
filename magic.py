'''
Program that handles a few magic the gathering functions, currently:
1. prints out the shareboard given a directory of decks
2. prints priceBoard, web scrapes deckbox to only print high priced shared cards
3. removes all duplicates of a card in a list (sorta)
4. prints an alphabetical list given a list of cards from deckbox
TODO: add error checking everywhere (mostly for inputs)
TO REDO: removes all cards that are in the sideboard from the mainboard 
TODO?: web scrape TappedOut for decks instead of files...changes often though

_____________USES PYTHON 3_______________
'''
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup

# different types of cards, for use to end reading in Reduce function
# there must be a better way to do this part as there are some cards with
# these terms in their actual name...will be updated eventually
types = ["Artifact", "Basic", "Creature", "Emblem", "Enchantment",
        "Instant", "Land", "Legendary", "Plane", "Planeswalker",
        "Scheme", "Sorcery", "Token", "Tribal"]
# different types of basic land, used to keep them from showing in shareboard
basics =["Forest", "Island", "Mountain", "Plains", "Swamp"]

'''
reads through input file, creates an array of (an arrray of words) for each line
@param string file - the file to parse
@return array - array of arrays of "words"
'''
def reader(file):
	content = []
	with open(file) as f:
		content = [line.strip('\n') for line in f.readlines()]
	f.close()
	cards = [line.split() for line in content]
	return cards

'''
prints the given results to command console and an output file if desired
@param array results - the results list to print
'''
def resultsPrinter(results):
  outFile = input("Do you wish to print results to a file? Y/N: ") or "N"
  if outFile.upper() == "Y":
    outFile = input("Enter outFile (default outFile1.txt): ") or "outFile1.txt"
    with open(outFile,'w') as f:
      [f.write(item + "\n") for item in results]
    f.close()
  else:
    [print(result) for result in results]

'''
prints the shareboard to some combination of console or files
@param dict decksDict - dict of the decks with arrays of shared cards in them
@param dict cardsDict - dict of shared cards with arrays of decks they are in
'''
def shareboardPrinter(decksDict, cardsDict):
  choice = input("Would you like to:\n"+
    "1. Print the decks shareboard to a file and the cards to the console\n"+
    "2. Print the the cards to a file and decks shareboard to the console\n"+
    "3. Print both to the console\n" + "4. Print both to files\n") or "4"

  # create an array of the properly printed string for each item in decksDict
  printDecksArray = [("\n\n\t\t" + key + " (" + str(len(decksDict[key])) +
  ")\n\n" + "\n".join(sorted(decksDict[key]))) for key in sorted(decksDict)]
  # create an array of the properly printed string for each item in decksDict
  printCardsArray = []
  for key in sorted(cardsDict):
    if (len(cardsDict[key]) > 1):
      printCardsArray.append(str(len(cardsDict[key])) + "x "+ key + " #" +
                            " #".join(sorted(cardsDict[key])))
  # print the decksDict to wherever it was meant to go
  if (choice == "1" or choice == "4"):
    outFile = input("\nEnter output file for shareboards: ") or "shDecks.txt"
    with open(outFile, "w") as fil:
      [fil.write(deck) for deck in printDecksArray]
    fil.close()
  else:
    [print(deck) for deck in printDecksArray]
  # print the cardsDict to wherever it was meant to go
  if (choice == "2" or choice == "4"):
    outFile = input("\nEnter output file for shared cards: ") or "shCards.txt"
    with open(outFile, "w") as fil:
      [fil.write(card+"\n") for card in printCardsArray]
    fil.close()
  else:
    print()
    [print(card) for card in printCardsArray]

'''
Reduces count of each item in input file to 1
@return array - array of the cards with 1x in front of them
'''
def commanderize():
  print ("\tCommanderize Beginning")
  file = input ("Enter list file (default list.txt): ") or "list.txt"
  print ("input: ", file)
  content = reader(file)
  noDupesList = ["1x "+" ".join(card[1:]) for card in content]
  resultsPrinter(noDupesList)
  print ("\tCommanderize Completed")
  return noDupesList

'''
Using a file made up of data copied from https://deckbox.org/games/mtg/cards
reduces this data to only have the name of the cards and prints it
@return array - the list of card names 
'''
def reduce():
  print ("\tReduce Beginning")
  file = input ("Enter list file (default list.txt): ") or "list.txt"
  print ("input: ", file)
  content = reader(file)
  reducedList = []
  for card in content:
    count = 0
    for word in card:
      #print (word)
      if word in types:
        break
      count+=1
    reducedList.append(" ".join(card[:count]))
  reducedList.sort()
  resultsPrinter(reducedList)
  print ("\tReduce Completed")
  return reducedList

'''
Creates two dictionaries. The first keeps track of all cards and which decks
they are shared across. The second keeps track of each deck and what cards
it has that are shared with others
@return tuple dict - tuple of the 2 dicts that were created here
'''
def share():
  direc = input ("Enter the subdirectory with all files: ") or "exDecks"
  sharedCards = {}
  deckShares = {}
  for filename in os.listdir(direc):      #grabs every file in the directory
    fullname = direc + '/' + filename
    cardsArray = reader(fullname)
    if (filename[-4:] == ".txt"):         #remove .txt from the names in dicts
      filename = filename[:-4]
    deckShares[filename] = []
    #creates dict of all the cards, along with an array of files theyre in
    for card in cardsArray:
      cardname= ' '.join(card[1:])        #grab the card name minus its count
      if (cardname in basics):
        continue                          #do nothing with it if it's a basic
      if (cardname in sharedCards):
        # add the card to the deckShares dict of the original deck since it
        # hasn't been put there previously and now is legit to be there
        if (len(sharedCards[cardname]) == 1):
          deckShares[sharedCards[cardname][0]].append(cardname)

        sharedCards[cardname].append(filename)
        deckShares[filename].append(cardname)
      else:                             # if it's a new value, = new array
        sharedCards[cardname] = [filename]
  return (deckShares, sharedCards)

'''
helper function to print just the base share function's shareboard
@return tuple dict - tuple of the 2 dicts that were created in share
'''
def sharedHelper():
  print ("Shareboard beginning")
  results = share()
  shareboardPrinter(results[0], results[1])
  print ("Share Completed")
  return results

'''
Scrapes the deckbox site for the input card to find its price
@param string cardName - name of the card whose price we are trying to find
@return float - the normal price of the card or -1 if there was an issue
'''
def priceHelper(cardName):
  url = "https://deckbox.org/mtg/" + cardName.replace(" ", "%20")
  try:
    html = urlopen(url)
    soup = BeautifulSoup(html,"html.parser")
    avgPrice = soup.find("div", class_="price_avg").get_text()
    avgPrice = float(avgPrice[1:])
    lowPrice = soup.find("div", class_="price_min").get_text()
    lowPrice = float(lowPrice[2:])
    bestPrice = lowPrice if lowPrice > avgPrice else avgPrice
    return bestPrice
  except:
    return -1

'''
prints the shareboard minus the cheap cards that you're willing to buy bulk
@return tuple dict - tuple of the 2 dicts that were updated from share
'''
def priceBoard():
  print("Pricer Beginning")
  minPrice = float(input("What is the max price past which you want to "
                  "shareboard? (default 1.50)") or 1.5)
  initResults = share()
  deckShares = {}                             #~ initResults[0]
  for deck in initResults[0]:
    deckShares[deck] = []
  sharedCards =  {}                           #~ initResults[1]
  invalids = {}                               # ones that threw errors
  cheapCards = {}                             # the rejected (for testing)
  
  for card in sorted(initResults[1]):
    if len(initResults[1][card]) > 1:
      result = priceHelper(card)
      if result == -1:
        print("ERROR: COULD NOT FIND PAGE! Try", card, "another time")
        invalids[card] = initResults[1][card]
      elif result > minPrice:
        sharedCards[card] = initResults[1][card]
        for deck in sharedCards[card]:
          deckShares[deck].append(card)
      else:
        cheapCards[card] = initResults[1][card]
        
  #print("Cheap Cards: ", cheapCards)
  if len(invalid) > 0:
    print("Broken Cards: ", invalids)
  shareboardPrinter(deckShares, sharedCards) #eventuality
  print ("Pricer Completed")
  return deckShares, sharedCards
	
def main():
  print ("Current functionality:\n",
  "1. Commanderize: removes non-land duplicates from a decklist\n",
  "2. Reduce: takes input file of data from deckbox, returns just names\n",	
  "3. Shareboard: given a directory, compiles a list of all shared cards\n",
  "4. PriceBoard: Shareboard but display only cards over the input price\n")
  funct = input ("Which functionality would you like to access? ") or "4"
	
  if (funct == "1"):
    commanderize() 
  elif (funct == "2"):
    reduce()
  elif (funct == "3"):
    sharedHelper()
  elif (funct == "4"):
    priceBoard()
  else:
    print("Invalid input.")
  print ("Program has completed")

if __name__ == "__main__":
	main()

