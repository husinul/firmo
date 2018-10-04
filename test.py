import os
def extr():
    input('which tool you uses\n1.binwalk\n2.firmwalker\n:')
    firma = input("enter firmware:")
    os.system("binwalk"+'\t'+firma)

a= extr()
print(a)


