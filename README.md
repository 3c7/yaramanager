# Yara Manager
A simple program to manage your yara ruleset in a (sqlite) database.

## Todos
- [x] Add rules
- [x] Delete rules
- [x] List rules
- [x] Search strings
- [x] Actually edit rules with `edit` command - currently only file changes are detected, but changes are not merged into the rule itself.
- [x] Implement rule export
- [ ] Search rules
- [ ] Cluster rules in rulesets
- [ ] Enforce configurable default set of meta fields
- [ ] Implement backup and sharing possibilities
- [ ] Add database migrations

## Installation
```shell
pip install yaramanager
```

## Features
### Asciinema
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
  list     Lists rules available in DB.
  parse    Parses rule files.
  read     Read rules from stdin.
  search   Searches through your rules.
  stats    Prints stats about the database contents.
  version  Displays the current version.    
```
