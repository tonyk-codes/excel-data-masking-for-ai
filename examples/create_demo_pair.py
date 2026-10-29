from openpyxl import Workbook

before = Workbook()
ws = before.active
ws.title = "Raw Data"
ws.append(["Customer", "Location", "Amount"])
ws.append(["Example Company", "Hong Kong", 45000])
ws.append(["Another Company", "Singapore", 12000])
before.save("before_demo.xlsx")

after = Workbook()
ws = after.active
ws.title = "Summary"
ws.append(["Customer", "Amount"])
ws.append(["Example Company", 45000])
ws.append(["Another Company", 12000])
after.save("after_demo.xlsx")
print("Created before_demo.xlsx and after_demo.xlsx")
