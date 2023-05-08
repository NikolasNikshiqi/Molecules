import os
import sqlite3
import MolDisplay

class Database:
    def __init__(self,reset = False):
        if reset == True and os.path.exists( "molecules.db" ):
            os.remove( "molecules.db" )

        if os.path.exists( "molecules.db" ):
            self.conn = sqlite3.connect( "molecules.db" )
        else:
            self.conn = sqlite3.connect( "molecules.db" )
            self.create_tables();
            self['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 );
            self['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 );
            self['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 );
            self['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 );

    def create_tables( self ):
        
        # Elements table
        self.conn.execute("""
        CREATE TABLE Elements (
        ELEMENT_NO INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        ELEMENT_CODE VARCHAR(3) NOT NULL,
        ELEMENT_NAME VARCHAR(32) NOT NULL,
        COLOUR1 CHAR(6) NOT NULL,
        COLOUR2 CHAR(6) NOT NULL,
        COLOUR3 CHAR(6) NOT NULL,
        RADIUS DECIMAL(3) NOT NULL
        )
        """)

        #Atoms table
        self.conn.execute("""
        CREATE TABLE Atoms (
        ATOM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        ELEMENT_CODE VARCHAR(3) NOT NULL,
        X DECIMAL(7,4) NOT NULL,
        Y DECIMAL(7,4) NOT NULL,
        Z DECIMAL(7,4) NOT NULL,
        FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements(ELEMENT_CODE)
        )
        """)

        # Bonds table
        self.conn.execute("""
        CREATE TABLE Bonds (
        BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        A1 INTEGER NOT NULL,
        A2 INTEGER NOT NULL,
        EPAIRS INTEGER NOT NULL
        )
        """)

        # Molecules table
        self.conn.execute("""
        CREATE TABLE Molecules (
        MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        NAME TEXT UNIQUE NOT NULL
        )
        """)

        #MoleculeAtom table
        self.conn.execute("""
        CREATE TABLE MoleculeAtom (
        MOLECULE_ID INTEGER NOT NULL,
        ATOM_ID INTEGER NOT NULL,
        PRIMARY KEY (MOLECULE_ID, ATOM_ID),
        FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
        FOREIGN KEY (ATOM_ID) REFERENCES Atoms(ATOM_ID)
        )
        """)

        # MoleculeBond table
        self.conn.execute("""
        CREATE TABLE MoleculeBond (
        MOLECULE_ID INTEGER NOT NULL,
        BOND_ID INTEGER NOT NULL,
        PRIMARY KEY (MOLECULE_ID, BOND_ID),
        FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
        FOREIGN KEY (BOND_ID) REFERENCES Bonds(BOND_ID)
        )
        """)
        self.conn.commit()
    
    def __setitem__(self, table, values):
        placeholders = ','.join('?' * len(values))
        query = f"INSERT INTO {table} VALUES ({placeholders})"
        self.cursor = self.conn.cursor()  # Create a cursor instance
        self.cursor.execute(query, values)
        self.conn.commit()

    def add_atom(self, molname, atom):
        self["Atoms"] = (None, atom.atom.element, atom.atom.x, atom.atom.y, atom.z)
        atom_id = self.cursor.lastrowid
        molecule_id = self.conn.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME=?", (molname,)).fetchone()[0]
        self["MoleculeAtom"] = (molecule_id, atom_id)

    def add_bond(self, molname, bond):
        #print("Testing " + str(bond.bond.a1))
        #print("Testing " + str(bond.bond.a2) )
        self["Bonds"] = (None, bond.bond.a1, bond.bond.a2, bond.bond.epairs)
        bond_id = self.cursor.lastrowid
        molecule_id = self.conn.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME=?", (molname,)).fetchone()[0]
        self["MoleculeBond"] = (molecule_id, bond_id)
    
    def add_molecule(self, name, file):
        mol = MolDisplay.Molecule()
        mol.parse(file)

        self["Molecules"] = (None, name)

        for i in range(mol.atom_no):
            atom_obj = mol.get_atom(i)
            self.add_atom(name, MolDisplay.Atom(atom_obj))

        for i in range(mol.bond_no):
            bond_obj = mol.get_bond(i)
            self.add_bond(name, MolDisplay.Bond(bond_obj))

    def load_mol(self, name):
        mol = MolDisplay.Molecule()

        atom_query = """
            SELECT * FROM Atoms
            JOIN MoleculeAtom ON Atoms.ATOM_ID = MoleculeAtom.ATOM_ID
            JOIN Molecules ON MoleculeAtom.MOLECULE_ID = Molecules.MOLECULE_ID
            WHERE Molecules.NAME = ?
            ORDER BY Atoms.ATOM_ID
        """
        # Load atoms
        data1 = self.conn.execute(atom_query , (name,))
        for atom in data1.fetchall():
            #print("Testing " + atom[1])
            mol.append_atom(atom[1], atom[2], atom[3], atom[4])

        bond_query = """
            SELECT * FROM Bonds
            JOIN MoleculeBond ON Bonds.BOND_ID = MoleculeBond.BOND_ID
            JOIN Molecules ON MoleculeBond.MOLECULE_ID = Molecules.MOLECULE_ID
            WHERE Molecules.NAME = ?
            ORDER BY Bonds.BOND_ID
        """
        # Load bonds
        data2 = self.conn.execute(bond_query, (name,))
        for bond in data2.fetchall():
            #since append_bond takes away 1 from a1 and a2 I added 1 here since we are getting data from db and it is listed from 0 
            mol.append_bond(int(bond[1]), int(bond[2]), bond[3])

        return mol

    def radius(self):
        data = self.conn.execute("SELECT ELEMENT_CODE, RADIUS FROM Elements")
        return dict(data.fetchall())

    def element_name(self):
        data = self.conn.execute("SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements")
        return dict(data.fetchall())

    def radial_gradients(self):

        
        data = self.conn.execute("SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements")
        gradients = [f'<radialGradient id="{row[0]}" cx="-50%" cy="-50%" r="220%" fx="20%" fy="20%">'
             f'<stop offset="0%" stop-color="#{row[1]}"/>'
             f'<stop offset="50%" stop-color="#{row[2]}"/>'
             f'<stop offset="100%" stop-color="#{row[3]}"/>'
             f'</radialGradient>' for row in data.fetchall()]

        return ''.join(gradients)
    
    def get_all_molecules(self):
        query = """
        SELECT Molecules.MOLECULE_ID, Molecules.NAME, COUNT(DISTINCT MoleculeAtom.ATOM_ID) AS atom_count, COUNT(DISTINCT MoleculeBond.BOND_ID) AS bond_count
        FROM Molecules
        LEFT JOIN MoleculeAtom ON Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
        LEFT JOIN MoleculeBond ON Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
        GROUP BY Molecules.MOLECULE_ID, Molecules.NAME
        """
        data = self.conn.execute(query)
        molecules = data.fetchall()
        return molecules
