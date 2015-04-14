#IPP projekt 2
#Autor: Jindrich Dudek
#JMP:xdudek04
import sys, getopt
import os.path

#nastaveni zadanych tagu na hodnotu False, tagy slouzi pro overeni duplicitnich zadani:
input_tag = False
output_tag = False
cmd_tag = False
r_tag = False

#nastaveni vychozich souboru pro vstup, vystup a parametr cmd
input_file = sys.stdin
output_file = sys.stdout
cmd_text = ""

#zpracovani parametru:
try:
	options, args = getopt.getopt(sys.argv[1:], "r", ["help", "input=", "output=", "cmd="]) #zpracovani parametru prikazove radky
except getopt.GetoptError: #osetreni chybovych stavu
	print("CHYBA: Prepinace byly chybne zadany.", file=sys.stderr)
	sys.exit(1)
for option, arg in options:
	if (option == "--help"):
		if (len(sys.argv) != 2): #Pokud byly spolu s --help zadany i jine prepinace
			print("CHYBA: Prepinac --help nelze kombinovat s jinymi prepinaci.", file=sys.stderr)
			sys.exit(1)
		print("Zadana napoveda.")
		sys.exit(0)
	elif (option == "--input"):
		if (input_tag == True): #pokud je prepinac zadan podruhe
			print("CHYBA: Prepinac --input byl zadan duplicitne.", file=sys.stderr)
			sys.exit(1)
		input_filename = arg
		input_tag = True
	elif (option == "--output"):
		if (output_tag == True): #pokud je prepinac zadan podruhe
			print("CHYBA: Prepinac --output byl zadan duplicitne.", file=sys.stderr)
			sys.exit(1)
		output_filename = arg
		output_tag = True
	elif (option == "--cmd"): #pokud je prepinac zadan podruhe
		if (cmd_tag == True):
			print("CHYBA: Prepinac --cmd byl zadan duplicitne.", file=sys.stderr)
			sys.exit(1)
		cmd_text = arg
		cmd_tag = True
	elif (option == "-r"):
		if (r_tag == True): #pokud je prepinac zadan podruhe
			print("CHYBA: Prepinac -r byl zadan duplicitne.", file=sys.stderr)
			sys.exit(1)
		r_tag = True

if (len(args) != 0): #Pokud byly zadany neplatne prepinace
	print("CHYBA: Prepinace byly chybne zadany.", file=sys.stderr)
	sys.exit(1)

#Samotna cinnost skriptu:
if (input_tag == True): #Pokud byl zadan prepinac --input
	if (os.path.isfile(input_filename) == True): #Overeni, zda soubor existuje
		try: #Overeni, zda lze soubor otevrit
			input_file = open(input_filename, "r")
		except IOError:
			print("CHYBA: Nelze otevrit vstupni soubor.", file=sys.stderr)
			sys.exit(2)
	else: #Pokud soubor neexistuje
		print("CHYBA: Soubor zadany pomoci prepinace --input neexistuje.", file=sys.stderr)
		sys.exit(2)
file_content = input_file.read() #Nacteni obsahu souboru do promenne
if (input_tag == True): #Zavreni souboru
	input_file.close()

#Inicializace promennych uzivanych v konecnem automatu:
content_len = len(file_content) #Zjisteni delky retezce
i = 0 #Ridici promenna
present_state = "common_text" #Nastaveni pocatecniho stavu pro konecny automat
brackets_count = 0 #Pocitadlo zavorek v bloku

#Konecny automat:
while (i < content_len): #Prochazeni souboru po jednotlivych znacich
	if (present_state == "common_text"): #Stav reprezentujici pozici v normalnim textu
		if (file_content[i] == '@'):
			present_state = "at_sign_read" #Nastaveni nasledujiciho stavu na stav, kde se rozhoduje, zda se jedna o makro nebo escape sekvenci
		elif (file_content[i] == '{'):
			present_state = "block" # Nastaveni nasledujiciho stavu na pocatek bloku
			i = i - 1 #Zajisti, ze v pristim cyklu budeme stale na stejnem znaku
		elif ((file_content[i] == '}') or (file_content[i] == '$')):
			print("CHYBA: Syntakticka chyba.", file=sys.stderr)
			sys.exit(55)
		else: #Pokud se jedna o jakykoliv jiny znak, tiskne se na vystup
			print(file_content[i], end="")
	elif (present_state == "at_sign_read"): #Stav reprezentujici nacteny znak @
		if ((file_content[i] == '@') or (file_content[i] == '{') or (file_content[i] == '}') or (file_content[i] == '$')): #Pokud se jedna o escape sekvenci
			print(file_content[i], end="")
			present_state = "common_text"
		elif (((ord(file_content[i]) >= ord('a')) and (ord(file_content[i]) <= ord('z'))) or ((ord(file_content[i]) >= ord('A')) and (ord(file_content[i]) <= ord('Z'))) or (file_content[i] == '_')): #Pokud je znak mezi A-Z nebo a-z nebo _ jedna se nazev makra
			i = i - 1 #Zajisti, ze v pristim cyklu budeme stale na stejnem znaku 
			present_state = "macro_beggining"
		else:
			print("CHYBA: Syntakticka chyba.", file=sys.stderr)
			sys.exit(55)
	elif (present_state == "block"):
		if (file_content[i] == '{'):
			if (brackets_count == 0):
				brackets_count = brackets_count + 1
			else:
				print(file_content[i], end="")
				brackets_count = brackets_count + 1
		elif (file_content[i] == '}'):
			brackets_count = brackets_count - 1
			if (brackets_count == 0):
				present_state = "common_text"
			else:
				print(file_content[i], end="")
		elif (file_content[i] == '@'):
			present_state = "at_sign_in_block"
		else:
			print(file_content[i], end="")
	elif (present_state == "at_sign_in_block"):
		if ((file_content[i] != '{') and (file_content[i] != '}') and (file_content[i] != '@')):
			print("@", end="")
		print(file_content[i], end="")
		present_state = "block"

	i = i + 1
if (present_state != "common_text"):
	print("CHYBA: Syntakticka chyba.", file=sys.stderr)
	sys.exit(55)
sys.exit(0)
