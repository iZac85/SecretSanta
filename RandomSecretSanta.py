#!/usr/bin/env python3

import os.path
from textmagic.rest import TextmagicRestClient
from random import choice
import pickle
import time
import json
import yaml
from pathlib import Path


def main():
    """
    # main

    This function will find a random secret santa for every person in every 
    family with the requirements that it is not the other family member and not 
    the person it self.

    It will then send text messages to all family members with their secret
    santa
    """
    # Get family data (names, relations and phone numbers)
    families, phonenumbers = getFamilyData()
    savefile, previousSavefile = getSaveFileNames()

    # Look for file with secret santas for previous year
    if os.path.isfile(previousSavefile):
        with open(previousSavefile, 'rb') as f:
            previousSecretSanta = pickle.load(f)

    # Generate randomized secret santa
    secretSanta = randomizeSecretSanta(families, previousSecretSanta)

    # Save the result to file if it needs to be reused later
    with open(savefile, 'wb') as f:
        pickle.dump(secretSanta, f)

    # Initiate text message client
    settings = get_settings()
    client = initiateTextMessageClient(settings)

    # Send text message to all secret santa
    for pair in secretSanta:
        sendTextMessageToSecretSanta(
            client, phonenumbers[pair[0]], pair[0], pair[1])
        # Wait for 1s to not spam the message service
        time.sleep(1)


def getSaveFileNames():
    """
    # getSaveFileNames

    Function that returns a file name for where secret santa data shall be 
    stored, as well as the name of the secret santa file for previous year
    """
    filename = 'secretSanta_'
    now = time.localtime()
    savefile = '{}{}'.format(filename, now.tm_year)
    previousSavefile = '{}{}'.format(filename, now.tm_year-1)
    return savefile, previousSavefile


def getFamilyData():
    """
    # getFamilyData

    Function that returns family data read from a json file
    """
    # Nested list with all families
    with open('family_data.json') as json_file:
        data = json.load(json_file)
    return data['families'], data['phonenumbers']


def randomizeSecretSanta(families, previousSecretSanta=[]):
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
            otherFamilies = [item for sublist in otherFamilies
                             for item in sublist]
            for member in family:
                # Remove people who already have a designated secret santa (the second person is the receiver)
                availableReceivers = list(
                    set(otherFamilies) - set([pair[1] for pair in secretSanta]))
                # If there is a previous secret santa list, remove the secret santa that the person
                # had as receiver last year
                if previousSecretSanta:
                    for pair in previousSecretSanta:
                        if pair[0] == member:
                            if pair[1] in availableReceivers:
                                availableReceivers.remove(pair[1])
                            break
                if len(availableReceivers) == 0:
                    # There are no available choices left. This can only happen if a member in the last
                    # family has not yet been randomly selected when it's time for the last member in the last
                    # family to get a randomly selected receiver. In this case we need to restart
                    # the whole randomizer.
                    randomizationSuccessful = False
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
            "Randomization failed. The maximum number of tries was reached")
    # print("=================================")
    #print("Final secretSanta: ", secretSanta)
    return secretSanta


def get_settings():
    """
    # get_settings

    Function that returns a dict with settings read from a yaml-file 
    """
    full_file_path = Path(__file__).parent.joinpath('settings.yaml')
    with open(full_file_path) as settings:
        settings_data = yaml.load(settings, Loader=yaml.Loader)
    return settings_data


def initiateTextMessageClient(settings):
    """
    # initiateTextMessageClient

    Function that initiates the connection with the text messaging service
    """
    username = settings['username']
    token = settings['token']
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
        text="Hej {}!\n\nDin hemliga julklappsmottagare är: {} \n\nGod Jul önskar Tomten!".
        format(secretSanta, receiver))


def sendTextMessageFromFile(
        textMessageRecipant, phonenumber, filename='secretSanta'):
    """
    # sendTextMessageFromFile

    Function that can be used to send text message to a secret santa, using an old randomization
    stored in a file using pickle
    """
    # Load the secretSanta variable from the provided filename
    with open(filename, 'rb') as f:
        secretSanta = pickle.load(f)
    # Initiate text message client
    client = initiateTextMessageClient()
    # Find the receiver for the secret santa
    receiver = [pair[1]
                for pair in secretSanta if pair[0] == textMessageRecipant][0]
    # Send text message to the secret santa
    sendTextMessageToSecretSanta(
        client, phonenumber, textMessageRecipant, receiver)


if __name__ == '__main__':
    main()
