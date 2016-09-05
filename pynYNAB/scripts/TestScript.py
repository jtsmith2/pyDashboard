from pynYNAB.Client import nYnabClient
from pynYNAB.connection import nYnabConnection
from pynYNAB.schema.budget import Payee, Transaction
import datetime

connection = nYnabConnection('jtsmith2@gmail.com', 'w1r3l355')
client = nYnabClient(connection, 'My Budget')

subs = {}
balances = {}

#Gets subcategories from YNAB that have "Show in Dashboard" in the notes section
for ctg in client.budget.be_subcategories:
    if ctg.note is not None:
        if 'Show in Dashboard' in ctg.note:
            subs[ctg.name]=ctg

#Gets current month budget calculations
for b in client.budget.be_monthly_subcategory_budget_calculations:
    if b.entities_monthly_subcategory_budget_id[4:11]==(datetime.datetime.now().strftime('%Y-%m')):
        balances[b.entities_monthly_subcategory_budget_id[12:]]=b

#Displays the balance for each subcategory in the subs dict
for s in subs:
    print s+':', balances[subs[s].id].balance


