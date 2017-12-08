from trainer import Trainer
import numpy as np


class SupervisedTrainer(Trainer):
    def __init__(
            self,
            model,
            loss,
            optimizer,
            epochs,
            batch_size,
            holdout_percent=0.0,
            data_preprocessor=lambda x: x,
            label_preprocessor=lambda x: x):

        super(SupervisedTrainer, self).__init__(
            epochs,
            batch_size)

        self.label_preprocessor = label_preprocessor
        self.data_preprocessor = data_preprocessor
        self.holdout_percent = holdout_percent
        self.optimizer = optimizer(model)
        self.loss = loss
        self.model = model

    def train(self, data):
        import torch
        from torch.autograd import Variable

        model = self.model.cuda()
        loss = self.loss.cuda()

        data, labels = data['data'], data['labels']

        test_size = int(self.holdout_percent * len(data))
        test_data, test_labels = data[:test_size], labels[:test_size]
        data, labels = data[test_size:], labels[test_size:]

        if data is labels:
            # this is an autoencoder scenario, so let's saved on memory
            data = data.astype(np.float32)
            test_data = data.astype(np.float32)
            labels = data
            test_labels = labels
        else:
            data = data.astype(np.float32)
            test_data = test_data.astype(np.float32)
            labels = labels.astype(np.float32)
            test_labels = test_labels.astype(np.float32)

        def batch(d, l, test=False):
            d = self.data_preprocessor(d).astype(np.float32)
            l = self.label_preprocessor(l).astype(np.float32)
            inp = torch.from_numpy(d)
            inp = inp.cuda()
            inp_v = Variable(inp, volatile=test)
            output = model(inp_v)

            labels_t = torch.from_numpy(l)
            labels_t = labels_t.cuda()
            labels_v = Variable(labels_t)

            error = loss(output, labels_v)

            if not test:
                error.backward()
                self.optimizer.step()

            return error.data[0]

        for epoch in xrange(self.epochs):
            for i in xrange(0, len(data), self.batch_size):

                model.zero_grad()

                # training batch
                minibatch_slice = slice(i, i + self.batch_size)
                minibatch_data = data[minibatch_slice]
                minibatch_labels = labels[minibatch_slice]

                e = training_error = batch(
                    minibatch_data, minibatch_labels, test=False)

                # test batch
                if test_size:
                    indices = np.random.randint(0, test_size, self.batch_size)
                    test_batch_data = test_data[indices, ...]
                    test_batch_labels = test_labels[indices, ...]

                    te = test_error = batch(
                        test_batch_data, test_batch_labels, test=True)
                else:
                    te = 'n/a'

                if i % 10 == 0:
                    print 'Epoch {epoch}, batch {i}, train error {e}, test error {te}'.format(
                        **locals())

        return model
