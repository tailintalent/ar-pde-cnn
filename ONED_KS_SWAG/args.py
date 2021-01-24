import argparse
import torch
import json
import random
from pprint import pprint
import time
import os, sys
sys.path.append(os.path.join(os.path.dirname("__file__"), '..', '..'))
from plasma.ar_pde_cnn.ONED_KS_SWAG.utils.utils import mkdirs


# always uses cuda if avaliable

class Parser(argparse.ArgumentParser):
    def __init__(self):
        super(Parser, self).__init__(description='Physics Constrained Auto-regressive Dense Encoder-Decoder')
        self.add_argument('--exp-name', type=str, default='swag', help='experiment name')
        self.add_argument('--exp-dir', type=str, default="./experiments", help='directory to save experiments')       

        # model      
        self.add_argument('--blocks', nargs="*", type=int, default=[4], help='list of # nodes in each hidden layer of encoder')
        self.add_argument('--growth-rate', type=int, default=4, help='number of output feature maps of each conv layer within each dense block')
        self.add_argument('--init-features', type=int, default=32, help='number of initial features after the first conv layer')        
        self.add_argument('--drop-rate', type=float, default=0., help='dropout rate')
        self.add_argument('--bn-size', type=int, default=8, help='bottleneck size: bn_size * growth_rate')
        self.add_argument('--bottleneck', action='store_true', default=False, help='enables bottleneck design in the dense blocks')
        self.add_argument('--dt', type=float, default=0.1, help='discrete time step')

        # data
        self.add_argument('--data-dir', type=str, default="./solver/validation_data", help='directory to testing data')
        self.add_argument('--ntrain', type=int, default=2560, help="number of training data")
        self.add_argument('--ntest', type=int, default=10, help="number of test data")
        self.add_argument('--noise-std', type=float, default=0.00, help='relative noise std')
        
        ## more details on dataset
        self.add_argument('--nic', type=int, default=2, help="number of input channels")
        self.add_argument('--noc', type=int, default=1, help="number of output channels")
        self.add_argument('--nel', type=int, default=96, help="number of elements/ collocation points")
        
        # training
        self.add_argument('--epoch-start', type=int, default=0, help='epoch to start at, will load pre-trained network')
        self.add_argument('--epochs', type=int, default=200, help='number of epochs to train')
        self.add_argument('--lr', type=float, default=0.001, help='ADAM learning rate')
        self.add_argument('--lr-beta', type=float, default=0.001, help='ADAM learning rate of output noise')
        self.add_argument('--batch-size', type=int, default=256, help='batch size for training')
        self.add_argument('--test-batch-size', type=int, default=5, help='batch size for testing')
        self.add_argument('--seed', type=int, default=12345, help='manual seed used in Tensor')

        # swag
        self.add_argument('--swag-start', type=int, default=101, help='epoch to start swag sampling')
        self.add_argument('--swag-freq', type=int, default=1, help='epoch frequency to sample postrior weights')
        self.add_argument('--swag-lr', type=float, default=1e-10, help='ADAM learning rate during swag sampling')
        self.add_argument('--swag-lr-beta', type=float, default=1e-6, help='ADAM learning rate of output noise during swag sampling')
        self.add_argument('--swag-max', type=int, default=10, help='Max number of models to store in discrepancy matrix')

        # logging
        self.add_argument('--plot-freq', type=int, default=10, help='how many epochs to wait before plotting test output')
        self.add_argument('--ckpt-freq', type=int, default=10, help='how many epochs to wait before saving model')
        self.add_argument('--notes', type=str, default='')

    def parse(self, dirs=True):
        '''
        Parse program arguements
        Args:
            dirs (boolean): True to make file directories for predictions and models
        '''
        args = self.parse_args()
        
        args.run_dir = args.exp_dir + '/' + args.exp_name \
            + '/ntrain{}_batch{}_lr{}_nic{}'.format(
                args.ntrain, args.batch_size, args.lr, args.nic)

        args.ckpt_dir = args.run_dir + '/checkpoints'
        if(dirs):
            mkdirs(args.run_dir, args.ckpt_dir)
        
        assert args.epochs % args.ckpt_freq == 0, 'epochs must'\
            'be divisible by ckpt_freq'

        # Set random seed
        if args.seed is None:
            args.seed = random.randint(1, 10000)
        print("Random Seed: ", args.seed)
        random.seed(args.seed)
        torch.manual_seed(args.seed)

        print('Arguments:')
        pprint(vars(args))

        return args
