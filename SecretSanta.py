#!/usr/bin/env python3

import json
import os.path
import pickle
import time
from pathlib import Path
from random import choice
from unittest import TestLoader, TestResult

import yaml
from textmagic.rest import TextmagicRestClient


def main(sendTextMessages=False, nPreviousSaveFiles=1):
    """
    # main

    This function will find a random secret santa for every person in every
    family with the requirements that it is not the other family member and not
    the person it self.

    Inputs: 
    - If sendTextMessages is set to True a text message will be sent to all
      family members with their secret santa

    - nPreviousSaveFiles states how many save files from previous years to
      search for when excluding secret santa receivers from previous years

    Return: Name of file containing the secret santas
    """
    print('\n================== Random Secret Santa ==================')
    # Get family data (names, relations and phone numbers)
    families, phonenumbers = getFamilyData()
    savefile, previousSavefiles = getSaveFileNames(nPreviousSaveFiles=nPreviousSaveFiles)
    print('Secret santa will be saved to: \'{}\''.format(savefile))

    previousSecretSanta = getSecretSantasFromPreviousYears(previousSavefiles)

    print('Generating secret santa')
    secretSanta = randomizeSecretSanta(families, previousSecretSanta)

    # Save the result to file if it needs to be reused later
    with open(savefile, "wb") as f:
        pickle.dump(secretSanta, f)
    print('Secret santa saved to: \'{}\''.format(savefile))

    # Run unittests on the saved file
    print('Verifying secret santa file')
    testSuccessful = runUnitTestOnSavedFile()
    if not testSuccessful:
        print('Verification failed')
        print('================== FAILED ==================')
        return
    print('All tests passed')
    if sendTextMessages:
        # Initiate text message client
        print('Initializing text message client')
        settings = get_settings()
        client = initiateTextMessageClient(settings)

        # Send text message to all secret santa
        print('Sending {} text messages: '.format(len(secretSanta)), end='')
        for pair in secretSanta:
            print('#', end='')
            sendTextMessageToSecretSanta(
                client, phonenumbers[pair[0]], pair[0], pair[1])
            # Wait for 1s to not spam the message service
            time.sleep(1)
        print(' Done')
    print('================== Finished successfully ==================')
    return savefile


def getSecretSantasFromPreviousYears(previousSavefiles):
    previousSecretSanta = {}
    for fileName in previousSavefiles:
        if os.path.isfile(fileName):
            with open(fileName, "rb") as f:
                secretSantas = pickle.load(f)
            print(
            'Found secret santa from previous year: \'{}\''
            ''.format(fileName))
            for pair in secretSantas:
                if pair[0] in previousSecretSanta:
                    previousSecretSanta[pair[0]] += [pair[1]]
                else:
                    previousSecretSanta[pair[0]] = [pair[1]]
    return previousSecretSanta


def getSaveFileNames(nPreviousSaveFiles: int=1):
    """
    # getSaveFileNames

    Function that returns a file name for where secret santa data shall be
    stored, as well as the name of the secret santa file for previous year
    """
    filename = "secretSanta_"
    now = time.localtime()
    savefile = "{}{}".format(filename, now.tm_year)
    previousSavefiles = []
    for i in range(1, nPreviousSaveFiles + 1):
        previousSavefiles += ["{}{}".format(filename, now.tm_year - i)]
    return savefile, previousSavefiles


def getFamilyData():
    """
    # getFamilyData

    Function that returns family data read from a json file
    """
    # Nested list with all families
    with open("family_data.json") as json_file:
        data = json.load(json_file)
    return data["families"], data["phonenumbers"]


def randomizeSecretSanta(families, previousSecretSanta={}):
    """
    # randomizeSecretSanta

    Function that takes a nested list of families as input, where the sub lists contains
    people that should not get each other as secret santa.

    Outputs a nested list with names and for whom they are secret santa, e.g in the following format:
    [["santa_1","receiver_1"],["santa_2","receiver_2"],...,["santa_n","receiver_n"]]]
    """
    tries = 0
    randomizationSuccessful = False
    while not randomizationSuccessful and tries < 10:
        secretSanta = []
        availableReceivers = []
        for family in families:
            # Create a list that only contain members from other families
            otherFamilies = families.copy()
            otherFamilies.remove(family)
            # Flatten the list
            otherFamilies = [
                item for sublist in otherFamilies for item in sublist]
            for member in family:
                # Remove people who already have a designated secret santa (the second person is the receiver)
                availableReceivers = list(
                    set(otherFamilies) - set([pair[1] for pair in secretSanta])
                )
                # If there is a previous secret santa list, remove the secret santa that the person
                # had as receiver last year
                if previousSecretSanta:
                    if member in previousSecretSanta:
                        for previousReceiver in previousSecretSanta[member]:
                            if previousReceiver in availableReceivers:
                                availableReceivers.remove(previousReceiver)
                if len(availableReceivers) == 0:
                    # There are no available choices left. This can only happen if a member in the last
                    # family has not yet been randomly selected when it's time for the last member in the last
                    # family to get a randomly selected receiver. In this case we need to restart
                    # the whole randomizer.
                    randomizationSuccessful = False
                    print('Secret santa randomization failed. Trying again.')
                    break
                else:
                    # Generate a random receiver
                    receiver = choice(availableReceivers)
                    randomizationSuccessful = True
                # Add the secret santa and receiver as a pair to the secretSanta list
                secretSanta.append([member, receiver])
            else:
                continue  # only executed if the inner loop did NOT break
            break  # only executed if the inner loop DID break
        tries += 1
    if tries == 10:
        raise Exception(
            "randomizeSecretSanta",
            "Randomization failed. The maximum number of tries was reached",
        )
    return secretSanta


def get_settings():
    """
    # get_settings

    Function that returns a dict with settings read from a yaml-file
    """
    full_file_path = Path(__file__).parent.joinpath("settings.yaml")
    with open(full_file_path) as settings:
        settings_data = yaml.load(settings, Loader=yaml.Loader)
    return settings_data


def initiateTextMessageClient(settings):
    """
    # initiateTextMessageClient

    Function that initiates the connection with the text messaging service
    """
    username = settings["username"]
    token = settings["token"]
    client = TextmagicRestClient(username, token)
    return client


def sendTextMessageToSecretSanta(client, phonenumber, secretSanta, receiver):
    """
    # sendTextMessageToSecretSanta

    Function that sends a text message to the secret santa, informing about who
    that person is secret santa for.
    """
    message = client.messages.create(
        phones=phonenumber,
        text="Hej {}!\n\nDin hemliga julklappsmottagare är: {} \n\nGod Jul önskar Tomten!".format(
            secretSanta, receiver
        ),
    )


def sendTextMessageFromFile(
        textMessageRecipant, phonenumber, filename="secretSanta"):
    """
    # sendTextMessageFromFile

    Function that can be used to send text message to a secret santa, using an 
    old randomization stored in a file using pickle
    """
    # Load the secretSanta variable from the provided filename
    with open(filename, "rb") as f:
        secretSanta = pickle.load(f)
    # Initiate text message client
    client = initiateTextMessageClient()
    # Find the receiver for the secret santa
    receiver = [pair[1]
                for pair in secretSanta if pair[0] == textMessageRecipant][0]
    # Send text message to the secret santa
    sendTextMessageToSecretSanta(
        client, phonenumber, textMessageRecipant, receiver)


def runUnitTestOnSavedFile():
    """
    # runUnitTestOnSavedFile

    Function that runs unit tests to verify that the file with secret 
    santa is following all the rules specified in the tests.

    The function returns a boolean stating if all tests have passed or not
    """
    test_loader = TestLoader()
    test_result = TestResult()

    # Use resolve() to get an absolute path
    # https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve
    test_directory = str(Path(__file__).resolve().parent)

    test_suite = test_loader.discover(test_directory, pattern='test_*.py')
    test_suite.run(result=test_result)

    # See the docs for details on the TestResult object
    # https://docs.python.org/3/library/unittest.html#unittest.TestResult

    if test_result.wasSuccessful():
        return True
    else:
        print('Tests of secretSanta-file failed:')
        if test_result.errors != []:
            print(test_result.errors)
        if test_result.failures != []:
            for message in test_result.failures:
                print(message)
        return False

def printReceiversFromFile(saved_file: str, secretSantaReceiversToPrint: list=[]):
    """
    # printReceiversFromFile
    Function that prints secret santa receivers from a loaded file.
    
    secretSantaReceiversToPrint contains a list of secret santa pairs for the
    receiver names in the list will be printed. If left empty, all secret
    santas will be printed out.
    """

    # Look for file with secret santas for previous year
    with open(saved_file, "rb") as f:
        randomizedSecretSanta = pickle.load(f)

    print_all_names = False
    if secretSantaReceiversToPrint == []:
        print_all_names = True

    for pair in randomizedSecretSanta:
        if print_all_names:
            print('{} is secret santa for {}'.format(pair[0], pair[1]))
        else:
            for name in secretSantaReceiversToPrint:
                if name in pair[1]:
                    print('{} is secret santa for {}'.format(pair[0], pair[1]))

if __name__ == "__main__":
    # Set live_run to true when testing is complete and text messages shall be
    # sent to all secret santas
    live_run = False
    savefile = main(sendTextMessages=live_run, nPreviousSaveFiles=4)
    if not live_run:
        print("\nResults:")
        printReceiversFromFile(savefile)