# MolDisplay.py
import molecule as ml

radius = {}

element_name = {}

header = """<svg version="1.1" width="1000" height="1000"
xmlns="http://www.w3.org/2000/svg">"""

footer = """</svg>"""

offsetx = 500
offsety = 500

#Atom class
class Atom:
    def __init__(self, c_atom):
        self.atom = c_atom
        self.z = c_atom.z

    def __str__(self):
        return "Atom"

    def svg(self):
        x = self.atom.x * 100.0 + offsetx
        y = self.atom.y * 100.0 + offsety
        r = radius[self.atom.element]
        fill = element_name[self.atom.element]

        return f' <circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="url(#{fill})"/>\n'

#Bond class
class Bond:
    def __init__(self, c_bond):
        self.bond = c_bond
        self.z = c_bond.z

    def __str__(self):
        return "Bond"

    def svg(self):
        x1 = self.bond.x1 * 100.0 + offsetx
        y1 = self.bond.y1 * 100.0 + offsety
        x2 = self.bond.x2 * 100.0 + offsetx
        y2 = self.bond.y2 * 100.0 + offsety
        dx, dy = self.bond.dx, self.bond.dy


        px1 = x1 - dy * 10
        py1 = y1 + dx * 10
        px2 = x1 + dy * 10
        py2 = y1 - dx * 10
        px3 = x2 + dy * 10
        py3 = y2 - dx * 10
        px4 = x2 - dy * 10
        py4 = y2 + dx * 10

        svg_str = '<polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (px1, py1, px2, py2, px3, py3, px4, py4)
        return svg_str

# Molecule class
class Molecule(ml.molecule):

    def __str__(self):
        return "Molecule"

    def svg(self):
        atom_objects = []
        bond_objects = []
        for i in range(self.atom_no):
            atom = self.get_atom(i)
            atom_objects.append(Atom(atom))

        for i in range(self.bond_no):
            bond = self.get_bond(i)
            bond_objects.append(Bond(bond))

        svg_elements = []
        while atom_objects or bond_objects:
            if not atom_objects:
                b1 = bond_objects.pop(0)
                svg_elements.append(b1.svg())
            elif not bond_objects:
                a1 = atom_objects.pop(0)
                svg_elements.append(a1.svg())
            else:
                a1 = atom_objects[0]
                b1 = bond_objects[0]
                if a1.z < b1.z:
                    svg_elements.append(a1.svg())
                    atom_objects.pop(0)
                else:  # b1.z <= a1.z
                    svg_elements.append(b1.svg())
                    bond_objects.pop(0)

        return header + ''.join(svg_elements) + footer


    def parse(self, f):
        
        lines = f.readlines()

        num_atoms = int(lines[3][:3].strip())
        num_bonds = int(lines[3][3:6].strip())

        for i in range(4, 4 + num_atoms):
            atom_info = lines[i].strip().split()
            self.append_atom(atom_info[3],float(atom_info[0]),float(atom_info[1]),float(atom_info[2]))

        for i in range(4 + num_atoms, 4 + num_atoms + num_bonds):
            bond_info = lines[i].strip().split()
            a1, a2, epairs = map(int, bond_info[:3])
            self.append_bond(int(a1 - 1),int(a2 - 1),int(epairs))


