"""
Original code from Denny Britz
http://www.wildml.com/2015/12/implementing-a-cnn-for-text-classification-in-tensorflow/
"""

import tensorflow as tf
import numpy as np
import os
import time
import datetime
from cnn import CNN
from tensorflow.contrib import learn


class train():
    def __init__(self):
        # Flags
        # ==================================================
        # Data loading params
        tf.flags.DEFINE_float("dev_sample_percentage", .1, "Percentage of the training data to use for validation")
        tf.flags.DEFINE_string("coherent_data_file", "./data/txt/coherent_sentences.txt", "Data source for the coherent data.")
        tf.flags.DEFINE_string("incoherent_data_file", "./data/txt/incoherent_sentences_arg2_diff_sense.txt", "Data source for the incoherent data.")

        # Model Hyperparameters
        tf.flags.DEFINE_string("word2vec", "./data/model/GoogleNews-vectors-negative300.bin", "Word2vec file with pre-trained embeddings (default: None)")
        tf.flags.DEFINE_integer("embedding_dim", 300, "Dimensionality of character embedding (default: 300, to match GoogleNews embeddings)")
        tf.flags.DEFINE_string("filter_sizes", "3", "Comma-separated filter sizes (default: '3,4,5')")
        tf.flags.DEFINE_integer("num_filters", 16, "Number of filters per filter size (default: 128)")
        tf.flags.DEFINE_float("dropout_keep_prob", 0.5, "Dropout keep probability (default: 0.5)")
        tf.flags.DEFINE_float("l2_reg_lambda", 0.1, "L2 regularization lambda (default: 0.0)")

        # Training parameters
        tf.flags.DEFINE_integer("batch_size", 128, "Batch Size (default: 64)")
        tf.flags.DEFINE_integer("num_epochs", 200, "Number of training epochs (default: 200)")
        tf.flags.DEFINE_integer("evaluate_every", 100, "Evaluate model on dev set after this many steps (default: 100)")
        tf.flags.DEFINE_integer("checkpoint_every", 100, "Save model after this many steps (default: 100)")
        tf.flags.DEFINE_integer("num_checkpoints", 5, "Number of checkpoints to store (default: 5)")
        tf.flags.DEFINE_integer("learning_rate", 1e-3, "Learning rate")

        # Misc Parameters
        tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
        tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")

        self.FLAGS = tf.flags.FLAGS
        self.FLAGS._parse_flags()


    def prepare_data(self):
        # Data Preparation
        # ==================================================

        # Load data
        coherent_sentences = list(open(self.FLAGS.coherent_data_file, 'r').readlines())
        coherent_sentences = [c.strip() for c in coherent_sentences]
        incoherent_sentences = list(open(self.FLAGS.incoherent_data_file, 'r').readlines())
        incoherent_sentences = [c.strip() for c in incoherent_sentences]
        x_text = coherent_sentences + incoherent_sentences

        # Build vocabulary
        max_document_length = max([len(x.split(" ")) for x in x_text])
        self.vocab_processor = learn.preprocessing.VocabularyProcessor(max_document_length)

        x = np.array(list(self.vocab_processor.fit_transform(x_text)))

        # Labels: [1, 0]: coherent, [0, 1]: incoherent
        coherent_labels = [[0, 1] for _ in coherent_sentences]
        incoherent_labels = [[1, 0] for _ in incoherent_sentences]
        y = np.concatenate([coherent_labels, incoherent_labels])

        # Shuffle Data
        np.random.seed(10)
        shuffle_indices = np.random.permutation(np.arange(len(y)))
        x_shuffled = x[shuffle_indices]
        y_shuffled = y[shuffle_indices]

        # Split train/test set
        dev_sample_index = -1 * int(self.FLAGS.dev_sample_percentage * float(len(y)))
        self.x_train, self.x_dev = x_shuffled[:dev_sample_index], x_shuffled[dev_sample_index:]
        self.y_train, self.y_dev = y_shuffled[:dev_sample_index], y_shuffled[dev_sample_index:]

    def init_cnn(self):
        FLAGS = self.FLAGS
        self.cnn = CNN(
            sequence_length=self.x_train.shape[1],
            num_classes=self.y_train.shape[1],
            vocab_size=len(self.vocab_processor.vocabulary_),
            embedding_size=FLAGS.embedding_dim,
            filter_sizes=list(map(int, FLAGS.filter_sizes.split(","))),
            num_filters=FLAGS.num_filters,
            l2_reg_lambda=FLAGS.l2_reg_lambda)

    def define_training_procedure(self):
        # Define Training procedure
        self.global_step = tf.Variable(0, name="global_step", trainable=False)
        optimizer = tf.train.AdamOptimizer(self.FLAGS.learning_rate)
        self.grads_and_vars = optimizer.compute_gradients(self.cnn.loss)
        self.train_op = optimizer.apply_gradients(self.grads_and_vars, global_step=self.global_step)


    def track_gradient_values_and_sparcity(self):
        # Keep track of gradient values and sparsity (optional)
        grad_summaries = []
        for g, v in self.grads_and_vars:
            if g is not None:
                grad_hist_summary = tf.summary.histogram("{}/grad/hist".format(v.name), g)
                sparsity_summary = tf.summary.scalar("{}/grad/sparsity".format(v.name), tf.nn.zero_fraction(g))
                grad_summaries.append(grad_hist_summary)
                grad_summaries.append(sparsity_summary)
        return tf.summary.merge(grad_summaries)

    def start(self):
        # Training
        # ==================================================
        FLAGS = self.FLAGS
        with tf.Graph().as_default():
            session_conf = tf.ConfigProto(
                allow_soft_placement=FLAGS.allow_soft_placement,
                log_device_placement=FLAGS.log_device_placement)
            self.sess = tf.Session(config=session_conf)
            with self.sess.as_default():
                self.init_cnn()
                self.define_training_procedure()
                grad_summaries_merged = self.track_gradient_values_and_sparcity()

                # Output directory for models and summaries
                timestamp = str(int(time.time()))
                out_dir = os.path.abspath(os.path.join(os.path.curdir, "runs", timestamp))
                print("Writing to {}\n".format(out_dir))

                # Summaries for loss and accuracy
                loss_summary = tf.summary.scalar("loss", self.cnn.loss)
                acc_summary = tf.summary.scalar("accuracy", self.cnn.accuracy)

                # Train Summaries
                self.train_summary_op = tf.summary.merge([loss_summary, acc_summary, grad_summaries_merged])
                train_summary_dir = os.path.join(out_dir, "summaries", "train")
                self.train_summary_writer = tf.summary.FileWriter(train_summary_dir, self.sess.graph)

                # Dev summaries
                self.dev_summary_op = tf.summary.merge([loss_summary, acc_summary])
                dev_summary_dir = os.path.join(out_dir, "summaries", "dev")
                self.dev_summary_writer = tf.summary.FileWriter(dev_summary_dir, self.sess.graph)

                # Checkpoint directory. Tensorflow assumes this directory already exists so we need to create it
                checkpoint_dir = os.path.abspath(os.path.join(out_dir, "checkpoints"))
                checkpoint_prefix = os.path.join(checkpoint_dir, "model")
                if not os.path.exists(checkpoint_dir):
                    os.makedirs(checkpoint_dir)
                saver = tf.train.Saver(tf.global_variables(), max_to_keep=FLAGS.num_checkpoints)

                # Write vocabulary
                self.vocab_processor.save(os.path.join(out_dir, "vocab"))

                # Initialize all variables
                self.sess.run(tf.global_variables_initializer())

                if FLAGS.word2vec:
                    self.enable_word_to_vec_embedding()

                # Generate batches
                batches = self.batch_iter(
                    list(zip(self.x_train, self.y_train)), FLAGS.batch_size, FLAGS.num_epochs)

                # Training loop. For each batch...
                best_dev_acc = 0
                best_dev_step = 0
                for batch in batches:
                    x_batch, y_batch = zip(*batch)
                    self.train_step(x_batch, y_batch)
                    current_step = tf.train.global_step(self.sess, self.global_step)
                    if current_step % FLAGS.evaluate_every == 0:
                        print("\nEvaluation:")
                        best_dev_acc, best_dev_step = self.dev_step(self.x_dev, self.y_dev, best_dev_acc, best_dev_step,
                                                                    writer=self.dev_summary_writer)
                        print("")
                    if current_step % FLAGS.checkpoint_every == 0:
                        path = saver.save(self.sess, checkpoint_prefix, global_step=current_step)
                        print("Saved model checkpoint to {}\n".format(path))

    def train_step(self, x_batch, y_batch):
        """
        A single training step
        """
        cnn = self.cnn

        FLAGS = self.FLAGS

        feed_dict = {
            cnn.input_x: x_batch,
            cnn.input_y: y_batch,
            cnn.dropout_keep_prob: FLAGS.dropout_keep_prob
        }
        _, step, summaries, loss, accuracy = self.sess.run(
            [self.train_op, self.global_step, self.train_summary_op, cnn.loss, cnn.accuracy],
            feed_dict)
        time_str = datetime.datetime.now().isoformat()
        # print("{}: step {}, loss {:g}, acc {:g}".format(time_str, step, loss, accuracy))
        self.train_summary_writer.add_summary(summaries, step)


    def dev_step(self, x_batch, y_batch, best_dev_acc, best_dev_step, writer=None):
        """
        Evaluates model on a dev set
        """
        cnn = self.cnn
        FLAGS = self.FLAGS

        feed_dict = {
            cnn.input_x: x_batch,
            cnn.input_y: y_batch,
            cnn.dropout_keep_prob: 1.0
        }
        step, summaries, loss, accuracy = self.sess.run(
            [self.global_step, self.dev_summary_op, cnn.loss, cnn.accuracy],
            feed_dict)
        time_str = datetime.datetime.now().isoformat()
        if accuracy > best_dev_acc:
            best_dev_acc = accuracy
            best_dev_step = step
        print("{}: step {}, loss {:g}, acc {:g}".format(time_str, step, loss, accuracy))
        print("Best accuracy: {:g} at step {}".format(best_dev_acc, best_dev_step))
        if writer:
            writer.add_summary(summaries, step)
        return best_dev_acc, best_dev_step


    def batch_iter(self, data, batch_size, num_epochs, shuffle=True):
        """
        Generates a batch iterator for a dataset.
        """
        data = np.array(data)
        data_size = len(data)
        num_batches_per_epoch = int((len(data) - 1) / batch_size) + 1
        for epoch in range(num_epochs):
            # Shuffle the data at each epoch
            if shuffle:
                shuffle_indices = np.random.permutation(np.arange(data_size))
                shuffled_data = data[shuffle_indices]
            else:
                shuffled_data = data
            for batch_num in range(num_batches_per_epoch):
                start_index = batch_num * batch_size
                end_index = min((batch_num + 1) * batch_size, data_size)
                yield shuffled_data[start_index:end_index]

    def enable_word_to_vec_embedding(self):

        FLAGS = self.FLAGS
        # initial matrix with random uniform
        initW = np.random.uniform(-0.25, 0.25, (len(self.vocab_processor.vocabulary_), FLAGS.embedding_dim))
        # load any vectors from the word2vec
        print("Load word2vec file {}\n".format(FLAGS.word2vec))
        with open(FLAGS.word2vec, "rb") as f:
            header = f.readline()
            vocab_size, layer1_size = map(int, header.split())
            binary_len = np.dtype('float32').itemsize * layer1_size
            for line in xrange(vocab_size):
                word = []
                while True:
                    ch = f.read(1)
                    if ch == ' ':
                        word = ''.join(word)
                        break
                    if ch != '\n':
                        word.append(ch)
                idx = self.vocab_processor.vocabulary_.get(word)
                if idx != 0:
                    initW[idx] = np.fromstring(f.read(binary_len), dtype='float32')
                else:
                    f.read(binary_len)

        self.sess.run(self.cnn.W.assign(initW))


if __name__ == '__main__':

    training = train()
    print("\nParameters:")
    for attr, value in sorted(training.FLAGS.__flags.items()):
        print("{}={}".format(attr.upper(), value))
    print("")

    training.prepare_data()
    print("Vocabulary Size: {:d}".format(len(training.vocab_processor.vocabulary_)))
    print("Train/Dev split: {:d}/{:d}".format(len(training.y_train), len(training.y_dev)))

    training.start()

