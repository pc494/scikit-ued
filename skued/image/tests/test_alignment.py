# -*- coding: utf-8 -*-
import numpy as np
from random import randint
import unittest
from skimage import data
from skimage.filters import gaussian
from skimage.transform import rotate

from .. import shift_image, align, diff_register, ialign
from .test_powder import circle_image

np.random.seed(23)

class TestDiffRegister(unittest.TestCase):

	def test_trivial_skimage_data(self):
		""" Test that the translation between two identical images is (0,0), even
		with added random noise and random masks """

		im = np.asfarray(data.camera())

		with self.subTest('No noise'):
			shift = diff_register(im, im)

			self.assertTrue(np.allclose(shift, (0,0), atol = 1))
		
		with self.subTest('With 5% noise'):
			noise1 = 0.05 * im.max() * np.random.random(size = im.shape)
			noise2 = 0.05 * im.max() * np.random.random(size = im.shape)

			shift = diff_register(im + noise1, im + noise2)
			self.assertTrue(np.allclose(shift, (0,0), atol = 1))
		
		with self.subTest('With random masks'):
			m1 = np.random.choice([True, False], size = im.shape)

			shift = diff_register(im, im, m1)
			self.assertTrue(np.allclose(shift, (0,0), atol = 1))
	
	def test_shifted_skimage_data(self):
		""" Test that translation is registered for data from scikit-image """
		random_shift = np.random.randint(low = 0, high = 10, size = (2,))

		im = np.asfarray(data.camera())
		im2 = np.asfarray(data.camera())
		im2[:] = shift_image(im2, shift = random_shift, fill_value = 0)

		# Masking the edges due to shifting
		edge_mask = np.ones_like(im, dtype = np.bool)
		edge_mask[6:-6, 6:-6] = False

		with self.subTest('No noise'):
			shift = diff_register(im, im2, edge_mask)

			self.assertTrue(np.allclose(shift, -random_shift, atol = 1))
		
		with self.subTest('With 5% noise'):
			noise1 = 0.05 * im.max() * np.random.random(size = im.shape)
			noise2 = 0.05 * im.max() * np.random.random(size = im.shape)

			shift = diff_register(im + noise1, im2 + noise2, edge_mask)
			self.assertTrue(np.allclose(shift, -random_shift, atol = 1))
		
		with self.subTest('With random mask'):
			m1 = np.random.choice([True, False], size = im.shape)

			shift = diff_register(im, im2, m1)
			self.assertTrue(np.allclose(shift, -random_shift, atol = 1))
	
	def test_side_effects(self):
		""" Test that arrays registered by diff_register are not modified """
		im1 = np.random.random(size = (32,32))
		im2 = np.random.random(size = (32,32))
		mask = np.random.choice([True, False], size = im1.shape)

		# If arrays are written to, ValueError is raised
		for arr in (im1, im2, mask):
			arr.setflags(write = False)
		
		shift = diff_register(im1, im2, mask)

class TestIAlign(unittest.TestCase):

	def test_trivial(self):
		""" Test alignment of identical images """
		aligned = tuple(ialign([data.camera() for _ in range(5)]))
		
		self.assertEqual(len(aligned), 5)
		self.assertSequenceEqual(data.camera().shape, aligned[0].shape)
		
	def test_misaligned_canned_images(self):
		""" shift images from skimage.data by entire pixels.
	   We don't expect perfect alignment."""
		original = data.camera()
		misaligned = [shift_image(original, (randint(-4, 4), randint(-4, 4))) 
					  for _ in range(5)]

		aligned = ialign(misaligned, reference = original)

		# TODO: find a better figure-of-merit for alignment
		for im in aligned:
			# edge will be filled with zeros, we ignore
			diff = np.abs(original[5:-5, 5:-5] - im[5:-5, 5:-5])

			# Want less than 1% difference
			percent_diff = np.sum(diff) / (diff.size * (original.max() - original.min()))
			self.assertLess(percent_diff, 1)

class TestShiftImage(unittest.TestCase):
	
	def test_trivial(self):
		""" Shift an array by (0,0) """
		arr = np.random.random( size = (64, 64) )
		shifted = shift_image(arr, (0,0))
		self.assertTrue(np.allclose(arr, shifted))
	
	def test_back_and_forth(self):
		""" Test shift_image in two directions """
		arr = np.random.random( size = (64, 64) )
		shifted1 = shift_image(arr, (5, -3))
		shifted2 = shift_image(shifted1, (-5, 3))
		self.assertTrue(np.allclose(arr[5:-5, 5:-5], shifted2[5:-5, 5:-5]))
	
	def test_out_of_bounds(self):
		""" Test that shifting by more than the size of an array
		returns an array full of the fill_value parameter """
		arr = np.random.random( size = (64, 64) ) + 1 # no zeros in this array
		shifted = shift_image(arr, (128, 128), fill_value = 0.0)
		self.assertTrue(np.allclose(np.zeros_like(arr), shifted))
	
	def test_fill_value(self):
		""" Test that shifted array edges are filled with the correct value """
		arr = np.random.random( size = (64, 64) )
		shifted = shift_image(arr, shift = (0, 10), fill_value = np.nan)
		self.assertTrue(np.all(np.isnan(shifted[:10, :])))
	
	def test_axes(self):
		""" Test shift_image on 3D array """
		arr = np.random.random( size = (64, 64, 8) )
		shifted = shift_image(arr, shift = (0, 10), fill_value = np.nan, axes = (1, 2))
		self.assertTrue(np.all(np.isnan(shifted[:, :10, :])))

class TestAlign(unittest.TestCase):

	def test_trivial(self):
		""" Test alignment of identical images """
		im = data.coins()[0:64, 0:64]
		aligned = align(im, reference = im)

		diff = np.abs(im - aligned)

		# Want less than 1% difference
		percent_diff = np.sum(diff) / (diff.size * (im.max() - im.min()))
		self.assertLess(percent_diff, 1)

	def test_misaligned_canned_images(self):
		""" shift images from skimage.data by entire pixels.
	   We don't expect perfect alignment."""
		original = data.camera()
		misaligned = shift_image(original, (randint(-4, 4), randint(-4, 4))) 

		aligned = align(misaligned, reference = original)

		# edge will be filled with zeros, we ignore
		diff = np.abs(original[5:-5, 5:-5] - aligned[5:-5, 5:-5])

		# Want less than 1% difference
		percent_diff = np.sum(diff) / (diff.size * (original.max() - original.min()))
		self.assertLess(percent_diff, 1)

if __name__ == '__main__':
	unittest.main()