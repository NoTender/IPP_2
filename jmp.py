#IPP projekt 2
#Autor: Jindrich Dudek
#JMP:xdudek04
import sys, getopt
import os.path
import re

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

def get_paramname(content_len): #Funkce, ktera ziska nazev parametru pri definici makra 
	global i
	global file_content
	param = "$"
	while ((i < content_len) and (file_content[i].isalnum() or file_content[i] == '_')):
		param = param + file_content[i]
		i = i + 1
	i = i - 1
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

help_text = ("Program:                 Jednoduchy makroprocesor\n"
"Autor:                   Jindrich Dudek, 2015\n"
"Funkce:                  Skript plni funkci jednoducheho makroprocesoru.\n"
"Parametry skriptu:\n"
"   --help                Vypise napovedu ke skriptu, parametr nesmi byt kombinovan s\n"
"                         jinymi parametry.\n"
"   --input=filename      Zadany vstupni textovy soubor s ASCII kodovanim.\n"
"   --output=filename     Zadany vystupni soubor v ASCII kodovani.\n"
"   --cmd=text            Zadany text bude pred zacatkem zpracovani vstupu umisten na jeho zacatek.\n"
"   -r                    V pripade redefinice jiz existujiciho makra zpusobi skript chybu.")

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
		print(help_text)
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
file_content = "" #Inicializace retezce do ktereho se bude nacitat obsah souboru
if (cmd_tag == True):
	file_content = file_content + cmd_text
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
file_content = file_content + input_file.read() #Nacteni obsahu souboru do promenne
if (input_tag == True): #Zavreni souboru
	input_file.close()

if (output_tag == True): #Pokud byl zadan prepinac --output
	try: #Overeni, zda jde soubor otevrit
		output_file = open(output_filename, "w")
	except IOError:
		print("CHYBA: Nelze otevrit soubor pro zapis", file=sys.stderr)
		sys.exit(3)


#Inicializace promennych uzivanych v konecnem automatu:
content_len = len(file_content) #Zjisteni delky retezce
i = 0 #Ridici promenna
present_state = "common_text" #Nastaveni pocatecniho stavu pro konecny automat
brackets_count = 0 #Pocitadlo zavorek v bloku
macro_name = "" #Retezec na ukladani jmena makra
macro_names = ["def", "undef", "set", "__def__", "__undef__", "__set__"] #Inicializace pole s nazvy maker preddefinovanymi makry
macro_table = {'def':[[], ""], 'undef':[[],""], 'set':[[],""], '__def__':[[],""], '__undef__':[[],""], '__set__':[[],""]}
def_redefined = False
undef_redefined = False
set_redefined = False
skip_whitespaces = False
macro_args = [] #Do teto promenne se ukladaji hodnoty parametru pri expanzi makra
error_tag = False #Promenna urcujici, zda doslo k urcite chybe


#Konecny automat:
while (i < content_len): #Prochazeni souboru po jednotlivych znacich
	if (skip_whitespaces == True): #Pokud se jedna o bily znak a bile znaky se maji preskakovat
		if (file_content[i].isspace()):
			if (present_state == "at_sign_read"):
				print("CHYBA: Syntakticka chyba.", file=sys.stderr)
				sys.exit(55)
			if (present_state not in ["block", "at_sign_in_block"]): #Pokud se nevyskytujem v bloku, preskoc znak
				i = i + 1
				continue
	else:
		if ((file_content[i].isspace()) and (present_state == "macro_definition_params_2")):
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
			print(file_content[i], end="", file=output_file)
	elif (present_state == "at_sign_read"): #Stav reprezentujici nacteny znak @
		if ((file_content[i] == '@') or (file_content[i] == '{') or (file_content[i] == '}') or (file_content[i] == '$')): #Pokud se jedna o escape sekvenci
			print(file_content[i], end="", file=output_file)
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
				print(file_content[i], end="", file=output_file)
				brackets_count = brackets_count + 1
		elif (file_content[i] == '}'):
			brackets_count = brackets_count - 1
			if (brackets_count == 0): #Pokud se jednalo o posledni zavorku
				present_state = "common_text"
			else:
				print(file_content[i], end="", file=output_file)
		elif (file_content[i] == '@'): #Pokud se jedna o @
			present_state = "at_sign_in_block"
		else: #Pokud se jedna o jakykoliv jiny znak, vytiskne se
			print(file_content[i], end="", file=output_file)
	elif (present_state == "at_sign_in_block"): #Escape sekvence nalezena v bloku
		if ((file_content[i] != '{') and (file_content[i] != '}') and (file_content[i] != '@')):
			print("@", end="", file=output_file)
		print(file_content[i], end="", file=output_file)
		present_state = "block"
	elif (present_state == "macro_beggining"): #Stav do ktereho se dostane automat, pokud je na vstupu @ za kterym nasleduje A-Z,a-z,_
		macro_name = get_macroname(content_len)
		if (macro_name == "def" and (macro_name in macro_names)):
			if (def_redefined == False):
				present_state = "macro_definition"
				error_tag = True
			else:
				present_state = "macro_expansion"
				i = i - 1
				macro_args = []
		elif (macro_name == "undef" and (macro_name in macro_names)):
			if (undef_redefined == False):
				present_state = "macro_undefinition"
				error_tag = True
			else:
				present_state = "macro_expansion"
				i = i - 1
				macro_args = []
		elif (macro_name == "set" and (macro_name in macro_names)):
			if (set_redefined == False):
				present_state = "macro_set"
				error_tag = True
			else:
				present_state = "macro_expansion"
				i = i - 1
				macro_args = []
		elif (macro_name == "__def__"):
			present_state = "macro_definition"
			error_tag = True
		elif (macro_name == "__undef__"):
			present_state = "macro_undefinition"
			error_tag = True
		elif (macro_name == "__set__"):
			present_state = "macro_set"
			error_tag = True
		elif (macro_name in macro_names):
			present_state = "macro_expansion"
			i = i - 1
			macro_args = []
		else:
			print("CHYBA: Semanticka chyba.", file=sys.stderr)
			sys.exit(56)
	elif (present_state == "macro_set"): #Pokud je na vstupu makro set
		error_tag = False
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
						print("CHYBA: Semanticka chyba.", file=sys.stderr)
						sys.exit(56) #OVERIT CHYBU
				else: #Pokud se zasahuje mimo string
					print("CHYBA: Semanticka chyba.", file=sys.stderr)
					sys.exit(56) #OVERIT CHYBU
			else: #Pokud se zasahuje mimo string
				print("CHYBA: Semanticka chyba.", file=sys.stderr)
				sys.exit(56) #OVERIT CHYBU
		else: #Pokud za makrem set neni {
			print("CHYBA: Semanticka chyba.", file=sys.stderr)
			sys.exit(56) #OVERIT CHYBU
		present_state = "common_text"
	elif (present_state == "macro_definition"): #proces definice makra - ziskani nazvu definovaneho makra
		error_tag = False
		if (file_content[i] == '@'): #Dalsim znakem po makru def/__def__ musi byt @
			if (i + 1 < content_len):
				i = i + 1 #Posunuti na dalsi znak
				if (file_content[i].isalpha() or file_content[i] == '_'): #Povolene znaky, kterymi muze zacinat makro
					macro_name = get_macroname(content_len) #Ziska se nazev makra
					if (r_tag == True):
						if (macro_name in macro_names):
							print("CHYBA: Nelze predefinovat jiz definovane makro.", file=sys.stderr)
							sys.exit(57)
					if ((macro_name == "__def__") or (macro_name == "__set__") or (macro_name == "__undef__")): #Pokud se uzivatel snazi predefinovat nepredefinovatelna makra
						print("CHYBA: Snaha predefinovat makra, ktera predefinovat nelze.", file=sys.stderr)
						sys.exit(57)
					elif (macro_name == "def"): #Nastaveni tagu pokud je nejake z vestavenych maker predefinovano
						def_redefined = True
					elif (macro_name == "set"):
						set_redefined = True
					elif (macro_name == "undef"):
						undef_redefined = True
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
	elif (present_state == "macro_definition_params_1"): #Kontrola, zda za nazvem makra nasleduje { a inicializace prazdneho seznamu pro parametry
		if (file_content[i] == '{'):
			macro_parameters = []
			present_state = "macro_definition_params_2"
		else:
			print("CHYBA: Semanticka chyba.", file=sys.stderr)
			sys.exit(56) #OVERIT CHYBU
	elif (present_state == "macro_definition_params_2"): #Nacitani jednotlivych parametru makra
		if (file_content[i] != '}'): #Pokud jsou jeste nenactene argumenty
			if (file_content[i] == '$'): #Pokud je prvnim znakem parametru $
				if (i + 1 < content_len): #Kontrola meze stringu
					i = i + 1 #Posunuti na dalsi radek
					if (file_content[i].isalpha() or (file_content[i] == '_')): #Prvni znak po $ musi byt A-Z,a-z,_
						parameter = get_paramname(content_len)
						macro_parameters.append(parameter)
					else: #Neplatny nazev makra
						print("CHYBA: Syntakticka chyba.", file=sys.stderr)
						sys.exit(55)
				else: #Pokud jsme predcasne narazili na konec stringu
					print("CHYBA: Syntakticka chyba.", file=sys.stderr)
					sys.exit(55)
			else: #Pokud prvnim znakem parametru neni dolar
				print("CHYBA: Syntakticka chyba.", file=sys.stderr)
				sys.exit(55) #OVERIT CHYBU
		else: #Pokud byla nactena } konci cast ziskavani parametru
			present_state = "macro_definition_body"
	elif (present_state == "macro_definition_body"): #Stav reprezentujici nacitani tela makra
		if (file_content[i] == '{'):
			brackets_count_body = 0
			macro_body = ""
			while (True): #Nacteni tela makra do retezce
				if (file_content[i] == '{'):
					if (brackets_count_body == 0): #Pokud se jedna o prvni zavorku, neni soucasti tela makra
						brackets_count_body = brackets_count_body + 1
					else: #Pokud se jedna o dalsi uzaviraci zavorku
						macro_body = macro_body + file_content[i]
						brackets_count_body = brackets_count_body + 1
				elif (file_content[i] == '}'):
					brackets_count_body = brackets_count_body - 1
					if (brackets_count_body == 0): #Pokud je zavorka posledni zavorkou
						break
					else:
						macro_body = macro_body + file_content[i]
				else: #Pokud se jedna o jakykoliv jiny znak
					macro_body = macro_body + file_content[i]
				i = i + 1
				if (i >= content_len): #Pokud je predcasny konec souboru
					break
			if (brackets_count_body != 0):
				print("CHYBA: Syntakticka chyba.", file=sys.stderr)
				sys.exit(55)
			if (macro_name not in macro_names):
				macro_names.append(macro_name)
			macro_table[macro_name] = [macro_parameters, macro_body]
			present_state = "common_text"
		else: #Chybi pocatecni zavorka {
			print("CHYBA: Semanticka chyba.", file=sys.stderr)
			sys.exit(56)
	elif (present_state == "macro_expansion"): #Nacitani argumentu a expanze makra
		#Na zacatku tohoto stavu se v souboru nachazime na poslednim znaku expandovaneho makra
		#Cast nacitani argumentu makra:
		if (len(macro_args) < len(macro_table[macro_name][0])): #Pokud je pocet nactenych argumentu mensi nez pocet parametru makra - tzn. je potreba nacist argumenty
			i = i + 1 #Posunuti se na dalsi znak - prvni znak za nazvem makra
			while ((i < content_len) and (len(macro_args) < len(macro_table[macro_name][0]))): #Dokud nenarazime na konec souboru nebo nejsou nacteny vsechny argumenty makra
				if (file_content[i].isspace() and skip_whitespaces == True): #Pokud je znakem bily znak a je zapotrebi ho preskocit
					i = i + 1
					continue
				if (file_content[i] == '{'): #Pokud je parametrem blok
					brackets_count_expansion = 0
					param = "" #Vynulovani na prazdny retezec
					while (True): #Nacteni tela parametru do retezce
						if (file_content[i] == '{'):
							if (brackets_count_expansion == 0): #Pokud se jedna o prvni zavorku, neni soucasti tela makra
								brackets_count_expansion = brackets_count_expansion + 1
							else: #Pokud se jedna o dalsi oteviraci zavorku
								param = param + file_content[i]
								brackets_count_expansion = brackets_count_expansion + 1
						elif (file_content[i] == '}'):
							brackets_count_expansion = brackets_count_expansion - 1
							if (brackets_count_expansion == 0): #Pokud je zavorka posledni zavorkou
								break
							else:
								param = param + file_content[i]
						else: #Pokud se jedna o jakykoliv jiny znak
							param = param + file_content[i]
						i = i + 1
						if (i >= content_len): #Pokud je predcasny konec souboru
							break
					if (brackets_count_expansion != 0):
						print("CHYBA: Syntakticka chyba.", file=sys.stderr)
						sys.exit(55)
					macro_args.append(param)
				elif (file_content[i] == '@'): #Pokud je argumentem makro
					param = '@'
					if (i + 1 < content_len): #Pokud se za @ jeste neco nachazi
						i = i + 1
						if (file_content[i].isalpha() or file_content[i] == '_'):
							param = param + get_macroname(content_len)
							macro_args.append(param)
						else: #Pokud makro nezacina jednim z povolenych znaku
							print("CHYBA: Syntakticka chyba.", file=sys.stderr)
							sys.exit(55)
					else: #Pokud je @ poslednim znakem v souboru
						print("CHYBA: Syntakticka chyba.", file=sys.stderr)
						sys.exit(55)
				else: #Pokud se jedna o jakykoliv jiny znak
					macro_args.append(file_content[i])
				i = i + 1
			if (len(macro_args) != len(macro_table[macro_name][0])): #Pokud skoncil cyklus a vsechny parametry jeste nejsou nacteny
				print("CHYBA: Semanticka chyba.", file=sys.stderr)
				sys.exit(56)
			i = i -1 #Posunuti se o znak dozadu, nachazime se na poslednim znaku posledniho parametru (zavorka } nebo posledni pismeno makra nebo nacteny znak jako parametr)
		#Pokud jsou jiz argumenty nacteny, nebo nebylo zapotrebi argumenty nacitat:
		j = 0 #Pocitadlo cyklu
		expanded_body = macro_table[macro_name][1] #Do promenne se nacte telo makra
		while (j < len (macro_args)): #pro kazdy parametr udelej nasledujici - nahrad promennou v tele jeji hodnotou
			pattern = '(?<!@)\\' + macro_table[macro_name][0][j] + '\\b' #Vytvoreni regexu, kterym se bude nahrazovat v tele makra
			expanded_body = re.sub(pattern, macro_args[j], expanded_body) #Nahrazeni promenne jeji hodnotou
			j = j + 1
		expanded_body = re.sub('@\$','$', expanded_body) #Nahrazeni escape sekvence dolaru
		file_content = file_content[0:i+1] + expanded_body + file_content[i+1:] #Pridani expandovaneho tela na vstup
		content_len = len(file_content) #Prepocitani delky retezce
		present_state = "common_text" #Prechod do normalniho stavu
	elif (present_state == "macro_undefinition"):
		error_tag = False
		if (file_content[i] == '@'): #Pokud je prvnim znakem @
			if (i + 1 < content_len): #Pokud je za @ jeste nejaky znak
				i = i + 1
				if (file_content[i].isalpha() or file_content[i] == '_'): #Prvni znak nazvu makra musi byt A-Z,a-z,_
					macro_name = get_macroname(content_len) #Zjisteni nazvu makra
					if ((macro_name == "__def__") or (macro_name == "__undef__") or (macro_name == "__set__")):
						print("CHYBA: Snaha undefinovat makra, ktera undefinovat nelze.", file=sys.stderr)
						sys.exit(57)
					if (macro_name in macro_names): #Pokud je makro definovane
						del macro_table[macro_name]
						macro_names.remove(macro_name)
					else: #Pokud makro neexistuje
						print("CHYBA: Makro, ktere se snazite undefinovat neexistuje.", file=sys.stderr)
					present_state = "common_text"
				else:
					print("CHYBA: Syntakticka chyba.", file=sys.stderr)
					sys.exit(55)
			else:
				print("CHYBA: Syntakticka chyba.", file=sys.stderr)
				sys.exit(55)
		else: #Pokud prvnim znakem neni @
			print("CHYBA: Semanticka chyba.", file=sys.stderr)
			sys.exit(56)
	i = i + 1
if (error_tag == True):
	print("CHYBA: Semanticka chyba.", file=sys.stderr)
	sys.exit(56)
if (present_state == "macro_definition_params_1" or present_state == "macro_definition_body"):
	print("CHYBA: Semanticka chyba.", file=sys.stderr)
	sys.exit(56)
if (present_state != "common_text"):
	print("CHYBA: Syntakticka chyba.", file=sys.stderr)
	sys.exit(55)
if(output_tag == True): #Zavreni vystupniho souboru
	output_file.close()
sys.exit(0)
