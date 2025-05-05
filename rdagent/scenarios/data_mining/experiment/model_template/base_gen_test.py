import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

from rdkit import Chem
from rdkit.Chem import AllChem

from rdagent import config as rd_config
from rdagent.utils import agent as agent_utils
from rdagent.utils.agent import ret

logger = logging.getLogger(__name__)

_mol_cache = {}


def _parse_mol_list_str(mol_list_str: str) -> List[Chem.Mol]:
    """Parse a list of molecules from a string."""
    mol_list: List[Chem.Mol] = []
    for smiles in mol_list_str.strip().split(","):
        smiles = smiles.strip()
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smiles}")
        mol_list.append(mol)
    return mol_list


def _parse_mol_str(smiles_str: str) -> Chem.Mol:
    """Parse a single molecule from a SMILES string."""
    mol = Chem.MolFromSmiles(smiles_str)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles_str}")
    return mol


def _get_mol_from_smiles(smiles: str) -> Chem.Mol:
    """Get a molecule from a SMILES string, using cache."""
    if smiles not in _mol_cache:
        _mol_cache[smiles] = Chem.MolFromSmiles(smiles)
    return _mol_cache[smiles]


def _get_mol_from_file(file_path: str) -> List[Chem.Mol]:
    """Get a molecule from a file path."""
    mol_list = []
    with open(file_path, "r") as file:
        for line in file:
            smiles = line.strip()
            mol = _get_mol_from_smiles(smiles)
            if mol is not None:
                mol_list.append(mol)
    return mol_list


def _get_mols_from_input(mol_input: Union[str, List[str]]) -> List[Chem.Mol]:
    """Get a list of molecules from various input types."""
    mol_list: List[Chem.Mol] = []
    if isinstance(mol_input, list):
        for item in mol_input:
            mol = _get_mol_from_smiles(item)
            if mol is not None:
                mol_list.append(mol)
    elif isinstance(mol_input, str):
        if os.path.isfile(mol_input):
            mol_list.extend(_get_mol_from_file(mol_input))
        else:
            mol = _get_mol_from_smiles(mol_input)
            if mol is not None:
                mol_list.append(mol)
    return mol_list


def generate_mols(
    mol_input: Union[str, List[str]],
    mol_num: int,
    **kwargs,
) -> ret.Ret:
    """Generate molecules based on given input."""
    logger.info(f"input: {mol_input}")
    mols = _get_mols_from_input(mol_input)
    if not mols:
        return ret.Ret(
            False,
            "invalid mol",
            mol_list_new=[],
        )
    gen_smiles = [Chem.MolToSmiles(mol) for mol in mols]
    if len(gen_smiles) >= mol_num:
        logger.info(f"Generated {len(gen_smiles)} molecules.")
        return ret.Ret(
            True,
            "",
            mol_list_new=gen_smiles[:mol_num],
        )
    logger.info(f"Input list size {len(gen_smiles)}  less than {mol_num}.")
    logger.info(f"Start generate {mol_num - len(gen_smiles)} molecules.")

    gen_smiles = agent_utils.gen_smiles_from_list(gen_smiles, mol_num - len(gen_smiles))
    if gen_smiles is None:
        return ret.Ret(
            False,
            "invalid mol",
            mol_list_new=[],
        )

    gen_smiles = gen_smiles + [Chem.MolToSmiles(mol) for mol in mols]
    return ret.Ret(
        True,
        "",
        mol_list_new=gen_smiles,
    )


def gen_reaction(
    mol_input: str,
    reaction_num: int,
    reaction_smarts: List[str] = [],
    **kwargs,
) -> ret.Ret:
    """Generate chemical reactions based on given input."""
    logger.info(f"input: {mol_input}")
    mols = _get_mols_from_input(mol_input)
    if not mols:
        return ret.Ret(False, "invalid mol")
    if not reaction_smarts:
        reaction_smarts = rd_config.reaction_smarts
    reaction_list = []
    for _ in range(reaction_num):
        for smiles in reaction_smarts:
            rxn = AllChem.ReactionFromSmarts(smiles)
            if rxn is None:
                continue
            products = rxn.RunReactants((mols[0],))
            for product in products:
                for mol in product:
                    reaction_list.append(Chem.MolToSmiles(mol))
    if not reaction_list:
        return ret.Ret(
            False,
            "invalid reaction",
            reaction_list=[],
        )
    return ret.Ret(
        True,
        "",
        reaction_list=reaction_list,
    )


def gen_reaction_list(
    mol_input_list: List[str],
    reaction_num: int,
    reaction_smarts: List[str] = [],
    **kwargs,
) -> ret.Ret:
    """Generate chemical reactions for a list of molecules."""
    logger.info(f"input: {mol_input_list}")
    mols = []
    for mol_input in mol_input_list:
        mols.extend(_get_mols_from_input(mol_input))
    if not mols:
        return ret.Ret(False, "invalid mol")
    if not reaction_smarts:
        reaction_smarts = rd_config.reaction_smarts
    reaction_list = []
    for _ in range(reaction_num):
        for smiles in reaction_smarts:
            rxn = AllChem.ReactionFromSmarts(smiles)
            if rxn is None:
                continue
            products = rxn.RunReactants((mols[0],))
            for product in products:
                for mol in product:
                    reaction_list.append(Chem.MolToSmiles(mol))

    if not reaction_list:
        return ret.Ret(
            False,
            "invalid reaction",
            reaction_list=[],
        )
    return ret.Ret(
        True,
        "",
        reaction_list=reaction_list,
    )


def gen_reaction_from_str(
    mol_input: str,
    reaction_num: int,
    reaction_smarts: str,
    **kwargs,
) -> ret.Ret:
    """Generate chemical reactions from a string representation of reaction SMART."""
    logger.info(f"input: {mol_input}")
    logger.info(f"reaction_smarts: {reaction_smarts}")

    mols = _get_mols_from_input(mol_input)
    if not mols:
        return ret.Ret(False, "invalid mol")
    reaction_list = []

    rxn = AllChem.ReactionFromSmarts(reaction_smarts)
    if rxn is None:
        return ret.Ret(
            False,
            "invalid reaction",
            reaction_list=[],
        )
    for _ in range(reaction_num):
        products = rxn.RunReactants((mols[0],))
        for product in products:
            for mol in product:
                reaction_list.append(Chem.MolToSmiles(mol))

    if not reaction_list:
        return ret.Ret(
            False,
            "invalid reaction",
            reaction_list=[],
        )
    return ret.Ret(
        True,
        "",
        reaction_list=reaction_list,
    )