from sys import platform
import tkinter as tk
from tkinter import scrolledtext
import mysql.connector
from datetime import datetime, timedelta

# Select the order_id to start from and how many results to show
start_from=13925
limit_by=20


def sqlGetResults():
    con = mysql.connector.connect(user='username', password='replace_with_working_pass',
                              host='demohost.com',
                              database='adhoc_gr_elast')
    txt_main.delete(1.0,'end')
    cursor = con.cursor()

    query = ("SELECT adhoc_gr_elast.vhy5i_virtuemart_orders.virtuemart_order_id as order_id,"
                    "adhoc_gr_elast.vhy5i_virtuemart_orders.created_on as order_date,"
                    "adhoc_gr_elast.vhy5i_virtuemart_userinfos.name as name,"
                    "cast(adhoc_gr_elast.vhy5i_virtuemart_orders.order_total as decimal(6,2)) as total,"
                    "adhoc_gr_elast.vhy5i_virtuemart_orders.ip_address as ip,"
                    "adhoc_gr_elast.vhy5i_virtuemart_orders.customer_note as note "
             "FROM "
                    "adhoc_gr_elast.vhy5i_virtuemart_orders inner join adhoc_gr_elast.vhy5i_virtuemart_userinfos "
                    "ON adhoc_gr_elast.vhy5i_virtuemart_orders.virtuemart_user_id "
                    "= adhoc_gr_elast.vhy5i_virtuemart_userinfos.virtuemart_user_id "
             "WHERE virtuemart_order_id > %s "
             "ORDER BY virtuemart_order_id desc "
             "LIMIT %s;")

    cursor.execute(query, (start_from, limit_by))

    result_header = 'Order | Ημερομηνία        | Επωνυμία πελάτη              | Σύνολο   | Σχόλια παραγγελίας   |\n' + \
            '======|===================|==============================|==========|======================|\n'

    txt_main.insert('insert', result_header)

    for ( order_id, order_date, name, total, ip, note) in cursor:
            txt_main.insert('insert',f'{order_id} | {order_date + timedelta(hours=3):%d %b %Y %H:%M} \
| {name[:28]:28} | {total:8.2f} | {note[:20]:20} |\n')

    cursor.close()
    con.close()


def copy(event=None):
    txt_main.event_generate('<<Copy>>')
    txt.focus()
    txt_main.selection_clear()
    return 'break'

def closeApp(event=None):
    window.quit()
    return 'break'

def selectAll(event=None):
    txt_main.focus()
    txt_main.tag_add('sel', 1.0, 'end')
    return 'break'

# Cosmetics go here, color and such
windowclr = 'LightBlue4'
searchclr = 'orange'
textclr = 'floral white'

window = tk.Tk()
window.title('Παραγγελίες Β2Β')
window.geometry('800x480')
window.config(border=8, background=windowclr)

frame = tk.Frame(window, background=windowclr)
# Adding the top menu
menu_bar = tk.Menu(window)
file_menu = tk.Menu(menu_bar, tearoff=0)
# File menu item are beneath
menu_bar.add_cascade(label='File', menu=file_menu, underline=0)
file_menu.add_command(label='Exit', accelerator='Ctrl + Q', underline=0, command=closeApp)

edit_menu = tk.Menu(menu_bar, tearoff=0)
# Edit menu item are beneath
menu_bar.add_cascade(label='Edit', menu=edit_menu, underline=0)
edit_menu.add_command(label='Copy', accelerator='Ctrl + C', underline=0, command=copy)
edit_menu.add_command(label='Select All', accelerator='Ctrl + A', underline=7, command=selectAll)

window.config(menu=menu_bar)


btn = tk.Button(frame, text='Ανανέωση', font=('Arial', 10), bg=searchclr, fg='white', padx=6, command=sqlGetResults)
txt_main = scrolledtext.ScrolledText(window, wrap='none', selectbackground='yellow', selectforeground='black', padx=5, pady=5, font=("DejaVu Sans Mono", 10))
txt_main.bind('<Button-3>', copy)
window.bind('<Control-c>', copy)
window.bind('<Control-q>', closeApp)
window.bind('<Control-a>', selectAll)
window.bind('<Control-C>', copy)
window.bind('<Control-Q>', closeApp)
window.bind('<Control-A>', selectAll)

btn.pack( side = 'left', padx=10)
frame.pack( pady = 6)
txt_main.pack( fill = 'both', expand=1)

window.mainloop()
