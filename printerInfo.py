import win32print

flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
names = sorted({p[2] for p in win32print.EnumPrinters(flags)})
print("Принтеры в системе:")
for n in names:
    print(" -", n)

print("\nПринтер по умолчанию:", win32print.GetDefaultPrinter())


