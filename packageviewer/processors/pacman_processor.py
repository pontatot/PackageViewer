from packageviewer.parsers.pacman_parser import PacmanParser
from packageviewer.inserters.pacman_inserter import PacmanInserter

class PacmanProcessor:

    def __init__(self, distro_name, distro_version, dir_path, output_db_path) -> None:
        self.distro_name = distro_name
        self.distro_version = distro_version
        self.parser = PacmanParser(distro_name, distro_version, dir_path)
        self.inserter = PacmanInserter(output_db_path)

    def process(self):
        sums_data, files_data = self.process_parser()

        self.inserter.table_tmp_package.add_rows(sums_data)
        self.inserter.table_tmp_file.add_rows(files_data)

        self.inserter.normalize(self.distro_name, self.distro_version)

    def process_parser(self):
        all_list = self.parser.parse()
        sums_data = []
        files_data = []

        for i in all_list:
            for j in i:
                sums_data.append(j["sum"])
                files_data.extend(j["files"])


        
        return sums_data, files_data