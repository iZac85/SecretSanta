# SecretSanta

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

For the Textmagic service to work, a file called settings.yaml must also be created which contains two fields, 'username' and 'api_key':
```yaml
username: "YOUR_TEXTMAGIC_USERNAME"
api_key: "YOUR_TEXTMAGIC_API_KEY"
```

## Installation

The script requires Python >= 3.9 and uses the modern [TextMagic REST Python SDK](https://docs.textmagic.com/#tag/SDKs/Python/Installation).

> **Note:** The modern TextMagic SDK is distributed via GitHub (the legacy PyPI package is outdated).

```bash
# Set up a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Alternatively, install the TextMagic SDK directly:
```bash
pip install git+https://github.com/textmagic/textmagic-rest-python-v2.git@v3.0.50169
pip install pyyaml
```

## Running

```bash
# 1. Local test (generates pairs, saves file, and runs tests without contacting TextMagic)
python SecretSanta.py

# 2. Dry run (verifies TextMagic connection/credentials via ping and previews all SMS messages without sending)
python SecretSanta.py --dry-run

# 3. Live run (sends SMS text messages to all participants)
python SecretSanta.py --live

# 4. Automated unit tests
python -m unittest test_SecretSanta.py
```
