<div align="center">

![License:MIT](https://img.shields.io/github/license/3c7/yaramanager?style=flat-square&color=blue) 
![Version](https://img.shields.io/pypi/v/yaramanager?style=flat-square&color=blue)
![PyPI - Downloads](https://img.shields.io/pypi/dm/yaramanager?color=blue&style=flat-square)
[![Awesome Yara](https://img.shields.io/static/v1?label=awesome&message=yara&style=flat-square&color=ff69b4&logo=awesome-lists)](https://github.com/InQuest/awesome-yara)

</div>

# Yara Manager
A simple program to manage your yara ruleset in a (sqlite) database.

## Todos
- [ ] Implement backup and sharing possibilities

## Installation
Install it using pip:
```shell
pip install yaramanager
```
Or grab one of the prebuilt binaries from the release page.

## Configuration
Yara Manager creates a fresh config if none exists. If you update from an older version, please pay attention to freshly
added [config options](resources/config.toml). You can reset you configuration using `ym config reset`, however, this
will also overwrite any custom changes you made.  

```toml
## Editor
# editor contains the command used to start the editor. Note that this must be a list of the command and the needed
# parameters, e.g. `editor = ["codium", "-w"]`.
editor = [ "codium", "-w" ]
```
The most important configuration to change is probably your editor. The default configuration uses `codium -w` for 
opening rules. You can use e.g. `EDITOR=vim DISABLE_STATUS=1 ym config edit` to open you config in Vim (and you can type
`:wq` to save your changes and quit :P). After changing the editor path, you are good to go! The following asciinema
shows how to quickly overwrite the editor set in the config:

[![Asciinema: Temporarily overwrite the used editor.](https://asciinema.org/a/auX5tjpeUiHCnsfCrO0MEPRY9.svg)](https://asciinema.org/a/auX5tjpeUiHCnsfCrO0MEPRY9)

```toml
# Databases
# A list of databases. Every database needs to define a driver and a path, such as
#
# [[yaramanager.db.databases]]
# driver = "sqlite"
# path = "/home/user/.config/yaramanager/data.db"
[[yaramanager.db.databases]]
driver = "sqlite"
path = "/home/3c7/.config/yaramanager/myrules.db"
```
If you want to use multiple databases (which is pretty useful if you use rules from different sources or with different 
classifications), you can add them to the config file, too.

## Features
### General usage
```
$ ym
Usage: ym [OPTIONS] COMMAND [ARGS]...

  ym - yaramanager. Use the commands shown below to manage your yara
  ruleset. By default, the manager uses codium as editor. You can change
  that in the config file or using EDITOR environment variable. When using
  editors in the console, you might want to disable the status display using
  DISABLE_STATUS.

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
  new      Create a new rule using you preferred editor.
  parse    Parses rule files.
  read     Read rules from stdin.
  ruleset  Manage your rulesets
  scan     Scan files using your rulesets.
  search   Searches through your rules.
  stats    Prints stats about the database contents.
  tags     Show tags and the number of tagged rules
  version  Displays the current version.
```

### Yara Manager Showcase
[![Asciiname: Yara Manager showcase](https://asciinema.org/a/8QbXQoBEeJIwVcf2mWqiRTNBj.svg)](https://asciinema.org/a/8QbXQoBEeJIwVcf2mWqiRTNBj)
