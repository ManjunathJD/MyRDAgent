import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs, Descriptors

from rdagent.log.base import LogManager
from rdagent.log.storage import FileStorage
from rdagent.log.utils import check_log_file_path

log_manager = LogManager("rdagent_logger")
logger = log_manager.logger

class InvalidFilePathException(Exception):
    """Exception raised for invalid file paths."""
    pass

class LogFileHandler:
    """
    Handles the logging operations to files, including checking for
    valid paths and handling exceptions.
    """
    def __init__(self, log_file_path: str, mode: str = "a", encoding: str = "utf-8") -> None:
        """
        Initialize the LogFileHandler with a specific log file path.

        Args:
            log_file_path (str): The path to the log file.
            mode (str, optional): The mode in which the file should be opened. Defaults to "a".
            encoding (str, optional): The encoding of the file. Defaults to "utf-8".
        """
        self.log_file_path = log_file_path
        self.mode = mode
        self.encoding = encoding
        self.storage = FileStorage(self.log_file_path, mode=self.mode, encoding=self.encoding)

        if not check_log_file_path(self.log_file_path):
            raise InvalidFilePathException(f"Invalid log file path: {self.log_file_path}")

    def write_log(self, log_message: str) -> None:
        """
        Writes a log message to the log file.

        Args:
            log_message (str): The message to log.
        """
        try:
            self.storage.write(log_message)
        except IOError as e:
            logger.error(f"Failed to write log message due to IOError: {e}")
            raise

    def read_logs(self) -> List[str]:
        """
        Reads all log messages from the log file.

        Returns:
            List[str]: A list of all log messages in the file.
        """
        try:
            return self.storage.read_all_lines()
        except IOError as e:
            logger.error(f"Failed to read logs due to IOError: {e}")
            raise

    def clear_logs(self) -> None:
        """Clears all logs from the log file."""
        try:
            self.storage.clear()
        except IOError as e:
            logger.error(f"Failed to clear logs due to IOError: {e}")
            raise

class SmilesConverter:
    """
    Converts SMILES strings to RDKit Mol objects and computes
    fingerprints and descriptors.
    """
    def __init__(self, smiles_str: str) -> None:
        """
        Initialize the SmilesConverter with a SMILES string.

        Args:
            smiles_str (str): The SMILES string of the molecule.
        """
        self.smiles_str = smiles_str
        self.mol = self._get_mol_object()
        self.fingerprint = self._get_fingerprint()
        self.descriptors = self._get_descriptors()

    def _get_mol_object(self) -> Optional[Chem.Mol]:
        """
        Gets the RDKit Mol object from the SMILES string.

        Returns:
            Optional[Chem.Mol]: The RDKit Mol object or None if SMILES is invalid.
        """
        try:
            mol = Chem.MolFromSmiles(self.smiles_str)
            if mol is None:
                logger.error(f"Failed to create Mol object from SMILES: {self.smiles_str}")
            return mol
        except Exception as e:
            logger.error(f"Failed to create Mol object from SMILES due to an unexpected error: {e}")
            return None

    def _get_fingerprint(self) -> Optional[DataStructs.cDataStructs.ExplicitBitVect]:
        """
        Gets the Morgan fingerprint of the molecule.

        Returns:
            Optional[DataStructs.cDataStructs.ExplicitBitVect]: The Morgan fingerprint or None if molecule is invalid.
        """
        if self.mol is None:
            return None
        try:
            fingerprint = AllChem.GetMorganFingerprintAsBitVect(self.mol, 2, nBits=1024)
            return fingerprint
        except Exception as e:
            logger.error(f"Failed to get fingerprint for SMILES: {self.smiles_str} due to {e}")
            return None

    def _get_descriptors(self) -> Optional[Dict[str, float]]:
        """
        Gets the descriptors of the molecule.

        Returns:
            Optional[Dict[str, float]]: A dictionary of descriptors or None if molecule is invalid.
        """
        if self.mol is None:
            return None
        try:
            descriptors = {name: func(self.mol) for name, func in Descriptors.descList}
            return descriptors
        except Exception as e:
            logger.error(f"Failed to get descriptors for SMILES: {self.smiles_str} due to {e}")
            return None

class SmilesSimilarityChecker:
    """
    Checks the similarity between two SMILES strings based on their fingerprints.
    """
    def __init__(self, smiles1: str, smiles2: str) -> None:
        """
        Initialize the SmilesSimilarityChecker with two SMILES strings.

        Args:
            smiles1 (str): The first SMILES string.
            smiles2 (str): The second SMILES string.
        """
        self.smiles1 = smiles1
        self.smiles2 = smiles2
        self.converter1 = SmilesConverter(self.smiles1)
        self.converter2 = SmilesConverter(self.smiles2)

    def calculate_similarity(self) -> Optional[float]:
        """
        Calculates the Tanimoto similarity between the two molecules.

        Returns:
            Optional[float]: The Tanimoto similarity score or None if fingerprints are invalid.
        """
        if self.converter1.fingerprint is None or self.converter2.fingerprint is None:
            return None
        try:
            similarity = DataStructs.TanimotoSimilarity(self.converter1.fingerprint, self.converter2.fingerprint)
            return similarity
        except Exception as e:
            logger.error(f"Failed to calculate similarity between {self.smiles1} and {self.smiles2} due to {e}")
            return None

def convert_smiles_to_fingerprint_and_descriptors(smiles_str: str) -> Tuple[Optional[DataStructs.cDataStructs.ExplicitBitVect], Optional[Dict[str, float]]]:
    """
    Converts a SMILES string to a fingerprint and descriptors.

    Args:
        smiles_str (str): The SMILES string of the molecule.

    Returns:
        Tuple[Optional[DataStructs.cDataStructs.ExplicitBitVect], Optional[Dict[str, float]]]:
        A tuple containing the fingerprint and descriptors,
        or (None, None) if the SMILES string is invalid.
    """
    try:
        converter = SmilesConverter(smiles_str)
        return converter.fingerprint, converter.descriptors
    except Exception as e:
        logger.error(f"Error during converting smiles {smiles_str}: {e}")
        return None, None