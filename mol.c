#include "mol.h"

void atomset(atom *atom, char element[3], double *x, double *y, double *z)
{
    strcpy(atom->element, element);
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}

void atomget(atom *atom, char element[3], double *x, double *y, double *z)
{
    strcpy(element, atom->element);
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}

void compute_coords(bond *bond) {
    atom *a1 = &bond->atoms[bond->a1];
    atom *a2 = &bond->atoms[bond->a2];

    bond->x1 = a1->x;
    bond->y1 = a1->y;
    bond->x2 = a2->x;
    bond->y2 = a2->y;

    bond->z = (a1->z + a2->z) / 2.0;

    double dx = bond->x2 - bond->x1;
    double dy = bond->y2 - bond->y1;
    bond->len = sqrt(dx * dx + dy * dy);

    bond->dx = dx / bond->len;
    bond->dy = dy / bond->len;
}

void bondset(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->atoms = *atoms;
    bond->epairs = *epairs;

    compute_coords(bond);
}


void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
    *a1 = bond->a1;
    *a2 = bond->a2;
    *atoms = bond->atoms;
    *epairs = bond->epairs;
}

molecule *molmalloc(unsigned short atom_max, unsigned short bond_max)
{
    
    molecule *molec = malloc(sizeof(molecule));
    if (molec == NULL)
    {
        return NULL;
    }
    //set atom_max and atom_no
    molec->atom_max = atom_max;
    molec->atom_no = 0;
    molec->atoms = malloc(atom_max * sizeof(atom));

    //Allocate memory for the pointers
    if (molec->atoms == NULL)//Error during allocation
    {
        return NULL;
    }
    molec->atom_ptrs = malloc(atom_max * sizeof(atom *));
    if (molec->atom_ptrs == NULL)//Error during allocation
    {
        return NULL;
    }

    for (int i = 0; i < atom_max; i++)
    {
        molec->atom_ptrs[i] = &molec->atoms[i];
    }
    //set bond_max and bond_no
    molec->bond_max = bond_max;
    molec->bond_no = 0;

    molec->bonds = malloc(bond_max * sizeof(bond));
    if (molec->bonds == NULL)//Error during allocation
    {
        return NULL;
    }
    molec->bond_ptrs = malloc(bond_max * sizeof(bond *));
    if (molec->bond_ptrs == NULL)//Error during allocation
    {
        return NULL;
    }
    for (int i = 0; i < bond_max; i++)
    {
        molec->bond_ptrs[i] = &molec->bonds[i];
    }
    return molec;
}

void molappend_atom(molecule *molecule, atom *atom)
{
    
    if (molecule->atom_no == molecule->atom_max)
    {
        
        if (molecule->atom_max == 0)
        {
            molecule->atom_max = 1;
        }
        else
        {
            molecule->atom_max *= 2;
        }

        // increase the capacity
        molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * molecule->atom_max);

        // make atom_ptrs point to the atoms in the new atoms array
        for (int i = 0; i < molecule->atom_no; i++)
        {
            molecule->atom_ptrs[i] = &molecule->atoms[i];
        }
    }
    

    // copy the atom to the first empty atom in molecule
    molecule->atoms[molecule->atom_no] = *atom;

    // set the first empty pointer in atom_ptrs to the same atom as in the atoms array
    molecule->atom_ptrs[molecule->atom_no] = &molecule->atoms[molecule->atom_no];

    // increment
    molecule->atom_no++;
}

void molappend_bond(molecule *molecule, bond *bond)
{
    
    if (molecule->bond_no == molecule->bond_max)
    {
        
        if (molecule->bond_max == 0)
        {
            molecule->bond_max = 1;
        }
        else
        {
            molecule->bond_max *= 2;
        }
        // increase the capacity
        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, molecule->bond_max * sizeof(struct bond*));

        // make bond_ptrs point to the bonds in the new bonds array
        for (int i = 0; i < molecule->bond_no; i++)
        {
            molecule->bond_ptrs[i] = &molecule->bonds[i];
        }
    }
    // copy the bond to the first empty bond in molecule
    molecule->bonds[molecule->bond_no] = *bond;

    // set the first empty pointer in bond_ptrs to the same bond as in the bonds array
    molecule->bond_ptrs[molecule->bond_no] = &molecule->bonds[molecule->bond_no];

    // increment
    molecule->bond_no++;
}

molecule *molcopy(molecule *src)
{
    molecule *mol = molmalloc(src->atom_max, src->bond_max);
    if (mol == NULL) {
        return NULL;
    }
    
    // copy atoms into the molecule
    for (int i = 0; i < src->atom_no; i++)
    {
        molappend_atom(mol, &src->atoms[i]);
    }
    // copy bonds into the molecule
    for (int i = 0; i < src->bond_no; i++)
    {
        molappend_bond(mol, &src->bonds[i]);
    }
    
    return mol;
}

void molfree(molecule *mol)
{
    if (mol != NULL)
    {
        free(mol->atoms);
        free(mol->atom_ptrs);
        free(mol->bonds);
        free(mol->bond_ptrs);
        free(mol);
    }
}

int compareAtomsByZ(const void *a, const void *b)
{
    const atom **one = (const atom **)a;
    const atom **two = (const atom **)b;
    if ((*one)->z > (*two)->z)
    {
        return 1;
    }
    else if ((*one)->z < (*two)->z)
    {
        return -1;
    }
    return 0;
}

int bond_comp(const void *a, const void *b)
{
    const bond *bond1 = (const bond*) a;
    const bond *bond2 = (const bond*) b;

    if (bond1->z < bond2->z) {
        return -1;
    } else if (bond1->z > bond2->z) {
        return 1;
    } else {
        return 0;
    }
}
void molsort(molecule *molecule)
{
    // sort atoms by increasing z value
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom *), compareAtomsByZ);
    // sort bonds by increasing z value 
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond *), bond_comp);
}

void xrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double rad = deg * (M_PI / 180);  // convert degrees to radians
    double cosVal = cos(rad);
    double sinVal = sin(rad);
    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cosVal;
    xform_matrix[1][2] = -sinVal;
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sinVal;
    xform_matrix[2][2] = cosVal;
}

void yrotation( xform_matrix xform_matrix, unsigned short deg ){
    double rad = deg * M_PI / 180;
    double cosVal = cos(rad);
    double sinVal = sin(rad);
    xform_matrix[0][0] = cosVal;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sinVal;
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = -sinVal;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cosVal;
}

void zrotation( xform_matrix xform_matrix, unsigned short deg ){
    float rad = deg * M_PI / 180.0;
    float cosVal = cos(rad);
    float sinVal = sin(rad);
    xform_matrix[0][0] = cosVal;
    xform_matrix[0][1] = -sinVal;
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = sinVal;
    xform_matrix[1][1] = cosVal;
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

void mol_xform(molecule *molecule, xform_matrix matrix) {
    for (int i = 0; i < molecule->atom_no; i++) {
        double x = molecule->atoms[i].x;
        double y = molecule->atoms[i].y;
        double z = molecule->atoms[i].z;
        molecule->atoms[i].x = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z;
        molecule->atoms[i].y = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z;
        molecule->atoms[i].z = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z;
    }

    //New modification
    for (int i = 0; i < molecule->bond_no; i++) {
        bond *b = &molecule->bonds[i];
        compute_coords(b);
    }
}

