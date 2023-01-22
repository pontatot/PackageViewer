import os


from packageparse.parsers.apt_parser import AptParser
from packageparse.parsers.dnf_parser import DnfParser
from packageparse.parsers.pacman_parser import PacmanParser
from packageparse.distro_data import DistroData
import packageparse.database


class DataParser:

    def __init__(self):
        self.ARCHIVES_DIR = "archives"
        self.TMP_DIR = "/tmp"
        
    def __get_parser_class__(self, distro_name):
        match distro_name:
            case "debian": return AptParser
            case "ubuntu": return AptParser
            case "fedora": return DnfParser
            case "archlinux": return PacmanParser
            case _: raise ValueError("Unknown distribution: "+distro_name)
    
    def __detect_data__(self, distro_data: DistroData):

        def value_or_loop_dir(value, *dir):
            if value:
                yield value
            else:
                path = os.path.join(self.ARCHIVES_DIR, *dir)
                for subdir in os.listdir(path):
                    if os.path.isdir(os.path.join(path, subdir)):
                        yield subdir
                
        for name_loop in value_or_loop_dir(distro_data.name):
            for version_loop in value_or_loop_dir(distro_data.version, name_loop):
                for repo_loop in value_or_loop_dir(distro_data.repo, name_loop, version_loop):
                    for content_loop in (("sums", "files") if distro_data.content == "all" else [distro_data.content]):
                        yield DistroData(
                            name=name_loop,
                            version=version_loop,
                            repo=repo_loop,
                            content=content_loop,
                        )

    def parse_multiple_data(self, distro_data: DistroData, create_output):

        for distro_data_loop in self.__detect_data__(distro_data):
            output = create_output(distro_data_loop)
            if output:
                self.parse_single_data(
                    distro_data_loop,
                    output
                )
                output.close()


    def parse_single_data(self, distro_data: DistroData, output):
        ParserClass = self.__get_parser_class__(distro_data.name)
        print(f"Using parser class '{ParserClass.__name__}'")
        
        parser = ParserClass(distro_data, self.ARCHIVES_DIR, output)
        
        match distro_data.content:
            case "sums":
                parser.parse_sums()
            case "files":
                parser.parse_files()
            case _:
                raise ValueError(f"SHOULD NOT HAPPEN: invalid content '{distro_data.content}'")