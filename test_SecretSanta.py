#!/usr/bin/env python3
"""
Test function for SecretSanta.py
"""
import os
import pickle
import unittest
from unittest.mock import MagicMock, mock_open, patch

import TextMagic
from TextMagic.rest import ApiException

target = __import__("SecretSanta")
getFamilyData = target.getFamilyData
getSaveFileNames = target.getSaveFileNames
initiateTextMessageClient = target.initiateTextMessageClient
sendTextMessageToSecretSanta = target.sendTextMessageToSecretSanta
sendTextMessageFromFile = target.sendTextMessageFromFile


class TestScript(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        # Get the secret santa lists created from previous script executions
        self.filename = getSaveFileNames()[0]
        super().__init__(methodName=methodName)

    def setUp(self):
        if not os.path.isfile(self.filename) or not os.path.isfile("family_data.json"):
            self.skipTest(f"Required files not found ({self.filename} or family_data.json)")

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
        filename, previousFilenames = getSaveFileNames(nPreviousSaveFiles=1)

        # Load the secretSanta variable from the provided filenames
        with open(filename, 'rb') as f:
            secretSanta = pickle.load(f)

        if not os.path.isfile(previousFilenames[0]):
            return

        with open(previousFilenames[0], 'rb') as f:
            previousSecretSanta = pickle.load(f)

        # Loop through all secretSanta pairs and typecast to set
        # to make sure there are no duplicates
        for pair in secretSanta:
            # Find receiver for previous year
            for prevPair in previousSecretSanta:
                if prevPair[0] == pair[0]:
                    self.assertNotEqual(prevPair[1], pair[1])
                    break

    def test_not_same_receiver_as_any_of_four_previous_year(self):
        """
        Test that no secret santa have the same receiver as previous year
        """
        filename, previousFilenames = getSaveFileNames(nPreviousSaveFiles=4)

        with open(filename, 'rb') as f:
            secretSanta = pickle.load(f)

        previousSecretSanta = {}
        for fileName in previousFilenames:
            if os.path.isfile(fileName):
                with open(fileName, "rb") as f:
                    secretSantas = pickle.load(f)
                for pair in secretSantas:
                    if pair[0] in previousSecretSanta:
                        previousSecretSanta[pair[0]] += [pair[1]]
                    else:
                        previousSecretSanta[pair[0]] = [pair[1]]

        for pair in secretSanta:
            # A secret santa shall not have the same receiver as any previous
            # year
            if pair[0] in previousSecretSanta:
                self.assertNotIn(pair[1], previousSecretSanta[pair[0]])


class TestTextMessage(unittest.TestCase):

    def test_initiate_text_message_client_success(self):
        settings = {"username": "test_user", "api_key": "test_api_key"}
        client = initiateTextMessageClient(settings)
        self.assertIsInstance(client, TextMagic.TextMagicApi)
        self.assertEqual(client.api_client.configuration.username, "test_user")
        self.assertEqual(client.api_client.configuration.password, "test_api_key")

    def test_initiate_text_message_client_missing_credentials(self):
        with self.assertRaises(KeyError):
            initiateTextMessageClient({"username": "user_only"})
        with self.assertRaises(KeyError):
            initiateTextMessageClient({"api_key": "api_key_only"})

    @patch("SecretSanta.get_settings")
    def test_initiate_text_message_client_default_settings(self, mock_get_settings):
        mock_get_settings.return_value = {"username": "u", "api_key": "k"}
        client = initiateTextMessageClient()
        mock_get_settings.assert_called_once()
        self.assertIsInstance(client, TextMagic.TextMagicApi)

    def test_send_text_message_to_secret_santa(self):
        mock_api = MagicMock()
        mock_response = MagicMock(id=987654)
        mock_api.send_message.return_value = mock_response

        response = sendTextMessageToSecretSanta(
            mock_api, "+46701234567", "Alice", "Bob"
        )
        self.assertEqual(response, mock_response)
        mock_api.send_message.assert_called_once()
        kwargs = mock_api.send_message.call_args[1]
        input_object = kwargs["send_message_input_object"]
        self.assertEqual(input_object["phones"], "+46701234567")
        self.assertIn("Alice", input_object["text"])
        self.assertIn("Bob", input_object["text"])

    @patch("builtins.print")
    def test_send_text_message_to_secret_santa_api_exception(self, mock_print):
        mock_api = MagicMock()
        mock_api.send_message.side_effect = ApiException(status=400, reason="Bad Request")

        with self.assertRaises(ApiException):
            sendTextMessageToSecretSanta(
                mock_api, "+46701234567", "Alice", "Bob"
            )
        mock_print.assert_called()

    @patch("SecretSanta.initiateTextMessageClient")
    @patch("SecretSanta.sendTextMessageToSecretSanta")
    def test_send_text_message_from_file(self, mock_send, mock_init):
        fake_data = [["Alice", "Bob"], ["Charlie", "Diana"]]
        fake_pickle = pickle.dumps(fake_data)
        with patch("builtins.open", mock_open(read_data=fake_pickle)):
            sendTextMessageFromFile("Alice", "+46701234567", filename="fake_file")
            mock_init.assert_called_once_with()
            mock_send.assert_called_once_with(
                mock_init.return_value, "+46701234567", "Alice", "Bob"
            )

