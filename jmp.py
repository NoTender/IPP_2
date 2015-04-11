#IPP projekt 2
#Autor: Jindrich Dudek
#JMP:xdudek04
import sys, getopt

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

sys.exit(0)
