import argparse
import logging
from .lib import TADClassifier

# taken and altered from hicFindTads
log = logging.getLogger(__name__)
from hicexplorer._version import __version__


def parse_arguments(args=None):
    """
        get command line arguments
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        conflict_handler='resolve',
        description="""
Uses Supervised Learning to call TAD boundaries. One or multiple HiC-Matrices can be passed, from which a BED file will be produced containing the predicted boundary positions. By default, a EasyEnsembleClassifier as described in Liu et al.: “Exploratory Undersampling for Class-Imbalance Learning” will be used to call TADs. Internally this classifier relies on Resampling, Boosting and Bagging. Passed matrices will be range normalized by default. Alternatively, obs/exp normalization can be used. Currently, only classifiers for 10kb resolution are implemented. For building own classifiers or tune existing ones, hicTrainClassifier can be used and passed with the saved_classifer argument. A simple usage example can be seen here:

$ hicTADClassifier -m my_matrix.cool -o predictions -n range
        """)

    parserRequired = parser.add_argument_group('Required arguments')

    parserRequired.add_argument('--matrices', '-m',
                                help='HiC-Matrix file or list of files for input. Only COOLER files are supported!',
                                required=True,
                                nargs='+')

    parserRequired.add_argument('--out_file', '-o',
                                help='output file path for predictions',
                                required=True,
                                nargs='+')

    parserOpt = parser.add_argument_group('Optional arguments')

    parserOpt.add_argument('--normalization_method', '-n',
                           help='set the normalization mode, with which the passed matrices will be normalized. If not set, matrices will be range normalized',
                           type=str,
                           choices=[
                               'obs_exp',
                               'range'
                           ],
                           default='range')

    parserOpt.add_argument('--saved_classifier',
                           help='Default classifier are available for 10kb, 25kb, 50kb and 100kb resolution. Do not set this parameter to use the default models. '
                           'Pass a self-trained classifier (from hicTrainTADClassifier) to load a non-default model.',
                           type=str,
                           default=None)

    parserOpt.add_argument('--unselect_border_cases',
                           help='set whether genes at the border of the matrices will not be predicted',
                           required=False,
                           action='store_true')

    parserOpt.add_argument('--threads', '-t',
                           help='number of threads used',
                           default=4,
                           type=int)

    parserOpt.add_argument('--chromosomes',
                           help='Chromosomes to include in the analysis. If not set, all chromosomes are included.',
                           nargs='+')
    parserOpt.add_argument("--help", "-h", action="help",
                           help="show this help message and exit")

    parserOpt.add_argument('--version', action='version',
                           version='%(prog)s {}'.format(__version__))

    return parser


def main(args=None):

    args = parse_arguments().parse_args(args)
    program = TADClassifier('predict',
                            args.out_file,
                            saved_classifier=args.saved_classifier,
                            normalization_method=args.normalization_method,
                            unselect_border_cases=args.unselect_border_cases,
                            threads=args.threads,
                            pAddRemoveChrPrexix=None
                            )

    program.run_hicTADClassifier(args.matrices, args.chromosomes)
