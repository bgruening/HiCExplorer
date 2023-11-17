import warnings
warnings.simplefilter(action="ignore", category=RuntimeWarning)
warnings.simplefilter(action="ignore", category=PendingDeprecationWarning)
from hicexplorer import hicBuildMatrix, hicInfo
from hicmatrix import HiCMatrix as hm
from tempfile import NamedTemporaryFile, mkdtemp
import shutil
import os
import numpy.testing as nt
import pytest
from hicexplorer.test.test_compute_function import compute

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_data/")
sam_R1 = ROOT + "small_test_R1_unsorted.bam"
sam_R2 = ROOT + "small_test_R2_unsorted.bam"
dpnii_file = ROOT + "DpnII.bed"
delta = 80000


def are_files_equal(file1, file2, delta=1):
    equal = True
    if delta:
        mismatches = 0
    with open(file1) as textfile1, open(file2) as textfile2:
        for x, y in zip(textfile1, textfile2):
            if x.startswith('File'):
                continue
            if x != y:
                if delta:
                    mismatches += 1
                    if mismatches > delta:
                        equal = False
                        break
                else:
                    equal = False
                    break
    return equal


def test_build_matrix(capsys):
    outfile = NamedTemporaryFile(suffix='.h5', delete=False)
    outfile.close()
    outfile_bam = NamedTemporaryFile(suffix='.bam', delete=False)
    outfile.close()
    qc_folder = mkdtemp(prefix="testQC_")
    args = "-s {} {} --outFileName {} -bs 5000 -b {} --QCfolder {} --threads 4 \
            --restrictionSequence GATC --danglingSequence GATC -rs {}".format(sam_R1, sam_R2,
                                                                              outfile.name, outfile_bam.name,
                                                                              qc_folder, dpnii_file).split()
    # hicBuildMatrix.main(args)
    compute(hicBuildMatrix.main, args, 5)
    test = hm.hiCMatrix(ROOT + "small_test_matrix_parallel_one_rc.h5")
    new = hm.hiCMatrix(outfile.name)
    nt.assert_equal(test.matrix.data, new.matrix.data)
    nt.assert_equal(test.cut_intervals, new.cut_intervals)
    # print("MATRIX NAME:", outfile.name)
    print(set(os.listdir(ROOT + "QC/")))
    assert are_files_equal(ROOT + "QC/QC.log", qc_folder + "/QC.log")
    assert set(os.listdir(ROOT + "QC/")) == set(os.listdir(qc_folder))

    # accept delta of 80 kb, file size is around 4.5 MB
    assert abs(os.path.getsize(ROOT + "small_test_matrix_result.bam") - os.path.getsize(outfile_bam.name)) < delta

    os.unlink(outfile.name)
    shutil.rmtree(qc_folder)
    # os.unlink("/tmp/test.bam")


def test_build_matrix_restriction_enzyme(capsys):
    outfile = NamedTemporaryFile(suffix='.h5', delete=False)
    outfile.close()
    outfile_bam = NamedTemporaryFile(suffix='.bam', delete=False)
    outfile.close()
    qc_folder = mkdtemp(prefix="testQC_")
    args = "-s {} {} --outFileName {} -bs 5000 -b {} --QCfolder {} --threads 4 --danglingSequence GATC AGCT --restrictionSequence GATC AAGCTT -rs {} {}".format(sam_R1, sam_R2,
                                                                                                                                                                outfile.name, outfile_bam.name,
                                                                                                                                                                qc_folder, dpnii_file, ROOT + 'hicFindRestSite/hindIII.bed').split()
    # hicBuildMatrix.main(args)
    compute(hicBuildMatrix.main, args, 5)

    test = hm.hiCMatrix(ROOT + "small_test_matrix_parallel_two_rc.h5")
    new = hm.hiCMatrix(outfile.name)
    nt.assert_equal(test.matrix.data, new.matrix.data)
    nt.assert_equal(test.cut_intervals, new.cut_intervals)
    # print("MATRIX NAME:", outfile.name)
    print(set(os.listdir(ROOT + "QC_multi_restriction/")))
    assert are_files_equal(ROOT + "QC_multi_restriction/QC.log", qc_folder + "/QC.log")
    assert set(os.listdir(ROOT + "QC_multi_restriction/")) == set(os.listdir(qc_folder))

    # accept delta of 80 kb, file size is around 4.5 MB
    assert abs(os.path.getsize(ROOT + "small_test_matrix_result.bam") - os.path.getsize(outfile_bam.name)) < delta

    os.unlink(outfile.name)
    shutil.rmtree(qc_folder)
    # os.unlink("/tmp/test.bam")


def test_build_matrix_restriction_enzyme_region(capsys):
    outfile = NamedTemporaryFile(suffix='.h5', delete=False)
    outfile.close()
    outfile_bam = NamedTemporaryFile(suffix='.bam', delete=False)
    outfile.close()
    qc_folder = mkdtemp(prefix="testQC_")
    args = "-s {} {} --outFileName {} -bs 5000 -b {} --QCfolder {} --threads 4 --danglingSequence GATC AGCT --restrictionSequence GATC AAGCTT -rs {} {} --region {}".format(sam_R1, sam_R2,
                                                                                                                                                                            outfile.name, outfile_bam.name,
                                                                                                                                                                            qc_folder, dpnii_file, ROOT + 'hicFindRestSite/hindIII.bed', 'chr3R').split()
    # hicBuildMatrix.main(args)
    compute(hicBuildMatrix.main, args, 5)

    test = hm.hiCMatrix(ROOT + "small_test_matrix_parallel_two_rc_chr3R.h5")
    new = hm.hiCMatrix(outfile.name)

    # print('test.cut_intervals {}'.format(test.cut_intervals))
    # print('new.cut_intervals {}'.format(new.cut_intervals))
    nt.assert_equal(test.matrix.data, new.matrix.data)
    nt.assert_equal(len(test.cut_intervals), len(new.cut_intervals))

    # print("MATRIX NAME:", outfile.name)
    print(set(os.listdir(ROOT + "QC_region/")))
    assert are_files_equal(ROOT + "QC_region/QC.log", qc_folder + "/QC.log")
    assert set(os.listdir(ROOT + "QC_region/")) == set(os.listdir(qc_folder))

    # accept delta of 80 kb, file size is around 4.5 MB
    assert abs(os.path.getsize(ROOT + "build_region.bam") - os.path.getsize(outfile_bam.name)) < delta

    os.unlink(outfile.name)
    shutil.rmtree(qc_folder)


def test_build_matrix_chromosome_sizes(capsys):
    outfile = NamedTemporaryFile(suffix='.h5', delete=False)
    outfile.close()
    outfile_bam = NamedTemporaryFile(suffix='.bam', delete=False)
    outfile.close()
    qc_folder = mkdtemp(prefix="testQC_")
    args = "-s {} {} --outFileName {} -bs 5000 -b {} --QCfolder {} --threads 4 --chromosomeSizes {}  \
            --restrictionSequence GATC --danglingSequence GATC -rs {}".format(sam_R1, sam_R2,
                                                                              outfile.name, outfile_bam.name,
                                                                              qc_folder, ROOT + 'hicBuildMatrix/dm3.chrom.sizes', dpnii_file).split()
    # hicBuildMatrix.main(args)
    compute(hicBuildMatrix.main, args, 5)

    test = hm.hiCMatrix(ROOT + "hicBuildMatrix/chromosome_sizes/small_test_chromosome_size.h5")
    new = hm.hiCMatrix(outfile.name)
    nt.assert_equal(test.matrix.data, new.matrix.data)
    nt.assert_equal(test.cut_intervals, new.cut_intervals)
    # print("MATRIX NAME:", outfile.name)
    print(set(os.listdir(ROOT + "QC/")))
    assert are_files_equal(ROOT + "QC/QC.log", qc_folder + "/QC.log")
    assert set(os.listdir(ROOT + "QC/")) == set(os.listdir(qc_folder))

    # accept delta of 80 kb, file size is around 4.5 MB
    assert abs(os.path.getsize(ROOT + "hicBuildMatrix/chromosome_sizes/test.bam") - os.path.getsize(outfile_bam.name)) < delta

    os.unlink(outfile.name)
    shutil.rmtree(qc_folder)
    # os.unlink("/tmp/test.bam")


def test_build_matrix_cooler():
    outfile = NamedTemporaryFile(suffix='.cool', delete=False)
    outfile.close()
    outfile_bam = NamedTemporaryFile(suffix='.bam', delete=False)
    outfile.close()
    qc_folder = mkdtemp(prefix="testQC_")
    args = "-s {} {} --outFileName {} -bs 5000 -b {} --QCfolder {} --threads 4  \
            --restrictionSequence GATC --danglingSequence GATC -rs {}".format(sam_R1, sam_R2,
                                                                              outfile.name, outfile_bam.name,
                                                                              qc_folder, dpnii_file).split()
    # hicBuildMatrix.main(args)
    compute(hicBuildMatrix.main, args, 5)

    test = hm.hiCMatrix(ROOT + "small_test_matrix_parallel.h5")
    new = hm.hiCMatrix(outfile.name)

    nt.assert_equal(test.matrix.data, new.matrix.data)
    # nt.assert_equal(test.cut_intervals, new.cut_intervals)
    nt.assert_equal(len(new.cut_intervals), len(test.cut_intervals))
    cut_interval_new_ = []
    cut_interval_test_ = []
    for x in new.cut_intervals:
        cut_interval_new_.append(x[:3])
    for x in test.cut_intervals:
        cut_interval_test_.append(x[:3])

    nt.assert_equal(cut_interval_new_, cut_interval_test_)
    # print(set(os.listdir(ROOT + "QC/")))
    assert are_files_equal(ROOT + "QC/QC.log", qc_folder + "/QC.log")
    assert set(os.listdir(ROOT + "QC/")) == set(os.listdir(qc_folder))

    os.unlink(outfile.name)
    shutil.rmtree(qc_folder)


def test_build_matrix_cooler_metadata():
    outfile = NamedTemporaryFile(suffix='.cool', delete=False)
    outfile.close()
    outfile_bam = NamedTemporaryFile(suffix='.bam', delete=False)
    outfile.close()
    qc_folder = mkdtemp(prefix="testQC_")
    args = "-s {} {} --outFileName {} -bs 5000 -b {} --QCfolder {} --threads 4 --genomeAssembly dm3  \
            --restrictionSequence GATC --danglingSequence GATC -rs {}".format(sam_R1, sam_R2,
                                                                              outfile.name, outfile_bam.name,
                                                                              qc_folder, dpnii_file).split()
    # hicBuildMatrix.main(args)
    compute(hicBuildMatrix.main, args, 5)

    test = hm.hiCMatrix(ROOT + "small_test_matrix_parallel.h5")
    new = hm.hiCMatrix(outfile.name)

    nt.assert_equal(test.matrix.data, new.matrix.data)
    # nt.assert_equal(test.cut_intervals, new.cut_intervals)
    nt.assert_equal(len(new.cut_intervals), len(test.cut_intervals))
    cut_interval_new_ = []
    cut_interval_test_ = []
    for x in new.cut_intervals:
        cut_interval_new_.append(x[:3])
    for x in test.cut_intervals:
        cut_interval_test_.append(x[:3])

    nt.assert_equal(cut_interval_new_, cut_interval_test_)
    # print(set(os.listdir(ROOT + "QC/")))
    assert are_files_equal(ROOT + "QC/QC.log", qc_folder + "/QC.log")
    assert set(os.listdir(ROOT + "QC/")) == set(os.listdir(qc_folder))

    outfile_metadata = NamedTemporaryFile(suffix='.txt', delete=False)
    outfile_metadata.close()
    args = "-m {} -o {}".format(outfile.name, outfile_metadata.name).split()
    hicInfo.main(args)
    assert are_files_equal(ROOT + "hicBuildMatrix/metadata.txt", outfile_metadata.name, delta=7)

    os.unlink(outfile.name)
    shutil.rmtree(qc_folder)


def test_build_matrix_cooler_multiple():
    outfile = NamedTemporaryFile(suffix='.mcool', delete=False)
    outfile.close()
    outfile_bam = NamedTemporaryFile(suffix='.bam', delete=False)
    outfile.close()
    qc_folder = mkdtemp(prefix="testQC_")
    args = "-s {} {} --outFileName {} -bs 5000 10000 20000 -b {} --QCfolder {} --threads 4  \
            --restrictionSequence GATC --danglingSequence GATC -rs {}".format(sam_R1, sam_R2,
                                                                              outfile.name, outfile_bam.name,
                                                                              qc_folder, dpnii_file).split()
    # hicBuildMatrix.main(args)
    compute(hicBuildMatrix.main, args, 5)

    test_5000 = hm.hiCMatrix(ROOT + "hicBuildMatrix/multi_small_test_matrix.mcool::/resolutions/5000")
    test_10000 = hm.hiCMatrix(ROOT + "hicBuildMatrix/multi_small_test_matrix.mcool::/resolutions/10000")
    test_20000 = hm.hiCMatrix(ROOT + "hicBuildMatrix/multi_small_test_matrix.mcool::/resolutions/20000")

    new_5000 = hm.hiCMatrix(outfile.name + '::/resolutions/5000')
    new_10000 = hm.hiCMatrix(outfile.name + '::/resolutions/10000')
    new_20000 = hm.hiCMatrix(outfile.name + '::/resolutions/20000')

    nt.assert_equal(test_5000.matrix.data, new_5000.matrix.data)
    nt.assert_equal(test_10000.matrix.data, new_10000.matrix.data)
    nt.assert_equal(test_20000.matrix.data, new_20000.matrix.data)

    # nt.assert_equal(test.cut_intervals, new.cut_intervals)
    nt.assert_equal(len(new_5000.cut_intervals), len(test_5000.cut_intervals))
    nt.assert_equal(len(new_10000.cut_intervals), len(test_10000.cut_intervals))
    nt.assert_equal(len(new_20000.cut_intervals), len(test_20000.cut_intervals))

    cut_interval_new_ = []
    cut_interval_test_ = []
    for x in new_5000.cut_intervals:
        cut_interval_new_.append(x[:3])
    for x in test_5000.cut_intervals:
        cut_interval_test_.append(x[:3])

    nt.assert_equal(cut_interval_new_, cut_interval_test_)

    cut_interval_new_ = []
    cut_interval_test_ = []
    for x in new_10000.cut_intervals:
        cut_interval_new_.append(x[:3])
    for x in test_10000.cut_intervals:
        cut_interval_test_.append(x[:3])

    nt.assert_equal(cut_interval_new_, cut_interval_test_)

    cut_interval_new_ = []
    cut_interval_test_ = []
    for x in new_20000.cut_intervals:
        cut_interval_new_.append(x[:3])
    for x in test_20000.cut_intervals:
        cut_interval_test_.append(x[:3])

    nt.assert_equal(cut_interval_new_, cut_interval_test_)
    # print(set(os.listdir(ROOT + "QC/")))
    assert are_files_equal(ROOT + "QC/QC.log", qc_folder + "/QC.log")
    assert set(os.listdir(ROOT + "QC/")) == set(os.listdir(qc_folder))

    os.unlink(outfile.name)
    shutil.rmtree(qc_folder)


def test_build_matrix_rf():
    outfile = NamedTemporaryFile(suffix='.h5', delete=False)
    outfile.close()
    qc_folder = mkdtemp(prefix="testQC_")
    args = "-s {} {} -rs {} --outFileName {}  --QCfolder {} " \
           "--restrictionSequence GATC " \
           "--danglingSequence GATC " \
           "--minDistance 150 " \
           "--maxLibraryInsertSize 1500 --threads 4".format(sam_R1, sam_R2, dpnii_file,
                                                            outfile.name,
                                                            qc_folder).split()
    # hicBuildMatrix.main(args)
    compute(hicBuildMatrix.main, args, 5)

    test = hm.hiCMatrix(ROOT + "small_test_rf_matrix.h5")
    new = hm.hiCMatrix(outfile.name)

    nt.assert_equal(test.matrix.data, new.matrix.data)
    nt.assert_equal(test.cut_intervals, new.cut_intervals)

    print(set(os.listdir(ROOT + "QC_rc/")))
    assert are_files_equal(ROOT + "QC_rc/QC.log", qc_folder + "/QC.log")
    assert set(os.listdir(ROOT + "QC_rc/")) == set(os.listdir(qc_folder))

    os.unlink(outfile.name)
    shutil.rmtree(qc_folder)


def test_build_matrix_rf_multi():
    outfile = NamedTemporaryFile(suffix='.h5', delete=False)
    outfile.close()
    qc_folder = mkdtemp(prefix="testQC_")
    args = "-s {} {} -rs {} {} --outFileName {}  --QCfolder {} " \
           "--restrictionSequence GATC AAGCTT " \
           "--danglingSequence GATC AGCT " \
           "--minDistance 150 " \
           "--maxLibraryInsertSize 1500 --threads 4".format(sam_R1, sam_R2, dpnii_file, ROOT + 'hicFindRestSite/hindIII.bed',
                                                            outfile.name,
                                                            qc_folder).split()
    # --danglingSequence GATC AGCT --restrictionSequence GATC AAGCTT
    # hicBuildMatrix.main(args)
    compute(hicBuildMatrix.main, args, 5)

    test = hm.hiCMatrix(ROOT + "small_test_rf_matrix_multiple.h5")
    new = hm.hiCMatrix(outfile.name)

    nt.assert_equal(test.matrix.data, new.matrix.data)
    nt.assert_equal(test.cut_intervals, new.cut_intervals)

    print(set(os.listdir(ROOT + "QC_rc_multiple/")))
    assert are_files_equal(ROOT + "QC_rc_multiple/QC.log", qc_folder + "/QC.log")
    assert set(os.listdir(ROOT + "QC_rc_multiple/")) == set(os.listdir(qc_folder))

    os.unlink(outfile.name)
    shutil.rmtree(qc_folder)


@pytest.mark.xfail
def test_build_matrix_fail(capsys):
    outfile = NamedTemporaryFile(suffix='', delete=False)
    outfile.close()
    outfile_bam = NamedTemporaryFile(suffix='.bam', delete=False)
    outfile.close()
    qc_folder = mkdtemp(prefix="testQC_")
    args = "-s {} {} --outFileName {} -bs 5000 -b {} --QCfolder {} --threads 4 ".format(sam_R1, sam_R2, outfile_bam.name,
                                                                                        outfile.name,
                                                                                        qc_folder).split()
    # hicBuildMatrix.main(args)
    compute(hicBuildMatrix.main, args, 5)
