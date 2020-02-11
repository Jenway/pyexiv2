# -*- coding: utf-8 -*-
import psutil

from .common import *
from . import test_func


@check_md5
def test_memory_leak_when_reading():
    p = psutil.Process(os.getpid())
    m0 = p.memory_info().rss
    for _ in range(1000):
        test_func.test_read_exif()
        test_func.test_read_iptc()
        test_func.test_read_xmp()
        test_func.test_read_raw_xmp()
    m1 = p.memory_info().rss
    delta = (m1 - m0) / 1024
    assert delta < 1024, 'Memory grew by {}KB, possibly due to the memory leak.'.format(delta)
    # On my machine, if img.close() hasn't been called, the memory will increase by at least 100M.


def test_memory_leak_when_writing():
    p = psutil.Process(os.getpid())
    m0 = p.memory_info().rss
    for _ in range(1000):
        test_func.test_modify_exif()
        test_func.test_modify_iptc()
        test_func.test_modify_xmp()
    m1 = p.memory_info().rss
    delta = (m1 - m0) / 1024
    assert delta < 1024, 'Memory grew by {}KB, possibly due to the memory leak.'.format(delta)


def test_stack_overflow():
    with Image(path) as img:
        dict1 = {'Exif.Image.ImageDescription': '(test_stack_overflow)' * 1000,
                'Exif.Image.Artist': '0123456789 hello!' * 1000}
        for _ in range(10):
            img.modify_exif(dict1)
            dict2 = img.read_exif()
            for k, v in dict1.items():
                assert dict2.get(k, '') == v


def test_transmit_various_characters():
    """
    Test whether various characters can be transmitted correctly between Python and C++ API.
    Even if a value is correctly transmitted, it does not mean that it will be successfully saved by C++ API.
    """
    import string
    values = (string.digits * 5,
                string.ascii_letters * 5,
                string.punctuation * 5,
                string.whitespace * 5,
                'test-中文-' * 5,
                )
    with Image(path) as img:
        for v in values:
            img.modify_exif({'Exif.Image.ImageDescription': v})
            assert img.read_exif().get('Exif.Image.ImageDescription') == v

            img.modify_iptc({'Iptc.Application2.ObjectName': v})
            assert img.read_iptc().get('Iptc.Application2.ObjectName') == v

            # A known problem: XMP text does not support \v \f
            _v = v.replace('\v', ' ').replace('\f', ' ')
            img.modify_xmp({'Xmp.MicrosoftPhoto.LensModel': _v})
            assert img.read_xmp().get('Xmp.MicrosoftPhoto.LensModel') == _v


@check_md5
def _test_recovery_exif():
    """ Test whether pyexiv2 can delete metadata and recover it completely. """
    with Image(path) as img:
        original_dict = img.read_exif()
        img.clear_exif()
        img.modify_exif(original_dict)
        new_dict = img.read_exif()
        for key in original_dict.keys():
            for key in original_dict.keys():
                assert original_dict[key] == new_dict.get(key), "{} didn't recover".format(key)
