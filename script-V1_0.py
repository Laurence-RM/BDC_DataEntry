import requests
import urllib.request
import time
import csv
import math
import traceback
import os.path
from datetime import datetime
from bs4 import BeautifulSoup
from io import StringIO
from shutil import copyfile

class Tags:
    def __init__(self, duty, materials, vendor):
        self.duty = duty
        self.materials = materials
        self.vendor = vendor
    
    def format(self, details):
        return self.duty+", "+details+" "+self.vendor

class Item:
    def __init__(self, title, vendor, type, details, sku, price, dimensions, image, url, weight = None, option = None, tags = None):
        self.title = title
        self.vendor = vendor
        self.type = type
        self.details = details
        self.option = option or ''
        self.sku = sku
        self.price = price
        self.weight = weight or ''
        self.dimensions = dimensions
        self.image = image
        self.tags = tags or Tags(duty = ".26", materials = "", vendor = vendor)
        self.url = url

    def format(self):
        return ['','', self.title,'',self.vendor,self.type,self.tags.format(self.details),
        '','','','','','','','',self.url,'','','','','','','','','','','','',
        self.sku,'','','','','','','','','','','','','','','','','','','','','',self.dimensions]


def main():
    #outputF = open('./BDC_Upload.csv')
    outObjects = []

    while True:
        choice = input("Please select a vendor:\n\t1. Dovetail\n\t2. Remove Dupes\n\t0. Exit\n: ")
        if (choice == '0'):
            break
        elif (choice == '1'):
            outObjects = dovetail()
            break
        elif (choice == '2'):
            with open('./dupes.txt', 'r') as dupesF, open('./Upload.csv', 'r') as uploadF, open('./UploadNoDupes.csv', 'w') as out:
                dupes = []
                for sku in dupesF:
                    dupes.append(sku[0:-1])
                writer = csv.writer(out)
                for row in csv.reader(uploadF):
                    if row[1] == "Command": continue
                    found = False
                    for sku in dupes:
                        if sku == row[28]:
                            print("Found dupe: %s" % row[28])
                            # add removal of images?
                            found = True
                            break
                    if not found:
                        print("%s is not a dupe" % row[28])
                        writer.writerow(row)
            return
        else:
            print("Answer not recognized, please select a number...\n")


    tempF = open('./Upload.csv', 'w')
    outData = [["","Command","Title","Body HTML","Vendor","Type","Tags (duty percentage,tags,vendor)","Tags Command","Created At","Updated At","Published","Published At","Published Scope","Template Suffix","Gift Card","URL","Row #","Top Row","Variant Inventory Item ID","Variant ID","Variant Command","Option1 Name","Option1 Value","Option2 Name","Option2 Value","Option3 Name","Option3 Value","Variant Position","Variant SKU","Variant Barcode","Variant Image","Variant Weight(KG)","Variant Weight","Variant Weight Unit","Variant Price","Variant Compare At Price","Variant Taxable","Variant Tax Code","Variant Inventory Tracker","Variant Inventory Policy","Variant Fulfillment Service","Variant Requires Shipping","Variant Inventory Qty","Variant Inventory Adjust","Image Src","Image Command","Image Position","Image Width","Image Height","Image Alt Text","Metafield: dimensions.heightwidthlength [string]"]]

    for obj in outObjects:
        outData.append(obj.format())
        # Check details length
        if (len(obj.details) > 110):
            print("Excess details in: "+obj.sku)
            
    #write out to file using outObjects
    with tempF:
        writer = csv.writer(tempF)
        writer.writerows(outData)
        
    now_ = datetime.now()
    filename_ = now_.strftime("Upload_%m-%d-%y_%H-%M")
    print("Data written to file. Backup written as %s!" % filename_)
    copyfile("./Upload.csv", "./Backups/"+filename_+".csv")
    copyfile("./log.txt", "./Backups/log_"+filename_+".txt")

    if (len(outObjects) > 0):
        print("\nListing Scraped Objects:\n")
        i = 0
        for obj in outObjects:
            i += 1
            print("\t"+str(i)+".   "+obj.title)
        print("\t0.   Exit Program\n")
        while True:
            try:
                inp = int(input("Select a number to view more information: "))
            except ValueError:
                print("Input not recognized, please try again...")
                continue

            if (inp == 0):
                break
            elif (inp >= 1 and inp <= len(outObjects)):
                print("Vendor: "+outObjects[inp-1].vendor)
                print("Type: "+outObjects[inp-1].type)
                print("Title: "+outObjects[inp-1].title)
                print("SKU: "+outObjects[inp-1].sku)
                print("Details: "+outObjects[inp-1].details[0:-2])
                #print(outObjects[inp-1].option +"\n")
                print("Price: "+outObjects[inp-1].price)
                #print(outObjects[inp-1].weight +"\n")
                print("Dimensions: "+outObjects[inp-1].dimensions)
                print("Duty: "+outObjects[inp-1].tags.duty+"\n")

                continue
            else:
                print("Input not recognized, please try again...")
            
    tempF.close()

def authDove():
    # Site Login and Authentication
    session = requests.Session()

    cookies = {
        '99c2f63156e1e68f3cb5d4f9d34efdff': 'b1ef5cb53563b3775e5a7be4c3fc6a4d',
        'ja_purity_tpl': 'ja_purity',
    }

    data = {
    'username': USERNAME,
    'passwd': PASSWORD,
    'Submit': 'Login',
    'option': 'com_user',
    'task': 'login',
    'return': 'aW5kZXgucGhwP29wdGlvbj1jb21fY29udGVudCZ2aWV3PWFydGljbGUmaWQ9MiZJdGVtaWQ9MjU=',
    '2ff21070c00c5f254b2eb5d9d72b8d7e': '1'
    }
    session.post('http://www.dovetailfurnitureonline.com/index.php', cookies=cookies, data=data)

    return session


def dovetail():
    inputF = []
    session = authDove()
    type_ = ''
    USERNAME = 'email@gmail.com'
    PASSWORD = 'ExamplePass123'

    print("WARNING: Ensure dupes file is updated!")
    while(True):
        select = input("Please choose an option:\n\t1. Download SKUs from a category\n\t2. Download SKUs from a list of links (Type then URLs)\n: ")
        if (select == "1"):
            categories = ("Accessories", "Bedroom", "Benches", "Benches one of a kind", "Bookcase", "Bookcase one of a kind", "Cabinets", "Cabinets one of a kind", "Chairs & Stools", "Chairs Bar & Counter", "Chairs occasional", "ERROR - MISSING CATEGORY", "Consoles & Sofa Table", "Consoles & Sofa Tables one of a kind", "Coffee tables", "Coffee tables one of a kind", "Columns", "Desk", "Doors/Screens", "Dressers", "End Tables/Night Stands", "Lamps", "Mirrors", "ERROR - MISSING CATEGORY", "Outdoor", "Painting/Art", "Planters & Large Pots", "Poufs & ottomans", "Rugs & Pillows etc", "Sideboards / buffets", "ERROR - MISSING CATEGORY", "Sofa", "Tables", "Table Bar & Counter", "Table Bistro", "Trunks/Boxes", "Tv/Plasma", "ERROR - MISSING CATEGORY", "Sideboard / Buffet one of a kind",)

            catID = 200
            
            # Select category
            while(True):
                search = input("Type a category to search or press 0 to list\n: ")
                search = search[0].upper() + search[1:]
                if (search == "0"):
                    for i in range(0, len(categories)):
                        print("\t%i. %s" % (i+1, categories[i]))
                    while(True):
                        try:
                            catN = int(input("Selection: "))
                            if (1 <= catN <= len(categories)):
                                catID += catN
                                break
                            else:
                                print("Invalid input. Enter a number in the range.")
                                continue
                        except ValueError:
                            print("Invalid input. Enter a number in the range.")
                            continue
                    break
                elif search in categories:
                    catID += categories.index(search) + 1
                    break
                else:
                    print("Category could not be found.")
                    continue
            
            # load inputF with list of URLs
            type_ = categories[catID-201]
            limitS = 0
            while(True):
                try:
                    s = session.get("http://www.dovetailfurnitureonline.com/index.php?option=com_virtuemart&category_id="+str(catID)+"&page=shop.browse&Itemid=1&limitstart=0&limit=200")
                    soup = BeautifulSoup(s.text, 'lxml')
                    itemCount = int(soup.select_one("#vmMainPage > div:nth-of-type(3)").get_text().rsplit(' ', 1)[1])
                    break
                except AttributeError:
                    input("Error connecting to category page. Press enter to try again...")
                    session = authDove()
                    continue
            print("%i items found for category: %s" % (itemCount, type_))

            if (itemCount > 200):
                loops = math.ceil(itemCount / 200) 
                for x in range(loops):
                    s = session.get("http://www.dovetailfurnitureonline.com/index.php?option=com_virtuemart&category_id="+str(catID)+"&page=shop.browse&Itemid=1&limitstart="+str(limitS)+"&limit=200")
                    soup = BeautifulSoup(s.text, 'lxml')
                    aElement = soup.select_one("#vmMainPage > table:nth-of-type(1)").find_all("a", attrs={"style":"font-size: 9px; font-weight: bold;"})
                    for element in aElement:
                        inputF.append("http://www.dovetailfurnitureonline.com"+element.attrs.get("href")+'.')
                    limitS += 200
            else:
                aElement = soup.select_one("#vmMainPage > table:nth-of-type(1)").find_all("a", attrs={"style":"font-size: 9px; font-weight: bold;"})
                for element in aElement:
                    inputF.append("http://www.dovetailfurnitureonline.com"+element.attrs.get("href")+'.')
    
            print("URLs loaded from category...")
            break
        elif (select == "2"):
            file = input("Enter the name of the file containing links: ")
            inputF = open('./'+file, mode='r', encoding='utf-8-sig')
            break
        else:
            print("Invalid option selected")
            continue

    # Globalish Variables
    vendor_ = 'Dovetail'
    objects = []
    logF = open("log.txt", 'w')
    count = 0
    dupeF = open("./dupes.txt", 'r')
    dupes = dupeF.read().replace(' ', '').split("\n")
    dupeCount = 0

    # Loop through each URL
    for line in inputF:

        if (line[0:4] != 'http'):
            type_ = line.strip()
            count = 0
        else:
            url = line[:-1]

            count += 1
            time.sleep(1.5)
            while(True):
                try:
                    s = session.get(url)
                    if (s.url != url):
                        print("Session url deviates from input url")
                        inp = input("\t1. Attempt Reconnect\n\t2. Stash objects\n\t3. Continue with URL\n")
                        if (inp == '1'):
                            session = authDove()
                            continue
                        elif (inp == '2'):
                            return objects
                        elif (inp == '3'):
                            break
                        else:
                            continue
                    break
                except Exception as err:
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    logF.write(current_time+" | Connection Error: \n"+traceback.format_exc())
                    print("Client has been Remotely Disconnected at "+current_time+"\nError:\n"+str(err))
                    opt = input("\t1. Continue script\n\t2. Break and write to file\n")
                    if (opt == '1'):
                        print("Attempting Reconnect..")
                        logF.write("Attempting Reconnect..\n")
                        session = authDove()
                        continue
                    elif (opt == '2'):
                        return objects
                    else:
                        continue


            print('Requesting... | '+type_+' #'+str(count)+"\tStatus: "+str(s.status_code)+"")
            logF.write("Requesting "+url+"\n\t"+type_+" #"+str(count)+"\tStatus: "+str(s.status_code)+"\n")

            if (s.status_code != 200):
                print("Error Encountered")
                continue

            soup = BeautifulSoup(s.text, 'lxml')

            forceNext = False
            while(True):
                try:
                    sku_ = soup.select_one("#vmMainPage > table:nth-of-type(1) >  tbody:nth-of-type(1) > tr:nth-of-type(1) > td:nth-of-type(1) > font:nth-of-type(1)").get_text().strip()
                    # Temporary Duplicate checking
                    if sku_ in dupes:
                        dupeCount += 1
                        dupes.remove(sku_)
                        print("\tDuplicate. Skipping...")
                        logF.write("\tDuplicate. Skipping...\n")
                        forceNext = True
                        break
                    
                    title_ = soup.select_one("#vmMainPage > table:nth-of-type(1) >  tbody:nth-of-type(1) > tr:nth-of-type(1) > td:nth-of-type(1) > p:nth-of-type(1)").get_text().strip()
                    image_ = soup.select_one("#vmMainPage > table:nth-of-type(1) > tbody:nth-of-type(1) > tr:nth-of-type(1) > td:nth-of-type(1)").find("a").attrs.get("href")
                    tempdet = soup.select_one("#vmMainPage > table:nth-of-type(1) > tbody:nth-of-type(1) > tr:nth-of-type(1) > td:nth-of-type(1)").find_all("li")
                    price_ = soup.select_one(".productPrice").get_text().strip()
                    dimensions_ = soup.select_one("#vmMainPage > table:nth-of-type(1) > tbody:nth-of-type(1) > tr:nth-of-type(2) > td:nth-of-type(1)").get_text().strip().replace("\t", "").replace("  ","").split("\n")
                    images = soup.select_one("#vmMainPage > table:nth-of-type(1) > tbody:nth-of-type(1) > tr:nth-of-type(4)").find_all("img")
                    break
                except AttributeError as err:
                    print("Scraping Error, field not defined: "+str(err))
                    logF.write("Scraping Error: \n"+traceback.format_exc())
                    inp = input("Try again? Or enter 0 to exit. (Y/n): ").lower()
                    if (inp == 'n'):
                        forceNext = True
                        break
                    elif (inp =='0'):
                        return objects
                    else:
                        print("Retrying...")
                        session=authDove()
                        continue


            if(forceNext):
                continue
            
            while ("" in dimensions_):
                dimensions_.remove("")

            details_ = ""
            for det in tempdet:
                details_ += det.get_text().strip() + ', '

            dimFormatted = []
            for item in dimensions_:
                unwantedWords = ("Availability","$","order")
                if not any(x in item for x in unwantedWords):
                    dimFormatted.append(item.split(' ')[1])
    
            imgtitle_ = title_.replace("W/","WITH").replace("/", "_")
            
            titleOption = 0
            
            while(os.path.isfile("./images/dovetail/"+imgtitle_+".jpg")):
                if (titleOption == 0):
                    print("File with existing name found.\n\t%s\n\t%s" % (title_, url))
                titleOption += 1
                if (titleOption == 1):
                    imgtitle_ += '-' + str(titleOption)
                else:
                    imgtitle_ = imgtitle_[0:-1] + str(titleOption)

            if (titleOption != 0):
                title_ += ' ' + str(titleOption)

            item_ = Item(title_, vendor_, type_, details_, sku_, price_, "x".join(dimFormatted), image_, url, None, None, None)
            objects.append(item_)
                
            while(True):
                try:
                    urllib.request.urlretrieve(image_, "./images/dovetail/"+imgtitle_+".jpg")
                    if (imgtitle_ != title_):
                        print("Image saved, title changed")
                    break
                except urllib.error.HTTPError as err:
                    print("\tError downloading main image")
                    logF.write("\tError downloading main image: "+str(err)+"\n")
                    break
                except FileNotFoundError as err:
                    print("Could not save image with title: "+imgtitle_)
                    imgtitle_ = input("Choose a new title: ")
                    logF.write("Image title renamed to "+imgtitle_+"\n")
                    continue

            if (images):
                del images[0]
                for i in range(len(images)):
                    time.sleep(1)
                    images[i] = "http://www.dovetailfurnitureonline.com"+images[i].attrs.get("src")
                    images[i] = images[i].replace("_S_", "_M_")
                    try:
                        urllib.request.urlretrieve(images[i], "./images/dovetail/"+imgtitle_+"_"+str(i+1)+".jpg")
                    except urllib.error.HTTPError as err:
                        print("\tError downloading image: "+images[i])
                        logF.write("\tError downloading image: "+images[i]+"\n\t\t"+str(err))
                        try:
                            print("\tAttempting download of smaller image... ", end="")
                            logF.write("\n\tAttempting download of smaller image... ")
                            images[i] = images[i].replace("_M_", "_S_")
                            urllib.request.urlretrieve(images[i], "./images/dovetail/"+imgtitle_+"_"+str(i+1)+".jpg")

                            logF.write("Success\n")
                            print("Success")
                        except urllib.error.HTTPError as err:
                            print("Failure")
                            logF.write("Failure\n")

    print("%i duplicates removed." % (dupeCount))
    logF.close()
    dupeF.close()
    try:
        inputF.close()
    except AttributeError:
        pass
        # not a file
    finally:
        return objects
            

#Call main
if __name__ == "__main__":
    main()
