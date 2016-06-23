import operator
import os
import sys

from pandas.core.frame import DataFrame
import networkx as nx
from networkx.algorithms import bipartite

import matplotlib.pylab as pylab
import matplotlib.patches as mpatches
import numpy as np
import pylab as plt
import math


class Ms2Lda_Viz(object):
    
    def __init__(self, model, ms1, ms2, docdf, topicdf):
        self.model = model
        self.ms1 = ms1
        self.ms2 = ms2
        self.docdf = docdf
        self.topicdf = topicdf        

    def rank_topics(self, sort_by="h_index", selected_topics=None, top_N=None, interactive=False):

        raise ValueError("rank_topics is now called rank_motifs")
    
    def rank_motifs(self, sort_by="h_index", selected_motifs=None, top_N=None, interactive=False):

        print "Ranking motifs ..."
        self.sort_by = sort_by
        if sort_by == 'h_index':
            topic_sort_criteria = self._h_index() 
        elif sort_by == 'in_degree':
            topic_sort_criteria = self._in_degree() 
        print "DONE!"
        print
        
        sorted_topic_counts = sorted(topic_sort_criteria.items(), key=operator.itemgetter(1), reverse=True)

        # also create a matrix of topics and their h-indices for later use in front-end visualisation
        if interactive:        
            num_topics = len(sorted_topic_counts)
            topic_degree = self._in_degree()
            self.topic_ranking = np.zeros((num_topics, 3), dtype=int)
            for k in range(num_topics):
                item = sorted_topic_counts[k]
                topic_id = item[0]
                self.topic_ranking[k, 0] = topic_id
                self.topic_ranking[k, 1] = item[1] # the h-index or in-degree of that topic
                self.topic_ranking[k, 2] = topic_degree[topic_id]
            self.sort_by_min = np.min(self.topic_ranking[:, 2])
            self.sort_by_max = np.max(self.topic_ranking[:, 2])
        
        return topic_sort_criteria, sorted_topic_counts                
                
    def plot_lda_fragments(self, consistency=0.50, sort_by="h_index", 
                           selected_motifs=None, interactive=False,
                           to_highlight=None):
        
        self.to_highlight = to_highlight
                
        if selected_motifs is not None and interactive:
            raise ValueError("For interactive mode, the selected_motifs parameter is not yet supported so you must visualise all motifs.")
                
        topic_ranking, sorted_topic_counts = self.rank_motifs(sort_by=sort_by, 
                                                              selected_motifs=selected_motifs, interactive=interactive)               
        self.topic_plots = {}
        self.topic_ms1_count = {}
        self.topic_ms1_ordering = {}
        self.topic_coordinates = {}
        self.topic_wordfreqs = {}
        for (i, c) in sorted_topic_counts:
            
            # skip non-selected topics
            if selected_motifs is not None:
                if i not in selected_motifs:
                    continue

            if not interactive:            
                if sort_by == 'h_index':
                    print "Mass2Motif " + str(i) + " h-index=" + str(topic_ranking[i])
                elif sort_by == 'in_degree':
                    print "Mass2Motif " + str(i) + " in-degree=" + str(topic_ranking[i])
                    print "====================="
                    print

            column_values = np.array(self.docdf.columns.values)    
            doc_dist = self.docdf.iloc[[i]].as_matrix().flatten()
            
            # argsort in descending order
            idx = np.argsort(doc_dist)[::-1] 
            topic_d = np.array(column_values)[idx]
            topic_p = np.array(doc_dist)[idx]
            
            # pick the top-n documents
            # top_n_docs = topic_d[1:n_docs+1]
            # top_n_docs_p = topic_p[1:n_docs+1]

            # pick the documents with non-zero values
            nnz_idx = topic_p>0
            top_n_docs = topic_d[nnz_idx]
            top_n_docs_p = topic_p[nnz_idx]
            
            if not interactive:            
                if len(top_n_docs) == 0:
                    print "No parent peaks above the threshold found for this motif"
                    continue
                print "Parent peaks"
                print
                if 'annotation' in self.ms1.columns:
                    print '     %s\t%s\t\t%s\t\t%s\t\t%s\t\t%s' % ('peakID', 'mz', 'rt', 'int', 'score', 'annotation')
                else:
                    print '     %s\t%s\t\t%s\t\t%s\t\t%s' % ('peakID', 'mz', 'rt', 'int', 'score')
                    
#             else:
#                 if len(top_n_docs) == 0:
#                     continue

            parent_ids = []
            parent_masses = []
            parent_rts = []
            parent_intensities = []
            parent_all_fragments = {}
            parent_word_counts = []
            parent_annots = []
            count = 1
            for t in zip(top_n_docs, top_n_docs_p):
    
                # split mz_rt_peakid string into tokens
                tokens = t[0].split('_')
                peakid = int(tokens[2])
                ms1_row = self.ms1.loc[[peakid]]
                mz = ms1_row[['mz']]
                mz = np.asscalar(mz.values)
                rt = ms1_row[['rt']]
                rt = np.asscalar(rt.values)
                intensity = ms1_row[['intensity']]
                intensity = np.asscalar(intensity.values)
                prob = t[1]
                if 'annotation' in ms1_row.columns:
                    annot = ms1_row[['annotation']].values.ravel().tolist()[0]
                else:
                    annot = None
    
                if not interactive:
                    if 'annotation' in ms1_row.columns:
                        print '%-5d%-5d\t%3.5f\t%6.3f\t\t%.3e\t%.3f\t\t%s' % (count, peakid, mz, rt, intensity, prob, annot)
                    else:
                        print '%-5d%-5d\t%3.5f\t%6.3f\t\t%.3e\t%.3f' % (count, peakid, mz, rt, intensity, prob)                        
                parent_ids.append(peakid)
                parent_masses.append(mz)
                parent_rts.append(rt)
                parent_intensities.append(intensity)
                parent_annots.append(annot)
                
                # find all the fragment peaks of this parent peak
                ms2_rows = self.ms2.loc[self.ms2['MSnParentPeakID']==peakid]
                peakids = ms2_rows[['peakID']]
                mzs = ms2_rows[['mz']]
                intensities = ms2_rows[['intensity']]
                parentids = ms2_rows[['MSnParentPeakID']]
    
                # convert from pandas dataframes to list
                peakids = peakids.values.ravel().tolist()
                mzs = mzs.values.ravel().tolist()
                intensities = intensities.values.ravel().tolist()
                parentids = parentids.values.ravel().tolist()
    
                # save all the fragment peaks of this parent peak into the dictionary
                parentid = peakid
                items = []
                for n in range(len(peakids)):
                    mz = mzs[n]
                    intensity = intensities[n]
                    fragment_peakid = peakids[n]
                    item = (fragment_peakid, parentid, mz, intensity)
                    items.append(item)
                parent_all_fragments[parentid] = items
    
                count += 1
    
            sys.stdout.flush()
            
            if len(parent_masses) > 0:
                max_parent_mz = np.max(np.array(parent_masses))

            # argsort in descending order by p(w|d)
            word_dist = self.topicdf.transpose().iloc[[i]].as_matrix().flatten()                          
            column_values = np.array(self.topicdf.transpose().columns.values)    

            # argsort in descending order
            idx = np.argsort(word_dist)[::-1] 
            topic_w = np.array(column_values)[idx]
            topic_p = np.array(word_dist)[idx]    
            
            # pick the words with non-zero values
            nnz_idx = topic_p>0
            topic_w = topic_w[nnz_idx]
            topic_p = topic_p[nnz_idx]
            
            # split words into either fragment or loss words                        
            fragments = []
            fragments_p = []
            losses = []
            losses_p = []
            counter = 0
            for w, p in zip(topic_w, topic_p):
                if w.startswith('fragment'):
                    fragments.append(w)
                    fragments_p.append(p)
                elif w.startswith('loss'):
                    losses.append(w)
                    losses_p.append(p)
                counter += 1

            wordfreq = {}
            self.topic_wordfreqs[i] = wordfreq
                    
            if not interactive:
                print
                print "Fragments"
                print
            parent_topic_fragments = {}
            count = 1
            for t in zip(fragments, fragments_p):
    
                fragment = t[0]
                tokens = fragment.split('_')
                bin_id = tokens[1]
                bin_prob = t[1]
                ms2_rows = self.ms2.loc[self.ms2['fragment_bin_id']==bin_id]
                ms2_rows = ms2_rows.loc[ms2_rows['MSnParentPeakID'].isin(parent_ids)]

                if not interactive:
                    print '%-5d%s (%.3f)' % (count, t[0], t[1])
                    if not ms2_rows.empty:
                        if 'annotation' in ms2_rows.columns:
                            print ms2_rows[['peakID', 'MSnParentPeakID', 'mz', 'rt', 'intensity', 'annotation']].to_string(index=False, justify='left')
                        else:
                            print ms2_rows[['peakID', 'MSnParentPeakID', 'mz', 'rt', 'intensity']].to_string(index=False, justify='left')
                    else:
                        print "\tNothing found for the selected parent peaks"
    
                count += 1
    
                peakids = ms2_rows[['peakID']]
                mzs = ms2_rows[['mz']]
                intensities = ms2_rows[['intensity']]
                parentids = ms2_rows[['MSnParentPeakID']]
    
                # convert from pandas dataframes to list
                peakids = peakids.values.ravel().tolist()
                mzs = mzs.values.ravel().tolist()
                intensities = intensities.values.ravel().tolist()
                parentids = parentids.values.ravel().tolist()
                if 'annotation' in ms2_rows.columns:
                    annotations = ms2_rows[['annotation']]
                    annotations = annotations.values.ravel().tolist()                
                else:
                    annotations = None

                for n in range(len(parentids)):
                    parentid = parentids[n]
                    mz = mzs[n]
                    intensity = intensities[n]
                    peakid = peakids[n]
                    word = fragment
                    if annotations is not None:
                        ann = annotations[n]
                    else:
                        ann = None
                    item = (peakid, parentid, mz, intensity, word, ann)
                    if parentid in parent_topic_fragments:
                        existing_list = parent_topic_fragments[parentid]
                        existing_list.append(item)
                    else:
                        new_list = [item]
                        parent_topic_fragments[parentid] = new_list
                    # count how many times this fragment word appears in the retrieved set
                    if fragment in wordfreq:
                        wordfreq[fragment] = wordfreq[fragment] + 1
                    else:
                        wordfreq[fragment] = 1

            if not interactive:
                print
                print "Losses"
                print
            parent_topic_losses = {}
            count = 1
            for t in zip(losses, losses_p):
    
                loss = t[0]
                tokens = loss.split('_')
                bin_id = tokens[1]
                bin_prob = t[1]
                ms2_rows = self.ms2.loc[self.ms2['loss_bin_id']==bin_id]
                ms2_rows = ms2_rows.loc[ms2_rows['MSnParentPeakID'].isin(parent_ids)]

                if not interactive:
                    print '%-5d%s (%.3f)' % (count, t[0], t[1])
                    if not ms2_rows.empty:
                        if 'annotation' in ms2_rows.columns:
                            print ms2_rows[['peakID', 'MSnParentPeakID', 'mz', 'rt', 'intensity', 'annotation']].to_string(index=False, justify='left')
                        else:
                            print ms2_rows[['peakID', 'MSnParentPeakID', 'mz', 'rt', 'intensity']].to_string(index=False, justify='left')
                    else:
                        print "\tNothing found for the selected parent peaks"

                count += 1
    
                peakids = ms2_rows[['peakID']]
                mzs = ms2_rows[['mz']]
                intensities = ms2_rows[['intensity']]
                parentids = ms2_rows[['MSnParentPeakID']]
    
                # convert from pandas dataframes to list
                peakids = peakids.values.ravel().tolist()
                mzs = mzs.values.ravel().tolist()
                intensities = intensities.values.ravel().tolist()
                parentids = parentids.values.ravel().tolist()
                if 'annotation' in ms2_rows.columns:
                    annotations = ms2_rows[['annotation']]
                    annotations = annotations.values.ravel().tolist()                
                else:
                    annotations = None                

                for n in range(len(parentids)):
                    parentid = parentids[n]
                    mz = mzs[n]
                    intensity = intensities[n]
                    peakid = peakids[n]
                    word = loss
                    if annotations is not None:
                        ann = annotations[n]
                    else:
                        ann = None                    
                    item = (peakid, parentid, mz, intensity, word, ann)
                    if parentid in parent_topic_losses:
                        existing_list = parent_topic_losses[parentid]
                        existing_list.append(item)
                    else:
                        new_list = [item]
                        parent_topic_losses[parentid] = new_list
                    # count how many times this fragment word appears in the retrieved set
                    if loss in wordfreq:
                        wordfreq[loss] = wordfreq[loss] + 1
                    else:
                        wordfreq[loss] = 1
    
            if not interactive:
                print
                sys.stdout.flush()
    
            # plot the n_docs parent peaks in this topic            
            # make plot for every parent peak
            num_peaks = len(parent_ids)
            if not interactive:
            
                for n in range(num_peaks):
                        # compute the ordering of ms1 peaks to be plotted in this topic
                        self._update_topic_ordering(i, parent_ids, parent_topic_fragments, parent_topic_losses, wordfreq, consistency)
                        # make the plot
                        self._make_ms1_plot(i, n, parent_masses, parent_rts, parent_ids, 
                           parent_all_fragments, parent_topic_fragments, parent_topic_losses,
                           wordfreq, consistency, max_parent_mz, parent_annots)
                        plt.show()

            else: # interactive mode

                # set MS1 plot data
                plot_data = (parent_masses, parent_rts, parent_ids, 
                           parent_all_fragments, parent_topic_fragments, parent_topic_losses,
                           wordfreq, consistency, max_parent_mz, parent_annots)

                # compute the ordering of ms1 peaks to be plotted in this topic
                self._update_topic_ordering(i, parent_ids, parent_topic_fragments, parent_topic_losses, wordfreq, consistency)

                # save the plot data for interactive use later
                self.topic_plots[i] = plot_data
                self.topic_ms1_count[i] = num_peaks                
                print "Generating plots for Mass2Motif " + str(i) + " h-index=" + str(topic_ranking[i]) + ", degree=" + str(num_peaks)

                # set coordinate of each circle too
                x_coord = topic_ranking[i]
                if num_peaks > 0:
                    y_coord = math.log10(num_peaks)   
                else :
                    y_coord = 0
                self.topic_coordinates.update({i:(x_coord, y_coord)})
                                                    
        # convert topic_coordinates from dictionary to a list of coordinates, sorted by the topic id
        sorted_coords = sorted(self.topic_coordinates.iteritems(), key=lambda key_value: key_value[0])
        self.topic_coordinates = [item[1] for item in sorted_coords]        
        
    def plot_cosine_clustering(self, motif_id, ions_of_interest, clustering, peak_names):  
        
        C, P, G, pos, peak_nodes, cluster_interests = self._get_cosine_network_graph(ions_of_interest, clustering, peak_names)
        interest_nodes = [n for i,n in peak_nodes.items() if i in ions_of_interest]      
        
        scaling = 10
        fig = plt.figure(figsize=(12,12))
        ax = fig.add_subplot(111)
        nx.draw_networkx_edges(G, pos, width=0.2, ax=ax)
        nx.draw_networkx_nodes(G, pos, nodelist=C, node_size = 1*scaling, node_color = 'g', linewidths=0.1, ax=ax)
        nx.draw_networkx_nodes(G, pos, nodelist=P, node_size = 0.5*scaling, node_color = 'b', linewidths=0.1, ax=ax)
        nx.draw_networkx_nodes(G, pos, nodelist=interest_nodes, node_size=2*scaling, node_color='r', linewidths=0.1, ax=ax)
        
        labels_pos = {}
        labels = {} 
        for c in C:
            cluster = G.node[c]['name']
            if cluster in cluster_interests:
                labels_pos[c] = pos[c]
                labels[c] = cluster
        nx.draw_networkx_labels(G, labels_pos, labels, font_size=10, font_weight='bold')

        title = 'Mass2Motif ' + str(motif_id)
        plt.title(title)
        plt.axis('off')
        plt.show()
        
        return G, cluster_interests
        
    def _get_cosine_network_graph(self, ions_of_interest, clustering, peak_names):

        ions_of_interest_clustering = []
        for item in ions_of_interest:
            pos = peak_names.index(item)
            cl = clustering[pos]
            ions_of_interest_clustering.append(cl)
        ions_of_interest_clustering = np.array(ions_of_interest_clustering)

        # Create the networkx graph object.
        # Clusters with fewer than min_size_to_plot members are not plotted
        min_size_to_plot = 4
        node_no = 0
        G = nx.Graph()
        uc = np.unique(clustering)
        cluster_nodes = {}
        singleton_clusters = []
        cluster_interests = {}
        for cluster in uc:
            # check cluster size
            members = np.where(clustering == cluster)[0]
            if len(members) < min_size_to_plot:
                # print "Not plotting cluster %d with %d members." % (cluster, len(members))
                singleton_clusters.append(cluster)
                continue
            # append to graph
            cluster_nodes[cluster] = node_no
            G.add_node(node_no, bipartite=0, name=cluster)
            node_no += 1
            # also print out the ions of interest in this cluster
            interest_members = np.where(ions_of_interest_clustering == cluster)[0]
            if len(interest_members) > 0:
                cluster_interests[cluster] = []
                for idx in interest_members:
                    tokens = ions_of_interest[idx].split('_')
                    pid = int(tokens[2])
                    cluster_interests[cluster].append(pid)
        
        peak_nodes = {}
        for i,name in enumerate(peak_names):
            this_cluster = clustering[i]
            if this_cluster in cluster_nodes:
                peak_nodes[name] = node_no
                G.add_node(node_no,bipartite=1, name=name)
                G.add_edge(node_no,cluster_nodes[clustering[i]])
                node_no += 1
        
        # Position the clusters in a grid, and their members in circle coming out from the cluster. 
        # cstep determines the distance between grid points. 
        # If you want cluster members closer to the cluster centers, change the 0.75 in 
        # the x_pos and y_pos lines
        C,P = bipartite.sets(G)
        n_clusters = len(C)
        n_rows = np.ceil(np.sqrt(n_clusters))
        pos = {}
        current_row = 0
        current_col = 0
        cstep = 2.0
        for c in C:
            n_list = G.neighbors(c)
            pos[c] = [cstep*current_row,cstep*current_col]
            # find neighbours
            step = 2*np.pi/len(n_list)
            angle = 0.0
            for n in n_list:
                x_pos = 0.75*np.sin(angle)
                y_pos = 0.75*np.cos(angle)
                pos[n] = [pos[c][0]+x_pos,pos[c][1]+y_pos]
                angle += step
            current_col += 1
            if current_col >= n_rows:
                current_col = 0
                current_row += 1
                
        return C, P, G, pos, peak_nodes, cluster_interests
        
    def _update_topic_ordering(self, i, parent_ids, parent_topic_fragments, parent_topic_losses, wordfreq, consistency):

        # count how many words are being plotted (above the consistency ratio) for each parent id
        parent_word_counts = []
        for parent_id in parent_ids:
            count = 0
            if parent_id in parent_topic_fragments:        
                fragments_list = parent_topic_fragments[parent_id]
                num_peaks = len(fragments_list)
                for j in range(num_peaks):
                    item = fragments_list[j]
                    word = item[4]                           
                    freq = wordfreq[word]
                    ratio = float(freq)/len(parent_ids)
                    if ratio >= consistency:
                        count += 1
            if parent_id in parent_topic_losses:        
                losses_list = parent_topic_losses[parent_id]
                num_peaks = len(losses_list)
                for j in range(num_peaks):
                    item = losses_list[j]
                    word = item[4]
                    freq = wordfreq[word]
                    ratio = float(freq)/len(parent_ids)
                    if ratio >= consistency:
                        count += 1
            parent_word_counts.append(count)
         
        parent_word_counts = np.array(parent_word_counts)
        ms1_ordering = np.argsort(parent_word_counts)[::-1]
        self.topic_ms1_ordering[i] = ms1_ordering
        
    def plot_for_web(self, i, n):
        if i in self.topic_plots:
            parent_masses, parent_rts, parent_ids, parent_all_fragments, parent_topic_fragments, parent_topic_losses, wordfreq, consistency, max_parent_mz, parent_annots = self.topic_plots[i]
            fig = self._make_ms1_plot(i, n, parent_masses, parent_rts, parent_ids, 
                                      parent_all_fragments, parent_topic_fragments, parent_topic_losses,
                                      wordfreq, consistency, max_parent_mz, parent_annots)
            return fig
        else:
            return None
        
    def _make_ms1_plot(self, i, n, parent_masses, parent_rts, parent_ids, 
                       parent_all_fragments, parent_topic_fragments, parent_topic_losses,
                       wordfreq, consistency, max_parent_mz, parent_annots):
        
        # get the image content but in the right order
        pos = self.topic_ms1_ordering[i][n]
                
        parent_fontspec = {
            'size':'12', 
            'color':'blue', 
            'weight':'bold'
        }
        fragment_fontspec = {
            'size':'12', 
            'color':'#800000', 
            'weight':'bold'
        }
        loss_fontspec = {
            'size':'12', 
            'color':'green', 
            'weight':'bold'
        }        
        
        figsize=(10, 6)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        
        #set the bbox for the text. Increase txt_width for wider text.
        txt_width = 20*(plt.xlim()[1] - plt.xlim()[0])        
        txt_width_annot = 40*(plt.xlim()[1] - plt.xlim()[0])
        txt_height = 0.2*(plt.ylim()[1] - plt.ylim()[0])

        ## handle empty topic
        if len(parent_ids) == 0:

            parent_mass = 0
            parent_rt = 0
            parent_annot = None
            
        else:

            # plot the parent peak first
            parent_mass = parent_masses[pos]
            parent_rt = parent_rts[pos]
            parent_annot = parent_annots[pos]
    
            # TEMPORARILY HARDCODED FOR RELATIVE INTENSITY 
            parent_intensity = 0.25
            plt.plot((parent_mass, parent_mass), (0, parent_intensity), linewidth=2.0, color='b')
            x = parent_mass
            y = parent_intensity
            parent_id = parent_ids[pos]

            has_annotation = False
            if parent_annot is not None:
                if isinstance(parent_annot, float) and math.isnan(parent_annot): # when nan, parent_annot is of type float
                    has_annotation = False
                else:
                    has_annotation = True
            if has_annotation:
                label = "%.4f\n(%s)" % (parent_mass, parent_annot)
            else:
                label = "%.4f" % (parent_mass)                
            plt.text(x, y, label, **parent_fontspec)
    
            # plot all the fragment peaks of this parent peak
            fragments_list = parent_all_fragments[parent_id]
            num_peaks = len(fragments_list)
            for j in range(num_peaks):
                item = fragments_list[j]
                peakid = item[0]
                parentid = item[1]
                mass = item[2]
                intensity = item[3]
                plt.plot((mass, mass), (0, intensity), linewidth=1.0, color='#FF9933')
    
            x_data = []
            y_data = []
            line_type = []    
            labels = []        
            has_annots = []
            xlim_upper = max_parent_mz
    
            # plot the fragment peaks in this topic that also occur in this parent peak
            if parent_id in parent_topic_fragments:        
                fragments_list = parent_topic_fragments[parent_id]
                num_peaks = len(fragments_list)
                for j in range(num_peaks):
                    item = fragments_list[j]
                    peakid = item[0]
                    parentid = item[1]
                    mass = item[2]
                    if mass > xlim_upper:
                        xlim_upper = mass
                    intensity = item[3]
                    word = item[4]
                    annot = item[5]
                    freq = wordfreq[word]
                    ratio = float(freq)/len(parent_ids)
                    if ratio >= consistency:
                        plt.plot((mass, mass), (0, intensity), linewidth=2.0, color='#800000')
                        x = mass
                        y = intensity
                        has_annotation = False
                        if annot is not None:
                            if isinstance(annot, float) and math.isnan(annot): # when nan, annot is of type float
                                has_annotation = False
                            else:
                                has_annotation = True
                        if has_annotation:
                            label = '%.4f\n(%s)' % (x, annot)
                        else:
                            label = '%.4f' % (x)                            
                        x_data.append(x)
                        y_data.append(y)
                        line_type.append('fragment')
                        labels.append(label)
                        has_annots.append(has_annotation)
                
            # plot the neutral losses in this topic that also occur in this parent peak
            if parent_id in parent_topic_losses:        
                losses_list = parent_topic_losses[parent_id]
                num_peaks = len(losses_list)
                for j in range(num_peaks):
                    item = losses_list[j]
                    peakid = item[0]
                    parentid = item[1]
                    mass = item[2]
                    if mass > xlim_upper:
                        xlim_upper = mass
                    intensity = item[3]
                    word = item[4]
                    annot = item[5]
                    freq = wordfreq[word]
                    ratio = float(freq)/len(parent_ids)
                    if ratio >= consistency:
                        plt.plot((mass, mass), (0, intensity), linewidth=2.0, color='green')
                        x = mass
                        y = intensity
                        has_annotation = False
                        if annot is not None:
                            if isinstance(annot, float) and math.isnan(annot): # when nan, annot is of type float
                                has_annotation = False
                            else:
                                has_annotation = True
                        if has_annotation:
                            label = '%.4f\n(%s)' % (x, annot)
                        else:
                            label = '%.4f' % (x)
                        x_data.append(x)
                        y_data.append(y)
                        line_type.append('loss')
                        labels.append(label)
                        has_annots.append(has_annotation)
                
            # Get the corrected text positions, then write the text.
            x_data = np.array(x_data)
            y_data = np.array(y_data)
            text_positions = self._get_text_positions(x_data, y_data, has_annots, txt_width, txt_width_annot, txt_height)
            self._text_plotter(x_data, y_data, line_type, labels, has_annots, 
                               text_positions, ax, 
                               txt_width, txt_width_annot, txt_height, 
                               fragment_fontspec, loss_fontspec)
    
        plt.xlim([0, xlim_upper+100])
        plt.ylim([0, 1.5])

        plt.xlabel('m/z')
        plt.ylabel('relative intensity')                    
        ms1_peak_counts = str(len(parent_masses))
        pid_value = ("%d" % parent_id)
        mz_value = ("%.4f" % parent_mass)
        rt_value = ("%.3f" % parent_rt)
        title = 'Mass2Motif ' + str(i) + ' peak ' + str(n+1) + '/' + ms1_peak_counts
        title += ' (pid=' + pid_value + ' m/z=' + mz_value + ' RT=' + rt_value + ")"
        plt.title(title)
        
        blue_patch = mpatches.Patch(color='blue', label='Parent peak')
        yellow_patch = mpatches.Patch(color='#FF9933', label='Fragment peaks')
        red_patch = mpatches.Patch(color='#800000', label='M2M fragment')
        green_patch = mpatches.Patch(color='green', label='M2M loss')                
        plt.legend(handles=[blue_patch, yellow_patch, red_patch, green_patch])                

        return fig
                    
    # from http://stackoverflow.com/questions/8850142/matplotlib-overlapping-annotations
    def _get_text_positions(self, x_data, y_data, has_annots, txt_width, txt_width_annot, txt_height):
        a = zip(y_data, x_data)
        text_positions = y_data.copy()
        for index, (y, x) in enumerate(a):
            has_annot = has_annots[index]
            if has_annot:
                txtw = txt_width_annot
            else:
                txtw = txt_width
            local_text_positions = [i for i in a if i[0] > (y - txt_height) 
                                and (abs(i[1] - x) < txtw * 2) and i != (y,x)]
            if local_text_positions:
                sorted_ltp = sorted(local_text_positions)
                if abs(sorted_ltp[0][0] - y) < txt_height: #True == collision
                    differ = np.diff(sorted_ltp, axis=0)
                    a[index] = (sorted_ltp[-1][0] + txt_height, a[index][1])
                    text_positions[index] = sorted_ltp[-1][0] + txt_height
                    for k, (j, m) in enumerate(differ):
                        #j is the vertical distance between words
                        if j > txt_height * 2: #if True then room to fit a word in
                            a[index] = (sorted_ltp[k][0] + txt_height, a[index][1])
                            text_positions[index] = sorted_ltp[k][0] + txt_height
                            break
        return text_positions
    
    # from http://stackoverflow.com/questions/8850142/matplotlib-overlapping-annotations
    def _text_plotter(self, x_data, y_data, line_type, labels, has_annots, 
                      text_positions, axis, 
                      txt_width, txt_width_annot, txt_height, 
                      fragment_fontspec, loss_fontspec):
        for x,y,t,l,lab,has_annot in zip(x_data, y_data, text_positions, line_type, labels, has_annots):
            if has_annot:
                txtw = txt_width_annot
            else:
                txtw = txt_width
            if l == 'fragment':
                axis.text(x-txtw, 1.01*t, lab, rotation=0, **fragment_fontspec)
            elif l == 'loss':
                axis.text(x-txtw, 1.01*t, lab, rotation=0, **loss_fontspec)                
            if y != t:
                axis.arrow(x, t,0,y-t, color='black', alpha=0.2, width=txtw*0.01, 
                           head_width=txtw/4, head_length=txt_height*0.25, 
                           zorder=0,length_includes_head=True)
    
    # compute the h-index of topics TODO: this only works for fragment and loss words!
    def _h_index(self):
                
        K = self.model.K
        topic_counts = {}

        for i in range(K):
                        
            sys.stdout.flush()
            
            # find the words in this topic above the threshold
            topic_words = self.topicdf.ix[:, i]
            topic_words = topic_words.iloc[topic_words.nonzero()[0]]      

            fragment_words = {}
            loss_words = {}            
            for word in topic_words.index:
                tokens = word.split('_')
                word_type = tokens[0]
                value = tokens[1]
                if word_type == 'fragment':
                    fragment_words[value] = 0
                elif word_type == 'loss':
                    loss_words[value] = 0
            
            # find the documents in this topic above the threshold
            topic_docs = self.docdf.ix[i, :]
            topic_docs = topic_docs.iloc[topic_docs.nonzero()[0]]
            
            # handle empty topics
            if topic_docs.empty:
                
                topic_counts[i] = 0
                
            else:
            
                # now find out how many of the documents in this topic actually 'cite' the words    
                for docname in topic_docs.index:
    
                    # split mz_rt_peakid string into tokens
                    tokens = docname.split('_')
                    peakid = int(tokens[2])
                    
                    # find all the fragment peaks of this parent peak
                    ms2_rows = self.ms2.loc[self.ms2['MSnParentPeakID']==peakid]
                    fragment_bin_ids = ms2_rows[['fragment_bin_id']]
                    loss_bin_ids = ms2_rows[['loss_bin_id']]       
                    
                    # convert from pandas dataframes to list
                    fragment_bin_ids = fragment_bin_ids.values.ravel().tolist()
                    loss_bin_ids = loss_bin_ids.values.ravel().tolist()
                                        
                    # this code is too slow!
                    # count the citation numbers
#                     for cited in fragment_bin_ids:
#                         if cited == 'nan':
#                             continue
#                         else:
#                             if cited in fragment_words:
#                                 fragment_words[cited] = fragment_words[cited] + 1
#                     for cited in loss_bin_ids:
#                         if cited == 'nan':
#                             continue
#                         else:
#                             if cited in loss_words:
#                                 loss_words[cited] = loss_words[cited] + 1

                    # convert to dictionary for quick lookup
                    word_dict = {}
                    for word in fragment_bin_ids:
                        word_dict.update({word:word})
                    for word in loss_bin_ids:
                        word_dict.update({word:word})

                    # count the citation numbers                                
                    for word in fragment_words:
                        if word in word_dict:
                            fragment_words[word] = fragment_words[word] + 1
                    for word in loss_words:
                        if word in word_dict:
                            loss_words[word] = loss_words[word] + 1
                    
                    # make a dataframe of the articles & citation counts
                    fragment_df = DataFrame(fragment_words, index=['counts']).transpose()
                    loss_df = DataFrame(loss_words, index=['counts']).transpose()
                    df = fragment_df.append(loss_df)
                    df = df.sort(['counts'], ascending=False)
                    
                    # compute the h-index
                    h_index = 0
                    for index, row in df.iterrows():
                        if row['counts'] > h_index:
                            h_index += 1
                        else:
                            break

                print " - Mass2Motif " + str(i) + " h-index = " + str(h_index)
                topic_counts[i] = h_index
            
        return topic_counts
        
    # computes the in-degree of topics
    def _in_degree(self):    

        topic_fragments = self.model.topic_word_
        topic_counts = {}
        
        for i, topic_dist in enumerate(topic_fragments):
            
            sys.stdout.flush()
            
            # find the documents in this topic above the threshold
            topic_docs = self.docdf.ix[i, :]
            topic_docs = topic_docs.iloc[topic_docs.nonzero()[0]]
            topic_counts[i] = len(topic_docs)
            
        return topic_counts