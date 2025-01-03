# Copyright © 2023-2024 Apple Inc.

import unittest

import mlx.core as mx
import mlx_tests


class TestMetal(mlx_tests.MLXTestCase):
    @unittest.skipIf(not mx.metal.is_available(), "Metal is not available")
    def test_memory_info(self):
        old_limit = mx.metal.set_cache_limit(0)

        a = mx.zeros((4096,))
        mx.eval(a)
        del a
        self.assertEqual(mx.metal.get_cache_memory(), 0)
        self.assertEqual(mx.metal.set_cache_limit(old_limit), 0)
        self.assertEqual(mx.metal.set_cache_limit(old_limit), old_limit)

        old_limit = mx.metal.set_memory_limit(10)
        self.assertTrue(mx.metal.set_memory_limit(old_limit), 10)
        self.assertTrue(mx.metal.set_memory_limit(old_limit), old_limit)

        # Query active and peak memory
        a = mx.zeros((4096,))
        mx.eval(a)
        mx.synchronize()
        active_mem = mx.metal.get_active_memory()
        self.assertTrue(active_mem >= 4096 * 4)

        b = mx.zeros((4096,))
        mx.eval(b)
        del b
        mx.synchronize()

        new_active_mem = mx.metal.get_active_memory()
        self.assertEqual(new_active_mem, active_mem)
        peak_mem = mx.metal.get_peak_memory()
        self.assertTrue(peak_mem >= 4096 * 8)
        cache_mem = mx.metal.get_cache_memory()
        self.assertTrue(cache_mem >= 4096 * 4)

        mx.metal.clear_cache()
        self.assertEqual(mx.metal.get_cache_memory(), 0)

        mx.metal.reset_peak_memory()
        self.assertEqual(mx.metal.get_peak_memory(), 0)

        old_limit = mx.metal.set_wired_limit(1000)
        old_limit = mx.metal.set_wired_limit(0)
        self.assertEqual(old_limit, 1000)

        max_size = mx.metal.device_info()["max_recommended_working_set_size"]
        with self.assertRaises(ValueError):
            mx.metal.set_wired_limit(max_size + 10)


if __name__ == "__main__":
    unittest.main()
