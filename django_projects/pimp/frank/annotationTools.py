__author__ = 'scott greig'

from frank.models import *
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from decimal import *
from suds.client import Client, WebFault
import time
import jsonpickle
import re
from pimp.settings_dev import BASE_DIR
from subprocess import call, CalledProcessError
import os
from django.db.models import Max
from urllib2 import URLError

class MassBankQueryTool():
    """
    Class to query the external API for MassBank - can be modified when MassBank installed on internal server
    """

    def __init__(self, annotation_query_id, fragmentation_set_id):
        """
        Constructor for the MassBankQuery Tool
        :param annotation_query_id: Integer id of a AnnotationQuery model instance
        :param fragmentation_set_id: Integer id of a FragmentationSet model instance
        """
        # Check to ensure these id'd correspond to existing model instances
        try:
            self.annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
            self.fragmentation_set = FragmentationSet.objects.get(id=fragmentation_set_id)
            self.annotation_tool = self.annotation_query.annotation_tool
        except MultipleObjectsReturned:
            raise
        except ObjectDoesNotExist:
            raise
        except TypeError:
            raise

    def get_mass_bank_annotations(self):
        """
        Method to form a query to massbank for retrieval of candidate annotations
        :return:
        """
        print 'Forming MassBank Query Spectra'
        # The query spectra comprise grouping of parent ions and there associated fragments
        query_spectra = self._generate_query_spectra()
        # If both there are query spectra to be sent, extract the positive and negative spectra
        if query_spectra:
            positive_spectra = query_spectra['positive_spectra']
            negative_spectra = query_spectra['negative_spectra']
        try:
            print 'Querying MassBank...'
            # Queries are only sent to MassBank if there are spectra to be sent
            if len(positive_spectra)>0:
                print 'Sending Positive Spectra...'
                positive_annotations = self._query_mass_bank(positive_spectra, 'Positive')
                if positive_annotations:
                    print 'Populating Positive Annotations...'
                    self._populate_annotations_table(positive_annotations)
                    print 'Postivie Annotations Populated...'
            if len(negative_spectra)>0:
                print 'Sending Negative Spectra...'
                negative_annotations = self._query_mass_bank(negative_spectra, 'Negative')
                if negative_annotations:
                    print 'Populating Negative Annotations...'
                    self._populate_annotations_table(positive_annotations)
        except WebFault:
            raise
        except URLError:
            raise
        except AttributeError:
            raise
        except MultipleObjectsReturned:
            raise
        except ObjectDoesNotExist:
            raise
        except ValidationError:
            raise
        except InvalidOperation:
            raise
        print 'MassBank Query Completed Successfully'
        return True


    def _generate_query_spectra(self):
        """
        Method to format the query to be sent to MassBank
        :return: query_spectra: A dictionary containing both the 'positive_spectra' and 'negative_spectra'
                                of the fragmentation set.
        """
        # Retrieve all peak associated with this fragmentation set
        sample_peak_qset = Peak.objects.filter(fragmentation_set=self.fragmentation_set)
        total_number_of_peaks = len(sample_peak_qset)
        # If there are no peaks then there is no query_spectra
        if total_number_of_peaks == 0:
            return None
        number_of_msn_levels = sample_peak_qset.aggregate(Max('msn_level'))
        number_of_msn_levels = number_of_msn_levels['msn_level__max']
        positive_samples_query = []
        negative_samples_query = []
        # Each msn level is considered in turn
        for level in range(1, (number_of_msn_levels)):
            # Get all the peaks in the level
            peaks_in_msn_level = sample_peak_qset.filter(msn_level=level)
            # For each peak
            for peak in peaks_in_msn_level:
                # Retrieve the polarity and slug (used here as a unique identifier)
                polarity = peak.source_file.polarity
                peak_identifier = peak.slug
                # Retrieve the fragments associated with the precursor peak
                fragmented_peaks = sample_peak_qset.filter(parent_peak=peak)
                # Only if there are fragments is the spectra added to the query
                if len(fragmented_peaks)>0:
                    spectrum_query_string = list('Name:'+peak_identifier+';')
                    for fragment in fragmented_peaks:
                        # The fragmentation spectra consists of mass and intensity pairs
                        spectrum_query_string.append(''+str(fragment.mass)+','+str(fragment.intensity)+';')
                    if polarity == 'Positive':
                        positive_samples_query.append(''.join(spectrum_query_string))
                    elif polarity == 'Negative':
                        negative_samples_query.append(''.join(spectrum_query_string))
        query_spectra = {
            'positive_spectra':positive_samples_query,
            'negative_spectra':negative_samples_query,
        }
        return query_spectra

    def _query_mass_bank(self, query_spectra, polarity):
        """
        Method to send the query to mass bank and retrieve the results set
        :return: mass_bank_results: The result set returned by mass_bank
        """
        # Check to ensure there are spectra to send to mass bank
        if len(query_spectra) == 0:
            return None
        mass_bank_parameters = jsonpickle.decode(self.annotation_query.annotation_tool_params)
        # MassBank provides a service to email the recipiant upon completion of query
        mail_address = mass_bank_parameters['mail_address']
        # Spectra can be queried against pre-specified instrument types
        instruments = mass_bank_parameters['instrument_types']
        # The polarity of the spectra is included - although can be 'both'
        # However, positive and negative were seperated to improve identification
        ion = polarity
        # get the search parameters from the database
        search_parameters = jsonpickle.decode(self.annotation_tool.default_params)
        search_type = search_parameters['type']
        client_address = search_parameters['client']
        type = search_type
        client = Client(client_address)
        try:
            # Submit the batch search to MassBank an job ID is returned
            submission_response = client.service.execBatchJob(
                type,
                mail_address,
                query_spectra,
                instruments,
                ion,
            )
        except WebFault:
            raise
        except URLError:
            raise
        job_id = submission_response
        job_list = [job_id]
        for seconds in range(0, 200):
            # Sleep for 5 minutes between queries to MassBank
            time.sleep(300)
            try:
                # Query MassBank for the status of the job
                job_status = client.service.getJobStatus(job_list)
                print job_status
            except WebFault:
                raise
            except URLError:
                raise
            if job_status['status'] == 'Completed':
                break
        # If MassBank has failed to complete the job in the alloted time
        if job_status['status']!='Completed':
            raise WebFault('MassBank Service Unavailable or Busy')
        else: # MassBank completed the query
            try:
                response3 = client.service.getJobResult(job_list)
            except WebFault:
                raise
            mass_bank_results = response3
            return mass_bank_results


    def populate_annotations_table(self, annotation_results):
        """
        Method to populate the database tables of the application using the results generated from massbank
        :param annotation_results:
        :return: True   Indicates that the results of the query have been successfully created in the database
        """
        for result_set_list in annotation_results:
            peak_identifier_slug = result_set_list['queryName']
            print 'Processing...'+peak_identifier_slug
            annotations = ()
            number_of_annotations = 0
            try:
                annotations = result_set_list['results']
                number_of_annotations = result_set_list['numResults']
            except AttributeError:
                raise
            try:
                peak_object = Peak.objects.get(slug=peak_identifier_slug)
            except MultipleObjectsReturned:
                raise
            except ObjectDoesNotExist:
                raise
            for index in range(0, number_of_annotations):
                each_annotation = annotations[index]
                elements_of_title = re.split('; ', each_annotation['title'])
                try:
                    compound_object = Compound.objects.get_or_create(
                        formula = each_annotation['formula'],
                        exact_mass = each_annotation['exactMass'],
                        name=elements_of_title[0],
                    )[0]
                    compound_annotation_tool = CompoundAnnotationTool.objects.get_or_create(
                        compound = compound_object,
                        annotation_tool = self.annotation_tool,
                        annotation_tool_identifier = each_annotation['id'],
                    )[0]
                    annotation_mass = Decimal(each_annotation['exactMass'])
                    difference_in_mass = peak_object.mass-annotation_mass
                    ## Justin's suggestion - I am maybe doing this may be incorrect
                    ppm = 1000000*abs(difference_in_mass)/annotation_mass
                    mass_match = False
                    if ppm < 3.0:
                        mass_match = True
                    ## Try and obtain the adduct and collision energy from the description
                    adduct_label = None
                    collision_energy = None
                    for element in elements_of_title:
                        # There might be a better way to identify the adduct
                        if element.startswith('[M'):
                            adduct_label = element
                        if element.startswith('CE'):
                            collision_energy = re.findall('CE:(\d+) V', element)[0]
                    CandidateAnnotation.objects.create(
                        compound = compound_object,
                        peak = peak_object,
                        confidence = each_annotation['score'],
                        annotation_query = self.annotation_query,
                        difference_from_peak_mass = difference_in_mass,
                        mass_match = mass_match,
                        adduct = adduct_label,
                        instrument_type = elements_of_title[1],
                        collision_energy = collision_energy,
                        additional_information = each_annotation['title']
                    )
                except ValidationError:
                    # If the annotation cannot be formatted to a model instance, it may be ignored
                    # The thinking here is it is better to return as many annotations as possible
                    print 'Invalid Annotation - Annotation Ignored'
                    pass
                except MultipleObjectsReturned:
                    raise
                except InvalidOperation:
                    # If the annotation cannot be formatted to a model instance, it may be ignored
                    # The thinking here is it is better to return as many annotations as possible
                    print 'Invalid Annotation - Annotation Ignored'
                    pass
        return True


class NISTQueryTool():

    def __init__(self, annotation_query_id):
        try:
            self.annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
            self.fragmentation_set = self.annotation_query.fragmentation_set
            self.annotation_tool = self.annotation_query.annotation_tool
        except ObjectDoesNotExist:
            raise
        except MultipleObjectsReturned:
            raise
        except TypeError:
            raise
        self.query_file_name = os.path.join(os.path.dirname(BASE_DIR), 'pimp', 'frank','NISTQueryFiles', str(self.annotation_query.id)+'.msp')
        self.nist_output_file_name = os.path.join(os.path.dirname(BASE_DIR), 'pimp', 'frank','NISTQueryFiles', str(self.annotation_query.id)+'_nist_out.txt')

    def get_nist_annotations(self):
        try:
            print 'Writing MSP File...'
            self._write_nist_msp_file()
            print 'Generating NIST subprocess call...'
            nist_query_call = self._generate_nist_call()
            print 'Querying NIST...'
            self._query_NIST(nist_query_call)
            print 'Populating Annotations Table...'
            self._populate_annotation_list()
            print 'Annotations Completed'
            os.remove(self.nist_output_file_name)
            os.remove(self.query_file_name)
        except IOError:
            raise
        except OSError:
            raise
        except ValueError:
            raise
        except MultipleObjectsReturned:
            raise
        except ObjectDoesNotExist:
            raise
        except Warning:
            raise
        return True

    def _generate_nist_call(self):
        # From the annotation query - get the user selected parameters
        nist_parameters = jsonpickle.decode(self.annotation_query.annotation_tool_params)
        tool_parameters = jsonpickle.decode(self.annotation_tool.default_params)
        library_list = nist_parameters['library']
        if len(library_list)==0:
            raise ValueError('No NIST Libraries were selected by the user')
        max_number_of_hits = nist_parameters['max_hits']
        if max_number_of_hits<1 or max_number_of_hits>100:
            raise ValueError('The maximum number of hits exceeds specified bounds (between 1 and 100)')
        search_type = nist_parameters['search_type']
        nist_query_call = ["wine",
                           tool_parameters['source'],
                           search_type,
                           "/HITS",
                           str(max_number_of_hits),
                           '/PATH',
                           tool_parameters['library_path']]
        for library in library_list:
            if library == 'mainlib':
                nist_query_call.extend(['/MAIN', 'mainlib'])
            elif library == 'nist_msms':
                nist_query_call.extend(['/LIB', 'nist_msms'])
            elif library == 'nist_msms2':
                nist_query_call.extend(['/LIB', 'nist_msms2'])
            elif library == 'nist_ri':
                nist_query_call.extend(['/LIB', 'nist_ri'])
            elif library == 'replib':
                nist_query_call.extend(['/REPL', 'replib'])
        additional_parameters = ['/INP', self.query_file_name,
                                 '/OUT', self.nist_output_file_name]
        nist_query_call.extend(additional_parameters)
        return nist_query_call


    def _query_NIST(self,nist_query_call):
        try:
            call(nist_query_call)
        except CalledProcessError:
            raise
        except OSError:
            raise
        # Finally check to see if the call was successfull
        if os.path.isfile(self.nist_output_file_name)==False:
            raise Warning('NIST failed to write the output file')
        return True


    def _write_nist_msp_file(self):
        #### MSP file format as follows
        #   NAME: name_of_query
        #   DB#: name_of_query
        #   Precursormz: mass_of_parent_ion (required for 'G' type search)
        #   Comments: nothing
        #   Num Peaks: number_of_peaks_in_spectra
        #   mass    intensity   ### For each of the peaks in the spectra
        try:
            # Open new MSP file for writing
            with open(self.query_file_name, "w") as output_file:
                # Retrieve all the peaks in the fragmentation set
                peaks_in_fragmentation_set = Peak.objects.filter(fragmentation_set = self.fragmentation_set)
                # Determine if there are peaks to be written to the MSP file
                if len(peaks_in_fragmentation_set)<1:
                    raise ValueError('No peaks found in fragmentation set')
                # Determine the number of msn levels
                number_of_msn_levels = peaks_in_fragmentation_set.aggregate(Max('msn_level'))
                number_of_msn_levels = number_of_msn_levels['msn_level__max']
                for level in range(1, number_of_msn_levels):
                    peaks_in_msn_level = peaks_in_fragmentation_set.filter(msn_level=level)
                    for peak in peaks_in_msn_level:
                        fragmentation_spectra = peaks_in_fragmentation_set.filter(parent_peak = peak)
                        if len(fragmentation_spectra)>0:
                            output_file.write('NAME: '+peak.slug+'\nDB#: '+str(peak.id)+'\nComments: None\nPrecursormz:'+str(peak.mass)+'\nNum Peaks: '+str(len(fragmentation_spectra))+'\n')
                            for fragment in fragmentation_spectra:
                                output_file.write(str(fragment.mass)+' '+str(fragment.intensity)+'\n')
                            output_file.write('\n')
        except IOError:
            raise
        finally:
            # Using 'with' should close the file but make sure
            if output_file.closed==False:
                output_file.close()
        return True


    def _populate_annotation_list(self):
        peaks_in_fragmentation_set = Peak.objects.filter(fragmentation_set = self.fragmentation_set)
        try:
            with open(self.nist_output_file_name, "r") as input_file:
                current_parent_peak = None
                ## For each line which does not begin in a comment (in NIST.txt this is indicated by '>')
                for line in (line for line in input_file if not line.startswith('>')):
                    try:
                        line = line.decode('cp437').encode('utf-8', errors='strict')
                    except UnicodeError as ue:
                        print ue.message
                        # This type of error results from NIST output files using cp437 characters
                        # which seems to only impact on greek letters...therefore, exception is passed
                        pass
                    if line.startswith('Unknown:'):
                        # These lines indicate the title of the query spectra - i.e. the peak slug identifier
                        line_tokens = [token.split() for token in line.splitlines()]
                        parent_ion_slug = line_tokens[0][1]
                        if parent_ion_slug.startswith('<<') and parent_ion_slug.endswith('>>'):
                            ## The parent_ion_slug is encased in <<peak_slug>>, so create substring
                            parent_ion_slug = parent_ion_slug[2:-2]
                        try:
                            current_parent_peak = peaks_in_fragmentation_set.get(slug = parent_ion_slug)
                            print 'Populating Annotations For: '+current_parent_peak.slug
                        except MultipleObjectsReturned:
                            raise
                        except ObjectDoesNotExist:
                            raise
                    elif line.startswith('Hit'):
                        annotation_description = line.splitlines()[0]
                        string_annotation_attributes = re.findall('<<(.*?)>>', annotation_description, re.DOTALL)
                        compound_name = string_annotation_attributes[0]
                        compound_formula = string_annotation_attributes[1]
                        annotation_confidence = Decimal(re.findall('Prob: (.*?);', annotation_description, re.DOTALL)[0])
                        compound_cas = re.findall('CAS:(.*?);', annotation_description, re.DOTALL)[0]
                        if compound_cas == '0-00-0':
                            compound_cas = None
                        compound_mass = Decimal(re.findall('Mw: (.*?);', annotation_description, re.DOTALL)[0])
                        compound_annotation_tool_identifier = re.findall('Id: (\d+).', annotation_description)[0]
                        try:
                            compound_object = Compound.objects.get_or_create(
                                formula = compound_formula,
                                exact_mass = compound_mass,
                                name=compound_name,
                                cas_code=compound_cas,
                            )[0]
                            compound_annotation_tool = CompoundAnnotationTool.objects.get_or_create(
                                compound = compound_object,
                                annotation_tool = self.annotation_tool,
                                annotation_tool_identifier = compound_annotation_tool_identifier,
                            )[0]
                            difference_in_mass = current_parent_peak.mass-compound_mass
                            ## Justin's suggestion - I am maybe doing this wrong
                            ppm = 1000000*abs(difference_in_mass)/compound_mass
                            mass_match = False
                            if ppm < 3.0:
                                mass_match = True
                            CandidateAnnotation.objects.create(
                                compound = compound_object,
                                peak = current_parent_peak,
                                confidence = annotation_confidence,
                                annotation_query = self.annotation_query,
                                difference_from_peak_mass = difference_in_mass,
                                mass_match = mass_match,
                                additional_information = annotation_description
                            )
                        except ValidationError as ve:
                            print ve.message
                            # In the event of a validation error, simply ignore this candidate annotation
                            # and resume trying to add the remaining annotations
                            pass
                        except MultipleObjectsReturned:
                            raise
        except IOError:
            raise
        finally:
            # Using 'with' should close the file but make sure
            if input_file.closed==False:
                input_file.close()
        return True