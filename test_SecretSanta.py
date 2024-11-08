#!/usr/bin/env python3
"""
Test function for SecretSanta.py
"""
import pickle
import unittest

target = __import__("SecretSanta")
getFamilyData = target.getFamilyData
getSaveFileNames = target.getSaveFileNames


class TestScript(unittest.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        # Get the secret santa lists created from previous script executions
        self.filename, self.previousFilename = getSaveFileNames()
        super().__init__(methodName=methodName)

    def test_all_names_in_list(self):
        """
        Test that all names are present in saved file, 
        both as secret santa and as receivers
        """
        # Load the secretSanta variable from the provided filename
        with open(self.filename, 'rb') as f:
            secretSanta = pickle.load(f)

        # Get family data
        families = getFamilyData()[0]

        # Make a list of all people included in the secret santa lottery
        allPeople = [person for pair in families for person in pair]

        # Get all secret santas and receivers from the secretSanta list
        secretSantas = [pair[0] for pair in secretSanta]
        receivers = [pair[1] for pair in secretSanta]

        # Number of secret santa and number of receivers should be the same length
        # as people included in the lottery
        self.assertEqual(len(allPeople), len(secretSantas))
        self.assertEqual(len(allPeople), len(receivers))

        # To also make sure that all names in secret santa and receivers are
        # identical to the names in families, type-cast to set and compare
        # to the total numbers of people in the lottery
        self.assertEqual(len(allPeople), len(set(allPeople + secretSantas)))
        self.assertEqual(len(allPeople), len(set(allPeople + receivers)))

    def test_no_duplicates(self):
        """
        Test that all there are no duplicated names in either the list
        of secret santa, or the list of receivers.
        """
        # Load the secretSanta variable from the provided filename
        with open(self.filename, 'rb') as f:
            secretSanta = pickle.load(f)

        # Get family data
        families = getFamilyData()[0]

        # Make a list of all people included in the secret santa lottery
        allPeople = [person for pair in families for person in pair]

        # Get all secret santas and receivers from the secretSanta list
        secretSantas = [pair[0] for pair in secretSanta]
        receivers = [pair[1] for pair in secretSanta]

        # There shall be duplicates in secret santa or receivers.
        # By typecasting the list to a set, all duplicates will be removed as
        # sets do not allow duplicattes.
        self.assertEqual(len(allPeople), len(set(secretSantas)))
        self.assertEqual(len(allPeople), len(set(receivers)))

    def test_secretSanta_and_receiver_different(self):
        """
        Test that no secret santa have themself as receivers
        """
        # Load the secretSanta variable from the provided filename
        with open(self.filename, 'rb') as f:
            secretSanta = pickle.load(f)

        # Loop through all secretSanta pairs and typecast to set
        # to make sure there are no duplicates
        for pair in secretSanta:
            self.assertEqual(len(pair), len(set(pair)))

    def test_secretSanta_and_receiver_not_family(self):
        """
        Test that no secret santa and receiver are in the same family
        """
        # Load the secretSanta variable from the provided filename
        with open(self.filename, 'rb') as f:
            secretSanta = pickle.load(f)

        # Get family data
        families = getFamilyData()[0]

        # Loop through all secretSanta pairs and for every pair,
        # check that the receiver is not in the same family as the
        # secret santa.
        for pair in secretSanta:
            for family in families:
                if pair[0] in family:
                    self.assertTrue(pair[1] not in family)
                    break

    def test_not_same_receiver_as_previous_year(self):
        """
        Test that no secret santa have the same receiver as previous year
        """
        # Load the secretSanta variable from the provided filenames
        with open(self.filename, 'rb') as f:
            secretSanta = pickle.load(f)

        with open(self.previousFilename, 'rb') as f:
            previousSecretSanta = pickle.load(f)

        # Loop through all secretSanta pairs and typecast to set
        # to make sure there are no duplicates
        for pair in secretSanta:
            # Find receiver for previous year
            for prevPair in previousSecretSanta:
                if prevPair[0] == pair[0]:
                    self.assertNotEqual(prevPair[1], pair[1])
                    break
