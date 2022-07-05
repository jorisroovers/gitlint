from colorama import init, deinit
from colorama import Fore, Back, Style
init()

print(Fore.CYAN + 'some cyan text')
print(Style.RESET_ALL)
print('back to normal now')

deinit()