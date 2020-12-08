#!/usr/bin/python3
# coding: utf8

# This file generates a LateX source file and then compiles it to PDF.
# It assumes you have an installed LaTeX distribution on your system,
# or any package that provides the `latexmk` command.

import datetime
import getopt
import os
import random
import subprocess
import sys

# Constant definitions. They can be changed by using command line options.
YEAR = datetime.datetime.now().year
NEXERCICES = 2
AUTHOR = "sergiu.ivanov@univ-evry.fr"
FILENAME = "my_first_SYE_exercice.tex"
LANG = "FR"
L33TLVL = 0
TITLE_FR = "Mon premier TD de SYE"
TITLE_EN = "My first Operating Systems exam"

# ============= Exercices classes ===========================
# ============================================================
# They represent a template of an exercise and can be instanciated into
# a real problem.
# They all own a series of methods:
# .imagine() conceives a theoretical problem and stores its parameters in internal static members
# .question() which generates the LaTeX code to an understandable state
# .correction() which generates the LaTeX code to an understandable correction state


class ProcessStateExercice:
    """
    A kind of exercice where a series of states is proposed, and the student
    should tell if this series is realistic or obviously impossible.
    """

    def __init__(self):
        self.questions = []
        self.corrections = []
        self.transition_map = {"E": ["P"], "P": ["X", "S"], "X": [
            "T", "A", "P"], "S": ["P", "A"], "A": ["P", "S"], "T": []}
        self.codes_fr = {"E": "Extérieur", "P": "Prêt", "X": "Exécution",
                         "S": "Suspendu", "A": "Attente", "T": "Terminé"}
        self.codes_en = {"E": "External", "P": "Ready", "X": "Execution",
                         "S": "Suspended", "A": "Waiting", "T": "Terminated"}

    def imagine(self):
        """
        Imagines a series of states which should be near possible.
        """
        n_questions = random.randint(3, 5)
        for q in range(n_questions):
            seq_len = random.randint(5, 8)
            seq = ""
            is_feasible = True
            for state in range(seq_len):
                newstate = ""
                if random.random() < 0.1:
                    # Let's do a non-feasible sequence
                    is_feasible = False

                    if state:
                        # This is not the first state of the series, there is a previous one, seq[state-1]
                        possibles = ['E', 'P', 'X', 'S', 'T', 'A']
                        # remove the True solutions
                        for x in self.transition_map[seq[state-1]]:
                            possibles.remove(x)
                        possibles.remove(seq[state-1])  # remove itself
                        newstate = random.choice(possibles)
                    else:  # This is the first state of the series. Being impossible is, being not E
                        newstate = random.choice("PXSTA")

                else:
                    # Let's keep it feasible for now

                    if state:
                        if seq[state-1] == 'T':
                            # the previous was T, the only possibility is to terminate early, now
                            break
                        possibles = self.transition_map[seq[state-1]]

                        if 'T' in possibles and state == seq_len-1:
                            # This is the last state of the sequence and we want it to be possible
                            newstate = 'T'
                        newstate = random.choice(possibles)
                    else:
                        # The only right way to start is to start by E
                        newstate = 'E'

                seq += newstate

            self.questions.append(seq)
            self.corrections.append(is_feasible)
        print("Generated a series of process states: ", "\n\t",
              self.questions, '\n\t', self.corrections, '\n')

    def question(self, LANG):
        """
        Generates a LaTeX states of the imagined questions.
        """

        if "FR" in LANG:
            guidelines = "\\section{Suite d'états de processus}\n\n"
            guidelines += "Les processus dans un système d’exploitation ont très souvent un état. "
            guidelines += "Définissez l’état d’un processus et expliquez son utilité. "
            guidelines += "Rappelez le schéma des transitions entre états qu’un processus peut subir (son cycle de vie) et expliquez chaque transition.\n"
            guidelines += "Pour chaque suite d'états dans la liste suivante, indiquez si elle est possible ou non et argumentez votre réponse. \n\n"""
            state_map = self.codes_fr
        if "EN" in LANG:
            guidelines = "\\section{Process states series}\n\n"
            guidelines += "Processes in an operating system are almost often described by a state. "
            guidelines += "Define what is a process state and explain its uses. "
            guidelines += "Draw the possible relations of transition between the states (the proces life cycle) and explain each of the transitions.\n"
            guidelines += "For each series of states in the following list, indicate if it is likely to occur in real life or not, and argue. \n\n"""
            state_map = self.codes_en
        guidelines = to_l33t(guidelines, int(L33TLVL > 0))

        spacer = ' $\\rightarrow$ '
        for i in range(len(self.questions)):
            state_path = [state_map[state] for state in self.questions[i]]
            guidelines += f'{i+1}. {(spacer).join(state_path)}\n\n'

        return guidelines

    def correction(self, LANG):
        """
        Generates a LaTeX states of the correction of the imagined questions.
        """
        if "FR" == LANG:
            answer = "\\section{Suite d'états de processus}\n\n"
            answer += "Voici les réponses pour l'exercice Suite des états de processus.\n\n"
            for i, v in enumerate(self.corrections):
                if v:
                    answer += f"{i+1}. Cette suite d'états de processus était correcte.\n\n"
                else:
                    answer += f"{i+1}. Cette suite d'états de processus était fausse. "
                    answer += self.get_wrong_transitions(self.questions[i])
                    answer += "\n\n"

        if "EN" == LANG:
            answer = "\\section{Process states series}\n\n"
            answer += "Here are the answers for the Process states series exercice.\n\n"
            for i, v in enumerate(self.corrections):
                if v:
                    answer += f"{i+1}. This series of process states was correct.\n\n"
                else:
                    answer += f"{i+1}. This series of process states was wrong. "
                    answer += self.get_wrong_transitions(self.questions[i])
                    answer += "\n\n"

        return to_l33t(answer, int(L33TLVL > 0))

    def get_wrong_transitions(self, seq):
        """
        Identifies bad transitions in a sequence and output LaTeX code to explain why it is wrong.
        """
        answer = ""
        for i in range(len(seq)-1):
            if seq[i+1] not in self.transition_map[seq[i]]:
                if LANG == "FR":
                    answer += f"La transition {self.code_to_word(seq[i])} vers {self.code_to_word(seq[i+1])} est impossible. "
                if LANG == "EN":
                    answer += f"The transition {self.code_to_word(seq[i])} towards {self.code_to_word(seq[i+1])} is not possible. "

        return answer

    def code_to_word(self, code):
        if LANG == "FR":
            return self.codes_fr[code]

        if LANG == "EN":
            return self.codes_en[code]


class RunningTreeExercice:
    """
    An exercice to train the student to convert formulations of composed groups
    of tasks between the operator || formulation and the 'parbegin' pseudocode.
    """

    def __init__(self):
        self.questions = []
        self.corrections = []
        self.rev_questions = []
        self.rev_corrections = []

    def imagine(self):
        def expand(n, c, indent_level):
            s = ""
            r = ""

            brackets = (c > 1)
            if brackets:
                s += '('
            for m in range(indent_level):
                r += '\t'
            r += "parbegin\n"
            indent_level += 1

            # Iterate on the parallel groups
            for i in range(n):
                # tirer k étapes séquentielles à réaliser pour le ième groupe parallèle
                # randint(1,3) mais avec plus souvent des 1 que des 3
                k = 1+int(random.randint(1, 6)/3.0)

                if k > 1:
                    for m in range(indent_level):
                        r += '\t'
                    r += "begin\n"
                    indent_level += 1
                    s += '('

                for j in range(k):
                    if random.random() > 0.12:
                        s += f"T{c}"
                        for m in range(indent_level):
                            r += '\t'
                        r += f"T{c};\n"
                        c += 1
                    else:  # tirer à nouveau l choses parallèles pour le jième groupe séquentiel
                        l = random.randint(2, 3)
                        news, c, newr = expand(l, c, indent_level)
                        s += news
                        r += newr

                if k > 1:
                    indent_level -= 1
                    for m in range(indent_level):
                        r += '\t'
                    r += "end;\n"
                    s += ')'

                s += "||"

            indent_level -= 1
            for m in range(indent_level):
                r += '\t'
            r += "parend;\n"

            if brackets:
                return (s[:-2]+')', c, r)
            return (s[:-2], c, r)

        n_questions = random.randint(3, 5)
        tasks = []
        sols = []
        for _ in range(n_questions):
            seq_len = random.randint(1, 3)
            s, _, r = expand(seq_len, 1, 0)
            tasks.append(s)
            sols.append("begin\n"+r+"end;")
        self.questions = tasks
        self.corrections = sols
        print(to_l33t("Generating a series of composed tasks: ",
                      int(L33TLVL > 0)), '\n\t', self.questions, '\n')

        n_questions = random.randint(1, 2)
        tasks = []
        sols = []
        for _ in range(n_questions):
            seq_len = random.randint(1, 3)
            s, _, r = expand(seq_len, 1, 0)
            tasks.append(s)
            sols.append("begin\n"+r+"end;")
        self.rev_questions = sols
        self.rev_corrections = tasks
        print(to_l33t("Generating a second series of composed tasks to find: ", int(
            L33TLVL > 0)), '\n\t', self.questions, '\n')

    def question(self, LANG):
        """
        Generates a LaTeX states of the imagined questions.
        """

        if "FR" in LANG:
            guidelines = """
            \\section{Ecriture de programmes parallèles}

            La plupart des librairies de programmation parallèle fournissent des primitives réalisant la \\textit{composition parallèle} : la mise en parallèle de plusieurs tâches.
            Le paradigme de programmation impérative fournit à son tour la composition séquentielle : l'exécution de plusieurs tâches l'une à la suite de l'autre.\\

            La composition parallèle est souvent écrite en utilisant le symbole ||, alors que la composition séquentielle est notée en juxtaposant les tâches. Par exemple, $(T_1||T_2)T_3$ exprime la composition 
            parallèle des tâches $T_1$ et $T_2$, et ensuite la composition séquentielle du résultat avec la tâche $T_3$.\\

            Cependant, lorsqu'on souhaite décrire dans un pseudocode le contenu de tâches composées, il est plus pratique d'utiliser des constructions \\textbf{parbegin / parend} pour la composition parallèle et \\textbf{begin/end} pour la composition
            séquentielle. L'exemple précédent s'exprimerait avec ces constructions comme ceci:\\
            \\begin{verbatim}
            begin
                parbegin
                    T1;
                    T2;
                parend;
                T3;
            end;
            \\end{verbatim}

            Ecrivez les expressions suivantes avec les constructions \\textbf{parbegin / parend} et \\textbf{begin / end} :\\\\
            """

        if "EN" in LANG:
            guidelines = """
            \\section{Write parallel programs}

            Most of the parallel programming libraries provide templates implementing the \\textit{parallel composition} : the side-by-side execution of several tasks.
            The imperative programming paradigm also provides the sequential composition : execution of tasks successively, each after the previous one.\\

            The parallel composition is often written using the || symbol, while the sequential composition is written by putting tasks next to each other. As an example, $(T_1||T_2)T_3$ describes the parallel composition 
            of tasks $T_1$ et $T_2$, and then the sequential composition of the result with task $T_3$.\\

            However, when one wants to describe in pseudocode an ensemble of composed tasks, it is more convenient to use \\textbf{parbegin / parend} keywords for the parallel comparison, 
            and \\textbf{begin/end} for sequential composition. The previous example would be expressed using these constructions in the following way:\\\\
            \\begin{verbatim}
            begin
                parbegin
                    T1;
                    T2;
                parend;
                T3;
            end;
            \\end{verbatim}

            Write the following expressions using the \\textbf{parbegin / parend} and \\textbf{begin / end} formulations:\\\\
            """
        guidelines = to_l33t(guidelines, int(L33TLVL > 0))

        for i, v in enumerate(self.questions):
            guidelines += f"{i+1}. " + v + "\\\\\n"

        if LANG == "FR":
            if len(self.rev_questions) == 1:
                guidelines += to_l33t(
                    "\nA l'inverse, convertissez ce pseudo-code en formulation compacte à l'aide des opérateurs ||: \\\\", int(L33TLVL > 0))
            else:
                guidelines += to_l33t(
                    "\nA l'inverse, convertissez ces pseudo-codes en formulation compacte à l'aide des opérateurs ||: \\\\", int(L33TLVL > 0))

        if LANG == "EN":
            if len(self.rev_questions) == 1:
                guidelines += to_l33t(
                    "\nOn the opposite, convert this pseudocode into a compact formulation using the || operator: \\\\", int(L33TLVL > 0))
            else:
                guidelines += to_l33t(
                    "\nOn the opposite, convert these pseudocodes into compact formulations using the || operator: \\\\", int(L33TLVL > 0))

        for i, v in enumerate(self.rev_questions):
            guidelines += f"{i+len(self.questions)+1}" + r". \\" + '\n' + r"\begin{verbatim}" + \
                '\n' + v.replace('\t', "    ") + '\n' + \
                r"\end{verbatim}" + "\n~\\\\\n"

        return guidelines

    def correction(self, LANG):
        """
        Generates a LaTeX states of the correction of the imagined questions.
        """

        answer = ""
        if "FR" == LANG:
            answer += to_l33t(
                "\\section{Ecriture de programmes parallèles}\n\n", int(L33TLVL > 0))
            answer += to_l33t(
                "Voici les réponses pour l'exercice Ecriture de programmes parallèles.\n\n", int(L33TLVL > 0))

        if "EN" == LANG:
            answer += to_l33t("\\section{Write parallel programs}\n\n",
                              int(L33TLVL > 0))
            answer += to_l33t(
                "Here are the answers for exercice Write parallel programs.\n\n", int(L33TLVL > 0))

        for i, v in enumerate(self.corrections):
            answer += f"{i+1}" + r". \\" + '\n' + r"\begin{verbatim}" + \
                '\n' + v.replace('\t', "    ") + '\n' + \
                r"\end{verbatim}" + "\n\n"
        for i, v in enumerate(self.rev_corrections):
            answer += f"\\noindent {i+len(self.corrections)+1}. " + \
                v + "\\\\\n"

        return answer


leet_level_1 = {
    "a": "4", "b": "6", "l": "|", "o": "0", "e": "3", "t": "7", "s": "5", "i": "1"
}
leet_level_2 = {
    "a": "4", "b": "6", "l": "1", "o": "0", "e": "3", "t": "7",
    "c": "(", "d": "[)", "f": "|=", "h": "#", "i": "!", "j": ",|", "k": "]{", "m": "(\\\\/)", "n": "(\\\\)", "s": "5", "u": "(_)", "v": "\\\\/", "w": "'//", "x": "\\%", "y": "'/"
}
leet_level_3 = {
    "a": "/-\\\\", "b": "!3", "c": "(", "d": "|)", "e": "3", "f": "|=", "g": "(_+", "h": "]-[", "i": "!", "j": "_|", "k": "|<", "l": "|_", "m": "|\\\\/|", "n": "/\\\\/", "o": "()", "p": "|*",
    "q": "0_", "r": "|?", "s": "5", "t": "7", "u": "|_|", "v": "\\\\/", "w": "\\\\/\\\\/", "x": "><", "y": "'/", "z": "2"
}


def compile_latex(filename):
    """
    Runs latexmk through the system executable.
    """
    os.chdir("tmp")
    subprocess.run(["latexmk", "-pdf", "-bibtex",
                    "-shell-escape", filename], capture_output=True)
    subprocess.run(["latexmk", "-pdf", "-bibtex", "-shell-escape",
                    filename.replace(".tex", "_corr.tex")], capture_output=True)
    os.chdir("..")
    subprocess.run(["mv", "tmp/"+filename.replace(".tex", ".pdf"), "pdf"])
    subprocess.run(["mv", "tmp/"+filename.replace(".tex", "_corr.pdf"), "pdf"])


def generate_latex_header(filename, title):
    """
    Append the latex code that starts a file.
    """
    if LANG == "FR":
        m = "Systèmes d'exploitation (SYE)"
    elif LANG == "EN":
        m = "Operating Systems"
    correction = filename.replace(".tex", "_corr.tex")

    with open("tmp/"+filename, "a") as tex:
        tex.write("""
        \\documentclass[11pt]{article}
        \\usepackage[T1]{fontenc}
        \\usepackage{graphicx}
        \\usepackage{grffile}
        \\usepackage{longtable}
        \\usepackage{wrapfig}
        \\usepackage{rotating}
        \\usepackage[normalem]{ulem}
        \\usepackage{amsmath}
        \\usepackage{textcomp}
        \\usepackage{amssymb}
        \\usepackage{capt-of}
        \\usepackage{hyperref}
        \\usepackage{minted}
        \\usepackage{tabularx}
        \\usepackage[french]{babel}
        \\usepackage[text={17cm,24cm},centering]{geometry}
        \\usepackage{enumitem}
        \\usepackage{tikz}
        \\usetikzlibrary{positioning,arrows.meta}
        \\author{%s}
        \\date{sergiu.ivanov@univ-evry.fr\\\\%d-%d}
        \\title{%s}
        \\hypersetup{
          pdfauthor={%s},
          pdftitle={%s},
          pdfkeywords={},
          pdfsubject={},
          pdfcreator={OpenSYE TD Generator Pro Plus 11 SE Max}, 
          pdflang={French}}
        \\begin{document}

        \\maketitle
        """ % (m, YEAR, YEAR+1, title, AUTHOR, title))

    title = title + to_l33t(" (Correction)", int(L33TLVL > 0))
    with open("tmp/"+correction, "a") as corr:
        corr.write("""
        \\documentclass[11pt]{article}
        \\usepackage[T1]{fontenc}
        \\usepackage{graphicx}
        \\usepackage{grffile}
        \\usepackage{longtable}
        \\usepackage{wrapfig}
        \\usepackage{rotating}
        \\usepackage[normalem]{ulem}
        \\usepackage{amsmath}
        \\usepackage{textcomp}
        \\usepackage{amssymb}
        \\usepackage{capt-of}
        \\usepackage{hyperref}
        \\usepackage{minted}
        \\usepackage{tabularx}
        \\usepackage[french]{babel}
        \\usepackage[text={17cm,24cm},centering]{geometry}
        \\usepackage{enumitem}
        \\usepackage{tikz}
        \\usetikzlibrary{positioning,arrows.meta}
        \\author{%s}
        \\date{%d-%d}
        \\title{%s}
        \\hypersetup{
          pdfauthor={%s},
          pdftitle={%s},
          pdfkeywords={},
          pdfsubject={},
          pdfcreator={OpenSYE TD Generator Pro Plus 11 SE Max}, 
          pdflang={French}}
        \\begin{document}

        \\maketitle
        """ % (m, YEAR, YEAR+1, title, AUTHOR, title))


def generate_exercice(filename, exo):
    """
    Append the latex code that ends a file.
    """
    correction = filename.replace(".tex", "_corr.tex")

    with open("tmp/"+filename, "a") as tex:
        tex.write(exo.question(LANG))

    with open("tmp/"+correction, "a") as corr:
        corr.write(exo.correction(LANG))


def generate_latex_footer(filename):
    """
    Append the latex code that ends a file.
    """
    correction = filename.replace(".tex", "_corr.tex")

    with open("tmp/"+filename, "a") as tex:
        tex.write("""
        \\end{document}
        """)
    with open("tmp/"+correction, "a") as corr:
        corr.write("""
        \\end{document}
        """)


def to_l33t(string, level):
    if not level:
        return string
    string = string.lower()
    if level == 1:
        string = "".join(
            [leet_level_1[c] if c in leet_level_1.keys() else c for c in string])
    elif level == 2:
        string = "".join(
            [leet_level_2[c] if c in leet_level_2.keys() else c for c in string])
    else:
        string = "".join(
            [leet_level_3[c] if c in leet_level_3.keys() else c for c in string])
    if len(string) > 30:
        for word in ["section", "begin", "end", "textbf", "textit", "verbatim", "rightarrow"]:
            string = string.replace(to_l33t(word, level), word)
    return string


if __name__ == "__main__":
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "hl:n:", [
                                "year=", "help", "lang=", "l33t", "title="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h" or opt == "--help":
            print("This program generates Operating-System level exercises.")
            print()
            print("Created for the 2020 confined edition of the 'Nuit de l'Info',")
            print("and more specifically for the UEVE IT dept task.")
            print("Authors : L. Becquey & S. Besse.")
            print("Distributed under CC 4.0 Licence BY-SA.")
            print()
            print("Usage:\t./generator.py [ --year <yourYear> --title <SheetTitle> -l EN --l33t ]")
            print()
            print("-h, --help\t\tDisplays this help message")
            print(
                "-l, --lang [FR, EN] \tChanges the exercice's output language.")
            print("--l33t\t\t\tTranslates the exercices to l33t-5p34k, to facilitate\n\t\t\t understanding with the students. Using the option\n\t\t\t several times increases the l33t level.")
            print("--title <arg>\t\tTitle of the exam sheet.")
            print("--year <arg>\t\tPredicts the TD exercices that will be published\n\t\t\t in scholar year <arg/arg+1> ")
            sys.exit(0)
        if opt == "--year":
            YEAR = int(arg)
        if opt == "-n":
            NEXERCICES = int(arg)
        if opt == "-l" or opt == "--lang":
            if arg in ["FR", "EN"]:
                LANG = str(arg)
            else:
                print(
                    "People from that country do not deserve to study computer science.")
        if opt == "--l33t":
            L33TLVL += 1
        if opt == "--title":
            TITLE_FR = arg
            TITLE_EN = arg

    if L33TLVL == 0:
        print("OpenSYE Pro Plus Max 11 SE - Welcome")
        print(
            f"Generating {NEXERCICES} SYE exercices from year {YEAR}-{YEAR+1} exam sheets.")
        if L33TLVL:
            print(f"Translating them to level {L33TLVL} l33t-5p34k.")
    else:
        # FILENAME = to_l33t(FILENAME, L33TLVL)
        print(to_l33t("OpenSYE Pro Plus Max 11 SE - Welcome", L33TLVL))
        print(to_l33t(
            f"Generating {NEXERCICES} SYE exercices from year {YEAR}-{YEAR+1} exam sheets.", L33TLVL))
        if L33TLVL:
            print(
                to_l33t(f"Translating them to level {L33TLVL} l33t-5p34k.", L33TLVL))
    os.makedirs("tmp", exist_ok=True)
    os.makedirs("pdf", exist_ok=True)
    subprocess.run(["rm", '-f', "tmp/"+FILENAME])
    subprocess.run(["rm", '-f', "tmp/"+FILENAME.replace(".tex", "_corr.tex")])
    subprocess.run(["rm", '-f', "pdf/"+FILENAME.replace(".tex", ".pdf")])
    subprocess.run(["rm", '-f', "pdf/"+FILENAME.replace(".tex", "_corr.pdf")])

    if LANG == "FR":
        generate_latex_header(FILENAME, to_l33t(TITLE_FR, L33TLVL))
    elif LANG == "EN":
        generate_latex_header(FILENAME, to_l33t(TITLE_EN, L33TLVL))

    exercices = [ProcessStateExercice(), RunningTreeExercice()]
    random.shuffle(exercices)
    for i in range(NEXERCICES):
        exercices[i].imagine()
        generate_exercice(FILENAME, exercices[i])

    generate_latex_footer(FILENAME)
    compile_latex(FILENAME)
