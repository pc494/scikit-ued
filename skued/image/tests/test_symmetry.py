# -*- coding: utf-8 -*-
import numpy as np
from .. import nfold
import unittest
from warnings import catch_warnings, simplefilter

np.random.seed(23)

class TestNFoldSymmetry(unittest.TestCase):

    def test_trivial(self):
        """ Test nfold_symmetry averaging on trivial array """
        im = np.zeros( (256, 256) )
        rot = nfold(im, mod = 3)
        self.assertTrue(np.allclose(rot, im))

    def test_valid_mod(self):
        """ Test the the N-fold symmetry argument is valid """
        im = np.empty( (128, 128) )
        with self.assertRaises(ValueError):
            nfold(im, mod = 1.7)
    
    def test_mask(self):
        """ Test that nfold_symmetry() works correctly with a mask """
        im = np.zeros((128, 128), dtype = np.int)
        mask = np.zeros_like(im, dtype = np.bool)

        im[0:20] = 1
        mask[0:20] = True
        
        rot = nfold(im, mod = 2, mask = mask)
        self.assertTrue(np.allclose(rot, np.zeros_like(rot)))
    
    def test_no_side_effects(self):
        """ Test that nfold() does not modify the input image and mask """
        im = np.empty((128, 128), dtype = np.float)
        mask = np.zeros_like(im, dtype = np.bool)

        im.setflags(write = False)
        mask.setflags(write = False)

        rot = nfold(im, center = (67, 93),mod = 3, mask = mask)
    
    def test_fill_value(self):
        """ Test that the fill_value parameter of nfold() is working correctly """
        im = 1000*np.random.random(size = (256, 256))
        mask = np.random.choice([True, False], size = im.shape)

        with self.subTest('fill_value = np.nan'):
            with catch_warnings():
                simplefilter('ignore')
                rot = nfold(im, center = (100, 150), mod = 5, mask = mask, fill_value = np.nan)

            self.assertTrue(np.any(np.isnan(rot)))

        with self.subTest('fill_value = 0.0'):
            with catch_warnings():
                simplefilter('ignore')
                rot = nfold(im, center = (100, 150), mod = 5, mask = mask, fill_value = 0.0)

            self.assertFalse(np.any(np.isnan(rot)))
    
    def test_output_range(self):
        """ Test that nfold() does not modify the value range """
        im = 1000*np.random.random(size = (256, 256))
        mask = np.random.choice([True, False], size = im.shape)

        with catch_warnings():
            simplefilter('ignore')
            rot = nfold(im, center = (100, 150), mod = 5, mask = mask)

        self.assertLessEqual(rot.max(), im.max())
        # In the case of a mask that overlaps with itself when rotated,
        # the average will be zero due to nan_to_num
        self.assertGreaterEqual(rot.min(), min(im.min(), 0))
    
    def test_mod_1(self):
        """ Test that nfold(mod = 1) returns an unchanged image, except
        perhaps for a cast to float """
        im = 1000*np.random.random(size = (256, 256))
        rot = nfold(im, mod = 1)
        self.assertTrue(np.allclose(im, rot))


if __name__ == '__main__':
    unittest.main()