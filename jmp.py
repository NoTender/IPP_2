#IPP projekt 2
#Autor: Jindrich Dudek
#JMP:xdudek04
import sys, getopt
import os.path

def macro_defined(macro_names, macro_name): #Funkce, ktera vraci True v pripade, ze se zadane makro vyskytuje v seznamu definovanych maker 
	for macro in macro_names:
		if (macro == macro_name):
			return True
	return False

def get_macroname(content_len): #Funkce, ktera vraci jmeno makra ze souboru
	global i
	global file_content
	macro_name = ""
	while ((i < content_len) and (file_content[i].isalnum() or file_content[i] == '_')): #Prochazeni zdrojoveho textu
		macro_name = macro_name + file_content[i]
		i = i + 1
	i = i - 1 #Zajisti, ze v dalsim cyklu mimo funkci bude prvni znak nasledujici za jmenem makra
	return macro_name
def get_setparam(content_len): #Funkce, ktera ziska parametr pro makro set
	global i
	global file_content
	param = ""
	while ((i < content_len) and ((file_content[i] == "+") or (file_content[i] == "-") or (file_content[i] == "_") or ((ord(file_content[i]) >= ord("A")) and (ord(file_content[i]) <= ord("Z"))))): #Znak muze byt +,-,_,A-Z
		param = param + file_content[i]
		i = i + 1
	return param

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
macro_name = "" #Retezec na ukladani jmena makra
macro_names = ["def", "undef", "set", "__def__", "__undef__", "__set__"] #Inicializace pole s nazvy maker preddefinovanymi makry
def_redefined = False
undef_redefined = False
set_redefined = False
skip_whitespaces = False


#Konecny automat:
while (i < content_len): #Prochazeni souboru po jednotlivych znacich
	if (file_content[i].isspace() and (skip_whitespaces == True)): #Pokud se jedna o bily znak a bile znaky se maji preskakovat
		if (present_state == "at_sign_read"):
			print("CHYBA: Syntakticka chyba.", file=sys.stderr)
			sys.exit(55)
		if (present_state not in ["block", "at_sign_in_block"]): #Pokud se nevyskytujem v bloku, preskoc znak
			i = i + 1
			continue
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
	elif (present_state == "block"): #Stav reprezentujici blok v beznem textu
		if (file_content[i] == '{'): 
			if (brackets_count == 0): #Pokud se jedna o prvni oteviraci zavorku
				brackets_count = brackets_count + 1
			else: #Pokud se nejedna o oteviraci zavorku => vytiskne se
				print(file_content[i], end="")
				brackets_count = brackets_count + 1
		elif (file_content[i] == '}'):
			brackets_count = brackets_count - 1
			if (brackets_count == 0): #Pokud se jednalo o posledni zavorku
				present_state = "common_text"
			else:
				print(file_content[i], end="")
		elif (file_content[i] == '@'): #Pokud se jedna o @
			present_state = "at_sign_in_block"
		else: #Pokud se jedna o jakykoliv jiny znak, vytiskne se
			print(file_content[i], end="")
	elif (present_state == "at_sign_in_block"): #Escape sekvence nalezena v bloku
		if ((file_content[i] != '{') and (file_content[i] != '}') and (file_content[i] != '@')):
			print("@", end="")
		print(file_content[i], end="")
		present_state = "block"
	elif (present_state == "macro_beggining"): #Stav do ktereho se dostane automat, pokud je na vstupu @ za kterym nasleduje A-Z,a-z,_
		macro_name = get_macroname(content_len)
		if (macro_name == "def"):
			if (def_redefined == False):
				present_state = "macro_definition"
			else:
				present_state = "macro_expansion"
		elif (macro_name == "undef"):
			if (undef_redefined == False):
				present_state = "macro_undefinition"
			else:
				present_state = "macro_expansion"
		elif (macro_name == "set"):
			if (set_redefined == False):
				present_state = "macro_set"
			else:
				present_state = "macro_expansion"
		elif (macro_name == "__def__"):
			present_state = "macro_definition"
		elif (macro_name == "__undef__"):
			present_state = "macro_undefinition"
		elif (macro_name == "__set__"):
			present_state = "macro_set"
		elif (macro_name in macro_names):
			present_state = "macro_expansion"
		else:
			print("CHYBA: Semanticka chyba.", file=sys.stderr)
			sys.exit(56)
	elif (present_state == "macro_set"): #Pokud je na vstupu makro set
		if (file_content[i] == '{'): #Za @set musi byt {
			if (i + 1 < content_len): #Osetreni zda nezasahujem mimo string
				i = i + 1 #Posunuti na dalsi znak
				param = get_setparam(content_len) #Ziskani parametru makra set
				if (param == "+INPUT_SPACES"):
					skip_whitespaces = False
				elif (param == "-INPUT_SPACES"):
					skip_whitespaces = True
				else: #Pokud je chybny parametr makra set
					print("CHYBA: Semanticka chyba.", file=sys.stderr)
					sys.exit(56)
				if (i < content_len): #Osetreni zda nezasahujem mimo string
					if (file_content[i] != "}"): #Posledni znak musi byt }
						print("CHYBA: Syntakticka chyba.", file=sys.stderr)
						sys.exit(55) #OVERIT CHYBU
				else: #Pokud se zasahuje mimo string
					print("CHYBA: Syntakticka chyba.", file=sys.stderr)
					sys.exit(55) #OVERIT CHYBU
			else: #Pokud se zasahuje mimo string
				print("CHYBA: Syntakticka chyba.", file=sys.stderr)
				sys.exit(55) #OVERIT CHYBU
		else: #Pokud za makrem set neni {
			print("CHYBA: Syntakticka chyba.", file=sys.stderr)
			sys.exit(55) #OVERIT CHYBU
		present_state = "common_text"
	elif (present_state == "macro_definition"): #proces definice makra - ziskani nazvu definovaneho makra
		if (file_content[i] == '@'): #Dalsim znakem po makru def/__def__ musi byt @
			if (i + 1 < content_len):
				i = i + 1 #Posunuti na dalsi znak
				if (file_content[i].isalpha() or file_content[i] == '_'): #Povolene znaky, kterymi muze zacinat makro
					macro_name = get_macroname(content_len) #Ziska se nazev makra
					present_state = "macro_definition_params_1"
				else:
					print("CHYBA: Syntakticka chyba.", file=sys.stderr)
					sys.exit(55)
			else:
				print("CHYBA: Syntakticka chyba.", file=sys.stderr)
				sys.exit(55) #OVERIT CHYBU
		else:
			print("CHYBA: Semanticka chyba.", file=sys.stderr)
			sys.exit(56)
	elif (present_state == "macro_definition_params_1"):
		#Zde kontrolovat zavorku { a inicializovat seznam parametru, a zamyslet se nad tim, co se stane, pokud v parametrech nebude nic, za zacatek stavu s cislem 2 dat podminku, jestli je znak rozdilny od }


	i = i + 1
if (present_state != "common_text"):
	print("CHYBA: Syntakticka chyba.", file=sys.stderr)
	sys.exit(55)
sys.exit(0)
