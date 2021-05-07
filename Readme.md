# Symbol-Exporter

Symbol-Exporter was created with three major use cases in mind:
1. Enable better API/ABI version constraints (pins) and requirement discovery by inspecting compatibility as the symbol level.
2. Enable the creation of stripped down distributions via "tree-shaking" a process in which symbols are selectively removed to produce the minimal distribution.
3. Enable machine assisted migration of source code across API/ABI breaks

Each of these use cases requires a database relating exposed symbols and required symbols to individual packages.
A useful geometric analogy is that each package exposes symbols on it's surface area.
Each element of surface area can bound a volume made up of symbols that the surface symbol requires to operate.


There are three major parts to the system: the symbols, the symbol table, and the audit.
1. The symbols comprise a database indexed by the name of the artifact (package with version and build numbers). The values of the symbols database are the surface and volume symbols.
2. The symbol table is the reverse indexed form of the symbols. In this case the index is the name of the symbol and the values are the listing of artifacts which provide that symbol.
3. The audit identifies any gaps in the symbol table by checking that every symbol in the volume for a particular artifact are provided in the symbol table. Where there are gaps we know that either the source code is incorrect or that the inspection has errors. Additionallly the audit produces a version range for each discovered dependency, which can be checked against existing dependency metadata to evaluate the veracity of the Symbol-Exporter metadata.


