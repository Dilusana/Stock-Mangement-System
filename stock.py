
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter
import random
import pymysql
import csv
from datetime import datetime

window = tkinter.Tk()
window.title("Toshiba Enterprise")
window.geometry("1024x640")

# Create the Treeview
my_tree = ttk.Treeview(window, show='headings', height=20)
style = ttk.Style()
placeholderArray = ['', '', '', '', '', '', '', '', '']
numeric = '1234567890'
alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def connection():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='toshiba'
    )
    return conn

conn = connection()
cursor = conn.cursor()

placeholderArray = ['' for _ in range(9)]
for i in range(9):
    placeholderArray[i] = tkinter.StringVar()

def read():
    conn = connection()
    cursor = conn.cursor()
    sql = "SELECT `item_ID`, `item_code`, `name`, `price`, `quantity`, `category`, `date`, `in_amount`, `out_amount`, `description`, `balance` FROM stock_mane ORDER BY id DESC"
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.close()
    return results

def refreshTable():
    for data in my_tree.get_children():
        my_tree.delete(data)
    for array in read():
        my_tree.insert(parent='', index='end', iid=array, text="", values=(array), tag="orow")
    my_tree.tag_configure('orow', background="#EEEEEE")

def setph(word, num):
    for ph in range(0, 9):
        if ph == num:
            placeholderArray[ph].set(word)

def generateRand():
    itemId = ''
    for i in range(0, 3):
        randno = random.randrange(0, (len(numeric) - 1))
        itemId = itemId + str(numeric[randno])
    randno = random.randrange(0, (len(alpha) - 1))
    itemId = itemId + '-' + str(alpha[randno])
    print("generated: " + itemId)
    setph(itemId, 0)




def save():
    itemId = str(itemIdEntry.get())
    itemCode = str(itemCodeEntry.get())
    name = str(nameEntry.get())
    price = str(priceEntry.get())
    qnt = str(qntEntry.get())
    cat = str(categoryCombo.get())
    in_amount = str(inEntry.get())
    out_amount = str(outEntry.get())
    desc = str(descEntry.get())

    valid = True
    
    if not (itemId and itemId.strip()) or not (itemCode and itemCode.strip()) or not (name and name.strip()) or not (price and price.strip()) or not (qnt and qnt.strip()) or not (cat and cat.strip()): 
        messagebox.showwarning("", "Please fill the entries")
        return
    if len(itemId) < 5 or len(itemCode) < 3:
        messagebox.showwarning("", "Invalid Item Id or Item Code")
        return

    if itemId[3] != '-':
        valid = False
    for i in range(0, 3):
        if itemId[i] not in numeric:
            valid = False
            break
    if itemId[4] not in alpha:
        valid = False
    if not valid:
        messagebox.showwarning("", "Invalid Item Id")
        return

    balance = float(in_amount) - float(out_amount)
    
    try:
        conn = connection()
        cursor = conn.cursor()
        cursor.connection.ping(reconnect=True)
        sql = "SELECT * FROM stock_mane WHERE item_ID = %s"
        cursor.execute(sql, (itemId,))
        checkItemNo = cursor.fetchall()
        if len(checkItemNo) > 0:
            messagebox.showwarning("", "Item Id already used")
            return
        else:
            cursor.connection.ping(reconnect=True)
            sql = "INSERT INTO stock_mane (item_ID, item_code, name, price, quantity, category, date, in_amount, out_amount, description, balance) VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s)"
            cursor.execute(sql, (itemId, itemCode, name, price, qnt, cat, in_amount, out_amount, desc, balance))
        conn.commit()
        messagebox.showinfo("", "Item saved successfully!")
        refreshTable()
    except pymysql.Error as err:
        messagebox.showwarning("", f"Error while saving: {err}")
    finally:
        if conn.open:
            cursor.close()
            conn.close()

def update():
    selectedItemId = ''
    try:
        selectedItem = my_tree.selection()[0]
        selectedItemId = str(my_tree.item(selectedItem)['values'][0])
    except:
        messagebox.showwarning("", "Please select a data row")
    print(selectedItemId)
    itemId = str(itemIdEntry.get())
    itemCode = str(itemCodeEntry.get())
    name = str(nameEntry.get())
    price = str(priceEntry.get())
    qnt = str(qntEntry.get())
    cat = str(categoryCombo.get())
    in_amount = str(inEntry.get())
    out_amount = str(outEntry.get())
    desc = str(descEntry.get())

    if not (itemId and itemId.strip()) or not (itemCode and itemCode.strip()) or not (name and name.strip()) or not (price and price.strip()) or not (qnt and qnt.strip()) or not (cat and cat.strip()): 
        messagebox.showwarning("", "Please fill the entries")
        return
    if(selectedItemId != itemId):
        messagebox.showwarning("", "You can't change item ID")
        return
    
    balance = float(in_amount) - float(out_amount)
    
    try:
        cursor.connection.ping()
        sql = f"UPDATE stock_mane SET `item_code` = '{itemCode}', `name` = '{name}', `price` = '{price}', `quantity` = '{qnt}', `category` = '{cat}', `in_amount` = '{in_amount}', `out_amount` = '{out_amount}', `description` = '{desc}', `balance` = '{balance}' WHERE `item_id` = '{itemId}' "
        cursor.execute(sql)
        conn.commit()
        conn.close()
        for num in range(0, 9):
            setph('', (num))
    except Exception as err:
        messagebox.showwarning("", "Error occurred ref: " + str(err))
        return
    refreshTable()

def delete():
    try:
        if(my_tree.selection()[0]):
            decision = messagebox.askquestion("", "Delete the selected data?")
            if(decision != 'yes'):
                return
            else:
                selectedItem = my_tree.selection()[0]
                itemId = str(my_tree.item(selectedItem)['values'][0])
                try:
                    cursor.connection.ping()
                    sql = f"DELETE FROM stock_mane WHERE `item_id` = '{itemId}' "
                    cursor.execute(sql)
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("", "Data has been successfully deleted")
                except:
                    messagebox.showinfo("", "Sorry, an error occurred")
                refreshTable()
    except:
        messagebox.showwarning("", "Please select a data row")

def select():
    try:
        selectedItem = my_tree.selection()[0]
        itemId = str(my_tree.item(selectedItem)['values'][0])
        itemCode = str(my_tree.item(selectedItem)['values'][1])
        name = str(my_tree.item(selectedItem)['values'][2])
        price = str(my_tree.item(selectedItem)['values'][3])
        qnt = str(my_tree.item(selectedItem)['values'][4])
        cat = str(my_tree.item(selectedItem)['values'][5])
        in_amount = str(my_tree.item(selectedItem)['values'][7])
        out_amount = str(my_tree.item(selectedItem)['values'][8])
        desc = str(my_tree.item(selectedItem)['values'][9])
        setph(itemId, 0)
        setph(itemCode, 1)
        setph(name, 2)
        setph(price, 3)
        setph(qnt, 4)
        setph(cat, 5)
        setph(in_amount, 6)
        setph(out_amount, 7)
        setph(desc, 8)
    except:
        messagebox.showwarning("", "Please select a data row")
def find():
    itemId = str(itemIdEntry.get())
    itemCode = str(itemCodeEntry.get())
    name = str(nameEntry.get())
    price = str(priceEntry.get())
    cat = str(categoryCombo.get())
    in_amount = str(inEntry.get())
    out_amount = str(outEntry.get())
    desc = str(descEntry.get())
    
    cursor.connection.ping()
    
    sql = "SELECT `item_ID`, `item_code`, `name`, `price`, `quantity`, `category`, `date`, `in_amount`, `out_amount`,`description`, `balance` FROM stock_mane WHERE "
    conditions = []
    
    if itemId and itemId.strip():
        conditions.append(f"`item_ID` LIKE '%{itemId}%'")
    if itemCode and itemCode.strip():
        conditions.append(f"`item_code` LIKE '%{itemCode}%'")
    if name and name.strip():
        conditions.append(f"`name` LIKE '%{name}%'")
    if price and price.strip():
        conditions.append(f"`price` LIKE '%{price}%'")
    if cat and cat.strip():
        conditions.append(f"`category` LIKE '%{cat}%'")
    if in_amount and in_amount.strip():
        conditions.append(f"`in_amount` LIKE '%{in_amount}%'")
    if out_amount and out_amount.strip():
        conditions.append(f"`out_amount` LIKE '%{out_amount}%'")
    if desc and desc.strip():
        conditions.append(f"`description` LIKE '%{desc}%'")
    
    if not conditions:
        messagebox.showwarning("", "Please fill up one of the entries")
        return

    sql += " AND ".join(conditions)

    cursor.execute(sql)
    try:
        result = cursor.fetchall()
        if result:
            # Clear the Treeview
            for data in my_tree.get_children():
                my_tree.delete(data)
            
            for entry in result:
                item_id = entry[0]
                item_code = entry[1]
                name = entry[2]
                price = entry[3]
                quantity = entry[4]
                category = entry[5]
                date = entry[6]
                in_amount = entry[7]
                out_amount = entry[8]
                description = entry[9]
                balance = entry[10]

                values = (item_id, item_code, name, price, quantity, category, date, in_amount, out_amount, description, balance)
                my_tree.insert(parent='', index='end', iid=entry, text="", values=(values), tag="orow")
            my_tree.tag_configure('orow', background="#EEEEEE")
        else:
            messagebox.showwarning("", "No data Found")
        conn.commit()
        conn.close()
    except Exception as e:
        messagebox.showwarning("", f"No data Found: {e}")
        
def clear():
    for num in range(0, 9):
        setph('', (num))

def exportExcel():
    cursor.connection.ping()
    sql = f"SELECT `item_ID`, `item_code`, `name`, `price`, `quantity`, `category`, `date`, `in_amount`, `out_amount`, `description`, `balance` FROM stock_mane ORDER BY id DESC"
    cursor.execute(sql)
    dataraw = cursor.fetchall()
    date = str(datetime.now())
    date = date.replace(' ', '_')
    date = date.replace(':', '-')
    dateFinal = date[0:16]
    with open("stock_mane" + dateFinal + ".csv", 'a', newline='') as f:
        w = csv.writer(f, dialect='excel')
        for record in dataraw:
            w.writerow(record)
    print("saved: stock_mane" + dateFinal + ".csv")
    conn.commit()
    conn.close()
    messagebox.showinfo("", "Excel file downloaded")

# Create the main frame
main_frame = tkinter.Frame(window, bg="#02577A")
main_frame.pack()

# Manage Frame
btnColor = "#196E77"
manageFrame = tkinter.LabelFrame(main_frame, text="Manage", borderwidth=5)
manageFrame.grid(row=0, column=0, sticky="w", padx=[10, 200], pady=20, ipadx=[6])

savebtn = Button(manageFrame, text="SAVE", width=10, borderwidth=3, bg=btnColor, fg='white', command=save)
updatebtn = Button(manageFrame, text="UPDATE", width=10, borderwidth=3, bg=btnColor, fg='white', command=update)
deletebtn = Button(manageFrame, text="DELETE", width=10, borderwidth=3, bg=btnColor, fg='white', command=delete)
seletebtn = Button(manageFrame, text="SELETE", width=10, borderwidth=3, bg=btnColor, fg='white', command=select)
findbtn = Button(manageFrame, text="FIND", width=10, borderwidth=3, bg=btnColor, fg='white', command=find)
clearbtn = Button(manageFrame, text="CLEAR", width=10, borderwidth=3, bg=btnColor, fg='white', command=clear)
exportbtn = Button(manageFrame, text="EXPORT EXCEL", width=10, borderwidth=3, bg=btnColor, fg='white', command=exportExcel)

savebtn.grid(row=0, column=0, padx=5, pady=5)
updatebtn.grid(row=0, column=1, padx=5, pady=5)
deletebtn.grid(row=0, column=2, padx=5, pady=5)
seletebtn.grid(row=0, column=3, padx=5, pady=5)
findbtn.grid(row=0, column=4, padx=5, pady=5)
clearbtn.grid(row=0, column=5, padx=5, pady=5)
exportbtn.grid(row=0, column=6, padx=5, pady=5)

# Entry Frame
entryFrame = tkinter.LabelFrame(main_frame, text="Form", borderwidth=5)
entryFrame.grid(row=1, column=0, sticky="w", padx=[10, 200], pady=[0, 20], ipadx=[6])

itemIdLabel = Label(entryFrame, text="Reference No", anchor="e", width=10)
itemCodeLabel = Label(entryFrame, text="Item Code", anchor="e", width=10)
nameLabel = Label(entryFrame, text="Name", anchor="e", width=10)
priceLabel = Label(entryFrame, text="Price", anchor="e", width=10)
qntLabel = Label(entryFrame, text="Qnt", anchor="e", width=10)
categoryLabel = Label(entryFrame, text="Category", anchor="e", width=10)
inLabel = Label(entryFrame, text="In", anchor="e", width=10)
outLabel = Label(entryFrame, text="Out", anchor="e", width=10)
descLabel = Label(entryFrame, text="Description", anchor="e", width=10)

itemIdLabel.grid(row=0, column=0, padx=5)
itemCodeLabel.grid(row=1, column=0, padx=5)
nameLabel.grid(row=2, column=0, padx=5)
priceLabel.grid(row=3, column=0, padx=5)
qntLabel.grid(row=4, column=0, padx=5)
categoryLabel.grid(row=5, column=0, padx=5)
inLabel.grid(row=6, column=0, padx=5)
outLabel.grid(row=7, column=0, padx=5)
descLabel.grid(row=8, column=0, padx=5)

categoryArray = ['item category 1', 'item category 2', 'item category 3', 'item category 4']

# Data entries
itemIdEntry = Entry(entryFrame, width=50, textvariable=placeholderArray[0])
itemCodeEntry = Entry(entryFrame, width=50, textvariable=placeholderArray[1])
nameEntry = Entry(entryFrame, width=50, textvariable=placeholderArray[2])
priceEntry = Entry(entryFrame, width=50, textvariable=placeholderArray[3])
qntEntry = Entry(entryFrame, width=50, textvariable=placeholderArray[4])
categoryCombo = ttk.Combobox(entryFrame, width=47, textvariable=placeholderArray[5], values=categoryArray)
inEntry = Entry(entryFrame, width=50, textvariable=placeholderArray[6])
outEntry = Entry(entryFrame, width=50, textvariable=placeholderArray[7])
descEntry = Entry(entryFrame, width=50, textvariable=placeholderArray[8])

itemIdEntry.grid(row=0, column=2, padx=5, pady=5)
itemCodeEntry.grid(row=1, column=2, padx=5, pady=5)
nameEntry.grid(row=2, column=2, padx=5, pady=5)
priceEntry.grid(row=3, column=2, padx=5, pady=5)
qntEntry.grid(row=4, column=2, padx=5, pady=5)
categoryCombo.grid(row=5, column=2, padx=5, pady=5)
inEntry.grid(row=6, column=2, padx=5, pady=5)
outEntry.grid(row=7, column=2, padx=5, pady=5)
descEntry.grid(row=8, column=2, padx=5, pady=5)

generateIdBtn = Button(entryFrame, text="Generate ID", borderwidth=3, bg=btnColor, fg='white', command=generateRand)
generateIdBtn.grid(row=0, column=3, padx=5, pady=5)

# Configure Treeview
my_tree['columns'] = ("Item Id", "Item Code", "Name", "Price", "Quantity", "Category", "Date", "In", "Out", "Description", "Balance")
my_tree.column("#0", width=0, stretch=NO)
my_tree.column("Item Id", anchor=W, width=70)
my_tree.column("Item Code", anchor=W, width=100)
my_tree.column("Name", anchor=W, width=125)
my_tree.column("Quantity", anchor=W, width=125)
my_tree.column("Price", anchor=W, width=100)
my_tree.column("Category", anchor=W, width=150)
my_tree.column("Date", anchor=W, width=150)
my_tree.column("In", anchor=W, width=70)
my_tree.column("Out", anchor=W, width=70)
my_tree.column("Description", anchor=W, width=150)
my_tree.column("Balance", anchor=W, width=100)
my_tree.heading("Item Id", text="Item Id", anchor=W)
my_tree.heading("Item Code", text="Item Code", anchor=W)
my_tree.heading("Name",text="Name", anchor=W)
my_tree.heading("Quantity", text="Quantity", anchor=W)
my_tree.heading("Price", text="Price", anchor=W)
my_tree.heading("Category", text="Category", anchor=W)
my_tree.heading("Date", text="Date", anchor=W)
my_tree.heading("In", text="In", anchor=W)
my_tree.heading("Out", text="Out", anchor=W)
my_tree.heading("Description", text="Description", anchor=W)
my_tree.heading("Balance", text="Balance", anchor=W)
my_tree.tag_configure('orow', background="#EEEEEE")

# Pack the Treeview below all the frames
my_tree.pack(pady=20)
refreshTable()

window.resizable(False, False)
window.mainloop()
