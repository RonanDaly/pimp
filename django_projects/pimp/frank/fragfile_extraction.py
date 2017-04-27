# coding=utf8
import pymzml
import bisect


class MS1(object):
    def __init__(self, id ,mz, rt, intensity, file_name, scan_number = None):
        self.id = id
        self.mz = mz
        self.rt = rt
        self.intensity = intensity
        self.file_name = file_name
        self.scan_number = scan_number
        self.name = "{}_{}".format(self.mz,self.rt)

    def __str__(self):
        return self.name




# Abstract loader class
class Loader(object):
    def load_spectra(self, input_set):
        raise NotImplementedError("load spectra method must be implemented")




# A class to load mzml files
# Will ultimately be able to do method 3

# This method finds each ms2 spectrum in the file and then looks back at the last ms1 scan to find the most
# intense ms1 peak within plus and minus the isolation window. If nothing is found, no document is created
# If it is found, a document is created

# If a peak list is provided it then tries to match the peaks in the peaklist to the ms1 objects, just
# keeping the ms1 objects that can be matched. The matching is done with plus and minus the mz_tol (ppm)
# and plus and minus the rt_tol
class LoadMZML(Loader):
    def __init__(self,min_ms1_intensity = 0.0,peaklist = None,isolation_window = 1.0,mz_tol = 5,rt_tol=5.0,duplicate_filter_mz_tol = 0.5,duplicate_filter_rt_tol = 16,duplicate_filter = True,repeated_precursor_match = None,
                    min_ms1_rt = 0.0, max_ms1_rt = 1e6, min_ms2_intensity = 0.0):
        self.min_ms1_intensity = min_ms1_intensity
        self.peaklist = peaklist
        self.isolation_window = isolation_window
        self.mz_tol = mz_tol
        self.rt_tol = rt_tol
        self.duplicate_filter = duplicate_filter
        self.duplicate_filter_mz_tol = duplicate_filter_mz_tol
        self.duplicate_filter_rt_tol = duplicate_filter_rt_tol
        self.min_ms1_rt = min_ms1_rt
        self.max_ms1_rt = max_ms1_rt
        self.min_ms2_intensity = min_ms2_intensity
        if repeated_precursor_match:
            self.repeated_precursor_match = repeated_precursor_match
        else:
            self.repeated_precursor_match = 2*self.isolation_window

    def __str__(self):
        return "mzML loader"
    def load_spectra(self,input_file):

        ms1 = []
        ms2 = []
        metadata = {}
        nc = 0
        ms2_id = 0
        ms1_id = 0

        print "duplicate filter is", self.duplicate_filter
        print "Loading spectra from {}".format(input_file)
        current_ms1_scan_mz = None
        current_ms1_scan_intensity = None
        current_ms1_scan_rt = None
        run = pymzml.run.Reader(input_file, MS1_Precision=5e-6, extraAccessions = [('MS:1000016' , ['value','unitName'] )])
        file_name = input_file.split('/')[-1]
        previous_precursor_mz = -10
        previous_ms1 = None

        for spectrum in run:
            if spectrum['ms level'] == 1:
                current_ms1_scan_rt,units = spectrum['scan start time']
                if units == 'minute':
                    current_ms1_scan_rt *= 60.0
                # Note can sometimes get empty scans at the start. If this happens we should ignore.
                if len(spectrum.peaks) > 0:
                    current_ms1_scan_mz,current_ms1_scan_intensity = zip(*spectrum.peaks)
                else:
                    current_ms1_scan_mz = None
                    current_ms1_scan_intensity = None

                previous_precursor_mz = -10
                previous_ms1 = None
            elif spectrum['ms level'] == 2:
                # Check that we have an MS1 scan to refer to. If not, skip this one
                # this can happen if we have blank MS1 scans. We should never get an MS2 scan after a blank MS1
                # but better to be safe than sorry!
                if not current_ms1_scan_mz:
                    continue
                else:
                    precursor_mz = spectrum['precursors'][0]['mz']
                    if abs(precursor_mz-previous_precursor_mz) < self.repeated_precursor_match:
                        # Another collision energy perhaps??
                        # if this is the case, we don't bother looking for a parent, but add to the previous one
                        # Make the ms2 objects:
                        if previous_ms1:
                            for mz,intensity in spectrum.centroidedPeaks:
                                ms2.append((mz,current_ms1_scan_rt,intensity,previous_ms1,file_name,float(ms2_id)))
                                ms2_id += 1
                        else:
                            pass
                    else:
                        # This is a new fragmentation

                        # This finds the insertion position for the precursor mz (i.e. the position one to the right
                        # of the first element it is greater than)
                        precursor_index_ish = bisect.bisect_right(current_ms1_scan_mz,precursor_mz)
                        pos = precursor_index_ish - 1 # pos is now the largest value smaller than ours

                        # Move left and right within the precursor window and pick the most intense parent_scan_number
                        max_intensity = 0.0
                        max_intensity_pos = None
                        while abs(precursor_mz - current_ms1_scan_mz[pos]) < self.isolation_window:
                            if current_ms1_scan_intensity[pos] >= max_intensity:
                                max_intensity = current_ms1_scan_intensity[pos]
                                max_intensity_pos = pos
                            pos -= 1
                            if pos < 0:
                                break
                        pos = precursor_index_ish
                        if pos < len(current_ms1_scan_mz):
                            while abs(precursor_mz - current_ms1_scan_mz[pos]) < self.isolation_window:
                                if current_ms1_scan_intensity[pos] >= max_intensity:
                                    max_intensity = current_ms1_scan_intensity[pos]
                                    max_intensity_pos = pos
                                pos += 1
                                if pos > len(current_ms1_scan_mz)-1:
                                    break
                            # print current_ms1_scan_mz[max_intensity_pos],current_ms1_scan_rt
                        # Make the new MS1 object
                        if not max_intensity_pos == None:
                        # mz,rt,intensity,file_name,scan_number = None):
                            new_ms1 = MS1(ms1_id,current_ms1_scan_mz[max_intensity_pos],
                                          current_ms1_scan_rt,max_intensity,file_name,scan_number = nc)
                            metadata[new_ms1.name] = {'parentmass':current_ms1_scan_mz[max_intensity_pos],
                                                      'parentrt':current_ms1_scan_rt,'scan_number':nc,
                                                      'precursor_mass':precursor_mz}


                            previous_ms1 = new_ms1 # used for merging energies
                            previous_precursor_mz = new_ms1.mz


                            ms1.append(new_ms1)
                            ms1_id += 1

                            # Make the ms2 objects:
                            for mz,intensity in spectrum.centroidedPeaks:
                                ms2.append((mz,current_ms1_scan_rt,intensity,new_ms1,file_name,float(ms2_id)))
                                ms2_id += 1

        print "Found {} ms2 spectra, and {} individual ms2 objects".format(len(ms1),len(ms2))

        if self.min_ms1_intensity>0.0:
            ms1,ms2 = filter_ms1_intensity(ms1,ms2,min_ms1_intensity = self.min_ms1_intensity)

        if self.peaklist:
            ms1_peaks = self._load_peak_list()
            ms1 = sorted(ms1,key = lambda x: x.mz)
            new_ms1_list = []
            new_ms2_list = []
            new_metadata = {}
            # ms1_mz = [x.mz for z in ms1]
            n_peaks_checked = 0
            for n_peaks_checked,peak in enumerate(self.ms1_peaks):
                if n_peaks_checked % 500 == 0:
                    print n_peaks_checked
                peak_mz = peak[0]
                peak_rt = peak[1]
                peak_intensity = peak[2]

                min_mz = peak_mz - self.mz_tol*peak_mz/1e6
                max_mz = peak_mz + self.mz_tol*peak_mz/1e6
                min_rt = peak_rt - self.rt_tol
                max_rt = peak_rt + self.rt_tol


                ms1_hits = filter(lambda x: x.mz >= min_mz and x.mz <= max_mz and x.rt >= min_rt and x.rt <= max_rt,ms1)

                if len(ms1_hits) == 1:
                    # Found one hit, easy
                    old_ms1 = ms1_hits[0]
                elif len(ms1_hits) > 1:
                    # Find the one with the most intense MS2 peak
                    best_ms1 = None
                    best_intensity = 0.0
                    for frag_peak in ms2:
                        if frag_peak[3] in ms1_hits:
                            if frag_peak[2] > best_intensity:
                                best_intensity = frag_peak[2]
                                best_ms1 = frag_peak[3]
                    old_ms1 = best_ms1
                else:
                    # Didn't find any
                    continue

                # make a new ms1 object
                new_ms1 = MS1(old_ms1.id,peak_mz,peak_rt,peak_intensity,old_ms1.file_name,old_ms1.scan_number)
                new_ms1_list.append(new_ms1)
                new_metadata[new_ms1.name] = metadata[old_ms1.name]

                # Delete the old one so it can't be picked again - removed this, maybe it's not a good idea?
                # pos = ms1.index(old_ms1)
                # del ms1[pos]

                # Change the reference in the ms2 objects to the new ms1 object
                ms2_objects = filter(lambda x: x[3] == old_ms1,ms2)
                for frag_peak in ms2_objects:
                    new_frag_peak = (frag_peak[0],peak_rt,frag_peak[2],new_ms1,frag_peak[4],frag_peak[5])
                    new_ms2_list.append(new_frag_peak)

            # replace the ms1,ms2 and metadata with the new versions
            ms1 = new_ms1_list
            ms2 = new_ms2_list
            metadata = new_metadata
            print "Peaklist filtering results in {} documents".format(len(ms1))

        if self.duplicate_filter:
            ms1,ms2 = filter_ms1(ms1,ms2,mz_tol = self.duplicate_filter_mz_tol,rt_tol = self.duplicate_filter_rt_tol)

        ## class refactor, put filtering inside of the class
        ms1 = filter(lambda x: x.rt > self.min_ms1_rt and x.rt < self.max_ms1_rt, ms1)
        ms2 = filter(lambda x: x[3] in set(ms1),ms2)
        # ms2 = filter(lambda x: x[3].rt > self.min_ms1_rt and x[3].rt < self.max_ms1_rt, ms2)
        if self.min_ms2_intensity > 0.0:
            ms2 = filter_ms2_intensity(ms2, min_ms2_intensity = self.min_ms2_intensity)
        # Potenitally not used for frank_pimp
        # Chop out filtered docs from metadata
        filtered_metadata = {}
        for m in ms1:
            if m.name in metadata:
                filtered_metadata[m.name] = metadata[m.name]
        metadata = filtered_metadata

        return ms1,ms2,metadata

    #May not need - peak list from DF
    def _load_peak_list(self):
        self.ms1_peaks = []
        with open(self.peaklist,'r') as f:
            heads = f.readline()
            for line in f:
                tokens = line.split(',')
                # get mx,rt,intensity
                self.ms1_peaks.append((float(tokens[1]),float(tokens[2]),float(tokens[3])))

        # sort them by mass
        self.ms1_peaks = sorted(self.ms1_peaks,key = lambda x: x[0])
        print "Loaded {} ms1 peaks from {}".format(len(self.ms1_peaks),self.peaklist)

        # ms1_peaks = []
        # for p in Peak:
        #     val = (p.mz, p.rt, p.intensity)
        #     ms1_peaks.append(val)


def filter_ms1_intensity(ms1, ms2, min_ms1_intensity=1e6):
    ## Use filter function to simplify code
    print "Filtering MS1 on intensity"
    ## Sometimes ms1 intensity could be None
    ms1 = filter(lambda x: False if x.intensity and x.intensity < min_ms1_intensity else True, ms1)
    print "{} MS1 remaining".format(len(ms1))
    ms2 = filter(lambda x: x[3] in set(ms1), ms2)
    print "{} MS2 remaining".format(len(ms2))
    return ms1, ms2


def filter_ms2_intensity(ms2, min_ms2_intensity=1e6):
    print "Filtering MS2 on intensity"
    ms2 = filter(lambda x: x[2] >= min_ms2_intensity, ms2)
    print "{} MS2 remaining".format(len(ms2))
    return ms2


def filter_ms1(ms1, ms2, mz_tol=0.5, rt_tol=16):
    print "Filtering MS1 to remove duplicates"
    # Filters the loaded ms1s to reduce the number of times that the same molecule has been fragmented


    # Sort the remaining ones by intensity
    ms1_by_intensity = sorted(ms1, key=lambda x: x.intensity, reverse=True)

    final_ms1_list = []
    final_ms2_list = []
    while True:
        if len(ms1_by_intensity) == 0:
            break
        # Take the highest intensity one, find things within the window and remove them
        current_ms1 = ms1_by_intensity[0]
        final_ms1_list.append(current_ms1)
        del ms1_by_intensity[0]

        current_mz = current_ms1.mz
        mz_err = mz_tol * 1.0 * current_mz / (1.0 * 1e6)
        min_mz = current_mz - mz_err
        max_mz = current_mz + mz_err

        min_rt = current_ms1.rt - rt_tol
        max_rt = current_ms1.rt + rt_tol

        # find things inside this region
        hits = filter(lambda x: x.mz > min_mz and x.mz < max_mz and x.rt > min_rt and x.rt < max_rt, ms1_by_intensity)
        for hit in hits:
            pos = ms1_by_intensity.index(hit)
            del ms1_by_intensity[pos]

    print "{} MS1 remaining".format(len(final_ms1_list))
    for m in ms2:
        if m[3] in final_ms1_list:
            final_ms2_list.append(m)

    print "{} MS2 remaining".format(len(final_ms2_list))
    return final_ms1_list, final_ms2_list