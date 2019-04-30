"""
Wrapper Module using other packages to generate molecular descriptors
"""

import math
import numpy as np
import os
import pandas as pd

from abc import ABC, abstractmethod
from rdkit import Chem
from rdkit.Chem import AllChem
import rdkit.Chem.rdMolDescriptors as rdDesc
import rdkit.Chem.EState.EState_VSA as EState
from mordred import Calculator as mdCalc
import mordred.descriptors as mdDesc
import mordred.error as mdError

# from rdkit.Chem import ChemicalFeatures
# from rdkit import RDConfig

class Descriptors(ABC):
    """
    """
    def __init__(self, SMILES = None):
        """ Descriptor Constructor """
        if(SMILES is not None):
            self.set_molecule(SMILES)
        else:
            self.Molecule = None

    def set_molecule(self, SMILES):
        """ set molecule of the rdkitDecriptor"""
        self.Molecule = Chem.MolFromSmiles(SMILES)
        return

    @abstractmethod
    def compute_all_descriptors(self):
        pass


class rdkitDescriptors(Descriptors):
    """
    A wrapper class using rdkit to generate the different descpritors.

    Initilized with SIMLES of a molecule

    Attributes:
    Molecule       -- an object of rdkit.Chem.rdchem.Mol

    Methods:
    set_molecule

    compute_all_descriptors
    compute_properties
    compute_connectivity_and_shape_indexes
    compute_MOE_descriptors
    compute_MQN_descriptors
    compute_Morgan_fingerprint

    """

    def compute_all_descriptors(self):
        """ compute all descriptors avaiable from the rdkit package """
        desc_dict = {}
        desc_dict.update(self.compute_properties())
        desc_dict.update(self.compute_connectivity_and_shape_indexes())
        desc_dict.update(self.compute_MOE_descriptors())
        desc_dict.update(self.compute_MQN_descriptors())

        return desc_dict

    def compute_properties(self, feature_name = None):
        """
        compute the basic properties from the rdkit package

        return decriptors types: mixed integer and floats
        """

        assert type(self.Molecule) == Chem.rdchem.Mol

        if feature_name is not None:
            properties = rdDesc.Properties(feature_name)
        else:
            properties = rdDesc.Properties()

        props_dict = dict(zip(properties.GetPropertyNames(),
                              properties.ComputeProperties(self.Molecule)))

        return props_dict

    def compute_connectivity_and_shape_indexes(self):
        """
        compute the compute connectivity and shape indexes defined in
            Rev. Comput. Chem. 2:367-422 (1991)

        return decriptors types: floats
        """
        assert type(self.Molecule) == Chem.rdchem.Mol

        CSI_dict = {}

        CSI_dict['Chi0v'] = rdDesc.CalcChi0v(self.Molecule)
        CSI_dict['Chi1v'] = rdDesc.CalcChi1v(self.Molecule)
        CSI_dict['Chi2v'] = rdDesc.CalcChi2v(self.Molecule)
        CSI_dict['Chi3v'] = rdDesc.CalcChi3v(self.Molecule)
        CSI_dict['Chi4v'] = rdDesc.CalcChi4v(self.Molecule)
        CSI_dict['Chi0n'] = rdDesc.CalcChi0n(self.Molecule)
        CSI_dict['Chi1n'] = rdDesc.CalcChi1n(self.Molecule)
        CSI_dict['Chi2n'] = rdDesc.CalcChi2n(self.Molecule)
        CSI_dict['Chi3n'] = rdDesc.CalcChi3n(self.Molecule)
        CSI_dict['Chi4n'] = rdDesc.CalcChi4n(self.Molecule)
        CSI_dict['HallKierAlpha'] = rdDesc.CalcHallKierAlpha(self.Molecule)
        CSI_dict['Kappa1'] = rdDesc.CalcKappa1(self.Molecule)
        CSI_dict['Kappa2'] = rdDesc.CalcKappa2(self.Molecule)
        CSI_dict['Kappa3'] = rdDesc.CalcKappa3(self.Molecule)

        return CSI_dict

    def compute_MOE_descriptors(self):
        """
        compute the MOE-type descriptors defined in


        return decriptors types: floats
        """
        assert type(self.Molecule) == Chem.rdchem.Mol

        MOE_dict = {}

        SlogP_VSA_names = []
        for i in range(1,13):
            SlogP_VSA_names.append('SlogP_VSA' + str(i))

        MOE_dict.update(dict(zip(SlogP_VSA_names,
                                     rdDesc.SlogP_VSA_(self.Molecule))))

        SMR_VSA_names = []
        for i in range(1,11):
            SMR_VSA_names.append('SMR_VSA' + str(i))

        MOE_dict.update(dict(zip(SMR_VSA_names,
                                 rdDesc.SMR_VSA_(self.Molecule))))

        PEOE_VSA_names = []
        for i in range(1,15):
            PEOE_VSA_names.append('PEOE_VSA' + str(i))

        MOE_dict.update(dict(zip(PEOE_VSA_names,
                                 rdDesc.PEOE_VSA_(self.Molecule))))

        EState_VSA_names = []
        for i in range(1,12):
            EState_VSA_names.append('EState_VSA' + str(i))

        MOE_dict.update(dict(zip(EState_VSA_names,
                                 EState.EState_VSA_(self.Molecule))))

        VSA_EState_names = []
        for i in range(1,12):
            VSA_EState_names.append('VSA_EState' + str(i))

        MOE_dict.update(dict(zip(VSA_EState_names,
                                 EState.VSA_EState_(self.Molecule))))

        return MOE_dict

    def compute_MQN_descriptors(self):
        """
        compute the MQN-type descriptors defined in
            Nguyen et al. ChemMedChem 4:1803-5 (2009)

        return decriptors types: ints
        """
        assert type(self.Molecule) == Chem.rdchem.Mol

        MQN_names = []
        for i in range(1,43):
            MQN_names.append('MQN' + str(i))

        MQN_dict = dict(zip(MQN_names, rdDesc.MQNs_(self.Molecule)))

        return MQN_dict

    def compute_auto_2D_coorelation(self):
        """wrapper function for same function in rdkit"""
        return rdDesc.CalcAUTOCORR2D(self.Molecule)

    def compute_Morgan_fingerprint(self, radius=2, nBits=2048, use_features=False):
        """  """
        assert type(self.Molecule) == Chem.rdchem.Mol
        fp = AllChem.GetMorganFingerprintAsBitVect(self.Molecule, radius, nBits=nBits,
                                                   useFeatures=use_features)
        return list(fp.ToBinary())

class mordredDescriptors(Descriptors):
    """
    A wrapper class using mordred to generate the different descpritors.

    Initilized with SIMLES of a molecule

    Attributes:
    Molecule       -- an object of rdkit.Chem.rdchem.Mol

    Methods:
    set_molecule

    compute_all_descriptors

    """

    DESC_ENGINE = mdCalc(mdDesc, ignore_3D=True)

    def set_DESC_ENGINE(self):
        """To be implemented"""
        pass

    def compute_all_descriptors(self):
        """ """
        assert type(self.Molecule) == Chem.rdchem.Mol
        desc_list = dict(zip(list(self.DESC_ENGINE._name_dict.keys()),
                             self.DESC_ENGINE(self.Molecule)))

        desc_list ={k: self._convert_mdError_to_na(v)
                    for k, v in desc_list.items()}

        return desc_list

    def batch_compute_all_descriptors(self, SMILES_list):
        """  """
        Molecules = map(Chem.MolFromSmiles, SMILES_list)
        desc_df = self.DESC_ENGINE.pandas(Molecules)
        desc_df = desc_df.applymap(self._convert_mdError_to_na)
        return desc_df

    def _convert_mdError_to_na(self, x):
        """ """
        if type(x) == mdError.Missing:
            return np.nan
        else:
            return x
