"Run dothttp requests"
import argparse
import pathlib
from dothttp import Config, dothttp_model, MultidefHttp
from dothttp.request_base import RequestCompiler


def get_args():
    """ Get Args """
    parser = argparse.ArgumentParser(
        description='Run requests and generate report', prog="dothttp-test")
    general_group = parser.add_argument_group('general')
    general_group.add_argument('--out', help='output file',
                               type=str)
    general_group.add_argument(
        'file_or_dir', help="File or directory to run", type=list, default=[])
    general_group.add_argument(
        "--collect-only", help="print list of http requests", const=False, action="store_const"
    )

    return parser.parse_args()


class HttpTestRunner(RequestCompiler):
    """Runs http requests and generates report"""

    def __init__(self, content, model, args: Config):
        self.content = content
        self.model = model
        super().__init__(args)

    def load_content(self):
        pass

    def load_model(self):
        pass


def __main__():
    """ Run tests"""
    args = get_args()
    for file_or_dir in args.file_or_dir:
        files = (p.resolve() for p in pathlib.Path(file_or_dir).glob(
            "**/*") if p.suffix in {".hnbk", ".httpbook", ".http", ".dhttp", })
        for file in files:
            if file.suffix in ['.http', '.dhttp']:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    model: MultidefHttp = dothttp_model.model_from_str(content)
                for index, http in enumerate(model.allhttps):
                    comp = HttpTestRunner(content=content, model=model, args=Config(
                        curl=False,
                        content=False,
                        debug=True,
                        properties=[],
                        target=index + 1,
                        property_file=None,
                        info=True,
                        file=file,
                        env=[],
                        no_cookie=False,
                        format=False,
                    ))
                    # TODO get_resp_n_result api is not availabile
                    resp, script_result = comp.get_resp_n_result()
                    if 400 > resp.status_code >= 200:
                        if comp.http.namewrap:
                            print(f'Request {comp.httpdef.url} passed with target {http.namewrap.name} from file {file}')
                        else:
                            print(f'Request {comp.httpdef.url} passed with target {index+1} from file {file}')
                    comp.print_script_result(script_result)
                    


if __name__ == "__main__":
    __main__()
