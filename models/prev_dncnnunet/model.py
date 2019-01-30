import time
import os,sys
import random

import tensorflow as tf
import tensorflow.contrib as tc
import numpy as np
import scipy.io as sio                                                  

# refer: 
# [1] https://github.com/timctho/unet-tensorflow/blob/master/model/u_net_tf_v2.py

def dncnn_unet(input, is_training=True, output_channels=1):

    # dncnn : learning noise
    with tf.variable_scope('block1'):
        output = tf.layers.conv2d(input, 64, 3, padding='same', activation=tf.nn.relu)

    for layers in xrange(2, 10):
        with tf.variable_scope('block%d' % layers):
            output = tf.layers.conv2d(output, 64, 3, padding='same', name='conv%d' % layers, use_bias=False)
            output = tf.nn.relu(tf.layers.batch_normalization(output, training=is_training))

    with tf.variable_scope('block10'):
        output = tf.layers.conv2d(output, output_channels, 3, padding='same')


    #
    # assume, dncnn learned the noise well, but there are still residual noise left
    #


    with tf.variable_scope('dncnn-output'):
        input_unet = input - output 

    #
    # we will use unet to learn the left noise
    #

    with tf.variable_scope('down0'):
        # conv + conv + max_pool
        down0a = tc.layers.conv2d(input_unet,  64,  (3,3), padding='same', normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})
        down0b = tc.layers.conv2d(down0a, 64,  (3,3), padding='same', normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})
        down0c = tc.layers.max_pool2d(down0b,  (2,2), padding='same')

    with tf.variable_scope('down1'):
        down1a = tc.layers.conv2d(down0c,  128, (3,3), padding='same', normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})
        down1b = tc.layers.conv2d(down1a,  128, (3,3), padding='same', normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})
        down1c = tc.layers.max_pool2d(down1b,   (2,2), padding='same')

    with tf.variable_scope('down2'):
        down2a = tc.layers.conv2d(down1c,  256, (3,3), padding='same', normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})
        down2b = tc.layers.conv2d(down2a,  256, (3,3), padding='same', normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})

    with tf.variable_scope('up1'):
        up1a = tc.layers.conv2d_transpose(down2b, 128, (2,2), 2, normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})
        up1b = tf.concat([up1a, down1b], axis=3)
        up1c = tc.layers.conv2d(up1b, 128, (3,3), normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})
        up1d = tc.layers.conv2d(up1c, 128, (3,3), normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})
        up1e = tc.layers.conv2d(up1d, 128, (3,3), normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})

    with tf.variable_scope('up0'):
        up0a = tc.layers.conv2d_transpose(up1e, 64, (2,2), 2, normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})
        up0b = tf.concat([up0a, down0b], axis=3)
        up0c = tc.layers.conv2d(up0b, 64, (3,3), normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})
        up0d = tc.layers.conv2d(up0c, 64, (3,3), normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})
        up0e = tc.layers.conv2d(up0d, 64, (3,3), normalizer_fn=tc.layers.batch_norm, normalizer_params={'is_training': is_training})

    with tf.variable_scope('unet-output'):
        output_unet = tc.layers.conv2d(up0e, 1, [1, 1], activation_fn=None)


    return  output_unet




class denoiser(object):
    def __init__(self, sess, input_c_dim=1, batch_size=128):
        self.sess = sess
        self.input_c_dim = input_c_dim

        # build model
        self.X  = tf.placeholder(tf.float32, [None, None, None, self.input_c_dim], name='noisy_image')
        self.Y_ = tf.placeholder(tf.float32, [None, None, None, self.input_c_dim], name='clean_image')

        self.is_training = tf.placeholder(tf.bool, name='is_training')

        self.Y = dncnn_unet(self.X, is_training=self.is_training) # trained output

        self.loss = (1.0 / batch_size) * tf.nn.l2_loss(self.Y_ - self.Y)  # use L2 loss

        self.lr = tf.placeholder(tf.float32, name='learning_rate')

        #self.eva_psnr = tf_psnr(self.Y, self.Y_)

        optimizer = tf.train.AdamOptimizer(self.lr, name='AdamOptimizer')

        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)

        with tf.control_dependencies(update_ops):
            self.train_op = optimizer.minimize(self.loss)

        init = tf.global_variables_initializer()
        self.sess.run(init)
        print("[*] Initialize model successfully...")


    def load(self, checkpoint_dir):
        '''
        read checkpoint
        '''
        print("[*] Reading checkpoint...")
        saver = tf.train.Saver()
        ckpt = tf.train.get_checkpoint_state(checkpoint_dir)
        if ckpt and ckpt.model_checkpoint_path:
            full_path = tf.train.latest_checkpoint(checkpoint_dir)
            global_step = int(full_path.split('/')[-1].split('-')[-1])
            saver.restore(self.sess, full_path)
            return True, global_step
        else:
            return False, 0



    #--------------------------------------------------------------------------
    # training
    #--------------------------------------------------------------------------
    def train(self, noisy_data, clean_data, batch_size, ckpt_dir, epoch, lr, eval_every_epoch=2):

        # assert data range is between 0 and 1
        numBatch = int(noisy_data.shape[0] / batch_size)

        #-----------------------
        # load pretrained model
        #-----------------------
        load_model_status, global_step = self.load(ckpt_dir)
        if load_model_status:
            iter_num = global_step
            start_epoch = global_step // numBatch
            start_step = global_step % numBatch
            print("[*] Model restore success!")
        else:
            iter_num = 0
            start_epoch = 0
            start_step = 0
            print("[*] Not find pretrained model!")


        # make summary
        tf.summary.scalar('loss', self.loss)
        tf.summary.scalar('lr', self.lr)
        writer = tf.summary.FileWriter('./logs', self.sess.graph)
        merged = tf.summary.merge_all()


        print("[*] Start training, with start epoch %d start iter %d : " % (start_epoch, iter_num))

        start_time = time.time()

        ##self.evaluate(iter_num, eval_data, sample_dir=sample_dir, 
        ##        summary_merged=summary_psnr,
        ##        summary_writer=writer)  # eval_data value range is 0-255


        samples = noisy_data.shape[0]

        for epoch in xrange(start_epoch, epoch):
            ## randomize data 
            random.seed(a=epoch)
            row_idx = np.arange(samples)
            np.random.shuffle(row_idx)

            noisy_input = noisy_data[row_idx,:]
            clean_input = clean_data[row_idx,:]
            #print noisy_new.shape, clean_new.shape
            

            for batch_id in xrange(start_step, numBatch):
                batch_noisy = noisy_input[batch_id * batch_size:(batch_id + 1) * batch_size, :, :, :]
                batch_clean = clean_input[batch_id * batch_size:(batch_id + 1) * batch_size, :, :, :]


                _, loss, summary = self.sess.run([self.train_op, self.loss, merged],
                        feed_dict={self.X: batch_noisy, 
                            self.Y_: batch_clean, 
                            self.lr: lr[epoch],
                            self.is_training: True})


                print("Epoch: [%2d] [%4d/%4d] time: %4.4f, loss: %.6f"
                      % (epoch + 1, batch_id + 1, numBatch, time.time() - start_time, loss))

                iter_num += 1
                #writer.add_summary(summary, iter_num)

            if np.mod(epoch + 1, eval_every_epoch) == 0:
                #self.evaluate(iter_num, eval_data, summary_merged=summary_psnr, summary_writer=writer)  # eval_data value range is 0-255
                self.save(iter_num, ckpt_dir)

        print("[*] Finish training.")


    def save(self, iter_num, ckpt_dir, model_name='unet-tensorflow'):
        saver = tf.train.Saver()
        checkpoint_dir = ckpt_dir
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)
        print("[*] Saving model...")
        saver.save(self.sess,
                   os.path.join(checkpoint_dir, model_name),
                   global_step=iter_num)


    def test(self, noisydata, ckpt_dir, outFile=''):
        """Test unet"""
        import scipy.io as sio

        # init variables
        tf.initialize_all_variables().run()
        assert len(noisydata) != 0, 'No testing data!'

        load_model_status, global_step = self.load(ckpt_dir)
        assert load_model_status == True, '[!] Load weights FAILED...'
        print("[*] Load weights SUCCESS...")

        ## note: input is 4D
        startT = time.time()

        output_clean_image = self.sess.run([self.Y],
                feed_dict={self.X: noisydata, self.is_training: False})

        endT = time.time()
        print("=> denoiser runtime = {} (s)".format(endT - startT))


        output_clean_image = np.asarray(output_clean_image)
        #print output_clean_image.shape

        #output_clean = output_clean_image[0,0,:,:,0]
        output_clean = output_clean_image[0,:,:,:,0]
        #print output_clean.shape

        if len(outFile) == 0:
            return output_clean
        else:
            # save output_clean to mat file
            sio.savemat(outFile, {'output_clean':output_clean})

