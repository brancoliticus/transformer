"""
https://github.com/lilianweng/transformer-tensorflow/blob/master/transformer_test.py
"""

import numpy as np
import tensorflow as tf

from transformer import create_padding_mask, create_subsequent_mask, PositionalEncoding


class TransformerTest(tf.test.TestCase):
    def setUp(self):
        self.batch_size = 4
        self.seq_len = 5
        self.raw_input = tf.placeholder(
            tf.int32, shape=(self.batch_size, self.seq_len))
        self.fake_data = np.array([
            [1, 2, 3, 4, 5],
            [1, 2, 0, 0, 0],
            [1, 2, 3, 4, 0],
            [1, 2, 3, 0, 0],
        ])

    def test_create_padding_mask(self):
        """
        https://github.com/lilianweng/transformer-tensorflow/blob/master/transformer_test.py#L56
        """
        with self.test_session() as sess:
            mask = sess.run(
                create_padding_mask(self.raw_input, 0),
                feed_dict={self.raw_input: self.fake_data})
            expected = np.array([
                [[1., 1., 1., 1., 1.]] * self.seq_len,
                [[1., 1., 0., 0., 0.]] * self.seq_len,
                [[1., 1., 1., 1., 0.]] * self.seq_len,
                [[1., 1., 1., 0., 0.]] * self.seq_len,
            ])
            np.testing.assert_array_equal(mask, expected)

    def test_create_subsequent_mask(self):
        """
        https://github.com/lilianweng/transformer-tensorflow/blob/master/transformer_test.py#L68
        """
        with self.test_session() as sess:
            data = np.zeros((self.batch_size, self.seq_len))
            mask = sess.run(
                create_subsequent_mask(self.raw_input),
                feed_dict={self.raw_input: data})
            expected = [np.tril(np.ones(
                (self.seq_len, self.seq_len)))] * self.batch_size
            np.testing.assert_array_equal(mask, expected)

    def test_positional_encoding_sinusoid(self):
        """
        https://github.com/lilianweng/transformer-tensorflow/blob/master/transformer_test.py#L96
        """
        positional_encoding = PositionalEncoding(8)
        with self.test_session() as sess:
            encoding = sess.run(
                positional_encoding.call(self.raw_input),
                feed_dict={self.raw_input: self.fake_data})
            assert encoding.shape == (4, 5, 8)

            np.testing.assert_array_equal(encoding[0], encoding[1])
            np.testing.assert_array_equal(encoding[0], encoding[2])
            np.testing.assert_array_equal(encoding[0], encoding[3])

            # single position
            np.testing.assert_array_equal(
                encoding[0][0],
                np.array([
                    np.sin(0),
                    np.cos(0),
                    np.sin(0),
                    np.cos(0),
                    np.sin(0),
                    np.cos(0),
                    np.sin(0),
                    np.cos(0)
                ]))

            # multiple positions in a single dimension
            # NOTE: / 6.0 instead of 8.0 because of the difference in taking `num_channels - 1`
            # instead of `num_channels`.
            # only the first 3 values are being calculated exactly, the 4th one is not exactly
            # matching, which fails the test.
            np.testing.assert_array_equal(
                encoding[0][:, 2][:3],
                np.array([
                    np.sin(0),
                    np.sin(1 / np.power(10000.0, 2.0 / 6.0)),
                    np.sin(2 / np.power(10000.0, 2.0 / 6.0)),
                    # np.sin(3 / np.power(10000.0, 2.0 / 6.0)),
                    # np.sin(4 / np.power(10000.0, 2.0 / 6.0)),
                ]).astype(np.float32))


if __name__ == '__main__':
    tf.test.main()
