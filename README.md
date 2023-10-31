# RandomSecretSanta

A script for randomly selecting secret santa. It uses a service called Textmagic (https://www.textmagic.com) to send text messages to the family members with their randomly selected secret santa.

The script will find a random secret santa for every person in every family with the requirements that it is not the other family member and not the person it self.

The script reads in family data from a file called family_data.json. It should contain a list called families which contains pairs of names of the family members, e.g.: 
"families": [
        [
            "PersonA",
            "PersonB"
        ],
        [
            "PersonC",
            "PersonD"
        ]
]

It shall also include a dictionary called "phonenumbers" which contains names as keys and phone numbers as values, e.g:
"phonenumbers": {
        "PersonA": "+99123456789",
        "PersonB": "+99123456789",
        "PersonC": "+99123456789",
        "PersonD": "+99123456789"
}

For the Textmagic service to work, a file called settings.yaml must also be created which contains two field, 'username' and 'token'.
