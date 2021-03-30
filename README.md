<center>

![License:MIT](https://img.shields.io/github/license/3c7/yaramanager?style=flat-square&color=blue) 
![Version](https://img.shields.io/pypi/v/yaramanager?style=flat-square&color=blue)
![PyPI - Downloads](https://img.shields.io/pypi/dm/yaramanager?color=blue&style=flat-square)
[![Awesome Yara](https://img.shields.io/static/v1?label=awesome&message=yara&style=flat-square&color=ff69b4&logo=awesome-lists)](https://github.com/InQuest/awesome-yara)

</center>

# Yara Manager
A simple program to manage your yara ruleset in a (sqlite) database.

## Todos
- [ ] Search rules and descriptions
- [ ] Cluster rules in rulesets
- [ ] Enforce configurable default set of meta fields
- [ ] Implement backup and sharing possibilities

## Installation
```shell
pip install yaramanager
```

## Features
### Asciinema (out of date)
[![Watch how to use yaramanager](https://asciinema.org/a/HJJoaGaZIdWIFPG8h5AE5kUer.svg)](https://asciinema.org/a/HJJoaGaZIdWIFPG8h5AE5kUer)
Store your Yara rules in a DB locally and manage them.

### Usage
```
$ ym
Usage: ym [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add      Add a new rule to the database.
  config   Review and change yaramanager configuration.
  db       Manage your databases
  del      Delete a rule by its ID or name.
  edit     Edits a rule with your default editor.
  export   Export rules from the database.
  get      Get rules from the database.
  help     Displays help about commands
  list     Lists rules available in DB.
  parse    Parses rule files.
  read     Read rules from stdin.
  scan     Scan files using your rulesets.
  search   Searches through your rules.
  stats    Prints stats about the database contents.
  tags     Show tags and the number of tagged rules
  version  Displays the current version.   
```
