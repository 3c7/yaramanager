from pathlib import Path
from typing import Union

import yara
import yarabuilder

from yaramanager.utils.utils import write_ruleset_to_tmp_file


class YaraBuilder(yarabuilder.YaraBuilder):
    def write_rules_to_file(self, path: Union[str, Path], single_file: bool = False, compiled: bool = False):
        """Write yarabuilder defined ruleset to a file. single_file and compiled can be used to define how the file is
        written, either as a single file containing all rules, as a compiled yara rule or as a directory containing all
        rules as separate files."""
        if isinstance(path, str):
            path = Path(path)
        # Write rules as separate files
        if not single_file and not compiled:
            if not path.is_dir():
                raise NotADirectoryError()

            for rule_name in self.yara_rules.keys():
                with open(path.joinpath(rule_name + ".yar"), "w") as fh:
                    fh.write(self.build_rule(rule_name))

        # Write rules as single file
        else:
            if path.is_dir():
                raise IsADirectoryError()

            if single_file:
                if path.suffix != ".yar":
                    path = Path(str(path) + ".yar")
                with open(path, "w") as fh:
                    fh.write(self.build_rules())

            if compiled:
                if path.suffix == ".yar":
                    path = Path(str(path)[:-4] + ".yac")
                elif path.suffix != ".yac":
                    path = Path(str(path) + ".yac")
                tmp_path, size = write_ruleset_to_tmp_file(self)
                compiled: yara.Rules = yara.compile(tmp_path)
                compiled.save(str(path))
