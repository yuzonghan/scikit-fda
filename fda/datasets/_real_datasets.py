import numpy as np
import rdata

from ..grid import FDataGrid


def fdata_constructor(obj, attrs):
    names = obj["names"]

    return FDataGrid(data_matrix=obj["data"],
                     sample_points=obj["argvals"],
                     sample_range=obj["rangeval"],
                     dataset_label=names['main'][0],
                     axes_labels=[names['xlab'][0], names['ylab'][0]])


def functional_constructor(obj, attrs):

    name = obj['name']
    args_label = obj['args']
    values_label = obj['vals']
    target = np.array(obj['labels']).ravel()
    dataf = obj['dataf']

    sample_points_set = {a for o in dataf for a in o["args"]}

    args_init = min(sample_points_set)
    args_end = max(sample_points_set)

    sample_points = np.arange(args_init,
                              args_end + 1)

    data_matrix = np.zeros(shape=(len(dataf), len(sample_points)))

    for num_sample, o in enumerate(dataf):
        for t, x in zip(o["args"], o["vals"]):
            data_matrix[num_sample, t - args_init] = x

    return (FDataGrid(data_matrix=data_matrix,
                      sample_points=sample_points,
                      sample_range=(args_init, args_end),
                      dataset_label=name[0],
                      axes_labels=[args_label[0], values_label[0]]), target)


def fetch_cran_dataset(dataset_name, package_name, *, converter=None,
                       **kwargs):
    import skdatasets
    """
    Fetch a dataset from CRAN.

    """
    if converter is None:
        converter = rdata.conversion.SimpleConverter({
            **rdata.conversion.DEFAULT_CLASS_MAP,
            "fdata": fdata_constructor,
            "functional": functional_constructor})

    return skdatasets.cran.fetch_dataset(dataset_name, package_name,
                                         converter=converter, **kwargs)


_param_descr = """
    Args:
        return_X_y: Return only the data and target as a tuple.
"""

_phoneme_descr = """
    These data arose from a collaboration between  Andreas Buja, Werner
    Stuetzle and Martin Maechler, and it is used as an illustration in the
    paper on Penalized Discriminant Analysis by Hastie, Buja and
    Tibshirani (1995).

    The data were extracted from the TIMIT database (TIMIT
    Acoustic-Phonetic Continuous Speech Corpus, NTIS, US Dept of Commerce)
    which is a widely used resource for research in speech recognition.  A
    dataset was formed by selecting five phonemes for
    classification based on digitized speech from this database.  The
    phonemes are transcribed as follows: "sh" as in "she", "dcl" as in
    "dark", "iy" as the vowel in "she", "aa" as the vowel in "dark", and
    "ao" as the first vowel in "water".  From continuous speech of 50 male
    speakers, 4509 speech frames of 32 msec duration were selected,
    approximately 2 examples of each phoneme from each speaker.  Each
    speech frame is represented by 512 samples at a 16kHz sampling rate,
    and each frame represents one of the above five phonemes.  The
    breakdown of the 4509 speech frames into phoneme frequencies is as
    follows:

    === ==== === ==== ===
     aa   ao dcl   iy  sh
    === ==== === ==== ===
    695 1022 757 1163 872
    === ==== === ==== ===

    From each speech frame, a log-periodogram was computed, which is one of
    several widely used methods for casting speech data in a form suitable
    for speech recognition.  Thus the data used in what follows consist of
    4509 log-periodograms of length 256, with known class (phoneme)
    memberships.

    The data contain curves sampled at 256 points, a response
    variable, and a column labelled "speaker" identifying the
    diffferent speakers.

    Hastie, Trevor; Buja, Andreas; Tibshirani, Robert. Penalized Discriminant
    Analysis. Ann. Statist. 23 (1995), no. 1, 73--102.
    doi:10.1214/aos/1176324456. https://projecteuclid.org/euclid.aos/1176324456
    """


def fetch_phoneme(return_X_y: bool=False):
    """
    Load the phoneme dataset.

    The data is obtained from the R package 'ElemStatLearn', which takes it
    from the dataset in `https://web.stanford.edu/~hastie/ElemStatLearn/`.

    """
    DESCR = _phoneme_descr

    raw_dataset = fetch_cran_dataset(
        "phoneme", "ElemStatLearn",
        version="0.1-7.1")

    data = raw_dataset["phoneme"]

    curve_data = data.iloc[:, 0:256]
    sound = data["g"].values
    speaker = data["speaker"].values

    curves = FDataGrid(data_matrix=curve_data.values,
                       sample_points=range(0, 256),
                       dataset_label="Phoneme",
                       axes_labels=["frequency", "log-periodogram"])

    if return_X_y:
        return curves, sound
    else:
        return {"data": curves,
                "target": sound.codes,
                "target_names": sound.categories.tolist(),
                "target_feature_names": ["sound"],
                "meta": np.array([speaker]).T,
                "meta_feature_names": ["speaker"],
                "DESCR": DESCR}


if hasattr(fetch_phoneme, "__doc__"):  # docstrings can be stripped off
    fetch_phoneme.__doc__ += _phoneme_descr + _param_descr

_growth_descr = """
    The Berkeley Growth Study (Tuddenham and Snyder, 1954) recorded the
    heights of 54 girls and 39 boys between the ages of 1 and 18 years.
    Heights were measured at 31 ages for each child, and the standard
    error of these measurements was about 3mm, tending to be larger in
    early childhood and lower in later years.

    Tuddenham, R. D., and Snyder, M. M. (1954) "Physical growth of California
    boys and girls from birth to age 18", University of California
    Publications in Child Development, 1, 183-364.
"""


def fetch_growth(return_X_y: bool=False):
    """
    Load the Berkeley Growth Study dataset.

    The data is obtained from the R package 'fda', which takes it from the
    Berkeley Growth Study.

    """
    DESCR = _growth_descr

    raw_dataset = fetch_cran_dataset(
        "growth", "fda",
        version="2.4.7")

    data = raw_dataset["growth"]

    ages = data["age"]
    females = data["hgtf"].T
    males = data["hgtm"].T

    curves = FDataGrid(data_matrix=np.concatenate((males, females), axis=0),
                       sample_points=ages,
                       dataset_label="Berkeley Growth Study",
                       axes_labels=["age", "height"])

    sex = np.array([0] * males.shape[0] + [1] * females.shape[0])

    if return_X_y:
        return curves, sex
    else:
        return {"data": curves,
                "target": sex,
                "target_names": ["male", "female"],
                "target_feature_names": ["sex"],
                "DESCR": DESCR}


if hasattr(fetch_growth, "__doc__"):  # docstrings can be stripped off
    fetch_growth.__doc__ += _growth_descr + _param_descr

_tecator_descr = """
    This is the Tecator data set: The task is to predict the fat content of a
    meat sample on the basis of its near infrared absorbance spectrum.

    1. Statement of permission from Tecator (the original data source)

    These data are recorded on a Tecator Infratec Food and Feed Analyzer
    working in the wavelength range 850 - 1050 nm by the Near Infrared
    Transmission (NIT) principle. Each sample contains finely chopped pure
    meat with different moisture, fat and protein contents.

    If results from these data are used in a publication we want you to
    mention the instrument and company name (Tecator) in the publication.
    In addition, please send a preprint of your article to

        Karin Thente, Tecator AB,
        Box 70, S-263 21 Hoganas, Sweden

    The data are available in the public domain with no responsability from
    the original data source. The data can be redistributed as long as this
    permission note is attached.

    For more information about the instrument - call Perstorp Analytical's
    representative in your area.


    2. Description of the data

    For each meat sample the data consists of a 100 channel spectrum of
    absorbances and the contents of moisture (water), fat and protein.
    The absorbance is -log10 of the transmittance
    measured by the spectrometer. The three contents, measured in percent,
    are determined by analytic chemistry.

    There are 215 samples.
"""


def fetch_tecator(return_X_y: bool=False):
    """
    Load the Tecator dataset.

    The data is obtained from the R package 'fda.usc', which takes it from
    http://lib.stat.cmu.edu/datasets/tecator.

    """
    DESCR = _tecator_descr

    raw_dataset = fetch_cran_dataset(
        "tecator", "fda.usc",
        version="1.3.0")

    data = raw_dataset["tecator"]

    curves = data['absorp.fdata']
    target = data['y'].values
    target_feature_names = data['y'].columns.values.tolist()

    if return_X_y:
        return curves, target
    else:
        return {"data": curves,
                "target": target,
                "target_feature_names": target_feature_names,
                "DESCR": DESCR}


if hasattr(fetch_tecator, "__doc__"):  # docstrings can be stripped off
    fetch_tecator.__doc__ += _tecator_descr + _param_descr

_medflies_descr = """
    The data set medfly1000.dat  consists of number of eggs laid daily for
    each of 1000 medflies (Mediterranean fruit flies, Ceratitis capitata)
    until time of death. Data were obtained in Dr. Carey's laboratory.
    A description of the experiment which was done by Professor Carey of
    UC Davis and collaborators in a medfly rearing facility in
    Mexico is in Carey et al.(1998) below. The main questions are to
    explore the relationship of age patterns of fecundity to mortality,
    longevity and lifetime reproduction.

    A basic finding was that individual mortality is associated with the
    time-dynamics of the egg-laying trajectory. An approximate parametric model
    of the egg laying process was developed and used in Müller et al. (2001).
    Nonparametric approaches which extend principal component analysis for
    curve data to the situation when covariates are present have been
    developed and discussed in  Chiou, Müller and Wang (2003)
    and Chiou et al. (2003).

    Carey, J.R., Liedo, P., Müller, H.G., Wang, J.L., Chiou, J.M. (1998).
        Relationship of age patterns of fecundity to mortality, longevity,
        and lifetime reproduction in a large cohort of Mediterranean fruit
        fly females. J. of Gerontology --Biological Sciences 53, 245-251.
    Chiou, J.M., Müller, H.G., Wang, J.L. (2003). Functional quasi-likelihood
        regression models with smooth random effects. J. Royal Statist. Soc.
        B65, 405-423. (PDF)
    Chiou, J.M., Müller, H.G., Wang, J.L., Carey, J.R. (2003). A functional
        multiplicative effects model for longitudinal data, with application to
        reproductive histories of female medflies. Statistica Sinica 13,
        1119-1133. (PDF)
    Chiou, J.M., Müller, H.G., Wang, J.L. (2004).Functional response models.
        Statistica Sinica 14,675-693. (PDF)
"""


def fetch_medflies(return_X_y: bool=False):
    """
    Load the Medflies dataset, where the flies are separated in two classes
    according to their longevity.

    The data is obtained from the R package 'ddalpha', which its a modification
    of the dataset in http://www.stat.ucdavis.edu/~wang/data/medfly1000.htm.

    """
    DESCR = _medflies_descr

    raw_dataset = fetch_cran_dataset(
        "medflies", "ddalpha",
        version="1.3.4")

    data = raw_dataset["medflies"]

    curves = data[0]

    unique = np.unique(data[1], return_inverse=True)
    target_names = [unique[0][1], unique[0][0]]
    target = 1 - unique[1]
    target_feature_names = ["lifetime"]

    if return_X_y:
        return curves, target
    else:
        return {"data": curves,
                "target": target,
                "target_names": target_names,
                "target_feature_names": target_feature_names,
                "DESCR": DESCR}


if hasattr(fetch_medflies, "__doc__"):  # docstrings can be stripped off
    fetch_medflies.__doc__ += _medflies_descr + _param_descr
