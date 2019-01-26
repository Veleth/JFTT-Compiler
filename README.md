# Kompilator na kurs Języki Formalne i Techniki Translacji
## Autor: Gabriel Tański, nr indeksu 236346

### Wymagane oprogramowanie
* Interpreter Python 3.6 lub nowszy (testowane na Python 3.6.7)
* Biblioteka SLY (SLY Lex-Yacc) (github.com/dabeaz/sly) - biblioteka ta została dołączona do plików kompilatora, znajduje się w katalogu sly-master. Można ją zainstalować używając managera pakietów pip
* (Opcjonalnie) Manager pakietów pip

### Opis plików
* compiler.py - jest to główny plik projektu, odpowiada za I/O oraz odczytanie pliku wejściowego i rozpoczęcie odpowiednich kroków
* module/lexer.py - plik, który odpowiada za tokenizację kodu wejściowego; znajdowane są także błędy leksykalne
* module/parser.py - plik, w którym tokeny są dopasowywane do gramatyki i tworzone jest drzewo parsera; znajdowane są także błędy syntaktyczne
* module/machine.py - plik, w którym zawiera się klasa maszyny rejestrowej, drzewo parsera przekładane jest na kod maszynowy i wykrywane są błedy semantyczne
* module/__init__.py - pusty plik, którego obecność jest niezbędna do poprawnego połączenia powyższych

### Instalacja

#### Python3
Przykładowa instalacja Interpretera Pythona:
```
sudo apt-get update
sudo apt-get install python3.6
```

#### SLY (pip)
Instalacja pakietu SLY może odbyć się poprzez wykorzystanie managera pakietów pip.

```
sudo apt install python3-pip
pip3 install sly
```

#### SLY (alternatywnie)
ALternatywnie, pakiet sly może zostać zainstalowany z katalogu sly-master. Należy wówczas przejść do tego katalogu i wykonać polecenie
```
python3 setup.py install
```
Podczas wykonywania powyższego polecenia, może okazać się potrzebne wykonanie
```
apt-get install python3-distutils
```
w celu umożliwienia instalacji biblioteki

### Obsługa
```
python3 compiler.py <fileIN> <fileOUT>
```
Jeśli podana zostanie nieprawidłowa ilość argumentów, program przypomni o prawidłowym jego użytkowaniu.
W powyższym przypadku fileIN to plik wejściowy z kodem programu w języku, fileOUT to plik docelowy, w którym znajdzie się skompilowany program.
