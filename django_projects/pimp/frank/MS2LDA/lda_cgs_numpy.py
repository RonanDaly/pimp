import sys

from scipy.special import gammaln

import numpy as np
from lda_cgs import Sample

def sample_numpy(random_state, n_burn, n_samples, n_thin, 
            D, N, K, document_indices, 
            alpha, beta, 
            Z, cdk, cd, previous_K,
            ckn, ck, previous_ckn, previous_ck):

    samples = []
    all_lls = []
    thin = 0
    N_beta = np.sum(beta)
    K_alpha = np.sum(alpha)    
    for samp in range(n_samples):
    
        s = samp+1        
        if s > n_burn:
            print("Sample " + str(s) + " "),
        else:
            print("Burn-in " + str(s) + " "),
            
        for d in range(D):

            if d%10==0:                        
                sys.stdout.write('.')
                sys.stdout.flush()
            
            word_locs = document_indices[d]
            for pos, n in word_locs:
                
                # remove word from model
                k = Z[(d, pos)]
                cdk[d, k] -= 1
                cd[d] -= 1    
                ckn[k, n] -= 1
                ck[k] -= 1

                if previous_K == 0:

                    # for training
                    log_likelihood = np.log(ckn[:, n] + beta[n]) - np.log(ck + N_beta)
                                
                else:
                    
                    # for testing on unseen data
                    log_likelihood_previous = np.log(previous_ckn[:, n] + beta[n]) - np.log(previous_ck + N_beta)
                    log_likelihood_current = np.log(ckn[:, n] + beta[n]) - np.log(ck + N_beta)    

                    # The combined likelihood: 
                    # front is from previous topic-word distribution
                    # back is from current topic-word distribution
                    # Because of the values from the hyperparameter, we cannot do
                    # log_likelihood = log_likelihood_previous + log_likelihood_current  
                    front = log_likelihood_previous[0:previous_K]
                    back = log_likelihood_current[previous_K:]
                    log_likelihood = np.hstack((front, back))
                                
                log_prior = np.log(cdk[d, :] + alpha) - np.log(cd[d] + K_alpha)                

                # sample new k from the posterior distribution log_post
                log_post = log_likelihood + log_prior
                post = np.exp(log_post - log_post.max())
                post = post / post.sum()
                
                # k = random_state.multinomial(1, post).argmax()
                cumsum = np.empty(K, dtype=np.float64)
                random_number = random_state.rand()                                
                total = 0
                for i in range(len(post)):
                    val = post[i]
                    total += val
                    cumsum[i] = total
                k = 0
                for k in range(len(cumsum)):
                    c = cumsum[k]
                    if random_number <= c:
                        break
         
                # reassign word back into model
                cdk[d, k] += 1
                cd[d] += 1
                ckn[k, n] += 1
                ck[k] += 1
                Z[(d, pos)] = k

        ll = K * ( gammaln(N_beta) - np.sum(gammaln(beta)) )
        for k in range(K):
            for n in range(N):
                ll += gammaln(ckn[k, n]+beta[n])
            ll -= gammaln(ck[k] + N_beta)                        

        ll += D * ( gammaln(K_alpha) - np.sum(gammaln(alpha)) )
        for d in range(D):
            for k in range(K):
                ll += gammaln(cdk[d, k]+alpha[k])
            ll -= gammaln(cd[d] + K_alpha)                
        
        all_lls.append(ll)      
        print(" Log likelihood = %.3f " % ll)

        # store all the samples after thinning
        if n_burn > 0 and s > n_burn:
            thin += 1
            if thin%n_thin==0:                    
                cdk_copy = np.copy(cdk)
                ckn_copy = np.copy(ckn)
                to_store = Sample(cdk_copy, ckn_copy)
                samples.append(to_store)

    # store the last sample only
    if n_burn == 0:
        cdk_copy = np.copy(cdk)
        ckn_copy = np.copy(ckn)
        to_store = Sample(cdk_copy, ckn_copy)
        samples.append(to_store)                                      
            
    all_lls = np.array(all_lls)
    return all_lls, samples