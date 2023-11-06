from datetime import datetime, timedelta

A = datetime.strptime("09/05/2019", '%d/%m/%Y')
B = datetime.strptime("01/10/2020", '%d/%m/%Y')
lista = [A, B]

print(min(lista))
